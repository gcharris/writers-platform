"""Workflow execution endpoints for Factory AI operations.

This module provides FastAPI endpoints for:
- Scene generation with knowledge context
- Scene enhancement and voice testing
- Project creation workflows
- Real-time workflow progress tracking via WebSocket
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.manuscript import ManuscriptAct, ManuscriptChapter, ManuscriptScene

# Import workflow components
from app.core.workflow_engine import WorkflowEngine, WorkflowResult, WorkflowStatus
from app.workflows.scene_operations import (
    SceneGenerationWorkflow,
    SceneEnhancementWorkflow,
    VoiceTestingWorkflow
)
from app.services.knowledge.router import KnowledgeRouter
from app.core.agent_pool_initializer import create_default_agent_pool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Global agent pool (initialized once at startup)
_agent_pool = None

def get_agent_pool():
    """Get or create the global agent pool instance."""
    global _agent_pool
    if _agent_pool is None:
        logger.info("Initializing global agent pool...")
        _agent_pool = create_default_agent_pool()
    return _agent_pool

# ============================================================================
# Pydantic Schemas
# ============================================================================

class SceneGenerationRequest(BaseModel):
    """Request to generate a new scene."""
    project_id: UUID
    act_number: int = Field(..., ge=1, description="Act number (1, 2, 3, etc.)")
    chapter_number: int = Field(..., ge=1, description="Chapter number within act")
    scene_number: int = Field(..., ge=1, description="Scene number within chapter")
    outline: str = Field(..., min_length=10, description="Scene outline/scaffold")
    title: Optional[str] = Field(None, description="Scene title")
    model_name: str = Field("claude-sonnet-4.5", description="AI model to use")
    use_knowledge_context: bool = Field(True, description="Query knowledge base for context")
    context_queries: Optional[List[str]] = Field(None, description="Specific KB queries")

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "act_number": 1,
                "chapter_number": 3,
                "scene_number": 2,
                "outline": "POV: Mickey. Location: The Explants compound. Mickey confronts Noni about the memory glitches.",
                "title": "Memory Confrontation",
                "model_name": "claude-sonnet-4.5",
                "use_knowledge_context": True,
                "context_queries": ["Mickey's character traits", "Noni's relationship with Mickey"]
            }
        }


class SceneEnhancementRequest(BaseModel):
    """Request to enhance an existing scene."""
    scene_id: UUID
    model_name: str = Field("claude-sonnet-4.5", description="AI model to use")
    character: str = Field("protagonist", description="Character for voice consistency")

    class Config:
        json_schema_extra = {
            "example": {
                "scene_id": "123e4567-e89b-12d3-a456-426614174000",
                "model_name": "claude-sonnet-4.5",
                "character": "protagonist"
            }
        }


class VoiceTestingRequest(BaseModel):
    """Request to test voice consistency across models."""
    prompt: str = Field(..., min_length=10)
    models: List[str] = Field(..., min_items=2, max_items=5)
    character: str = Field("protagonist", description="Character for voice testing")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a paragraph where the protagonist reflects on their mission.",
                "models": ["claude-sonnet-4.5", "gpt-4o", "gemini-2-flash"],
                "character": "Mickey"
            }
        }


class WorkflowStatusResponse(BaseModel):
    """Workflow execution status."""
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_completed: int
    steps_total: int
    outputs: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    duration: Optional[float] = None
    success: bool

    class Config:
        from_attributes = True


class SceneGenerationResponse(BaseModel):
    """Response from scene generation workflow."""
    workflow_id: str
    status: str
    scene_id: Optional[UUID] = None
    scene_content: Optional[str] = None
    word_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


# ============================================================================
# In-memory workflow tracking (TODO: Replace with database persistence)
# ============================================================================

active_workflows: Dict[str, WorkflowResult] = {}
websocket_connections: Dict[str, List[WebSocket]] = {}


# ============================================================================
# Scene Generation Endpoint
# ============================================================================

@router.post("/scene/generate", response_model=SceneGenerationResponse)
async def generate_scene(
    request: SceneGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a new scene with knowledge context.

    This endpoint:
    1. Validates project and manuscript structure
    2. Queries knowledge base for relevant context (characters, plot, world)
    3. Executes scene generation workflow with selected AI model
    4. Saves generated scene to database
    5. Returns scene content and metadata

    The workflow can be monitored in real-time via WebSocket at
    /api/workflows/{workflow_id}/stream
    """
    # Validate project exists and user has access
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project {request.project_id} not found or access denied"
        )

    # Get or create manuscript structure
    act = db.query(ManuscriptAct).filter(
        ManuscriptAct.project_id == request.project_id,
        ManuscriptAct.act_number == request.act_number
    ).first()

    if not act:
        # Create act if it doesn't exist
        act = ManuscriptAct(
            project_id=request.project_id,
            act_number=request.act_number,
            title=f"Act {request.act_number}",
            volume=1  # Default to volume 1
        )
        db.add(act)
        db.flush()

    # Get or create chapter
    chapter = db.query(ManuscriptChapter).filter(
        ManuscriptChapter.act_id == act.id,
        ManuscriptChapter.chapter_number == request.chapter_number
    ).first()

    if not chapter:
        chapter = ManuscriptChapter(
            act_id=act.id,
            chapter_number=request.chapter_number,
            title=f"Chapter {request.chapter_number}"
        )
        db.add(chapter)
        db.flush()

    # Check if scene already exists
    existing_scene = db.query(ManuscriptScene).filter(
        ManuscriptScene.chapter_id == chapter.id,
        ManuscriptScene.scene_number == request.scene_number
    ).first()

    if existing_scene:
        raise HTTPException(
            status_code=400,
            detail=f"Scene {request.scene_number} already exists in Chapter {request.chapter_number}. Use enhancement endpoint to modify."
        )

    try:
        # Initialize knowledge router for this project
        knowledge_router = KnowledgeRouter(
            db=db,
            project_id=request.project_id,
            notebooklm_enabled=False,  # TODO: Read from project settings
            enable_caching=True
        )

        # Get agent pool
        agent_pool = get_agent_pool()

        # Initialize workflow engine and scene generation workflow
        engine = WorkflowEngine()
        workflow = SceneGenerationWorkflow(
            knowledge_router=knowledge_router,
            agent_pool=agent_pool
        )

        # Execute workflow
        logger.info(f"Starting scene generation workflow for project {request.project_id}")
        result = await workflow.run(
            outline=request.outline,
            model_name=request.model_name,
            use_knowledge_context=request.use_knowledge_context,
            context_queries=request.context_queries
        )

        # Store workflow result for status queries
        active_workflows[result.workflow_id] = result

        # Notify WebSocket listeners
        await _broadcast_workflow_update(result.workflow_id, {
            "type": "workflow_completed",
            "status": result.status.value,
            "outputs": result.outputs
        })

        if result.success:
            # Extract generated scene from workflow outputs
            scene_content = result.outputs.get("scene", "")

            # Create scene in database
            new_scene = ManuscriptScene(
                chapter_id=chapter.id,
                scene_number=request.scene_number,
                title=request.title or f"Scene {request.scene_number}",
                content=scene_content,
                metadata={
                    "workflow_id": result.workflow_id,
                    "model": request.model_name,
                    "outline": request.outline,
                    "kb_queries": request.context_queries or [],
                    "generation_timestamp": datetime.now().isoformat()
                }
            )
            new_scene.update_content(scene_content)  # Calculates word count

            db.add(new_scene)
            db.commit()
            db.refresh(new_scene)

            logger.info(f"Scene {new_scene.id} created successfully ({new_scene.word_count} words)")

            return SceneGenerationResponse(
                workflow_id=result.workflow_id,
                status=result.status.value,
                scene_id=new_scene.id,
                scene_content=scene_content,
                word_count=new_scene.word_count,
                metadata=result.metadata
            )
        else:
            # Workflow failed
            raise HTTPException(
                status_code=500,
                detail=f"Scene generation failed: {', '.join(result.errors)}"
            )

    except Exception as e:
        logger.error(f"Scene generation error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Scene generation failed: {str(e)}"
        )


