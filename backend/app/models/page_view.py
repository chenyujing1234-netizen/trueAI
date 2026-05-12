from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PageView(Base):
    __tablename__ = "page_views"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 请求基本信息
    ip: Mapped[str] = mapped_column(String(64), index=True)
    path: Mapped[str] = mapped_column(String(512), index=True)
    method: Mapped[str] = mapped_column(String(8), default="GET")
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 请求头信息（用于分析设备/来源）
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    referer: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # 时间（按日期索引便于按天聚合）
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
