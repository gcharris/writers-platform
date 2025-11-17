"""
Factory Projects Routes
=======================

CRUD operations for Factory workspace projects.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.scene import Scene
from app.services.file_parser import FileParser
from app.services.orchestrator import FactoryOrchestrator

router = APIRouter(tags=["projects"], prefix="/projects")


# Pydantic schemas
from pydantic import BaseModel

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    status: Optional[str] = None

class SceneCreate(BaseModel):
    content: str
    title: Optional[str] = None
    chapter_number: Optional[int] = None
    scene_number: Optional[int] = None

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    genre: Optional[str]
    status: str
    word_count: int
    scene_count: int
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True

class SceneResponse(BaseModel):
    id: str
    project_id: str
    content: str
    title: Optional[str]
    chapter_number: Optional[int]
    scene_number: Optional[int]
    sequence: int
    word_count: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new project from scratch.
    """
    new_project = Project(
        user_id=current_user.id,
        title=project.title,
        description=project.description,
        genre=project.genre,
        status="draft"
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return ProjectResponse(
        id=str(new_project.id),
        user_id=str(new_project.user_id),
        title=new_project.title,
        description=new_project.description,
        genre=new_project.genre,
        status=new_project.status,
        word_count=new_project.word_count,
        scene_count=new_project.scene_count,
        created_at=new_project.created_at.isoformat(),
        updated_at=new_project.updated_at.isoformat() if new_project.updated_at else None
    )


@router.post("/upload", response_model=ProjectResponse)
async def upload_project(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create project by uploading a file (DOCX, PDF, TXT).
    """
    # Read file content
    file_content = await file.read()

    # Parse file
    try:
        parsed = FileParser.parse_file(file_content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"File parser dependency missing: {str(e)}")

    # Create project
    project_title = title or parsed['title']
    new_project = Project(
        user_id=current_user.id,
        title=project_title,
        description=description,
        genre=genre,
        status="draft",
        word_count=parsed['word_count'],
        original_filename=file.filename
        # Note: file_path would be set if we stored files in cloud storage
    )

    db.add(new_project)
    db.flush()  # Get project ID

    # Create scenes from chapters
    scenes_created = 0
    for chapter in parsed.get('chapters', []):
        # Split chapter into scenes if needed
        from app.services.file_parser import FileParser
        chapter_scenes = FileParser.split_into_scenes(chapter['content'])

        for scene_data in chapter_scenes:
            scene = Scene(
                project_id=new_project.id,
                content=scene_data['content'],
                title=chapter['title'],
                chapter_number=chapter['number'],
                scene_number=scene_data['number'],
                sequence=scenes_created + 1,
                word_count=scene_data['word_count']
            )
            db.add(scene)
            scenes_created += 1

    # Update project scene count
    new_project.scene_count = scenes_created

    db.commit()
    db.refresh(new_project)

    return ProjectResponse(
        id=str(new_project.id),
        user_id=str(new_project.user_id),
        title=new_project.title,
        description=new_project.description,
        genre=new_project.genre,
        status=new_project.status,
        word_count=new_project.word_count,
        scene_count=new_project.scene_count,
        created_at=new_project.created_at.isoformat(),
        updated_at=new_project.updated_at.isoformat() if new_project.updated_at else None
    )


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List current user's projects.
    """
    projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).order_by(Project.updated_at.desc()).all()

    return [
        ProjectResponse(
            id=str(p.id),
            user_id=str(p.user_id),
            title=p.title,
            description=p.description,
            genre=p.genre,
            status=p.status,
            word_count=p.word_count,
            scene_count=p.scene_count,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat() if p.updated_at else None
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get project details.
    """
    project = db.query(Project).filter(
        Project.id == uuid.UUID(project_id),
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=str(project.id),
        user_id=str(project.user_id),
        title=project.title,
        description=project.description,
        genre=project.genre,
        status=project.status,
        word_count=project.word_count,
        scene_count=project.scene_count,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat() if project.updated_at else None
    )


@router.get("/{project_id}/scenes", response_model=List[SceneResponse])
async def get_project_scenes(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all scenes for a project.
    """
    project = db.query(Project).filter(
        Project.id == uuid.UUID(project_id),
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scenes = db.query(Scene).filter(
        Scene.project_id == project.id
    ).order_by(Scene.sequence).all()

    return [
        SceneResponse(
            id=str(s.id),
            project_id=str(s.project_id),
            content=s.content,
            title=s.title,
            chapter_number=s.chapter_number,
            scene_number=s.scene_number,
            sequence=s.sequence,
            word_count=s.word_count,
            created_at=s.created_at.isoformat()
        )
        for s in scenes
    ]


@router.post("/{project_id}/scenes", response_model=SceneResponse)
async def add_scene(
    project_id: str,
    scene: SceneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new scene to project.
    """
    project = db.query(Project).filter(
        Project.id == uuid.UUID(project_id),
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get next sequence number
    max_sequence = db.query(Scene).filter(
        Scene.project_id == project.id
    ).count()

    new_scene = Scene(
        project_id=project.id,
        content=scene.content,
        title=scene.title,
        chapter_number=scene.chapter_number,
        scene_number=scene.scene_number,
        sequence=max_sequence + 1,
        word_count=len(scene.content.split())
    )

    db.add(new_scene)

    # Update project stats
    project.scene_count += 1
    project.word_count += new_scene.word_count

    db.commit()
    db.refresh(new_scene)

    return SceneResponse(
        id=str(new_scene.id),
        project_id=str(new_scene.project_id),
        content=new_scene.content,
        title=new_scene.title,
        chapter_number=new_scene.chapter_number,
        scene_number=new_scene.scene_number,
        sequence=new_scene.sequence,
        word_count=new_scene.word_count,
        created_at=new_scene.created_at.isoformat()
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project details.
    """
    project = db.query(Project).filter(
        Project.id == uuid.UUID(project_id),
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields
    if update.title is not None:
        project.title = update.title
    if update.description is not None:
        project.description = update.description
    if update.genre is not None:
        project.genre = update.genre
    if update.status is not None:
        project.status = update.status

    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=str(project.id),
        user_id=str(project.user_id),
        title=project.title,
        description=project.description,
        genre=project.genre,
        status=project.status,
        word_count=project.word_count,
        scene_count=project.scene_count,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat() if project.updated_at else None
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete project and all its scenes.
    """
    project = db.query(Project).filter(
        Project.id == uuid.UUID(project_id),
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}
