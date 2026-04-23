from typing import List, Optional

from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    slug: str
    name: str
    icon: Optional[str] = None
    sort_order: int
    parent_id: Optional[int] = None
    tool_count: int = 0

    class Config:
        from_attributes = True


class CategoryTreeOut(CategoryOut):
    children: List["CategoryTreeOut"] = []


CategoryTreeOut.model_rebuild()
