from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.work import Work
from app.models.user import User
from app.models.project import Project
from app.models.scene import Scene
from app.schemas.work import WorkCreate, WorkResponse, WorkUpdate
from app.services.badge_engine import BadgeEngine

router = APIRouter(prefix="/works", tags=["Works"])

@router.post("/", response_model=WorkResponse, status_code=status.HTTP_201_CREATED)
async def create_work(
    work_data: WorkCreate,
    claim_human_authored: bool = Query(False, description="Claim human authorship for AI detection"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new work with automatic badge assignment.

    Phase 2: Community Platform Migration
    Automatically assigns badge based on AI detection.
    """

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
    db.flush()  # Get work.id before creating badge

    # Assign badge based on upload type
    badge_engine = BadgeEngine(db)
    badge = await badge_engine.assign_badge_for_upload(
        work=work,
        claim_human_authored=claim_human_authored,
        use_ai_detection=True
    )

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


@router.post("/from-factory/{factory_project_id}", response_model=WorkResponse)
async def publish_from_factory(
    factory_project_id: UUID,
    title: str = Query(..., description="Title for published work"),
    summary: str = Query(..., description="Summary for published work"),
    visibility: str = Query("public", description="Visibility: public, private, unlisted"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publish a Factory project to Community with AI-Analyzed badge.

    Phase 2: Community Platform Migration
    Links Factory project to published work and assigns ai_analyzed badge.
    """

    # Get Factory project (verify ownership)
    project = db.query(Project).filter(
        Project.id == factory_project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found or unauthorized")

    # Combine all scenes into content
    scenes = db.query(Scene).filter(
        Scene.project_id == factory_project_id
    ).order_by(Scene.sequence).all()

    if not scenes:
        raise HTTPException(400, "Project has no scenes to publish")

    content = "\n\n".join([f"# {scene.title}\n\n{scene.content}" for scene in scenes])
    word_count = len(content.split())

    # Create work
    work = Work(
        author_id=current_user.id,
        title=title,
        summary=summary,
        genre=project.genre or "Fiction",
        content=content,
        word_count=word_count,
        factory_project_id=factory_project_id,
        status="published",
        visibility=visibility
    )

    # Get Factory analysis scores if available
    from app.models.analysis_result import AnalysisResult
    latest_analysis = db.query(AnalysisResult).filter(
        AnalysisResult.project_id == factory_project_id
    ).order_by(AnalysisResult.created_at.desc()).first()

    if latest_analysis:
        work.factory_scores = {
            "best_score": latest_analysis.best_score,
            "hybrid_score": latest_analysis.hybrid_score,
            "total_cost": latest_analysis.total_cost
        }

    db.add(work)
    db.flush()

    # Assign AI-Analyzed badge
    badge_engine = BadgeEngine(db)
    badge = badge_engine.assign_badge_for_factory_work(
        work=work,
        factory_project=project
    )

    db.commit()
    db.refresh(work)

    return work
