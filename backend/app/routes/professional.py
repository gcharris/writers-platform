from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.professional import ProfessionalProfile, Submission
from app.models.work import Work
from app.models.rating import Rating
from pydantic import BaseModel

router = APIRouter(prefix="/professional", tags=["professional"])

# Schemas
class ProfessionalProfileCreate(BaseModel):
    type: str  # 'agent', 'editor', 'publisher'
    company: Optional[str] = None
    website: Optional[str] = None
    specialties: Optional[List[str]] = None
    bio: Optional[str] = None
    seeking_genres: Optional[List[str]] = None
    min_word_count: Optional[int] = None
    max_word_count: Optional[int] = None
    min_rating: Optional[float] = None

class ProfessionalProfileResponse(BaseModel):
    id: str
    user_id: str
    type: str
    company: Optional[str]
    website: Optional[str]
    specialties: Optional[List[str]]
    bio: Optional[str]
    verified: bool
    seeking_genres: Optional[List[str]]
    min_word_count: Optional[int]
    max_word_count: Optional[int]
    min_rating: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    message: Optional[str] = None  # Pitch message

class SubmissionResponse(BaseModel):
    id: str
    work_id: str
    author_id: str
    professional_id: str
    status: str
    message: Optional[str]
    response: Optional[str]
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    responded_at: Optional[datetime]
    work_title: Optional[str]
    author_username: Optional[str]

    class Config:
        from_attributes = True

class SubmissionResponseUpdate(BaseModel):
    status: str  # 'reviewing', 'accepted', 'declined'
    response: Optional[str] = None

class WorkDiscoveryResponse(BaseModel):
    id: str
    title: str
    description: str
    genre: str
    word_count: int
    author_username: str
    average_rating: float
    rating_count: int
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True

