from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.notification import Notification
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    message: str
    link: Optional[str]
    read: bool
    created_at: datetime
    actor_username: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notifications."""

    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.read == False)

    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

    result = []
    for n in notifications:
        actor_username = None
        if n.actor_id:
            actor = db.query(User).filter(User.id == n.actor_id).first()
            actor_username = actor.username if actor else None

        result.append(NotificationResponse(
            id=n.id,
            type=n.type,
            title=n.title,
            message=n.message,
            link=n.link,
            read=n.read,
            created_at=n.created_at,
            actor_username=actor_username
        ))

    return result

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications."""

    count = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.read == False
        )
    ).count()

    return {"count": count}

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read."""

    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.read = True
    db.commit()

    return {"message": "Marked as read"}

@router.put("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read."""

    db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.read == False
        )
    ).update({"read": True})

    db.commit()

    return {"message": "All notifications marked as read"}
