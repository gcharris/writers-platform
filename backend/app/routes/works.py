from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.work import Work
from app.models.user import User
from app.schemas.work import WorkCreate, WorkResponse, WorkUpdate

router = APIRouter(prefix="/works", tags=["Works"])

@router.post("/", response_model=WorkResponse, status_code=status.HTTP_201_CREATED)
async def create_work(
    work_data: WorkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new work."""

    # Calculate word count
    word_count = len(work_data.content.split())

    work = Work(
        author_id=current_user.id,
        title=work_data.title,
        genre=work_data.genre,
        content_rating=work_data.content_rating,
        content=work_data.content,
        word_count=word_count,
        summary=work_data.summary,
        status="draft"
    )

    db.add(work)
    db.commit()
    db.refresh(work)

    return work

@router.get("/{work_id}", response_model=WorkResponse)
async def get_work(work_id: UUID, db: Session = Depends(get_db)):
    """Get a work by ID."""

    work = db.query(Work).filter(Work.id == work_id).first()

    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    return work

@router.get("/", response_model=List[WorkResponse])
async def list_works(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List all published works."""

    works = db.query(Work).filter(Work.status == "published").offset(skip).limit(limit).all()
    return works

@router.patch("/{work_id}", response_model=WorkResponse)
async def update_work(
    work_id: UUID,
    work_data: WorkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a work."""

    work = db.query(Work).filter(Work.id == work_id, Work.author_id == current_user.id).first()

    if not work:
        raise HTTPException(status_code=404, detail="Work not found or unauthorized")

    # Update fields
    for field, value in work_data.dict(exclude_unset=True).items():
        setattr(work, field, value)

    # Recalculate word count if content changed
    if work_data.content:
        work.word_count = len(work.content.split())

    db.commit()
    db.refresh(work)

    return work

@router.delete("/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work(
    work_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a work."""

    work = db.query(Work).filter(Work.id == work_id, Work.author_id == current_user.id).first()

    if not work:
        raise HTTPException(status_code=404, detail="Work not found or unauthorized")

    db.delete(work)
    db.commit()

    return None
