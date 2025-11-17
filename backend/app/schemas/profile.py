from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class ProfileUpdate(BaseModel):
    """Update user profile."""
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

class ProfileResponse(BaseModel):
    """User profile response."""
    id: UUID
    username: str
    bio: Optional[str]
    avatar_url: Optional[str]
    location: Optional[str]
    website: Optional[str]
    role: str
    works_count: int
    followers_count: int
    following_count: int
    created_at: datetime
    is_following: Optional[bool] = None  # Set by endpoint based on current user

    class Config:
        from_attributes = True

class UserWorkSummary(BaseModel):
    """Summary of user's work for profile."""
    id: UUID
    title: str
    genre: Optional[str]
    word_count: int
    rating_average: float
    rating_count: int
    views_count: int
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class UserWorksResponse(BaseModel):
    """User's works with pagination."""
    works: List[UserWorkSummary]
    total: int
    page: int
    page_size: int

class FollowResponse(BaseModel):
    """Follow relationship response."""
    id: UUID
    follower_id: UUID
    following_id: UUID
    follower_username: Optional[str] = None
    following_username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FollowersResponse(BaseModel):
    """List of followers/following."""
    users: List[ProfileResponse]
    total: int
