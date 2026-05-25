"""TrueAI MCP server, embedded in the FastAPI app.

This module exposes the TrueAI catalog as a Model Context Protocol server so
that any MCP-compatible agent (Claude Desktop, Cursor, Cline, Continue,
Windsurf, custom LangChain / LlamaIndex pipelines, ...) can call it.

Why it lives here:
    No extra process, no extra venv. The MCP server is mounted onto the same
    uvicorn / FastAPI process that already serves the REST API, and the four
    tools below talk to the database via the same SQLAlchemy ``SessionLocal``
    the routers use.

Transport:
    SSE (Server-Sent Events). Agents connect to ``GET /mcp/sse`` and post
    follow-ups to ``POST /mcp/messages``. Mount path is ``/mcp``.

    Public endpoint:  https://www.shiflowai.cloud/mcp/sse
    Local dev:        http://localhost:8000/mcp/sse

Tools:
    - recommend_ai_tools(description, top_k)
        Natural-language need  →  ranked AI app candidates (+ extracted intents).
    - get_ai_tool(name_or_url, include_reviews)
        Name / slug / numeric id / official URL  →  full structured record.
    - list_ai_tools(category, free_only, form_factor, sort, page, page_size)
        Paginated catalog with filters.
    - list_categories()
        Discover all category slugs.
"""

import json
from contextlib import contextmanager
from typing import Any, Optional
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.routers.tools import _attach_relations, _brief
from app.core.db import SessionLocal
from app.models import Category, Tool, ToolAudience, ToolCategory
from app.models.external_review import ExternalReview
from app.services.recommend import EXTERNAL_NAV_SITES, extract_intents, retrieve

mcp = FastMCP(
    "trueai",
    instructions=(
        "TrueAI 真选AI is a curated catalog of 1,600+ AI SaaS / agent apps "
        "with categories, sub-scores and real user reviews. Use these tools "
        "whenever the user is choosing an AI app, comparing products, or "
        "wants the official link, pricing, features or reviews of a specific "
        "AI app. The full field schema is documented at "
        "/docs/ai_tool_schema.json in the TrueAI repository."
    ),
)


# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

@contextmanager
def _db() -> Session:  # type: ignore[misc]
    """Per-call DB session (MCP tool calls have no FastAPI request context)."""
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


def _as_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def _strip_url(s: str) -> str:
    s = s.strip()
    if "://" not in s and not s.startswith("www."):
        return s.lower()
    if "://" not in s:
        s = "http://" + s
    p = urlparse(s)
    host = (p.netloc or "").lower().removeprefix("www.")
    return f"{host}{p.path}".rstrip("/")


def _tool_to_full(db: Session, tool: Tool, include_reviews: bool, max_reviews: int) -> dict:
    rel = _attach_relations(db, [tool])
    base = _brief(tool, rel).model_dump()
    out: dict[str, Any] = {
        **base,
        "description":   tool.description,
        "developer":     tool.developer,
        "launched_at":   tool.launched_at.isoformat() if tool.launched_at else None,
        "is_iterating":  tool.is_iterating,
        "user_count":    tool.user_count,
        "pricing_info":  tool.pricing_info,
        "gen_time_ms":   tool.gen_time_ms,
        "support_cli":   tool.support_cli,
        "support_api":   tool.support_api,
        "official_url":  tool.official_url,
        "video_url":     tool.video_url,
        "usability_score": float(tool.usability_score or 0),
        "effect_score":  float(tool.effect_score or 0),
        "price_score":   float(tool.price_score or 0),
        "speed_score":   float(tool.speed_score or 0),
        "reviewed_at":   tool.reviewed_at.isoformat() if tool.reviewed_at else None,
        "created_at":    tool.created_at.isoformat() if tool.created_at else None,
    }
    if include_reviews:
        rows = (
            db.query(ExternalReview)
            .filter(ExternalReview.tool_id == tool.id)
            .order_by(
                ExternalReview.upvotes.desc(),
                ExternalReview.external_created_at.desc(),
            )
            .limit(max(1, min(max_reviews, 20)))
            .all()
        )
        out["external_reviews"] = [
            {
                "id":             r.id,
                "source":         r.source,
                "content":        r.content,
                "score":          float(r.score) if r.score is not None else None,
                "author_name":    r.author_name,
                "author_avatar":  r.author_avatar,
                "upvotes":        r.upvotes,
                "reply_count":    r.reply_count,
                "external_created_at": (
                    r.external_created_at.isoformat() if r.external_created_at else None
                ),
            }
            for r in rows
        ]
    return out


