from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class CommentCreate(BaseModel):
    content: str
    section_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: UUID
    work_id: UUID
    section_id: Optional[UUID]
    user_id: UUID
    username: str
    content: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    replies: List['CommentResponse'] = []

    class Config:
        from_attributes = True
