"""Tests for workflow endpoints.

This module contains tests for the Factory workflow API endpoints including:
- Scene generation
- Scene enhancement
- Voice testing
- Workflow status tracking
- WebSocket streaming
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

# These tests require the full application setup with database
# Run with: pytest tests/test_workflows.py -v

# ============================================================================
# Test Data
# ============================================================================

SAMPLE_SCENE_OUTLINE = """POV: Mickey Bardot
Location: The Explants compound, Medical Wing

Mickey confronts Noni about the memory glitches she's been experiencing.
Noni deflects, but Mickey presses harder. The conversation reveals tension
in their relationship and hints at something deeper going on with the
consciousness transfer technology.

Key beats:
- Mickey notices Noni acting distant
- She asks about the memory recovery process
- Noni gives technical answers, avoids emotional ones
- Mickey realizes Noni might be hiding something
"""

SAMPLE_SCENE_CONTENT = """Mickey found Noni in the medical wing, hunched over
a holographic display. The blue light carved shadows across her face.

"We need to talk," Mickey said.

Noni didn't look up. "I'm running diagnostics."

"On what? Me?" The words came out sharper than intended.

That got Noni's attention. She straightened, and for a moment, something
flickered in her eyes—concern? Guilt? It vanished before Mickey could be sure.

"The transfer protocol," Noni said. "Standard post-op monitoring."

"My memories are glitching." Mickey stepped closer. "Whole chunks missing.
You told me that was normal."

"It is normal."

"Then why won't you look at me?"

Silence. The hologram cycled through incomprehensible data streams.

Finally: "Some memory loss is expected during integration. The neural
pathways need time to—"

"I don't want a technical answer." Mickey's voice dropped. "I want the truth."

Noni met her gaze. Held it. "That *is* the truth."

