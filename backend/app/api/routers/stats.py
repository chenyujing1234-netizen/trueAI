from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Category, Review, Tool
from app.models.user import User

router = APIRouter()


@router.get("")
def stats(db: Session = Depends(get_db)):
    tools = db.query(func.count(Tool.id)).scalar() or 0
    cats = db.query(func.count(Category.id)).scalar() or 0
    reviews = db.query(func.count(Review.id)).filter(Review.status == "approved").scalar() or 0
    users = db.query(func.count(User.id)).scalar() or 0
    return {
        "tools": int(tools),
        "categories": int(cats),
        "reviews": int(reviews),
        "users": int(users),
        "ad_free": True,
        "values": [
            "我来帮你省钱",
            "我来帮你省时间",
            "无广告",
            "实时人工评测",
            "没有最好的，只有最适合你的",
        ],
    }
