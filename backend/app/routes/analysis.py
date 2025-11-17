"""
AI Analysis Routes
==================

Wraps the Factory engine for AI analysis.
Provides async job management for long-running tournaments.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.scene import Scene
from app.services.orchestrator import FactoryOrchestrator

router = APIRouter(tags=["analysis"], prefix="/analysis")


# Pydantic schemas
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    scene_outline: str
    chapter: Optional[str] = None
    context_requirements: Optional[List[str]] = None
    agents: Optional[List[str]] = None
    synthesize: bool = True

class AnalysisStatusResponse(BaseModel):
    id: str
    status: str  # pending, running, completed, failed
    scene_outline: str
    chapter: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    error_message: Optional[str]

class AnalysisResultResponse(BaseModel):
    id: str
    status: str
    scene_outline: str
    chapter: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    summary: Optional[dict]
    full_results: Optional[dict]


@router.post("/run")
async def run_analysis(
    project_id: str,
    analysis: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger AI analysis on a project or scene.

    Returns job ID immediately. Analysis runs in background.
    Poll /analysis/{job_id}/status for progress.
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == uuid.UUID(project_id),
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create orchestrator
    orchestrator = FactoryOrchestrator(db)

    # Start analysis job
    job_id = await orchestrator.run_analysis(
        project_id=uuid.UUID(project_id),
        scene_outline=analysis.scene_outline,
        chapter=analysis.chapter,
        context_requirements=analysis.context_requirements,
        agents=analysis.agents,
        synthesize=analysis.synthesize
    )

    # Run analysis in background
    background_tasks.add_task(
        orchestrator.run_analysis_sync,
        analysis_id=job_id,
        scene_outline=analysis.scene_outline,
        chapter=analysis.chapter,
        context_requirements=analysis.context_requirements,
        agents=analysis.agents,
        synthesize=analysis.synthesize
    )

    # Update project status
    project.status = "analyzing"
    db.commit()

    return {
        "job_id": str(job_id),
        "status": "pending",
        "message": "Analysis started. Poll /analysis/{job_id}/status for progress."
    }


@router.get("/{job_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analysis job status.
    """
    orchestrator = FactoryOrchestrator(db)
    status = orchestrator.get_analysis_status(uuid.UUID(job_id))

    if not status:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    return AnalysisStatusResponse(
        id=status['id'],
        status=status['status'],
        scene_outline=status['scene_outline'],
        chapter=status['chapter'],
        started_at=status['started_at'],
        completed_at=status['completed_at'],
        error_message=status.get('error_message')
    )


@router.get("/{job_id}/results", response_model=AnalysisResultResponse)
async def get_analysis_results(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analysis results.

    Returns full tournament data including:
    - All agent variations with scores
    - Cross-agent critiques
    - Hybrid synthesis (if requested)
    - Cost and token usage
    """
    orchestrator = FactoryOrchestrator(db)
    results = orchestrator.get_analysis_results(uuid.UUID(job_id))

    if not results:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    # If not completed, return status only
    if results['status'] != 'completed':
        return AnalysisResultResponse(
            id=str(job_id),
            status=results['status'],
            scene_outline=results.get('scene_outline', ''),
            chapter=results.get('chapter'),
            started_at=None,
            completed_at=None,
            summary=None,
            full_results=None
        )

    return AnalysisResultResponse(
        id=results['id'],
        status=results['status'],
        scene_outline=results['scene_outline'],
        chapter=results['chapter'],
        started_at=results['started_at'],
        completed_at=results['completed_at'],
        summary=results['summary'],
        full_results=results['full_results']
    )


@router.get("/project/{project_id}/analyses")
async def list_project_analyses(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all analyses for a project.
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == uuid.UUID(project_id),
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    orchestrator = FactoryOrchestrator(db)
    analyses = orchestrator.list_project_analyses(uuid.UUID(project_id))

    return {
        "project_id": project_id,
        "analyses": analyses
    }


@router.get("/models")
async def list_available_models():
    """
    List available AI models for analysis.
    """
    return {
        "models": [
            {
                "id": "claude-sonnet-4-5",
                "name": "Claude Sonnet 4.5",
                "description": "Primary agent - best at voice authenticity and emotional impact",
                "cost_per_1k_tokens": 0.003
            },
            {
                "id": "gemini-1-5-pro",
                "name": "Gemini 1.5 Pro",
                "description": "Best at philosophical arguments and structure",
                "cost_per_1k_tokens": 0.0025
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "description": "Best at dialogue and character consistency",
                "cost_per_1k_tokens": 0.0025
            },
            {
                "id": "grok-2",
                "name": "Grok 2",
                "description": "Best at worldbuilding integration",
                "cost_per_1k_tokens": 0.002
            },
            {
                "id": "claude-haiku",
                "name": "Claude Haiku",
                "description": "Budget option for simple scenes",
                "cost_per_1k_tokens": 0.0004
            }
        ],
        "default": ["claude-sonnet-4-5", "gemini-1-5-pro", "gpt-4o", "grok-2", "claude-haiku"],
        "note": "Costs are approximate and may vary"
    }
