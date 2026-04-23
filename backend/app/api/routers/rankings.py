from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Category, Tool, ToolCategory
from app.api.routers.tools import _attach_relations, _brief

router = APIRouter()


DIMENSION_COLS = {
    "overall": Tool.overall_score,
    "usability": Tool.usability_score,
    "effect": Tool.effect_score,
    "price": Tool.price_score,
    "speed": Tool.speed_score,
    "reviews": Tool.review_count,
}


@router.get("")
def rankings(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    dimension: str = Query("overall"),
    top: int = Query(10, ge=1, le=50),
):
    col = DIMENSION_COLS.get(dimension)
    if col is None:
        raise HTTPException(400, f"未知维度 {dimension}")

    query = db.query(Tool)
    if category:
        cat = db.query(Category).filter_by(slug=category).one_or_none()
        if not cat:
            raise HTTPException(404, "分类不存在")
        query = query.join(ToolCategory, ToolCategory.tool_id == Tool.id).filter(
            ToolCategory.category_id == cat.id
        )

    tools = query.order_by(col.desc(), Tool.id.desc()).limit(top).all()
    rel = _attach_relations(db, tools)
    return {
        "dimension": dimension,
        "category": category,
        "items": [
            {
                "rank": idx + 1,
                **_brief(t, rel).model_dump(),
                "dimension_score": float(getattr(t, col.key) or 0) if hasattr(col, "key") else 0,
            }
            for idx, t in enumerate(tools)
        ],
    }