# Create or update professional profile
@router.post("/profile", response_model=ProfessionalProfileResponse)
async def create_professional_profile(
    data: ProfessionalProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if profile already exists
    existing = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.user_id == current_user.id
    ).first()

    if existing:
        # Update existing profile
        for key, value in data.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    # Create new profile
    profile = ProfessionalProfile(
        user_id=current_user.id,
        **data.dict()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

# Get professional profile
@router.get("/profile", response_model=ProfessionalProfileResponse)
async def get_professional_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Professional profile not found")

    return profile

# Advanced work discovery for professionals
@router.get("/discover", response_model=List[WorkDiscoveryResponse])
async def discover_works(
    genres: Optional[str] = None,  # Comma-separated
    min_word_count: Optional[int] = None,
    max_word_count: Optional[int] = None,
    min_rating: Optional[float] = None,
    min_views: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get professional profile to use their preferences
    profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.user_id == current_user.id
    ).first()

    # Build query
    query = db.query(
        Work.id,
        Work.title,
        Work.description,
        Work.genre,
        Work.word_count,
        User.username.label('author_username'),
        func.coalesce(func.avg(Rating.score), 0.0).label('average_rating'),
        func.count(Rating.id).label('rating_count'),
        Work.view_count,
        Work.created_at
    ).join(User, Work.author_id == User.id).outerjoin(
        Rating, Work.id == Rating.work_id
    ).filter(
        Work.status == 'published'
    )

    # Apply filters from parameters or profile preferences
    if genres:
        genre_list = [g.strip() for g in genres.split(',')]
        query = query.filter(Work.genre.in_(genre_list))
    elif profile and profile.seeking_genres:
        query = query.filter(Work.genre.in_(profile.seeking_genres))

    if min_word_count:
        query = query.filter(Work.word_count >= min_word_count)
    elif profile and profile.min_word_count:
        query = query.filter(Work.word_count >= profile.min_word_count)

    if max_word_count:
        query = query.filter(Work.word_count <= max_word_count)
    elif profile and profile.max_word_count:
        query = query.filter(Work.word_count <= profile.max_word_count)

    if min_views:
        query = query.filter(Work.view_count >= min_views)

    # Group by work fields
    query = query.group_by(
        Work.id, Work.title, Work.description, Work.genre,
        Work.word_count, User.username, Work.view_count, Work.created_at
    )

    # Apply rating filter after grouping
    if min_rating:
        query = query.having(func.coalesce(func.avg(Rating.score), 0.0) >= min_rating)
    elif profile and profile.min_rating:
        query = query.having(func.coalesce(func.avg(Rating.score), 0.0) >= profile.min_rating)

    # Order by rating and views
    query = query.order_by(
        func.coalesce(func.avg(Rating.score), 0.0).desc(),
        Work.view_count.desc()
    )

    works = query.limit(limit).offset(offset).all()

    return [
        WorkDiscoveryResponse(
            id=str(w.id),
            title=w.title,
            description=w.description,
            genre=w.genre,
            word_count=w.word_count,
            author_username=w.author_username,
            average_rating=float(w.average_rating),
            rating_count=w.rating_count,
            view_count=w.view_count,
            created_at=w.created_at
        )
        for w in works
    ]

# Submit work to professional
@router.post("/submit/{work_id}", response_model=SubmissionResponse)
async def submit_to_professional(
    work_id: UUID,
    professional_id: UUID,
    data: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify work exists and belongs to current user
    work = db.query(Work).filter(
        Work.id == work_id,
        Work.author_id == current_user.id
    ).first()

    if not work:
        raise HTTPException(status_code=404, detail="Work not found or not owned by you")

    # Verify professional exists
    professional = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.id == professional_id
    ).first()

    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    # Check for existing submission
    existing = db.query(Submission).filter(
        Submission.work_id == work_id,
        Submission.professional_id == professional_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted this work to this professional")

    # Create submission
    submission = Submission(
        work_id=work_id,
        author_id=current_user.id,
        professional_id=professional_id,
        message=data.message,
        status="pending"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Get work title for response
    result = SubmissionResponse(
        id=str(submission.id),
        work_id=str(submission.work_id),
        author_id=str(submission.author_id),
        professional_id=str(submission.professional_id),
        status=submission.status,
        message=submission.message,
        response=submission.response,
        submitted_at=submission.submitted_at,
        reviewed_at=submission.reviewed_at,
        responded_at=submission.responded_at,
        work_title=work.title,
        author_username=current_user.username
    )

    return result

# Get user's submissions
@router.get("/submissions", response_model=List[SubmissionResponse])
async def get_my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submissions = db.query(Submission).filter(
        Submission.author_id == current_user.id
    ).order_by(Submission.submitted_at.desc()).all()

    results = []
    for sub in submissions:
        work = db.query(Work).filter(Work.id == sub.work_id).first()
        professional = db.query(ProfessionalProfile).filter(
            ProfessionalProfile.id == sub.professional_id
        ).first()

        results.append(SubmissionResponse(
            id=str(sub.id),
            work_id=str(sub.work_id),
            author_id=str(sub.author_id),
            professional_id=str(sub.professional_id),
            status=sub.status,
            message=sub.message,
            response=sub.response,
            submitted_at=sub.submitted_at,
            reviewed_at=sub.reviewed_at,
            responded_at=sub.responded_at,
            work_title=work.title if work else None,
            author_username=current_user.username
        ))

    return results

# Get submissions received (for professionals)
@router.get("/inbox", response_model=List[SubmissionResponse])
async def get_inbox(
    status: Optional[str] = None,  # Filter by status
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get professional profile
    profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=403, detail="You must have a professional profile to access inbox")

    # Query submissions
    query = db.query(Submission).filter(
        Submission.professional_id == profile.id
    )

    if status:
        query = query.filter(Submission.status == status)

    submissions = query.order_by(Submission.submitted_at.desc()).all()

    results = []
    for sub in submissions:
        work = db.query(Work).filter(Work.id == sub.work_id).first()
        author = db.query(User).filter(User.id == sub.author_id).first()

        results.append(SubmissionResponse(
            id=str(sub.id),
            work_id=str(sub.work_id),
            author_id=str(sub.author_id),
            professional_id=str(sub.professional_id),
            status=sub.status,
            message=sub.message,
            response=sub.response,
            submitted_at=sub.submitted_at,
            reviewed_at=sub.reviewed_at,
            responded_at=sub.responded_at,
            work_title=work.title if work else None,
            author_username=author.username if author else None
        ))

    return results

# Respond to submission
@router.put("/submissions/{submission_id}/respond", response_model=SubmissionResponse)
async def respond_to_submission(
    submission_id: UUID,
    data: SubmissionResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get professional profile
    profile = db.query(ProfessionalProfile).filter(
        ProfessionalProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=403, detail="You must have a professional profile to respond to submissions")

    # Get submission
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.professional_id == profile.id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Update submission
    submission.status = data.status
    if data.response:
        submission.response = data.response

    if data.status == "reviewing" and not submission.reviewed_at:
        submission.reviewed_at = datetime.utcnow()

    if data.status in ["accepted", "declined"]:
        submission.responded_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)

    # Get related data
    work = db.query(Work).filter(Work.id == submission.work_id).first()
    author = db.query(User).filter(User.id == submission.author_id).first()

    return SubmissionResponse(
        id=str(submission.id),
        work_id=str(submission.work_id),
        author_id=str(submission.author_id),
        professional_id=str(submission.professional_id),
        status=submission.status,
        message=submission.message,
        response=submission.response,
        submitted_at=submission.submitted_at,
        reviewed_at=submission.reviewed_at,
        responded_at=submission.responded_at,
        work_title=work.title if work else None,
        author_username=author.username if author else None
    )
