from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=5)
    review: Optional[str] = None

class RatingUpdate(BaseModel):
    score: int = Field(..., ge=1, le=5)
    review: Optional[str] = None

class RatingResponse(BaseModel):
    id: UUID
    work_id: UUID
    user_id: UUID
    username: str
    score: int
    review: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class WorkRatingStats(BaseModel):
    work_id: UUID
    rating_average: float
    rating_count: int
    rating_distribution: dict  # {1: count, 2: count, ...}
