from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ExternalReview(Base):
    """来自外部平台（如观猹 watcha.cn）的用户评论。"""
    __tablename__ = "external_reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 关联本站工具
    tool_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tools.id", ondelete="CASCADE"), index=True
    )

    # 外部来源
    source: Mapped[str] = mapped_column(String(32), default="watcha", index=True)
    external_id: Mapped[str] = mapped_column(String(64), index=True)  # 外部平台评论 ID

    # 评论内容
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)  # 评分（如 8.2）

    # 评论作者信息
    author_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    author_avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # 互动数据
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)

    # 时间
    external_created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
