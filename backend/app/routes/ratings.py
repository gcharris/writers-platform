from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.rating import Rating
from app.models.work import Work
from app.routes.reading import check_can_rate
from app.schemas.rating import RatingCreate, RatingUpdate, RatingResponse, WorkRatingStats
from app.services.notifications import NotificationService
from typing import List
import uuid

router = APIRouter(prefix="/ratings", tags=["ratings"])

@router.post("/works/{work_id}", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    work_id: uuid.UUID,
    data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a rating (requires full work read validation)."""

    # Verify user can rate
    if not check_can_rate(current_user.id, work_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must read the entire work before rating"
        )

    # Check if user already rated
    existing = db.query(Rating).filter(
        and_(
            Rating.user_id == current_user.id,
            Rating.work_id == work_id
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this work. Use PUT to update."
        )

    rating = Rating(
        work_id=work_id,
        user_id=current_user.id,
        score=data.score,
        review=data.review
    )

    db.add(rating)
    db.commit()

    # Update work's rating stats
    update_work_rating_stats(work_id, db)

    # Send notification to work author
    work = db.query(Work).filter(Work.id == work_id).first()
    if work:
        NotificationService.create_rating_notification(db, work, current_user, data.score)

    db.refresh(rating)
    rating.username = current_user.username

    return rating

@router.put("/works/{work_id}", response_model=RatingResponse)
async def update_rating(
    work_id: uuid.UUID,
    data: RatingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update own rating."""

    rating = db.query(Rating).filter(
        and_(
            Rating.user_id == current_user.id,
            Rating.work_id == work_id
        )
    ).first()

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    rating.score = data.score
    rating.review = data.review

    db.commit()

    # Update work's rating stats
    update_work_rating_stats(work_id, db)

    db.refresh(rating)
    rating.username = current_user.username

    return rating

@router.get("/works/{work_id}", response_model=List[RatingResponse])
async def get_work_ratings(
    work_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get all ratings for a work."""

    ratings = db.query(Rating).filter(Rating.work_id == work_id).join(User).all()

    for rating in ratings:
        rating.username = rating.user.username

    return ratings

@router.get("/works/{work_id}/stats", response_model=WorkRatingStats)
async def get_work_rating_stats(
    work_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get rating statistics for a work."""

    ratings = db.query(Rating).filter(Rating.work_id == work_id).all()

    if not ratings:
        return WorkRatingStats(
            work_id=work_id,
            rating_average=0.0,
            rating_count=0,
            rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        )

    scores = [r.score for r in ratings]
    distribution = {i: scores.count(i) for i in range(1, 6)}

    return WorkRatingStats(
        work_id=work_id,
        rating_average=sum(scores) / len(scores),
        rating_count=len(ratings),
        rating_distribution=distribution
    )

def update_work_rating_stats(work_id: uuid.UUID, db: Session):
    """Update cached rating stats on work."""

    result = db.query(
        func.avg(Rating.score).label("avg"),
        func.count(Rating.id).label("count")
    ).filter(Rating.work_id == work_id).first()

    work = db.query(Work).filter(Work.id == work_id).first()
    if work:
        work.rating_average = float(result.avg) if result.avg else 0.0
        work.rating_count = result.count
        db.commit()
