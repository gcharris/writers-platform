from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.work import Work
from app.models.rating import Rating
from app.models.comment import Comment
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class WorkStats(BaseModel):
    work_id: str
    title: str
    views: int
    reads: int
    comments: int
    ratings: int
    average_rating: float
    bookmarks: int

class DashboardStats(BaseModel):
    total_works: int
    total_views: int
    total_reads: int
    total_ratings: int
    average_rating: float
    total_followers: int
    work_stats: List[WorkStats]

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get writer dashboard statistics."""

    # Get all user's published works
    works = db.query(Work).filter(
        and_(
            Work.author_id == current_user.id,
            Work.status == "published"
        )
    ).all()

    total_views = sum(w.views_count for w in works)
    total_reads = sum(w.reads_count for w in works)
    total_ratings = sum(w.rating_count for w in works)

    # Calculate average rating across all works
    ratings = db.query(func.avg(Rating.score)).join(Work).filter(
        Work.author_id == current_user.id
    ).scalar()

    average_rating = float(ratings) if ratings else 0.0

    # Individual work stats
    work_stats = []
    for work in works:
        comment_count = db.query(Comment).filter(Comment.work_id == work.id).count()

        work_stats.append(WorkStats(
            work_id=str(work.id),
            title=work.title,
            views=work.views_count,
            reads=work.reads_count,
            comments=comment_count,
            ratings=work.rating_count,
            average_rating=work.rating_average,
            bookmarks=work.bookmarks_count
        ))

    return DashboardStats(
        total_works=len(works),
        total_views=total_views,
        total_reads=total_reads,
        total_ratings=total_ratings,
        average_rating=average_rating,
        total_followers=current_user.followers_count,
        work_stats=work_stats
    )

class RecentActivity(BaseModel):
    type: str
    message: str
    timestamp: datetime

@router.get("/activity", response_model=List[RecentActivity])
async def get_recent_activity(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent activity on user's works."""

    since = datetime.utcnow() - timedelta(days=days)
    activity = []

    # Recent comments
    comments = db.query(Comment).join(Work).filter(
        and_(
            Work.author_id == current_user.id,
            Comment.created_at >= since
        )
    ).order_by(Comment.created_at.desc()).limit(10).all()

    for c in comments:
        activity.append(RecentActivity(
            type="comment",
            message=f"New comment on '{c.work.title}'",
            timestamp=c.created_at
        ))

    # Recent ratings
    ratings = db.query(Rating).join(Work).filter(
        and_(
            Work.author_id == current_user.id,
            Rating.created_at >= since
        )
    ).order_by(Rating.created_at.desc()).limit(10).all()

    for r in ratings:
        activity.append(RecentActivity(
            type="rating",
            message=f"New {r.score}-star rating on '{r.work.title}'",
            timestamp=r.created_at
        ))

    # Sort by timestamp
    activity.sort(key=lambda x: x.timestamp, reverse=True)

    return activity[:20]
