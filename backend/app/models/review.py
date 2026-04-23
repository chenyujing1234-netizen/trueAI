from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tool_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tools.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float] = mapped_column(Numeric(3, 1), default=0)
    # 多维度评分 {"usability":4.5,"effect":4,"price":5,"speed":4}
    dims: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # pending / approved / rejected
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    reward_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
