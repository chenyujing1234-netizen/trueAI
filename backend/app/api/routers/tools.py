from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Category, Tool, ToolAudience, ToolCategory
from app.schemas.tool import ToolBrief, ToolDetail, ToolListResponse

router = APIRouter()


SORT_FIELDS = {
    "overall": Tool.overall_score,
    "usability": Tool.usability_score,
    "effect": Tool.effect_score,
    "price": Tool.price_score,
    "speed": Tool.speed_score,
    "reviews": Tool.review_count,
    "new": Tool.created_at,
}


def _attach_relations(db: Session, tools: list[Tool]) -> dict[int, dict[str, list[str]]]:
    if not tools:
        return {}
    ids = [t.id for t in tools]
    cat_rows = (
        db.query(ToolCategory.tool_id, Category.slug)
        .join(Category, Category.id == ToolCategory.category_id)
        .filter(ToolCategory.tool_id.in_(ids))
        .all()
    )
    aud_rows = (
        db.query(ToolAudience.tool_id, ToolAudience.audience)
        .filter(ToolAudience.tool_id.in_(ids))
        .all()
    )
    rel: dict[int, dict[str, list[str]]] = {i: {"categories": [], "audiences": []} for i in ids}
    for tid, slug in cat_rows:
        rel[tid]["categories"].append(slug)
    for tid, aud in aud_rows:
        rel[tid]["audiences"].append(aud)
    return rel


def _brief(t: Tool, rel: dict) -> ToolBrief:
    return ToolBrief(
        id=t.id,
        name=t.name,
        slug=t.slug,
        tagline=t.tagline,
        logo_url=t.logo_url,
        form_factor=t.form_factor,
        is_free=t.is_free,
        need_vpn=t.need_vpn,
        overall_score=float(t.overall_score or 0),
        review_count=t.review_count,
        categories=rel.get(t.id, {}).get("categories", []),
        audiences=rel.get(t.id, {}).get("audiences", []),
    )


@router.get("", response_model=ToolListResponse)
def list_tools(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    category: Optional[str] = None,
    form_factor: Optional[str] = None,
    audience: Optional[str] = None,
    free: Optional[bool] = None,
    need_vpn: Optional[bool] = None,
    sort: str = Query("overall"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
):
    query = db.query(Tool)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Tool.name.like(like), Tool.tagline.like(like), Tool.description.like(like))
        )
    if category:
        cat = db.query(Category).filter_by(slug=category).one_or_none()
        if not cat:
            raise HTTPException(404, "分类不存在")
        query = query.join(ToolCategory, ToolCategory.tool_id == Tool.id).filter(
            ToolCategory.category_id == cat.id
        )
    if form_factor:
        query = query.filter(Tool.form_factor == form_factor)
    if audience:
        query = query.join(ToolAudience, ToolAudience.tool_id == Tool.id).filter(
            ToolAudience.audience == audience
        )
    if free is not None:
        query = query.filter(Tool.is_free == free)
    if need_vpn is not None:
        query = query.filter(Tool.need_vpn == need_vpn)

    total = query.with_entities(func.count(func.distinct(Tool.id))).scalar() or 0

    sort_col = SORT_FIELDS.get(sort, Tool.overall_score)
    sort_col = sort_col.asc() if order == "asc" else sort_col.desc()

    tools = (
        query.distinct(Tool.id)
        .order_by(sort_col, Tool.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    rel = _attach_relations(db, tools)
    items = [_brief(t, rel) for t in tools]
    return ToolListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{id_or_slug}", response_model=ToolDetail)
def get_tool(id_or_slug: str, db: Session = Depends(get_db)):
    tool = None
    if id_or_slug.isdigit():
        tool = db.get(Tool, int(id_or_slug))
    if tool is None:
        tool = db.query(Tool).filter_by(slug=id_or_slug).one_or_none()
    if tool is None:
        raise HTTPException(404, "工具不存在")

    rel = _attach_relations(db, [tool])
    base = _brief(tool, rel).model_dump()
    return ToolDetail(
        **base,
        description=tool.description,
        developer=tool.developer,
        launched_at=tool.launched_at,
        is_iterating=tool.is_iterating,
        user_count=tool.user_count,
        pricing_info=tool.pricing_info,
        gen_time_ms=tool.gen_time_ms,
        support_cli=tool.support_cli,
        support_api=tool.support_api,
        official_url=tool.official_url,
        video_url=tool.video_url,
        usability_score=float(tool.usability_score or 0),
        effect_score=float(tool.effect_score or 0),
        price_score=float(tool.price_score or 0),
        speed_score=float(tool.speed_score or 0),
        reviewed_at=tool.reviewed_at,
        created_at=tool.created_at,
    )


@router.post("/compare")
def compare_tools(ids: list[int], db: Session = Depends(get_db)):
    if not ids or len(ids) > 3:
        raise HTTPException(400, "请提供 1~3 个工具 ID")
    tools = db.query(Tool).filter(Tool.id.in_(ids)).all()
    rel = _attach_relations(db, tools)
    order_map = {tid: idx for idx, tid in enumerate(ids)}
    tools.sort(key=lambda t: order_map.get(t.id, 999))
    return [
        {
            **_brief(t, rel).model_dump(),
            "usability_score": float(t.usability_score or 0),
            "effect_score": float(t.effect_score or 0),
            "price_score": float(t.price_score or 0),
            "speed_score": float(t.speed_score or 0),
            "pricing_info": t.pricing_info,
            "developer": t.developer,
            "support_cli": t.support_cli,
            "support_api": t.support_api,
            "official_url": t.official_url,
        }
        for t in tools
    ]
