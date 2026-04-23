from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class ToolBrief(BaseModel):
    id: int
    name: str
    slug: str
    tagline: Optional[str] = None
    logo_url: Optional[str] = None
    form_factor: str
    is_free: bool
    need_vpn: bool
    overall_score: float
    review_count: int
    categories: List[str] = []
    audiences: List[str] = []

    class Config:
        from_attributes = True


class ToolDetail(ToolBrief):
    description: Optional[str] = None
    developer: Optional[str] = None
    launched_at: Optional[date] = None
    is_iterating: bool
    user_count: Optional[str] = None
    pricing_info: Optional[str] = None
    gen_time_ms: Optional[int] = None
    support_cli: bool
    support_api: bool
    official_url: Optional[str] = None
    usability_score: float
    effect_score: float
    price_score: float
    speed_score: float
    reviewed_at: Optional[datetime] = None
    created_at: datetime


class ToolListResponse(BaseModel):
    items: List[ToolBrief]
    total: int
    page: int
    page_size: int
