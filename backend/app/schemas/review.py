from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    tool_id: int
    content: str = Field(min_length=5, max_length=2000)
    score: float = Field(ge=0, le=10)
    dims: Optional[dict] = None


class ReviewOut(BaseModel):
    id: int
    tool_id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    content: Optional[str] = None
    score: float
    dims: Optional[dict] = None
    status: str
    reward_amount: float
    created_at: datetime

    class Config:
        from_attributes = True