# ============================================================================
# Scene Enhancement Endpoint
# ============================================================================

@router.post("/scene/enhance")
async def enhance_scene(
    request: SceneEnhancementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enhance an existing scene with voice consistency checks.

    This endpoint:
    1. Retrieves the existing scene
    2. Queries knowledge base for voice requirements
    3. Enhances the scene using selected AI model
    4. Validates voice consistency
    5. Updates the scene in database
    """
    # Get scene and validate access
    scene = db.query(ManuscriptScene).filter(
        ManuscriptScene.id == request.scene_id
    ).first()

    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    # Validate user owns the project
    chapter = db.query(ManuscriptChapter).filter(
        ManuscriptChapter.id == scene.chapter_id
    ).first()
    act = db.query(ManuscriptAct).filter(ManuscriptAct.id == chapter.act_id).first()
    project = db.query(Project).filter(
        Project.id == act.project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        # Initialize knowledge router for this project
        knowledge_router = KnowledgeRouter(
            db=db,
            project_id=project.id,
            notebooklm_enabled=False,  # TODO: Read from project settings
            enable_caching=True
        )

        # Get agent pool
        agent_pool = get_agent_pool()

        # Initialize workflow
        engine = WorkflowEngine()
        workflow = SceneEnhancementWorkflow(
            knowledge_router=knowledge_router,
            agent_pool=agent_pool
        )

        # Execute enhancement workflow
        logger.info(f"Starting scene enhancement workflow for scene {request.scene_id}")
        result = await workflow.run(
            scene=scene.content,
            model_name=request.model_name,
            character=request.character
        )

        # Store workflow result
        active_workflows[result.workflow_id] = result

        if result.success:
            # Get enhanced scene from outputs
            enhanced_content = result.outputs.get("enhanced_scene", "")
            validation = result.outputs.get("validation", {})

            # Update scene in database
            original_content = scene.content
            scene.update_content(enhanced_content)

            # Update metadata
            if not scene.metadata:
                scene.metadata = {}
            scene.metadata["enhancement_history"] = scene.metadata.get("enhancement_history", [])
            scene.metadata["enhancement_history"].append({
                "workflow_id": result.workflow_id,
                "model": request.model_name,
                "timestamp": datetime.now().isoformat(),
                "validation_score": validation.get("score", 0),
                "original_word_count": len(original_content.split())
            })

            db.commit()
            db.refresh(scene)

            return {
                "workflow_id": result.workflow_id,
                "status": result.status.value,
                "scene_id": scene.id,
                "enhanced_content": enhanced_content,
                "word_count": scene.word_count,
                "validation": validation
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Enhancement failed: {', '.join(result.errors)}"
            )

    except Exception as e:
        logger.error(f"Scene enhancement error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Voice Testing Endpoint
# ============================================================================

@router.post("/voice/test")
async def test_voice(
    request: VoiceTestingRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Test voice consistency across multiple AI models.

    This endpoint:
    1. Generates outputs from all specified models
    2. Scores voice consistency for each output
    3. Compares results
    4. Recommends the best model for the character's voice

    Useful for determining which AI model best captures a character's voice.
    """
    try:
        # Get agent pool
        agent_pool = get_agent_pool()

        # Initialize workflow
        engine = WorkflowEngine()
        workflow = VoiceTestingWorkflow(
            agent_pool=agent_pool
        )

        # Execute voice testing workflow
        logger.info(f"Starting voice testing workflow with {len(request.models)} models")
        result = await workflow.run(
            prompt=request.prompt,
            models=request.models,
            character=request.character
        )

        # Store workflow result
        active_workflows[result.workflow_id] = result

        if result.success:
            return {
                "workflow_id": result.workflow_id,
                "status": result.status.value,
                "comparison": result.outputs.get("comparison", []),
                "recommendation": result.outputs.get("recommendation", {}),
                "metadata": result.metadata
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Voice testing failed: {', '.join(result.errors)}"
            )

    except Exception as e:
        logger.error(f"Voice testing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Workflow Status Endpoint
# ============================================================================

@router.get("/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the status of a running or completed workflow.

    Returns detailed execution information including:
    - Current status (pending, running, completed, failed)
    - Steps completed vs total steps
    - Outputs from completed steps
    - Any errors encountered
    - Execution duration
    """
    result = active_workflows.get(workflow_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow {workflow_id} not found"
        )

    return WorkflowStatusResponse(
        workflow_id=result.workflow_id,
        status=result.status.value,
        started_at=result.started_at,
        completed_at=result.completed_at,
        steps_completed=result.steps_completed,
        steps_total=result.steps_total,
        outputs=result.outputs,
        errors=result.errors,
        metadata=result.metadata,
        duration=result.duration,
        success=result.success
    )


# ============================================================================
# WebSocket Endpoint for Real-Time Updates
# ============================================================================

@router.websocket("/{workflow_id}/stream")
async def workflow_stream(
    websocket: WebSocket,
    workflow_id: str
):
    """
    WebSocket endpoint for real-time workflow progress updates.

    Clients can connect to receive live updates as the workflow executes:
    - Step start/completion events
    - Progress updates
    - Intermediate outputs
    - Error notifications
    - Final completion status

    Example client usage:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/workflows/{workflow_id}/stream');
    ws.onmessage = (event) => {
        const update = JSON.parse(event.data);
        console.log('Workflow update:', update);
    };
    ```
    """
    await websocket.accept()

    # Register connection
    if workflow_id not in websocket_connections:
        websocket_connections[workflow_id] = []
    websocket_connections[workflow_id].append(websocket)

    try:
        # Send initial status if workflow exists
        if workflow_id in active_workflows:
            result = active_workflows[workflow_id]
            await websocket.send_json({
                "type": "status",
                "workflow_id": workflow_id,
                "status": result.status.value,
                "steps_completed": result.steps_completed,
                "steps_total": result.steps_total
            })
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Workflow {workflow_id} not found"
            })

        # Keep connection alive and listen for client messages
        while True:
            try:
                # Receive any client messages (ping/pong, close, etc.)
                data = await websocket.receive_text()
                # Echo back for now (can handle commands in future)
                await websocket.send_json({"type": "echo", "data": data})
            except WebSocketDisconnect:
                break

    finally:
        # Unregister connection
        if workflow_id in websocket_connections:
            websocket_connections[workflow_id].remove(websocket)
            if not websocket_connections[workflow_id]:
                del websocket_connections[workflow_id]


# ============================================================================
# Helper Functions
# ============================================================================

async def _broadcast_workflow_update(workflow_id: str, message: Dict[str, Any]):
    """Broadcast update to all WebSocket connections for a workflow."""
    if workflow_id in websocket_connections:
        disconnected = []
        for ws in websocket_connections[workflow_id]:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.append(ws)

        # Clean up disconnected clients
        for ws in disconnected:
            websocket_connections[workflow_id].remove(ws)
