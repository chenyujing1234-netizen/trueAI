"""基于 query 从 MySQL 召回候选工具。

关键词抽取当前采用简单规则：对 query 按空格/标点切分 + 与类目/audience 字典匹配。
后续可替换为 LLM 结构化输出。
"""

from __future__ import annotations

import re

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Category, Tool, ToolAudience, ToolCategory


CATEGORY_ALIASES: dict[str, list[str]] = {
    "coding": ["编程", "代码", "程序员", "开发", "coding", "code", "ide", "编辑器"],
    "writing": ["写作", "文案", "写文章", "公众号", "小红书", "writing"],
    "image": ["画图", "绘画", "生图", "图片", "图像", "image", "ai画", "midjourney", "sd"],
    "video": ["视频", "剪辑", "短视频", "video"],
    "audio": ["音乐", "作曲", "配音", "语音", "tts", "audio"],
    "design": ["设计", "海报", "ppt", "logo", "ui", "设计稿"],
    "office": ["办公", "表格", "excel", "ppt", "word", "文档"],
    "search": ["搜索", "查资料", "search", "研究"],
    "agent": ["智能体", "agent", "bot", "机器人", "工作流", "自动化"],
    "translate": ["翻译", "英文", "translate"],
    "learning": ["学习", "考试", "论文", "教育"],
    "chat": ["聊天", "对话", "问答"],
}

AUDIENCE_ALIASES: dict[str, list[str]] = {
    "beginner": ["小白", "新手", "入门", "零基础"],
    "developer": ["程序员", "开发", "工程师"],
    "student": ["学生", "学习"],
    "designer": ["设计师", "设计"],
    "creator": ["创作者", "博主", "up主", "内容"],
    "child": ["小孩", "儿童"],
    "senior": ["老人", "长辈"],
    "female": ["女性", "小姐姐"],
}


def extract_intents(query: str) -> dict[str, list[str]]:
    q = query.lower()
    cats = [slug for slug, kws in CATEGORY_ALIASES.items() if any(k in q for k in kws)]
    auds = [slug for slug, kws in AUDIENCE_ALIASES.items() if any(k in q for k in kws)]
    wants_free = any(w in q for w in ["免费", "便宜", "省钱", "0 元", "不花钱"])
    hates_vpn = any(w in q for w in ["国内", "不翻墙", "不用魔法", "直连"])
    return {
        "categories": cats,
        "audiences": auds,
        "free": wants_free,
        "no_vpn": hates_vpn,
    }


def retrieve(db: Session, query: str, limit: int = 8) -> list[Tool]:
    intents = extract_intents(query)
    q = db.query(Tool)

    if intents["categories"]:
        cat_ids = [
            c.id
            for c in db.query(Category).filter(Category.slug.in_(intents["categories"])).all()
        ]
        if cat_ids:
            q = q.join(ToolCategory, ToolCategory.tool_id == Tool.id).filter(
                ToolCategory.category_id.in_(cat_ids)
            )

    if intents["audiences"]:
        q = q.join(ToolAudience, ToolAudience.tool_id == Tool.id).filter(
            ToolAudience.audience.in_(intents["audiences"])
        )

    if intents["free"]:
        q = q.filter(Tool.is_free.is_(True))
    if intents["no_vpn"]:
        q = q.filter(Tool.need_vpn.is_(False))

    tokens = [t for t in re.split(r"[\s,，。.、!！?？:：]+", query) if len(t) >= 2]
    if tokens and not intents["categories"]:
        likes = [Tool.name.like(f"%{t}%") for t in tokens[:5]] + [
            Tool.tagline.like(f"%{t}%") for t in tokens[:5]
        ]
        q = q.filter(or_(*likes))

    tools = (
        q.distinct(Tool.id)
        .order_by(Tool.overall_score.desc(), Tool.review_count.desc())
        .limit(limit)
        .all()
    )
    return tools


EXTERNAL_NAV_SITES = [
    {"name": "UISDC AI 导航", "url": "https://hao.uisdc.com/ai", "desc": "优设出品，设计师友好"},
    {"name": "AI 工具集", "url": "https://ai-bot.cn", "desc": "分类齐全的中文 AI 导航"},
    {"name": "Futurepedia", "url": "https://www.futurepedia.io", "desc": "海外 AI 产品最全库"},
]
