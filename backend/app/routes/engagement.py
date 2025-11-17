from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.work import Work
from app.models.bookmark import Bookmark
from app.models.reading_history import ReadingHistory
from app.schemas.engagement import (
    BookmarkResponse, ReadingHistoryResponse,
    BookmarksListResponse, ReadingHistoryListResponse
)
import uuid

router = APIRouter(prefix="/engagement", tags=["engagement"])

# Bookmarks

@router.post("/bookmarks/{work_id}", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    work_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bookmark a work."""

    # Check if work exists
    work = db.query(Work).filter(Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    # Check if already bookmarked
    existing = db.query(Bookmark).filter(
        and_(
            Bookmark.user_id == current_user.id,
            Bookmark.work_id == work_id
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Work already bookmarked")

    # Create bookmark
    bookmark = Bookmark(
        user_id=current_user.id,
        work_id=work_id
    )

    db.add(bookmark)

    # Update work's bookmark count
    work.bookmarks_count += 1

    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse(
        id=bookmark.id,
        user_id=bookmark.user_id,
        work_id=bookmark.work_id,
        work_title=work.title,
        work_author_username=work.author.username,
        work_genre=work.genre,
        work_summary=work.summary,
        work_word_count=work.word_count,
        created_at=bookmark.created_at
    )

@router.delete("/bookmarks/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    work_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove bookmark."""

    bookmark = db.query(Bookmark).filter(
        and_(
            Bookmark.user_id == current_user.id,
            Bookmark.work_id == work_id
        )
    ).first()

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    # Update work's bookmark count
    work = db.query(Work).filter(Work.id == work_id).first()
    if work and work.bookmarks_count > 0:
        work.bookmarks_count -= 1

    db.delete(bookmark)
    db.commit()

@router.get("/bookmarks", response_model=BookmarksListResponse)
async def get_my_bookmarks(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's bookmarks."""

    query = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id
    ).order_by(Bookmark.created_at.desc())

    total = query.count()
    offset = (page - 1) * page_size
    bookmarks = query.offset(offset).limit(page_size).all()

    bookmark_responses = []
    for bookmark in bookmarks:
        work = bookmark.work
        bookmark_responses.append(BookmarkResponse(
            id=bookmark.id,
            user_id=bookmark.user_id,
            work_id=bookmark.work_id,
            work_title=work.title,
            work_author_username=work.author.username,
            work_genre=work.genre,
            work_summary=work.summary,
            work_word_count=work.word_count,
            created_at=bookmark.created_at
        ))

    return BookmarksListResponse(
        bookmarks=bookmark_responses,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/bookmarks/check/{work_id}")
async def check_bookmark(
    work_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if work is bookmarked."""

    bookmark = db.query(Bookmark).filter(
        and_(
            Bookmark.user_id == current_user.id,
            Bookmark.work_id == work_id
        )
    ).first()

    return {"is_bookmarked": bookmark is not None}

# Reading History

@router.get("/history", response_model=ReadingHistoryListResponse)
async def get_reading_history(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's reading history."""

    query = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == current_user.id
    ).order_by(ReadingHistory.completed_at.desc())

    total = query.count()
    offset = (page - 1) * page_size
    history_items = query.offset(offset).limit(page_size).all()

    history_responses = []
    for item in history_items:
        work = item.work
        history_responses.append(ReadingHistoryResponse(
            id=item.id,
            user_id=item.user_id,
            work_id=item.work_id,
            work_title=work.title,
            work_author_username=work.author.username,
            work_genre=work.genre,
            work_word_count=work.word_count,
            completed_at=item.completed_at,
            read_time=item.read_time,
            progress=item.progress
        ))

    return ReadingHistoryListResponse(
        history=history_responses,
        total=total,
        page=page,
        page_size=page_size
    )
