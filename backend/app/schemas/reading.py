from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ReadingSessionStart(BaseModel):
    work_id: UUID
    section_id: Optional[UUID] = None

class ReadingSessionUpdate(BaseModel):
    time_on_page: int  # seconds
    scroll_depth: int  # percentage (0-100)
    scroll_event: Optional[datetime] = None

class ReadingSessionComplete(BaseModel):
    pass

class ReadingSessionResponse(BaseModel):
    id: UUID
    work_id: UUID
    section_id: Optional[UUID]
    time_on_page: int
    scroll_depth: int
    reading_speed: Optional[float]
    completed: bool
    validated: bool
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReadingValidationResponse(BaseModel):
    validated: bool
    can_comment: bool
    can_rate: bool
    message: str