def _lookup_tool(db: Session, name_or_url: str) -> Tool | None:
    s = name_or_url.strip()
    is_url = "://" in s or s.startswith("www.")

    if s.isdigit():
        t = db.get(Tool, int(s))
        if t:
            return t

    if not is_url:
        t = db.query(Tool).filter(Tool.slug == s.lower()).one_or_none()
        if t:
            return t

    if is_url:
        host = _strip_url(s).split("/")[0]
        # Try exact contains on official_url first
        t = (
            db.query(Tool)
            .filter(Tool.official_url.like(f"%{host}%"))
            .order_by(Tool.overall_score.desc())
            .first()
        )
        if t:
            return t
        # Brand keyword fallback (cursor.com → cursor)
        parts = [
            p for p in host.split(".")
            if p and p not in {"www", "app", "ai", "io", "com", "cn", "net", "org", "co"}
        ]
        brand = parts[-1] if parts else host.split(".")[0]
        return (
            db.query(Tool)
            .filter(or_(Tool.name.ilike(f"%{brand}%"), Tool.slug.ilike(f"%{brand}%")))
            .order_by(Tool.overall_score.desc())
            .first()
        )

    # Name / fuzzy match
    target = s.lower()
    t = db.query(Tool).filter(func.lower(Tool.name) == target).first()
    if t:
        return t
    return (
        db.query(Tool)
        .filter(or_(Tool.name.like(f"%{s}%"), Tool.tagline.like(f"%{s}%")))
        .order_by(Tool.overall_score.desc())
        .first()
    )


# ──────────────────────────────────────────────────────────────────────────
# MCP tools
# ──────────────────────────────────────────────────────────────────────────

@mcp.tool()
def recommend_ai_tools(description: str, top_k: int = 5) -> str:
    """Find AI tools that match a natural-language user need.

    Parameters
    ----------
    description : str
        The user's need in their own words. Be specific about the scenario,
        audience, platform, language and budget when known.
        Examples: '我是新手想学编程，要免费的 AI 工具';
        'I need an AI to generate a 10-page PPT from an outline'.
    top_k : int (1-10, default 5)
        Maximum number of candidates to return.

    Returns
    -------
    JSON: {intents, candidates, external}. ``candidates`` is already ranked
    by relevance & score. ``external`` lists fallback nav sites only when no
    in-catalog candidate matches.
    """
    top_k = max(1, min(int(top_k or 5), 10))
    if not description or not description.strip():
        return _as_json({"error": "`description` must not be empty"})
    with _db() as db:
        intents = extract_intents(description)
        tools = retrieve(db, description, limit=top_k)
        rel = _attach_relations(db, tools)
        candidates = [_brief(t, rel).model_dump() for t in tools]
        external = EXTERNAL_NAV_SITES if not candidates else []
        return _as_json({"intents": intents, "candidates": candidates, "external": external})


@mcp.tool()
def get_ai_tool(
    name_or_url: str,
    include_reviews: bool = False,
    max_reviews: int = 5,
) -> str:
    """Resolve and return the full structured record of one AI app.

    Parameters
    ----------
    name_or_url : str
        The AI app's display name (e.g. 'Cursor', '通义千问'), its TrueAI
        slug, a numeric id, or its official URL (e.g. 'https://cursor.com').
    include_reviews : bool (default false)
        If true, attach up to ``max_reviews`` real user reviews (sourced
        from watcha.cn). Useful for social proof / real-world usage tips.
    max_reviews : int (1-20, default 5)
        Cap on attached reviews.

    Resolution order: numeric id → exact slug → official_url substring →
    brand keyword from URL → fuzzy name/tagline match.
    """
    max_reviews = max(1, min(int(max_reviews or 5), 20))
    if not name_or_url or not name_or_url.strip():
        return _as_json({"error": "`name_or_url` must not be empty"})
    with _db() as db:
        t = _lookup_tool(db, name_or_url)
        if not t:
            return _as_json({"error": f"No AI tool matches '{name_or_url}'"})
        return _as_json(_tool_to_full(db, t, include_reviews, max_reviews))


