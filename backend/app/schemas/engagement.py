from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class BookmarkCreate(BaseModel):
    """Create bookmark (work_id from path)."""
    pass

class BookmarkResponse(BaseModel):
    """Bookmark response with work details."""
    id: UUID
    user_id: UUID
    work_id: UUID
    work_title: str
    work_author_username: str
    work_genre: Optional[str]
    work_summary: Optional[str]
    work_word_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReadingHistoryResponse(BaseModel):
    """Reading history response with work details."""
    id: UUID
    user_id: UUID
    work_id: UUID
    work_title: str
    work_author_username: str
    work_genre: Optional[str]
    work_word_count: int
    completed_at: datetime
    read_time: int
    progress: int

    class Config:
        from_attributes = True

class BookmarksListResponse(BaseModel):
    """Paginated bookmarks list."""
    bookmarks: List[BookmarkResponse]
    total: int
    page: int
    page_size: int

class ReadingHistoryListResponse(BaseModel):
    """Paginated reading history list."""
    history: List[ReadingHistoryResponse]
    total: int
    page: int
    page_size: int
