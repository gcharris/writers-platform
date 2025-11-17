from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.comment import Comment
from app.models.work import Work
from app.models.reading_session import ReadingSession
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services.notifications import NotificationService
from typing import List, Optional
import uuid

router = APIRouter(prefix="/comments", tags=["comments"])

def check_can_comment(user_id: uuid.UUID, work_id: uuid.UUID, section_id: Optional[uuid.UUID], db: Session) -> bool:
    """Check if user has validated reading session."""

    session = db.query(ReadingSession).filter(
        and_(
            ReadingSession.user_id == user_id,
            ReadingSession.work_id == work_id,
            ReadingSession.section_id == section_id if section_id else ReadingSession.section_id == None,
            ReadingSession.validated == True
        )
    ).first()

    return session is not None

@router.post("/works/{work_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    work_id: uuid.UUID,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a comment (requires validated reading)."""

    # Verify user can comment
    if not check_can_comment(current_user.id, work_id, data.section_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must read the content before commenting"
        )

    comment = Comment(
        work_id=work_id,
        section_id=data.section_id,
        user_id=current_user.id,
        content=data.content,
        parent_id=data.parent_id
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Add username for response
    comment.username = current_user.username

    # Send notifications
    work = db.query(Work).filter(Work.id == work_id).first()
    if work:
        NotificationService.create_comment_notification(db, work, current_user, comment)

        # If it's a reply, notify the parent comment author
        if comment.parent_id:
            parent = db.query(Comment).filter(Comment.id == comment.parent_id).first()
            if parent:
                NotificationService.create_reply_notification(db, parent, current_user, comment)

    return comment

@router.get("/works/{work_id}", response_model=List[CommentResponse])
async def get_work_comments(
    work_id: uuid.UUID,
    section_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    """Get all comments for a work or section."""

    query = db.query(Comment).filter(Comment.work_id == work_id)

    if section_id:
        query = query.filter(Comment.section_id == section_id)

    comments = query.join(User).all()

    # Add usernames
    for comment in comments:
        comment.username = comment.user.username

    return comments

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: uuid.UUID,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update own comment."""

    comment = db.query(Comment).filter(
        and_(
            Comment.id == comment_id,
            Comment.user_id == current_user.id
        )
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.content = data.content
    db.commit()
    db.refresh(comment)

    comment.username = current_user.username
    return comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete own comment."""

    comment = db.query(Comment).filter(
        and_(
            Comment.id == comment_id,
            Comment.user_id == current_user.id
        )
    ).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