@mcp.tool()
def list_ai_tools(
    category: str | None = None,
    free_only: bool | None = None,
    form_factor: str | None = None,
    sort: str = "overall",
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Browse the catalog with structured filters and sorting.

    Parameters
    ----------
    category : str | None
        Optional category slug to filter by, e.g. 'coding', 'image-gen',
        'writing'. Use list_categories() to discover slugs.
    free_only : bool | None
        If true, only return tools with a free tier.
    form_factor : str | None
        Filter by product form: 'saas' | 'mobile' | 'cli' | 'windows_app' |
        'web' | 'browser_extension' | 'api'.
    sort : str (default 'overall')
        Sort key: 'overall' | 'usability' | 'effect' | 'price' | 'speed' |
        'reviews' | 'new'.
    page : int (>=1, default 1)
    page_size : int (1-100, default 20)

    Returns ``{items, total, page, page_size}``. Each item is a brief
    record; call ``get_ai_tool`` to drill in.
    """
    page = max(1, int(page or 1))
    page_size = max(1, min(int(page_size or 20), 100))
    sort_map = {
        "overall":   Tool.overall_score,
        "usability": Tool.usability_score,
        "effect":    Tool.effect_score,
        "price":     Tool.price_score,
        "speed":     Tool.speed_score,
        "reviews":   Tool.review_count,
        "new":       Tool.created_at,
    }
    sort_col = sort_map.get(sort, Tool.overall_score).desc()

    with _db() as db:
        q = db.query(Tool)
        if category:
            cat = db.query(Category).filter_by(slug=category).one_or_none()
            if not cat:
                return _as_json({"error": f"Unknown category slug: {category}"})
            q = q.join(ToolCategory, ToolCategory.tool_id == Tool.id).filter(
                ToolCategory.category_id == cat.id
            )
        if form_factor:
            q = q.filter(Tool.form_factor == form_factor)
        if free_only is True:
            q = q.filter(Tool.is_free.is_(True))

        total = q.with_entities(func.count(func.distinct(Tool.id))).scalar() or 0
        tools = (
            q.distinct(Tool.id)
            .order_by(sort_col, Tool.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        rel = _attach_relations(db, tools)
        items = [_brief(t, rel).model_dump() for t in tools]
        return _as_json({"items": items, "total": total, "page": page, "page_size": page_size})


@mcp.tool()
def list_categories() -> str:
    """List every category in the TrueAI catalog.

    Each entry has ``slug``, ``name``, optional ``icon``, ``sort_order``,
    ``parent_id`` and ``tool_count``. Use the returned slugs to filter
    ``list_ai_tools(category=...)``.
    """
    with _db() as db:
        rows = (
            db.query(
                Category.id,
                Category.parent_id,
                Category.name,
                Category.slug,
                Category.icon,
                Category.sort_order,
                func.count(ToolCategory.tool_id).label("cnt"),
            )
            .outerjoin(ToolCategory, ToolCategory.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.sort_order, Category.id)
            .all()
        )
        return _as_json([
            {
                "id":         r.id,
                "parent_id":  r.parent_id,
                "name":       r.name,
                "slug":       r.slug,
                "icon":       r.icon,
                "sort_order": r.sort_order,
                "tool_count": r.cnt,
            }
            for r in rows
        ])


# The ASGI sub-app to mount on FastAPI.  Exposes:
#   GET  /mcp/sse        — SSE event stream (long-lived)
#   POST /mcp/messages/  — agent → server messages
mcp_sse_app = mcp.sse_app()