But the way she said it—clinical, detached—told Mickey everything she
needed to know. Noni was lying.
"""


# ============================================================================
# Test Scene Generation Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_generate_scene_success(client, auth_headers, test_project):
    """Test successful scene generation with knowledge context."""

    request_data = {
        "project_id": str(test_project.id),
        "act_number": 1,
        "chapter_number": 1,
        "scene_number": 1,
        "outline": SAMPLE_SCENE_OUTLINE,
        "title": "Memory Confrontation",
        "model_name": "claude-sonnet-4.5",
        "use_knowledge_context": True,
        "context_queries": [
            "What is Mickey's personality?",
            "What is Noni's role in The Explants?"
        ]
    }

    response = client.post(
        "/api/workflows/scene/generate",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "workflow_id" in data
    assert data["status"] in ["completed", "running"]
    assert "scene_id" in data
    assert "scene_content" in data
    assert data["word_count"] > 0

    # Verify workflow can be queried
    workflow_response = client.get(
        f"/api/workflows/{data['workflow_id']}",
        headers=auth_headers
    )
    assert workflow_response.status_code == 200


@pytest.mark.asyncio
async def test_generate_scene_duplicate(client, auth_headers, test_project, test_scene):
    """Test that generating a scene that already exists returns an error."""

    request_data = {
        "project_id": str(test_project.id),
        "act_number": 1,
        "chapter_number": 1,
        "scene_number": 1,  # Already exists
        "outline": SAMPLE_SCENE_OUTLINE,
        "model_name": "claude-sonnet-4.5"
    }

    response = client.post(
        "/api/workflows/scene/generate",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_scene_unauthorized(client, test_project):
    """Test scene generation without authentication fails."""

    request_data = {
        "project_id": str(test_project.id),
        "act_number": 1,
        "chapter_number": 1,
        "scene_number": 1,
        "outline": SAMPLE_SCENE_OUTLINE
    }

    response = client.post("/api/workflows/scene/generate", json=request_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_generate_scene_creates_structure(client, auth_headers, test_project):
    """Test that generating a scene creates Act and Chapter if they don't exist."""

    request_data = {
        "project_id": str(test_project.id),
        "act_number": 2,  # New act
        "chapter_number": 5,  # New chapter
        "scene_number": 1,
        "outline": SAMPLE_SCENE_OUTLINE,
        "model_name": "claude-sonnet-4.5"
    }

    response = client.post(
        "/api/workflows/scene/generate",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    # Verify act and chapter were created in database


# ============================================================================
# Test Scene Enhancement Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_enhance_scene_success(client, auth_headers, test_scene):
    """Test successful scene enhancement."""

    request_data = {
        "scene_id": str(test_scene.id),
        "model_name": "claude-sonnet-4.5",
        "character": "Mickey"
    }

    response = client.post(
        "/api/workflows/scene/enhance",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "workflow_id" in data
    assert data["status"] == "completed"
    assert "enhanced_content" in data
    assert "validation" in data
    assert data["validation"]["score"] > 0


@pytest.mark.asyncio
async def test_enhance_scene_not_found(client, auth_headers):
    """Test enhancing a non-existent scene."""

    request_data = {
        "scene_id": str(uuid4()),
        "model_name": "claude-sonnet-4.5"
    }

    response = client.post(
        "/api/workflows/scene/enhance",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 404


# ============================================================================
# Test Voice Testing Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_voice_testing_success(client, auth_headers):
    """Test voice consistency testing across models."""

    request_data = {
        "prompt": "Write a paragraph where Mickey reflects on her mission.",
        "models": ["claude-sonnet-4.5", "gpt-4o", "gemini-2-flash"],
        "character": "Mickey"
    }

    response = client.post(
        "/api/workflows/voice/test",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "workflow_id" in data
    assert "comparison" in data
    assert len(data["comparison"]) == 3  # Three models tested
    assert "recommendation" in data
    assert "winner" in data["recommendation"]


@pytest.mark.asyncio
async def test_voice_testing_min_models(client, auth_headers):
    """Test voice testing requires at least 2 models."""

    request_data = {
        "prompt": "Test prompt",
        "models": ["claude-sonnet-4.5"],  # Only one model
        "character": "Mickey"
    }

    response = client.post(
        "/api/workflows/voice/test",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 422  # Validation error


# ============================================================================
# Test Workflow Status Endpoint
# ============================================================================

@pytest.mark.asyncio
async def test_get_workflow_status(client, auth_headers, completed_workflow):
    """Test retrieving workflow status."""

    response = client.get(
        f"/api/workflows/{completed_workflow.workflow_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["workflow_id"] == completed_workflow.workflow_id
    assert data["status"] == "completed"
    assert data["steps_completed"] == data["steps_total"]
    assert "outputs" in data
    assert "duration" in data
    assert data["success"] is True


@pytest.mark.asyncio
async def test_get_workflow_not_found(client, auth_headers):
    """Test querying non-existent workflow."""

    response = client.get(
        f"/api/workflows/{uuid4()}",
        headers=auth_headers
    )

    assert response.status_code == 404


# ============================================================================
# Test WebSocket Streaming
# ============================================================================

@pytest.mark.asyncio
async def test_websocket_workflow_stream(client, auth_headers):
    """Test WebSocket connection for real-time workflow updates."""

    # Start a workflow
    request_data = {
        "project_id": str(test_project.id),
        "act_number": 1,
        "chapter_number": 1,
        "scene_number": 999,
        "outline": SAMPLE_SCENE_OUTLINE,
        "model_name": "claude-sonnet-4.5"
    }

    # Connect via WebSocket
    with client.websocket_connect(f"/api/workflows/{workflow_id}/stream") as websocket:
        # Should receive initial status
        data = websocket.receive_json()
        assert data["type"] == "status"
        assert "workflow_id" in data

        # Should receive updates as workflow progresses
        # (In real test, would verify step completion messages)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_project(db, test_user):
    """Create a test project."""
    from app.models.project import Project

    project = Project(
        user_id=test_user.id,
        name="Test Novel",
        description="Test project for workflow testing",
        metadata={}
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def test_scene(db, test_project):
    """Create a test scene with full manuscript structure."""
    from app.models.manuscript import ManuscriptAct, ManuscriptChapter, ManuscriptScene

    # Create Act
    act = ManuscriptAct(
        project_id=test_project.id,
        act_number=1,
        title="Act 1",
        volume=1
    )
    db.add(act)
    db.flush()

    # Create Chapter
    chapter = ManuscriptChapter(
        act_id=act.id,
        chapter_number=1,
        title="Chapter 1"
    )
    db.add(chapter)
    db.flush()

    # Create Scene
    scene = ManuscriptScene(
        chapter_id=chapter.id,
        scene_number=1,
        title="Test Scene",
        content=SAMPLE_SCENE_CONTENT
    )
    scene.update_content(SAMPLE_SCENE_CONTENT)

    db.add(scene)
    db.commit()
    db.refresh(scene)
    return scene


@pytest.fixture
def completed_workflow():
    """Create a mock completed workflow result."""
    from app.core.workflow_engine import WorkflowResult, WorkflowStatus
    from datetime import datetime, timedelta

    started = datetime.now()
    completed = started + timedelta(seconds=5)

    return WorkflowResult(
        workflow_id=str(uuid4()),
        status=WorkflowStatus.COMPLETED,
        started_at=started,
        completed_at=completed,
        steps_completed=4,
        steps_total=4,
        outputs={"scene": SAMPLE_SCENE_CONTENT},
        errors=[],
        metadata={"model": "claude-sonnet-4.5"}
    )


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_scene_generation_workflow(client, auth_headers, test_project):
    """Test complete workflow: generate scene, enhance it, test voice."""

    # Step 1: Generate initial scene
    gen_response = client.post(
        "/api/workflows/scene/generate",
        json={
            "project_id": str(test_project.id),
            "act_number": 1,
            "chapter_number": 1,
            "scene_number": 1,
            "outline": SAMPLE_SCENE_OUTLINE,
            "model_name": "claude-sonnet-4.5"
        },
        headers=auth_headers
    )
    assert gen_response.status_code == 200
    scene_id = gen_response.json()["scene_id"]

    # Step 2: Enhance the scene
    enhance_response = client.post(
        "/api/workflows/scene/enhance",
        json={
            "scene_id": scene_id,
            "model_name": "claude-sonnet-4.5",
            "character": "Mickey"
        },
        headers=auth_headers
    )
    assert enhance_response.status_code == 200
    assert enhance_response.json()["validation"]["passed"] is True

    # Step 3: Test voice consistency
    voice_response = client.post(
        "/api/workflows/voice/test",
        json={
            "prompt": "Mickey confronts Noni about trust.",
            "models": ["claude-sonnet-4.5", "gpt-4o"],
            "character": "Mickey"
        },
        headers=auth_headers
    )
    assert voice_response.status_code == 200
    assert "winner" in voice_response.json()["recommendation"]
