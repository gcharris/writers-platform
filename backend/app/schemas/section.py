from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class SectionCreate(BaseModel):
    title: str
    order_index: int
    content: str

class SectionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class SectionResponse(BaseModel):
    id: UUID
    work_id: UUID
    title: str
    order_index: int
    content: str
    word_count: int
    created_at: datetime

    class Config:
        from_attributes = True
