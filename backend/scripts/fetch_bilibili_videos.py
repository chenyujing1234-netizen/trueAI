"""
自动从 B 站搜索 AI 工具介绍/评测视频，并将视频链接写入数据库。

使用方法：
  # 为所有缺少视频的工具搜索（每次运行只更新没有 video_url 的工具）
  python fetch_bilibili_videos.py

  # 强制刷新所有工具（覆盖已有 video_url）
  python fetch_bilibili_videos.py --force

  # 只处理指定工具 slug
  python fetch_bilibili_videos.py --slugs chatgpt claude gemini

  # 只预览，不写入数据库
  python fetch_bilibili_videos.py --dry-run

选择策略：
  - 只选 "评测" 或 "介绍" 类视频（通过标题关键词过滤）
  - 按综合权重排序：播放量 × 0.5 + 点赞数 × 0.3 + 弹幕数 × 0.2
  - 优先选时长 3～30 分钟的视频（更有深度）
  - 过滤掉时长 < 60 秒的短视频
"""

import argparse
import re
import sys
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sqlalchemy as sa
from sqlalchemy import create_engine, text

sys.path.insert(0, "/home/chenyj/TrueAI/backend")
from app.core.config import settings

# ──────────────────────────────────────────────
# B 站公开搜索 API（无需登录）
# ──────────────────────────────────────────────
BILIBILI_SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://www.bilibili.com",
}

# 使用 Session + 自动重试，缓解 B 站频率限制
_session = requests.Session()
_session.headers.update(HEADERS)
# 先访问一次首页以获取必要 Cookie（bili_jct / buvid3 等）
try:
    _session.get("https://www.bilibili.com", timeout=8)
except Exception:
    pass

# 一级关键词：真正的评测 / 深度体验类，命中即加分
REVIEW_KEYWORDS = [
    "评测", "测评", "对比", "体验", "好用吗", "值得吗", "值得买",
    "深度", "实测", "横评", "review", "值不值", "怎么样", "好不好",
    "上手", "开箱",
]

# 二级关键词：使用介绍类，可作兜底，但不如一级
INTRO_KEYWORDS = [
    "介绍", "教程", "使用", "guide", "tutorial", "怎么用",
    "入门", "保姆级", "全攻略", "攻略",
]

# 黑名单：纯安装/注册/登录类视频，直接排除（除非同时含一级关键词）
EXCLUDE_KEYWORDS = [
    "安装", "注册", "登录", "登陆", "下载", "科学上网", "梯子",
    "破解", "白嫖", "免费领", "激活码",
]

# 搜索附加词，专注评测
SEARCH_SUFFIX = "评测 使用体验"


def search_bilibili(keyword: str, max_results: int = 20, retry: int = 3) -> list[dict]:
    """调用 B 站搜索 API，返回视频列表。遇到 412 限流自动退避重试。"""
    params = {
        "search_type": "video",
        "keyword": f"{keyword} {SEARCH_SUFFIX}",
        "order": "totalrank",
        "page": 1,
        "page_size": max_results,
    }
    for attempt in range(retry):
        try:
            resp = _session.get(BILIBILI_SEARCH_URL, params=params, timeout=10)
            if resp.status_code == 412:
                wait = (attempt + 1) * 4
                print(f"  ⚠ 触发限流(412)，等待 {wait}s 后重试…")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != 0:
                print(f"  ⚠ B 站 API 错误: {data.get('message')}")
                return []
            return data.get("data", {}).get("result", [])
        except requests.HTTPError:
            if attempt < retry - 1:
                time.sleep((attempt + 1) * 3)
        except Exception as e:
            print(f"  ✗ 搜索请求失败: {e}")
            return []
    print(f"  ✗ 重试 {retry} 次后仍失败，跳过")
    return []


def classify_title(title: str) -> str:
    """
    对标题分类：
      'review'  — 命中一级评测词，且未被黑名单屏蔽
      'intro'   — 命中二级介绍词，且未被黑名单屏蔽
      'exclude' — 命中黑名单且无一级评测词
      'none'    — 无任何有效关键词
    """
    t = title.lower()
    has_review = any(kw in t for kw in REVIEW_KEYWORDS)
    has_intro  = any(kw in t for kw in INTRO_KEYWORDS)
    has_excl   = any(kw in t for kw in EXCLUDE_KEYWORDS)

    if has_excl and not has_review:
        return "exclude"
    if has_review:
        return "review"
    if has_intro:
        return "intro"
    return "none"


def score_video(video: dict, title_class: str = "intro") -> float:
    """
    综合权重评分：播放量 × 0.5 + 点赞数 × 0.3 + 弹幕数 × 0.2
    - 评测类视频得分 × 3.0 倍，让其始终优先于教程类
    - 时长 5～25 分钟最佳，< 1 分钟直接 0 分
    """
    duration = parse_duration(video.get("duration", "0:00"))
    if duration < 60:
        return 0.0

    play    = int(str(video.get("play", 0)).replace(",", "") or 0)
    like    = int(str(video.get("like", 0)).replace(",", "") or 0)
    danmaku = int(str(video.get("video_review", 0)).replace(",", "") or 0)

    raw = play * 0.5 + like * 0.3 + danmaku * 0.2

    # 时长加权：5～25 分钟满分
    if 300 <= duration <= 1500:
        duration_factor = 1.0
    elif duration < 300:
        duration_factor = duration / 300
    else:
        duration_factor = 1500 / duration

    # 评测类视频额外 3 倍加权，确保排在纯教程前面
    review_factor = 3.0 if title_class == "review" else 1.0

    return raw * duration_factor * review_factor


