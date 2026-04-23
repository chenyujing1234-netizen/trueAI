from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Category, ToolCategory
from app.schemas.category import CategoryOut

router = APIRouter()


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    counts = dict(
        db.query(ToolCategory.category_id, func.count(ToolCategory.id))
        .group_by(ToolCategory.category_id)
        .all()
    )
    cats = db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc()).all()
    out = []
    for c in cats:
        out.append(
            CategoryOut(
                id=c.id,
                slug=c.slug,
                name=c.name,
                icon=c.icon,
                sort_order=c.sort_order,
                parent_id=c.parent_id,
                tool_count=int(counts.get(c.id, 0)),
            )
        )
    return out
