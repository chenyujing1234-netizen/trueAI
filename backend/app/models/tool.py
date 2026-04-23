from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tagline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    developer: Mapped[str | None] = mapped_column(String(128), nullable=True)
    launched_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_iterating: Mapped[bool] = mapped_column(Boolean, default=True)
    user_count: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # saas / mobile / cli / windows_app / web
    form_factor: Mapped[str] = mapped_column(String(32), default="saas", index=True)

    is_free: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    pricing_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gen_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    need_vpn: Mapped[bool] = mapped_column(Boolean, default=False)
    support_cli: Mapped[bool] = mapped_column(Boolean, default=False)
    support_api: Mapped[bool] = mapped_column(Boolean, default=False)

    official_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    overall_score: Mapped[float] = mapped_column(Numeric(3, 1), default=0)
    usability_score: Mapped[float] = mapped_column(Numeric(3, 1), default=0)
    effect_score: Mapped[float] = mapped_column(Numeric(3, 1), default=0)
    price_score: Mapped[float] = mapped_column(Numeric(3, 1), default=0)
    speed_score: Mapped[float] = mapped_column(Numeric(3, 1), default=0)

    review_count: Mapped[int] = mapped_column(Integer, default=0)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ToolCategory(Base):
    __tablename__ = "tool_categories"
    __table_args__ = (UniqueConstraint("tool_id", "category_id", name="uq_tool_category"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tool_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tools.id", ondelete="CASCADE"), index=True
    )
    category_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )


class ToolAudience(Base):
    __tablename__ = "tool_audiences"
    __table_args__ = (UniqueConstraint("tool_id", "audience", name="uq_tool_audience"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tool_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tools.id", ondelete="CASCADE"), index=True
    )
    # developer / child / beginner / female / senior / designer / student / creator
    audience: Mapped[str] = mapped_column(String(32), index=True)