def parse_duration(s: str) -> int:
    """'12:34' → 秒数。"""
    parts = str(s).strip().split(":")
    try:
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except ValueError:
        pass
    return 0


def title_contains_name(title: str, tool_name: str) -> bool:
    """标题里是否含有工具名（不区分大小写），短名称（≤3字）要求更严格的完整词匹配。"""
    title_lower = title.lower()
    name_lower = tool_name.lower()
    # 取工具名的第一个词（英文名通常是前缀）
    first_token = name_lower.split()[0]
    if len(first_token) <= 3:
        # 短名称防止误匹配，要求作为独立词出现
        return bool(re.search(rf"\b{re.escape(first_token)}\b", title_lower))
    return first_token in title_lower


def pick_best_video(tool_name: str) -> Optional[str]:
    """
    搜索并筛选最佳视频，返回 BV 号，失败返回 None。

    三轮筛选（依次尝试，前一轮有结果就不进下一轮）：
      1. 标题含工具名 + 一级评测词（最严格，质量最高）
      2. 标题含工具名 + 二级介绍词（放宽，但仍需含工具名）
      3. 仅含一级评测词（无工具名要求，最后兜底）
    黑名单词（安装/注册/登陆…）始终排除，除非同时含评测词。
    """
    print(f"  🔍 搜索：{tool_name} {SEARCH_SUFFIX}")
    results = search_bilibili(tool_name)

    # 预处理
    parsed = []
    for v in results:
        title = re.sub(r"<[^>]+>", "", v.get("title", ""))
        bvid  = v.get("bvid", "")
        if not bvid:
            continue
        tc = classify_title(title)
        if tc == "exclude" or tc == "none":
            continue
        s = score_video(v, tc)
        if s > 0:
            parsed.append((s, bvid, title, tc))

    def filter_by(require_name: bool, require_review: bool):
        out = []
        for s, bvid, title, tc in parsed:
            if require_review and tc != "review":
                continue
            if require_name and not title_contains_name(title, tool_name):
                continue
            out.append((s, bvid, title))
        return sorted(out, reverse=True)

    # 第 1 轮：含工具名 + 一级评测词
    candidates = filter_by(require_name=True, require_review=True)
    tier = "①含工具名+评测词"

    # 第 2 轮：含工具名 + 介绍词（评测词放宽）
    if not candidates:
        candidates = filter_by(require_name=True, require_review=False)
        tier = "②含工具名+介绍词"

    # 第 3 轮：仅评测词（放宽工具名要求）
    if not candidates:
        candidates = filter_by(require_name=False, require_review=True)
        tier = "③仅评测词兜底"

    if not candidates:
        print("  → 未找到符合条件的视频")
        return None

    best_score, best_bvid, best_title = candidates[0]
    print(f"  ✓ [{tier}] {best_title[:55]}  [{best_bvid}]  (score={best_score:.0f})")
    return best_bvid


# ──────────────────────────────────────────────
# 数据库操作
# ──────────────────────────────────────────────

def get_tools(engine, slugs: list[str] = None, force: bool = False) -> list[dict]:
    with engine.connect() as conn:
        if slugs:
            result = conn.execute(
                text("SELECT id, name, slug, video_url FROM tools WHERE slug IN :slugs"),
                {"slugs": tuple(slugs)},
            )
        elif force:
            result = conn.execute(
                text("SELECT id, name, slug, video_url FROM tools ORDER BY id")
            )
        else:
            result = conn.execute(
                text("SELECT id, name, slug, video_url FROM tools WHERE video_url IS NULL ORDER BY id")
            )
        return [dict(row._mapping) for row in result]


def update_video_url(engine, tool_id: int, bvid: str) -> None:
    video_url = f"https://www.bilibili.com/video/{bvid}"
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE tools SET video_url = :url WHERE id = :id"),
            {"url": video_url, "id": tool_id},
        )


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="自动抓取 B 站 AI 工具介绍视频链接")
    parser.add_argument("--slugs", nargs="+", help="只处理指定的工具 slug")
    parser.add_argument("--force", action="store_true", help="强制刷新已有 video_url 的工具")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不写入数据库")
    parser.add_argument("--delay", type=float, default=3.0, help="每次请求间隔（秒），默认 3.0")
    args = parser.parse_args()

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

    tools = get_tools(engine, slugs=args.slugs, force=args.force)
    if not tools:
        print("没有需要处理的工具，退出。")
        return

    print(f"共需处理 {len(tools)} 个工具\n")
    updated, skipped, failed = 0, 0, 0

    for tool in tools:
        print(f"[{tool['slug']}] {tool['name']}")
        bvid = pick_best_video(tool["name"])
        if bvid:
            if not args.dry_run:
                update_video_url(engine, tool["id"], bvid)
                print(f"  💾 已写入数据库")
            else:
                print(f"  🔵 dry-run，跳过写入")
            updated += 1
        else:
            failed += 1
        time.sleep(args.delay)   # 避免触发反爬

    print(f"\n完成：成功 {updated}，失败 {failed}，跳过 {skipped}")


if __name__ == "__main__":
    main()
