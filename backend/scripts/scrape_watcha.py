"""
观猹 (watcha.cn) 数据爬虫

功能：
  - 抓取所有 AI 产品：名称、描述、slogan、logo、官网、分类、评分、标签等
  - 抓取每个产品的用户评论（猹评）
  - 将结果保存为 JSON 文件，供 sync_watcha.py 导入数据库

使用方法：
  # 全量抓取（默认保存到 data/watcha_products.json）
  python scrape_watcha.py

  # 只抓取前 N 个产品（用于测试）
  python scrape_watcha.py --limit 10

  # 指定输出文件
  python scrape_watcha.py --output /tmp/watcha_data.json

  # 只抓取指定 slug 的产品
  python scrape_watcha.py --slugs chatgpt claude alice

  # 跳过评论抓取（加快速度）
  python scrape_watcha.py --no-reviews
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Optional

import requests

# ─────────────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────────────

BASE_URL = "https://watcha.cn"
API_BASE = f"{BASE_URL}/api/v2"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": BASE_URL + "/",
    "Origin": BASE_URL,
})

DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "data", "watcha_products.json")


# ─────────────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────────────

def _get(path: str, params: dict = None, retry: int = 3) -> Optional[dict]:
    """带重试的 GET 请求。"""
    url = f"{API_BASE}{path}"
    for attempt in range(retry):
        try:
            r = SESSION.get(url, params=params, timeout=12)
            if r.status_code == 429:
                wait = (attempt + 1) * 5
                print(f"    ⚠ 限流，等待 {wait}s …")
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()
            if data.get("statusCode") == 200:
                return data.get("data")
            return None
        except requests.exceptions.Timeout:
            print(f"    ⚠ 超时，重试 {attempt+1}/{retry} …")
            time.sleep(2)
        except Exception as e:
            print(f"    ✗ 请求失败 [{path}]: {e}")
            return None
    return None


def _rich_text_to_plain(content_json: str) -> str:
    """
    将观猹富文本 JSON（ProseMirror 格式）转为纯文本。
    结构：{"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"…"}]}]}
    """
    if not content_json:
        return ""
    try:
        doc = json.loads(content_json) if isinstance(content_json, str) else content_json
    except (json.JSONDecodeError, TypeError):
        return str(content_json)

    parts = []

    def _walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text":
                parts.append(node.get("text", ""))
            if node.get("type") == "hardBreak":
                parts.append("\n")
            for child in node.get("content", []):
                _walk(child)
            if node.get("type") in ("paragraph", "heading", "bulletList", "orderedList", "listItem"):
                if parts and parts[-1] != "\n":
                    parts.append("\n")
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(doc)
    return "".join(parts).strip()


def _extract_images(images_field) -> list[str]:
    """images 字段可能是逗号分隔字符串或列表，统一转为列表。"""
    if not images_field:
        return []
    if isinstance(images_field, list):
        return [str(i) for i in images_field if i]
    if isinstance(images_field, str):
        return [u.strip() for u in images_field.split(",") if u.strip()]
    return []


# ─────────────────────────────────────────────────────
# 核心抓取函数
# ─────────────────────────────────────────────────────

def fetch_product_list(batch_size: int = 20, max_items: int = 0) -> list[dict]:
    """
    分页抓取产品列表（基础信息）。
    观猹 API 使用 skip+limit 游标分页（不支持 page 参数）。
    max_items=0 表示不限制数量。
    """
    all_items: list[dict] = []
    skip = 0
    while True:
        if max_items and len(all_items) >= max_items:
            break
        fetch_size = batch_size
        if max_items:
            fetch_size = min(batch_size, max_items - len(all_items))
        print(f"  📄 产品列表 skip={skip} …")
        data = _get("/products", params={"skip": skip, "limit": fetch_size})
        if not data:
            break
        items = data.get("items") or []
        if not items:
            break
        all_items.extend(items)
        print(f"     获取 {len(items)} 条，累计 {len(all_items)}")
        if len(items) < fetch_size:
            break
        skip += len(items)
        time.sleep(0.8)
    return all_items


def fetch_product_detail(slug: str) -> Optional[dict]:
    """抓取单个产品详情。"""
    return _get(f"/products/{slug}")


def fetch_product_reviews(product_id: int, max_pages: int = 5) -> list[dict]:
    """抓取产品的猹评（最多 max_pages 页）。"""
    all_reviews = []
    page = 1
    while page <= max_pages:
        data = _get(f"/products/{product_id}/reviews", params={"page": page, "page_size": 20})
        if not data:
            break
        items = data.get("items", [])
        all_reviews.extend(items)
        if len(items) < 20:
            break
        page += 1
        time.sleep(0.5)
    return all_reviews


def parse_product(raw: dict) -> dict:
    """将 API 原始产品数据转换为结构化字典。"""
    stats = raw.get("stats", {}) or {}
    categories = [c.get("name", "") for c in (raw.get("categories") or [])]
    tags = [t.get("name", "") for t in ((raw.get("tag") or {}).get("items") or [])]

    # 解析富文本描述
    desc_raw = raw.get("description", "")
    description = _rich_text_to_plain(desc_raw)

    return {
        "external_id":   str(raw["id"]),
        "external_slug": raw.get("slug", ""),
        "name":          raw.get("name", ""),
        "slogan":        raw.get("slogan", ""),          # 一句话简介
        "description":   description,                     # 详细描述（纯文本）
        "organization":  raw.get("organization", ""),     # 开发商/组织
        "logo_url":      raw.get("avatar_url", ""),       # logo 图片
        "cover_url":     raw.get("image_url", ""),        # 封面图
        "images":        _extract_images(raw.get("images")),
        "website_url":   raw.get("website_url", ""),      # 官网
        "categories":    categories,
        "tags":          tags,
        "score":         stats.get("score", 0.0),         # 综合评分
        "review_count":  stats.get("review_count", 0),
        "upvotes":       stats.get("upvotes", 0),
        "stars":         stats.get("stars", 0),
        "source":        "watcha",
        "watcha_url":    f"https://watcha.cn/products/{raw.get('slug', '')}",
        "scraped_at":    datetime.utcnow().isoformat(),
    }


def parse_review(raw: dict) -> dict:
    """将 API 原始评论数据转换为结构化字典。"""
    content_raw = raw.get("content", {})
    content_text = _rich_text_to_plain(content_raw)
    stats = raw.get("stats", {}) or {}
    user = raw.get("user", {}) or {}

    # 评分从 vote_value（1=赞, -1=踩）或 stats.score 里取
    score = None
    if raw.get("vote_value") is not None:
        score = 10.0 if raw["vote_value"] >= 1 else None  # watcha 没有显式评分，只有点赞/踩

    return {
        "external_id":          str(raw["id"]),
        "content":              content_text,
        "score":                score,
        "author_name":          user.get("nickname", ""),
        "author_avatar":        user.get("avatar_url", ""),
        "upvotes":              stats.get("upvotes", raw.get("vote_value", 0)),
        "reply_count":          raw.get("reply_count", 0),
        "external_created_at":  raw.get("create_at", ""),
    }


# ─────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="观猹 watcha.cn 产品数据爬虫")
    parser.add_argument("--output",     default=DEFAULT_OUTPUT, help="输出 JSON 文件路径")
    parser.add_argument("--limit",      type=int, default=0,    help="只抓前 N 个产品（0=全量）")
    parser.add_argument("--slugs",      nargs="+",              help="只抓指定 slug")
    parser.add_argument("--no-reviews", action="store_true",    help="跳过评论抓取")
    parser.add_argument("--max-review-pages", type=int, default=3, help="每个产品最多抓几页评论")
    parser.add_argument("--delay",      type=float, default=1.0, help="请求间隔秒数")
    args = parser.parse_args()

    # 初始化 session（获取 cookie）
    print("🌐 初始化会话…")
    try:
        SESSION.get(BASE_URL, timeout=10)
    except Exception:
        pass

    # 获取产品列表
    if args.slugs:
        print(f"📋 仅抓取指定产品：{args.slugs}")
        basic_list = [{"slug": s} for s in args.slugs]
    else:
        print("📋 抓取产品列表…")
        basic_list = fetch_product_list(max_items=args.limit)
        print(f"✅ 共 {len(basic_list)} 个产品\n")

    results = []
    total = len(basic_list)

    for i, basic in enumerate(basic_list, 1):
        slug = basic.get("slug") or basic.get("external_slug", "")
        print(f"[{i}/{total}] {slug}")

        # 详情
        detail_raw = fetch_product_detail(slug)
        if not detail_raw:
            print(f"  ✗ 详情获取失败，跳过")
            time.sleep(args.delay)
            continue

        product = parse_product(detail_raw)
        product["reviews"] = []

        # 评论
        if not args.no_reviews:
            product_id = detail_raw.get("id")
            if product_id:
                raw_reviews = fetch_product_reviews(product_id, args.max_review_pages)
                product["reviews"] = [parse_review(r) for r in raw_reviews]
                print(f"  ✓ {product['name']} | score={product['score']:.1f} | {len(product['reviews'])} 条评论")
            time.sleep(args.delay * 0.5)
        else:
            print(f"  ✓ {product['name']} | score={product['score']:.1f}")

        results.append(product)
        time.sleep(args.delay)

    # 保存结果
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "scraped_at": datetime.utcnow().isoformat(),
            "total":      len(results),
            "products":   results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 完成！共抓取 {len(results)} 个产品，已保存到：{output_path}")


if __name__ == "__main__":
    main()
