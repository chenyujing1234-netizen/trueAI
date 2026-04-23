from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_user
from app.core.db import get_db
from app.models import Review, Tool
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut

router = APIRouter()


@router.get("", response_model=list[ReviewOut])
def list_reviews(
    tool_id: int,
    status_filter: str = "approved",
    db: Session = Depends(get_db),
):
    q = db.query(Review, User.username).outerjoin(User, User.id == Review.user_id).filter(
        Review.tool_id == tool_id
    )
    if status_filter != "all":
        q = q.filter(Review.status == status_filter)
    rows = q.order_by(desc(Review.created_at)).limit(100).all()
    out = []
    for r, username in rows:
        out.append(
            ReviewOut(
                id=r.id,
                tool_id=r.tool_id,
                user_id=r.user_id,
                username=username,
                content=r.content,
                score=float(r.score or 0),
                dims=r.dims,
                status=r.status,
                reward_amount=float(r.reward_amount or 0),
                created_at=r.created_at,
            )
        )
    return out


@router.post("", response_model=ReviewOut)
def create_review(
    payload: ReviewCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tool = db.get(Tool, payload.tool_id)
    if not tool:
        raise HTTPException(404, "工具不存在")
    r = Review(
        user_id=user.id,
        tool_id=payload.tool_id,
        content=payload.content,
        score=payload.score,
        dims=payload.dims,
        status="pending",
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return ReviewOut(
        id=r.id,
        tool_id=r.tool_id,
        user_id=r.user_id,
        username=user.username,
        content=r.content,
        score=float(r.score),
        dims=r.dims,
        status=r.status,
        reward_amount=float(r.reward_amount or 0),
        created_at=r.created_at,
    )
