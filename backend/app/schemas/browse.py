from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class WorkListItem(BaseModel):
    """Lightweight work representation for browse/search."""
    id: UUID
    title: str
    author_id: UUID
    author_username: str
    genre: Optional[str]
    summary: Optional[str]
    word_count: int
    rating_average: float
    rating_count: int
    comment_count: int
    bookmarks_count: int
    views_count: int
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class BrowseFilters(BaseModel):
    """Filters for browsing works."""
    genre: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    min_word_count: Optional[int] = None
    max_word_count: Optional[int] = None
    content_rating: Optional[str] = None
    sort_by: Optional[str] = "created_at"  # created_at, rating_average, word_count, views_count
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = 1
    page_size: int = 20

class BrowseResponse(BaseModel):
    """Paginated browse response."""
    works: List[WorkListItem]
    total: int
    page: int
    page_size: int
    total_pages: int

class SearchQuery(BaseModel):
    """Search query parameters."""
    query: str
    search_in: Optional[List[str]] = ["title", "summary"]  # title, summary, content
    filters: Optional[BrowseFilters] = None

class GenreStats(BaseModel):
    """Statistics for a genre."""
    genre: str
    count: int
    avg_rating: float
