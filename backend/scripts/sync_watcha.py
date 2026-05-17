"""
观猹数据同步脚本

将 scrape_watcha.py 输出的 JSON 数据导入到 TrueAI 数据库。

功能：
  - 按名称匹配已有工具 → 更新；无匹配 → 新建
  - 同步导入外部评论（去重，已存在的跳过）
  - 自动创建并绑定分类（如 watcha 分类与本站分类名相同则复用）

使用方法：
  # 从默认路径读取并同步
  python sync_watcha.py

  # 指定 JSON 文件
  python sync_watcha.py --input /tmp/watcha_data.json

  # 只更新已有工具，不新建
  python sync_watcha.py --no-create

  # 预览，不写入数据库
  python sync_watcha.py --dry-run

  # 跳过评论同步
  python sync_watcha.py --no-reviews
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Tool, ToolCategory, Category
from app.models.external_review import ExternalReview

DEFAULT_INPUT = os.path.join(os.path.dirname(__file__), "..", "data", "watcha_products.json")

# watcha 分类名 → 本站 slug 映射（可按需扩展）
CATEGORY_MAP = {
    "通用助手":  "general",
    "图像生成":  "image-gen",
    "视频生成":  "video-gen",
    "音频生成":  "audio-gen",
    "代码助手":  "coding",
    "写作助手":  "writing",
    "搜索引擎":  "search",
    "办公效率":  "productivity",
    "智能体":   "agent",
    "数据分析":  "data",
    "教育学习":  "education",
    "设计工具":  "design",
    "3D生成":   "3d-gen",
    "游戏娱乐":  "game",
}

# watcha 标签 → 本站 form_factor 映射
TAG_FORM_FACTOR_MAP = {
    "Web":   "saas",
    "iOS":   "mobile",
    "Android": "mobile",
    "App":   "mobile",
    "CLI":   "cli",
    "桌面端":  "windows_app",
    "浏览器插件": "web",
}


# ─────────────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────────────

def _resolve_form_factor(tags: list[str]) -> str:
    for tag in tags:
        if tag in TAG_FORM_FACTOR_MAP:
            return TAG_FORM_FACTOR_MAP[tag]
    return "saas"


def _get_or_create_category(db: Session, name: str, dry_run: bool) -> int | None:
    """按名称查找分类，不存在则创建（使用映射 slug）。"""
    slug = CATEGORY_MAP.get(name)
    if not slug:
        slug = name.lower().replace(" ", "-").replace("/", "-")

    cat = db.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()
    if cat:
        return cat.id
    cat = db.execute(select(Category).where(Category.name == name)).scalar_one_or_none()
    if cat:
        return cat.id

    # 新建分类
    if not dry_run:
        cat = Category(name=name, slug=slug, sort_order=99)
        db.add(cat)
        db.flush()
        return cat.id
    return None


def _match_existing_tool(db: Session, product: dict) -> Tool | None:
    """按 external_id / external_slug / 名称精确匹配已有工具。"""
    # 优先按外部 ID 匹配
    t = db.execute(
        select(Tool).where(Tool.external_id == product["external_id"])
    ).scalar_one_or_none()
    if t:
        return t
    # 按 slug 匹配
    t = db.execute(
        select(Tool).where(Tool.slug == product["external_slug"])
    ).scalar_one_or_none()
    if t:
        return t
    # 按名称精确匹配
    t = db.execute(
        select(Tool).where(Tool.name == product["name"])
    ).scalar_one_or_none()
    return t


def _make_slug(name: str, existing_slugs: set[str]) -> str:
    """将名称转为 slug，避免重复。"""
    import re
    base = re.sub(r'[^\w\u4e00-\u9fff-]', '-', name.lower()).strip('-')
    base = re.sub(r'-+', '-', base)
    slug = base
    i = 2
    while slug in existing_slugs:
        slug = f"{base}-{i}"
        i += 1
    return slug


def _sync_tool(db: Session, product: dict, dry_run: bool, no_create: bool) -> tuple[Tool | None, str]:
    """
    同步单个产品到 tools 表。
    返回 (tool, action)  action = 'created' | 'updated' | 'skipped'
    """
    existing = _match_existing_tool(db, product)

    if existing:
        # 更新
        if not dry_run:
            existing.external_id   = product["external_id"]
            existing.external_slug = product["external_slug"]
            existing.source        = "watcha"
            if product.get("logo_url"):
                existing.logo_url = product["logo_url"]
            if product.get("slogan") and not existing.tagline:
                existing.tagline = product["slogan"][:255]
            if product.get("description") and not existing.description:
                existing.description = product["description"]
            if product.get("website_url") and not existing.official_url:
                existing.official_url = product["website_url"]
            if product.get("organization") and not existing.developer:
                existing.developer = product["organization"][:128]
        return existing, "updated"

    if no_create:
        return None, "skipped"

    # 新建
    existing_slugs = set(
        r[0] for r in db.execute(select(Tool.slug)).all()
    )
    slug = _make_slug(product["name"], existing_slugs)

    tool = Tool(
        name          = product["name"][:128],
        slug          = slug,
        tagline       = (product.get("slogan") or "")[:255] or None,
        description   = product.get("description") or None,
        logo_url      = product.get("logo_url") or None,
        official_url  = product.get("website_url") or None,
        developer     = (product.get("organization") or "")[:128] or None,
        form_factor   = _resolve_form_factor(product.get("tags", [])),
        is_free       = True,
        need_vpn      = False,
        support_cli   = "CLI" in product.get("tags", []),
        support_api   = "API" in product.get("tags", []),
        overall_score = round(min(max(float(product.get("score", 0)) * 10, 0), 10), 1),
        review_count  = product.get("review_count", 0),
        source        = "watcha",
        external_id   = product["external_id"],
        external_slug = product["external_slug"],
    )
    if not dry_run:
        db.add(tool)
        db.flush()   # 获取 tool.id

    return tool, "created"


def _sync_categories(db: Session, tool: Tool, categories: list[str], dry_run: bool):
    """同步工具分类关联。"""
    for cat_name in categories:
        if not cat_name:
            continue
        cat_id = _get_or_create_category(db, cat_name, dry_run)
        if cat_id is None:
            continue
        exists = db.execute(
            select(ToolCategory).where(
                ToolCategory.tool_id == tool.id,
                ToolCategory.category_id == cat_id,
            )
        ).scalar_one_or_none()
        if not exists and not dry_run:
            db.add(ToolCategory(tool_id=tool.id, category_id=cat_id))


def _sync_reviews(
    db: Session, tool: Tool, reviews: list[dict], dry_run: bool
) -> tuple[int, int]:
    """同步外部评论，返回 (added, skipped)。"""
    added = skipped = 0
    for rev in reviews:
        content = (rev.get("content") or "").strip()
        if not content:
            skipped += 1
            continue
        ext_id = str(rev["external_id"])
        exists = db.execute(
            select(ExternalReview).where(
                ExternalReview.tool_id == tool.id,
                ExternalReview.external_id == ext_id,
            )
        ).scalar_one_or_none()
        if exists:
            skipped += 1
            continue

        ext_created = None
        if rev.get("external_created_at"):
            try:
                ext_created = datetime.fromisoformat(
                    rev["external_created_at"].replace("Z", "+00:00")
                )
            except ValueError:
                pass

        if not dry_run:
            db.add(ExternalReview(
                tool_id             = tool.id,
                source              = "watcha",
                external_id         = ext_id,
                content             = content,
                score               = rev.get("score"),
                author_name         = (rev.get("author_name") or "")[:128] or None,
                author_avatar       = (rev.get("author_avatar") or "")[:512] or None,
                upvotes             = int(rev.get("upvotes") or 0),
                reply_count         = int(rev.get("reply_count") or 0),
                external_created_at = ext_created,
            ))
        added += 1

    return added, skipped


# ─────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="将观猹数据同步到 TrueAI 数据库")
    parser.add_argument("--input",      default=DEFAULT_INPUT, help="JSON 文件路径")
    parser.add_argument("--dry-run",    action="store_true",   help="预览，不写入数据库")
    parser.add_argument("--no-create",  action="store_true",   help="只更新已有工具，不新建")
    parser.add_argument("--no-reviews", action="store_true",   help="跳过评论同步")
    args = parser.parse_args()

    # 读取 JSON
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"✗ 文件不存在：{input_path}")
        print("  请先运行 scrape_watcha.py 生成数据文件")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("products", [])
    print(f"📂 读取文件：{input_path}")
    print(f"📦 共 {len(products)} 个产品（爬取于 {data.get('scraped_at', '?')}）\n")

    if args.dry_run:
        print("🔵 [dry-run 模式] 不会实际写入数据库\n")

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

    stats = {"created": 0, "updated": 0, "skipped": 0,
             "reviews_added": 0, "reviews_skipped": 0}

    with Session(engine) as db:
        for i, product in enumerate(products, 1):
            name = product.get("name", "?")
            print(f"[{i}/{len(products)}] {name}", end="")

            try:
                tool, action = _sync_tool(db, product, args.dry_run, args.no_create)
            except Exception as e:
                print(f"  ✗ 同步失败: {e}")
                db.rollback()
                continue

            stats[action] += 1

            rev_added = rev_skipped = 0
            if tool and not args.no_reviews and product.get("reviews"):
                if not args.dry_run or True:   # dry-run 也统计
                    try:
                        rev_added, rev_skipped = _sync_reviews(
                            db, tool, product["reviews"], args.dry_run
                        )
                        stats["reviews_added"]   += rev_added
                        stats["reviews_skipped"] += rev_skipped
                    except Exception as e:
                        print(f"  ⚠ 评论同步失败: {e}")
                        db.rollback()

            mark = {"created": "✨", "updated": "✏️", "skipped": "⏭"}.get(action, "?")
            print(f"  {mark} {action}  评论 +{rev_added} (跳过 {rev_skipped})")

            if not args.dry_run:
                try:
                    if tool and tool.id and product.get("categories"):
                        _sync_categories(db, tool, product["categories"], args.dry_run)
                    db.commit()
                except Exception as e:
                    print(f"  ✗ 提交失败: {e}")
                    db.rollback()

    print(f"""
┌───────────────────────────────────────┐
│  同步完成                              │
├───────────────────────────────────────┤
│  工具 - 新建  : {stats['created']:>6}               │
│  工具 - 更新  : {stats['updated']:>6}               │
│  工具 - 跳过  : {stats['skipped']:>6}               │
│  评论 - 导入  : {stats['reviews_added']:>6}               │
│  评论 - 重复  : {stats['reviews_skipped']:>6}               │
└───────────────────────────────────────┘""")


if __name__ == "__main__":
    main()
