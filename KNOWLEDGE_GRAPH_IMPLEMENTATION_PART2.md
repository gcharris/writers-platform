# Knowledge Graph Implementation Part 2: API, Jobs, Frontend & Integration

**Continuation of**: KNOWLEDGE_GRAPH_IMPLEMENTATION.md

---

## Phase 4: API Layer

### 4.1: Knowledge Graph Router

**File**: `backend/app/routes/knowledge_graph.py`

```python
"""
Complete Knowledge Graph API endpoints.
Handles graph queries, extraction triggers, export, and visualization data.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.manuscript import ManuscriptScene
from app.models.knowledge_graph import ProjectGraph, ExtractionJob
from app.core.auth import get_current_user

from app.services.knowledge_graph.graph_service import KnowledgeGraphService
from app.services.knowledge_graph.extractors.llm_extractor import LLMExtractor
from app.services.knowledge_graph.extractors.ner_extractor import NERExtractor
from app.services.knowledge_graph.models import EntityType, RelationType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExtractRequest(BaseModel):
    """Request to extract entities from a scene."""
    scene_id: str
    extractor_type: str = "llm"  # llm, ner, or hybrid
    model_name: Optional[str] = "claude-sonnet-4.5"


class ExtractResponse(BaseModel):
    """Response from extraction request."""
    job_id: str
    status: str
    message: str


class EntityQuery(BaseModel):
    """Query for entities."""
    entity_type: Optional[EntityType] = None
    min_mentions: int = 0
    verified_only: bool = False
    search_term: Optional[str] = None


class PathQuery(BaseModel):
    """Query for path between entities."""
    source_id: str
    target_id: str


class GraphStats(BaseModel):
    """Graph statistics."""
    entity_count: int
    relationship_count: int
    scene_count: int
    extraction_stats: dict
    central_entities: List[dict]


# ============================================================================
# GRAPH MANAGEMENT
# ============================================================================

@router.get("/projects/{project_id}/graph")
async def get_graph(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete knowledge graph for visualization.

    Returns graph in D3.js/vis.js compatible format.
    """
    # Verify project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph from database
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        # No graph yet, return empty
        return {
            "nodes": [],
            "edges": [],
            "metadata": {
                "project_id": project_id,
                "entity_count": 0,
                "relationship_count": 0
            }
        }

    # Deserialize graph
    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Export for visualization
    return kg.export_for_visualization()


@router.get("/projects/{project_id}/graph/stats")
async def get_graph_stats(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get graph statistics and analytics."""
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        return {
            "entity_count": 0,
            "relationship_count": 0,
            "scene_count": 0,
            "extraction_stats": {},
            "central_entities": []
        }

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Get central entities
    central = kg.get_central_entities(top_n=10)
    central_entities = [
        {
            "entity_id": entity_id,
            "name": kg.get_entity(entity_id).name if kg.get_entity(entity_id) else entity_id,
            "centrality": score
        }
        for entity_id, score in central
    ]

    return {
        "entity_count": graph_record.entity_count,
        "relationship_count": graph_record.relationship_count,
        "scene_count": graph_record.scene_count,
        "extraction_stats": {
            "total": graph_record.total_extractions,
            "successful": graph_record.successful_extractions,
            "failed": graph_record.failed_extractions,
            "success_rate": (
                graph_record.successful_extractions / graph_record.total_extractions
                if graph_record.total_extractions > 0 else 0
            )
        },
        "central_entities": central_entities
    }


# ============================================================================
# ENTITY OPERATIONS
# ============================================================================

@router.get("/projects/{project_id}/entities")
async def list_entities(
    project_id: str,
    entity_type: Optional[str] = None,
    min_mentions: int = 0,
    verified_only: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List entities with filtering.

    Query params:
        entity_type: Filter by type (character, location, etc.)
        min_mentions: Minimum number of scene appearances
        verified_only: Only human-verified entities
        search: Search entity names/descriptions
    """
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        return []

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Query entities
    entity_type_enum = EntityType(entity_type) if entity_type else None
    entities = kg.query_entities(
        entity_type=entity_type_enum,
        min_mentions=min_mentions,
        verified_only=verified_only
    )

    # Apply search filter
    if search:
        search_lower = search.lower()
        entities = [
            e for e in entities
            if search_lower in e.name.lower() or search_lower in e.description.lower()
        ]

    return [e.to_dict() for e in entities]


@router.get("/projects/{project_id}/entities/{entity_id}")
async def get_entity_details(
    project_id: str,
    entity_id: str,
    include_stats: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about an entity."""
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        raise HTTPException(404, "Knowledge graph not found")

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Get entity
    entity = kg.get_entity(entity_id)
    if not entity:
        raise HTTPException(404, f"Entity '{entity_id}' not found")

    # Include stats if requested
    if include_stats:
        return kg.get_entity_stats(entity_id)
    else:
        return entity.to_dict()


@router.put("/projects/{project_id}/entities/{entity_id}")
async def update_entity(
    project_id: str,
    entity_id: str,
    updates: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update entity attributes.

    Common updates:
        - description: Updated description
        - verified: Mark as human-verified (true/false)
        - attributes: Custom attribute updates
    """
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        raise HTTPException(404, "Knowledge graph not found")

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Update entity
    success = kg.update_entity(entity_id, **updates)
    if not success:
        raise HTTPException(404, f"Entity '{entity_id}' not found")

    # Save back to database
    graph_record.graph_data = kg.to_json()
    db.commit()

    return {"status": "updated", "entity_id": entity_id}


@router.get("/projects/{project_id}/entities/{entity_id}/connections")
async def get_entity_connections(
    project_id: str,
    entity_id: str,
    max_depth: int = Query(2, ge=1, le=5),
    relation_types: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get entities connected to this one.

    Query params:
        max_depth: How far to traverse (1-5)
        relation_types: Filter by relationship types
    """
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        raise HTTPException(404, "Knowledge graph not found")

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Get connected entities
    rel_type_enums = None
    if relation_types:
        rel_type_enums = [RelationType(rt) for rt in relation_types]

    connected = kg.get_connected_entities(
        entity_id,
        max_depth=max_depth,
        relation_types=rel_type_enums
    )

    return [e.to_dict() for e in connected]


# ============================================================================
# RELATIONSHIP OPERATIONS
# ============================================================================

@router.get("/projects/{project_id}/relationships")
async def list_relationships(
    project_id: str,
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    relation_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List relationships with filtering.

    Query params:
        source_id: Filter by source entity
        target_id: Filter by target entity
        relation_type: Filter by relationship type
    """
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        return []

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Query relationships
    rel_type_enum = RelationType(relation_type) if relation_type else None
    relationships = kg.get_relationships(
        source_id=source_id,
        target_id=target_id,
        relation_type=rel_type_enum
    )

    return [r.to_dict() for r in relationships]


@router.post("/projects/{project_id}/path")
async def find_path(
    project_id: str,
    query: PathQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find shortest path between two entities."""
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        raise HTTPException(404, "Knowledge graph not found")

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Find path
    path = kg.find_path(query.source_id, query.target_id)

    if not path:
        return {
            "found": False,
            "message": "No path found between entities"
        }

    # Get entity details for path
    path_entities = [kg.get_entity(eid).to_dict() for eid in path if kg.get_entity(eid)]

    return {
        "found": True,
        "path": path,
        "entities": path_entities,
        "length": len(path) - 1  # Number of hops
    }


# ============================================================================
# EXTRACTION OPERATIONS
# ============================================================================

@router.post("/projects/{project_id}/extract")
async def extract_from_scene(
    project_id: str,
    request: ExtractRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger entity/relationship extraction from a scene.

    This runs as a background job and returns immediately.
    Poll /extraction-jobs/{job_id} for status.
    """
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Verify scene exists
    scene = db.query(ManuscriptScene).filter(
        ManuscriptScene.id == request.scene_id
    ).first()

    if not scene:
        raise HTTPException(404, "Scene not found")

    # Create extraction job
    from uuid import uuid4
    job = ExtractionJob(
        id=uuid4(),
        project_id=project_id,
        scene_id=request.scene_id,
        status="pending",
        extractor_type=request.extractor_type,
        model_name=request.model_name
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Schedule background extraction
    background_tasks.add_task(
        run_extraction_job,
        job_id=str(job.id),
        project_id=project_id,
        scene_id=request.scene_id,
        scene_content=scene.content,
        extractor_type=request.extractor_type,
        model_name=request.model_name
    )

    return {
        "job_id": str(job.id),
        "status": "pending",
        "message": "Extraction job started"
    }


@router.post("/projects/{project_id}/extract-all")
async def extract_from_all_scenes(
    project_id: str,
    extractor_type: str = "llm",
    model_name: Optional[str] = "claude-sonnet-4.5",
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extract entities from ALL scenes in project.

    WARNING: This can be expensive if using LLM extraction.
    Consider using 'ner' extractor for large projects.
    """
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Get all scenes
    scenes = db.query(ManuscriptScene).join(
        ManuscriptChapter
    ).join(
        ManuscriptAct
    ).filter(
        ManuscriptAct.project_id == project_id
    ).all()

    if not scenes:
        return {
            "jobs_created": 0,
            "message": "No scenes found in project"
        }

    # Create jobs for each scene
    from uuid import uuid4
    jobs_created = []

    for scene in scenes:
        job = ExtractionJob(
            id=uuid4(),
            project_id=project_id,
            scene_id=scene.id,
            status="pending",
            extractor_type=extractor_type,
            model_name=model_name
        )
        db.add(job)
        jobs_created.append(str(job.id))

        # Schedule background job
        background_tasks.add_task(
            run_extraction_job,
            job_id=str(job.id),
            project_id=project_id,
            scene_id=str(scene.id),
            scene_content=scene.content,
            extractor_type=extractor_type,
            model_name=model_name
        )

    db.commit()

    return {
        "jobs_created": len(jobs_created),
        "job_ids": jobs_created,
        "message": f"Extraction started for {len(jobs_created)} scenes"
    }


@router.get("/extraction-jobs/{job_id}")
async def get_extraction_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of an extraction job."""
    job = db.query(ExtractionJob).filter(
        ExtractionJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(404, "Extraction job not found")

    # Verify user owns the project
    project = db.query(Project).filter(
        Project.id == job.project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    return {
        "job_id": str(job.id),
        "project_id": str(job.project_id),
        "scene_id": str(job.scene_id),
        "status": job.status,
        "extractor_type": job.extractor_type,
        "model_name": job.model_name,
        "entities_extracted": job.entities_extracted,
        "relationships_extracted": job.relationships_extracted,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "duration_seconds": job.duration_seconds,
        "error_message": job.error_message,
        "tokens_used": job.tokens_used,
        "cost": job.cost
    }


@router.get("/projects/{project_id}/extraction-jobs")
async def list_extraction_jobs(
    project_id: str,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List extraction jobs for a project."""
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Query jobs
    query = db.query(ExtractionJob).filter(
        ExtractionJob.project_id == project_id
    )

    if status:
        query = query.filter(ExtractionJob.status == status)

    jobs = query.order_by(ExtractionJob.created_at.desc()).limit(limit).all()

    return [
        {
            "job_id": str(job.id),
            "scene_id": str(job.scene_id),
            "status": job.status,
            "extractor_type": job.extractor_type,
            "entities_extracted": job.entities_extracted,
            "relationships_extracted": job.relationships_extracted,
            "created_at": job.created_at.isoformat(),
            "duration_seconds": job.duration_seconds,
            "cost": job.cost
        }
        for job in jobs
    ]


# ============================================================================
# EXPORT OPERATIONS
# ============================================================================

@router.get("/projects/{project_id}/export/graphml")
async def export_graphml(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export graph as GraphML for Gephi/Cytoscape."""
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        raise HTTPException(404, "Knowledge graph not found")

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Export as GraphML
    graphml = kg.export_graphml()

    from fastapi.responses import Response
    return Response(
        content=graphml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename=knowledge_graph_{project_id}.graphml"
        }
    )


@router.get("/projects/{project_id}/export/notebooklm")
async def export_for_notebooklm(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export graph as markdown summaries for NotebookLM upload.

    Creates one summary document with:
    - Character profiles
    - Location descriptions
    - Relationship summaries
    - Plot connections
    """
    # Verify access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Load graph
    graph_record = db.query(ProjectGraph).filter(
        ProjectGraph.project_id == project_id
    ).first()

    if not graph_record:
        raise HTTPException(404, "Knowledge graph not found")

    kg = KnowledgeGraphService.from_json(graph_record.graph_data)

    # Build markdown document
    markdown_lines = [
        f"# Knowledge Graph Summary: {project.title}",
        f"\nGenerated from {kg.metadata.entity_count} entities and {kg.metadata.relationship_count} relationships.\n",
        "---\n"
    ]

    # Characters section
    characters = kg.query_entities(entity_type=EntityType.CHARACTER)
    if characters:
        markdown_lines.append("## Characters\n")
        for char in sorted(characters, key=lambda e: e.mentions, reverse=True):
            markdown_lines.append(f"### {char.name}\n")
            markdown_lines.append(f"{char.description}\n")
            if char.attributes:
                markdown_lines.append("**Attributes**:")
                for key, value in char.attributes.items():
                    markdown_lines.append(f"- {key}: {value}")
            markdown_lines.append(f"\n**Appearances**: {char.mentions} scenes\n")

    # Locations section
    locations = kg.query_entities(entity_type=EntityType.LOCATION)
    if locations:
        markdown_lines.append("\n## Locations\n")
        for loc in sorted(locations, key=lambda e: e.mentions, reverse=True):
            markdown_lines.append(f"### {loc.name}\n")
            markdown_lines.append(f"{loc.description}\n")

    # Key relationships
    markdown_lines.append("\n## Key Relationships\n")
    all_relationships = kg.get_relationships()
    # Sort by strength
    sorted_rels = sorted(all_relationships, key=lambda r: r.strength, reverse=True)[:50]

    for rel in sorted_rels:
        source = kg.get_entity(rel.source_id)
        target = kg.get_entity(rel.target_id)
        if source and target:
            markdown_lines.append(
                f"- **{source.name}** {rel.relation_type.value} **{target.name}**: {rel.description}\n"
            )

    markdown_content = "\n".join(markdown_lines)

    from fastapi.responses import Response
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=knowledge_graph_summary_{project_id}.md"
        }
    )


# ============================================================================
# BACKGROUND JOB RUNNER
# ============================================================================

async def run_extraction_job(
    job_id: str,
    project_id: str,
    scene_id: str,
    scene_content: str,
    extractor_type: str,
    model_name: Optional[str]
):
    """
    Background task to run entity/relationship extraction.

    Updates job status in database as it progresses.
    """
    from datetime import datetime
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os

    # Create new DB session for background task
    engine = create_engine(os.getenv('DATABASE_URL'))
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Update job status to running
        job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
        if not job:
            logger.error(f"Extraction job {job_id} not found")
            return

        job.status = "running"
        job.started_at = datetime.now()
        db.commit()

        start_time = datetime.now()

        # Load existing graph
        graph_record = db.query(ProjectGraph).filter(
            ProjectGraph.project_id == project_id
        ).first()

        if graph_record:
            kg = KnowledgeGraphService.from_json(graph_record.graph_data)
            existing_entities = list(kg._entity_index.values())
        else:
            kg = KnowledgeGraphService(project_id)
            existing_entities = []

        # Run extraction
        entities = []
        relationships = []
        tokens_used = 0
        cost = 0.0

        if extractor_type == "llm":
            # LLM extraction
            extractor = LLMExtractor(model_name=model_name or "claude-sonnet-4.5")

            entities = await extractor.extract_entities(
                scene_content,
                scene_id,
                existing_entities=existing_entities
            )

            relationships = await extractor.extract_relationships(
                scene_content,
                scene_id,
                entities
            )

            # Estimate tokens (rough)
            tokens_used = len(scene_content.split()) * 2  # Rough estimate
            cost = tokens_used / 1000 * 0.003  # Claude pricing

        elif extractor_type == "ner":
            # NER extraction (fast, no cost)
            extractor = NERExtractor()
            entities = extractor.extract_entities(scene_content, scene_id)
            # NER doesn't extract relationships

        # Add entities to graph
        for entity in entities:
            kg.add_entity(entity)

        # Add relationships to graph
        for relationship in relationships:
            kg.add_relationship(relationship)

        # Save graph back to database
        if graph_record:
            graph_record.graph_data = kg.to_json()
            graph_record.last_updated = datetime.now()
            graph_record.last_extracted_scene = scene_id
            graph_record.entity_count = kg.metadata.entity_count
            graph_record.relationship_count = kg.metadata.relationship_count
            graph_record.total_extractions += 1
            graph_record.successful_extractions += 1
        else:
            graph_record = ProjectGraph(
                project_id=project_id,
                graph_data=kg.to_json(),
                last_extracted_scene=scene_id,
                entity_count=kg.metadata.entity_count,
                relationship_count=kg.metadata.relationship_count,
                total_extractions=1,
                successful_extractions=1
            )
            db.add(graph_record)

        # Update job status to completed
        job.status = "completed"
        job.completed_at = datetime.now()
        job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
        job.entities_extracted = len(entities)
        job.relationships_extracted = len(relationships)
        job.tokens_used = tokens_used
        job.cost = cost

        db.commit()

        logger.info(
            f"Extraction job {job_id} completed: "
            f"{len(entities)} entities, {len(relationships)} relationships"
        )

    except Exception as e:
        logger.error(f"Extraction job {job_id} failed: {e}", exc_info=True)

        # Update job status to failed
        job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.completed_at = datetime.now()
            if job.started_at:
                job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
            job.error_message = str(e)

            # Update graph stats
            graph_record = db.query(ProjectGraph).filter(
                ProjectGraph.project_id == project_id
            ).first()
            if graph_record:
                graph_record.total_extractions += 1
                graph_record.failed_extractions += 1

            db.commit()

    finally:
        db.close()
```

---

*Continue in KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md for:*
- Frontend visualization components
- React hooks for graph data
- D3.js/vis.js integration
- Automatic extraction triggers
- WebSocket updates
- Integration with workflow system
- Testing strategy
- Deployment instructions

**Should I create Part 3 with the frontend implementation?**
