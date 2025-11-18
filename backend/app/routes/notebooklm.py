"""
NotebookLM API Endpoints

Provides REST API for querying NotebookLM notebooks and extracting
research-grounded entities into the knowledge graph.

Phase 9: NotebookLM MCP Integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import json
import logging

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.knowledge_graph import ProjectGraph
from app.services.notebooklm import get_mcp_client
from app.services.notebooklm.mcp_client import NotebookInfo, NotebookQuery, NotebookResponse
from app.services.knowledge_graph.graph_service import KnowledgeGraphService
from app.services.knowledge_graph.models import Entity, Relationship
from app.services.knowledge_graph.extractors.llm_extractor import LLMExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notebooklm", tags=["notebooklm"])


@router.get("/status")
async def get_notebooklm_status():
    """
    Check NotebookLM MCP server status.

    Returns:
        Status information about MCP server availability
    """
    client = get_mcp_client()
    is_available = await client.is_available()

    return {
        "available": is_available,
        "server_type": "NotebookLM MCP",
        "message": "MCP server is running" if is_available else "MCP server not available"
    }


@router.get("/notebooks", response_model=List[NotebookInfo])
async def list_notebooks(
    current_user: User = Depends(get_current_user)
):
    """
    List all NotebookLM notebooks accessible to the user.

    This queries the MCP server for available notebooks.
    """
    client = get_mcp_client()

    try:
        notebooks = await client.list_notebooks()
        return notebooks
    except Exception as e:
        logger.error(f"Error listing notebooks: {e}")
        raise HTTPException(500, f"Failed to list notebooks: {str(e)}")


@router.post("/query", response_model=NotebookResponse)
async def query_notebook(
    query: NotebookQuery,
    current_user: User = Depends(get_current_user)
):
    """
    Query a NotebookLM notebook with a question.

    Example:
        POST /api/notebooklm/query
        {
            "notebook_id": "abc123",
            "query": "How would Mo Gawdat describe AI in 10 years?",
            "max_sources": 5
        }

    Returns:
        Answer with citations from notebook sources
    """
    client = get_mcp_client()

    try:
        response = await client.query_notebook(
            notebook_id=query.notebook_id,
            query=query.query,
            max_sources=query.max_sources
        )
        return response
    except Exception as e:
        logger.error(f"Error querying notebook: {e}")
        raise HTTPException(500, f"Failed to query notebook: {str(e)}")


@router.post("/projects/{project_id}/extract-character")
async def extract_character_from_notebook(
    project_id: UUID,
    notebook_id: str = Query(..., description="NotebookLM notebook ID or URL"),
    character_name: str = Query(..., description="Name of character to extract"),
    add_to_graph: bool = Query(True, description="Add extracted entities to knowledge graph"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract a character profile from NotebookLM and add to knowledge graph.

    This queries the NotebookLM notebook for character information,
    uses LLM extraction to parse entities, and adds them to the
    project's knowledge graph with proper deduplication.

    Args:
        project_id: UUID of the project
        notebook_id: NotebookLM notebook ID or URL
        character_name: Name of the character to extract
        add_to_graph: Whether to add extracted entities to knowledge graph

    Returns:
        Character profile with entities and sources
    """
    # Verify project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Extract character profile from NotebookLM
    client = get_mcp_client()

    try:
        profile = await client.extract_character_profile(
            notebook_id=notebook_id,
            character_name=character_name
        )

        # Optionally add to knowledge graph
        if add_to_graph and profile["profile"]:
            # Get or create project graph
            project_graph = db.query(ProjectGraph).filter(
                ProjectGraph.project_id == project_id
            ).first()

            if not project_graph:
                project_graph = ProjectGraph(
                    project_id=project_id,
                    graph_data={}
                )
                db.add(project_graph)
                db.flush()

            # Load knowledge graph
            kg = KnowledgeGraphService(str(project_id))
            if project_graph.graph_data:
                kg.load_from_json(json.dumps(project_graph.graph_data))

            # Use LLM extractor to parse the profile into entities
            extractor = LLMExtractor(model="claude-sonnet-4.5")
            extraction = await extractor.extract_entities(
                content=profile["profile"],
                scene_id=f"notebooklm-{notebook_id}",
                project_id=str(project_id)
            )

            # Add entities to graph with deduplication
            entities_added = 0
            relationships_added = 0

            for entity_dict in extraction.get("entities", []):
                # Check if entity already exists (fuzzy match)
                existing = kg.find_entity_by_name(entity_dict["name"], fuzzy=True)

                if existing:
                    # Entity exists - ENRICH instead of duplicate
                    logger.info(f"Enriching existing entity: {entity_dict['name']}")

                    # Append NotebookLM research to description
                    enriched_description = existing.description + "\n\n[From NotebookLM]: " + entity_dict.get("description", "")

                    # Add NotebookLM sources to properties
                    if "notebooklm_sources" not in existing.properties:
                        existing.properties["notebooklm_sources"] = []

                    existing.properties["notebooklm_sources"].extend(profile["sources"])
                    existing.properties["notebooklm_notebook_id"] = notebook_id
                    existing.properties["enriched_from_notebooklm"] = True

                    kg.update_entity(
                        existing.id,
                        description=enriched_description
                    )

                else:
                    # New entity - create fresh
                    entity = Entity(
                        id=entity_dict.get("id", str(UUID(int=0))),  # Will generate new ID
                        name=entity_dict["name"],
                        entity_type=entity_dict.get("type", "character"),
                        description=entity_dict.get("description", ""),
                        attributes=entity_dict.get("attributes", {}),
                        source_scene_id=f"notebooklm:{notebook_id}"
                    )

                    # Mark as NotebookLM-sourced
                    entity.properties["source_type"] = "notebooklm"
                    entity.properties["notebooklm_notebook_id"] = notebook_id
                    entity.properties["notebooklm_sources"] = profile["sources"]

                    kg.add_entity(entity)
                    entities_added += 1

            # Add relationships
            for rel_dict in extraction.get("relationships", []):
                relationship = Relationship(
                    source_id=rel_dict["source"],
                    target_id=rel_dict["target"],
                    relationship_type=rel_dict.get("type", "related_to"),
                    properties=rel_dict.get("properties", {})
                )
                kg.add_relationship(relationship)
                relationships_added += 1

            # Save graph back to database
            project_graph.graph_data = json.loads(kg.to_json())
            db.commit()

            profile["entities_added"] = entities_added
            profile["entities_enriched"] = len(extraction.get("entities", [])) - entities_added
            profile["relationships_added"] = relationships_added

        return profile

    except Exception as e:
        logger.error(f"Error extracting character: {e}")
        raise HTTPException(500, f"Failed to extract character: {str(e)}")


@router.post("/projects/{project_id}/extract-world-building")
async def extract_world_building_from_notebook(
    project_id: UUID,
    notebook_id: str = Query(..., description="NotebookLM notebook ID or URL"),
    aspect: str = Query(..., description="World-building aspect to extract (e.g., 'AI in 2035')"),
    add_to_graph: bool = Query(True, description="Add extracted entities to knowledge graph"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Extract world-building details from NotebookLM and add to knowledge graph.

    Example:
        POST /api/notebooklm/projects/uuid-123/extract-world-building
        ?notebook_id=abc123
        &aspect=AI technology in 2035
        &add_to_graph=true
    """
    # Verify project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Extract world-building details from NotebookLM
    client = get_mcp_client()

    try:
        details = await client.extract_world_building(
            notebook_id=notebook_id,
            aspect=aspect
        )

        # Add to knowledge graph
        if add_to_graph and details["details"]:
            # Get or create project graph
            project_graph = db.query(ProjectGraph).filter(
                ProjectGraph.project_id == project_id
            ).first()

            if not project_graph:
                project_graph = ProjectGraph(
                    project_id=project_id,
                    graph_data={}
                )
                db.add(project_graph)
                db.flush()

            # Load knowledge graph
            kg = KnowledgeGraphService(str(project_id))
            if project_graph.graph_data:
                kg.load_from_json(json.dumps(project_graph.graph_data))

            # Use LLM extractor
            extractor = LLMExtractor(model="claude-sonnet-4.5")
            extraction = await extractor.extract_entities(
                content=details["details"],
                scene_id=f"notebooklm-{notebook_id}-{aspect}",
                project_id=str(project_id)
            )

            # Add entities with deduplication
            entities_added = 0

            for entity_dict in extraction.get("entities", []):
                existing = kg.find_entity_by_name(entity_dict["name"], fuzzy=True)

                if existing:
                    # Enrich existing entity
                    enriched_description = existing.description + "\n\n[World Building]: " + entity_dict.get("description", "")

                    if "notebooklm_sources" not in existing.properties:
                        existing.properties["notebooklm_sources"] = []

                    existing.properties["notebooklm_sources"].extend(details["sources"])
                    existing.properties["world_building_aspect"] = aspect

                    kg.update_entity(existing.id, description=enriched_description)

                else:
                    # Create new entity
                    entity = Entity(
                        id=entity_dict.get("id", str(UUID(int=0))),
                        name=entity_dict["name"],
                        entity_type=entity_dict.get("type", "concept"),
                        description=entity_dict.get("description", ""),
                        attributes=entity_dict.get("attributes", {}),
                        source_scene_id=f"notebooklm:{notebook_id}"
                    )

                    entity.properties["source_type"] = "notebooklm"
                    entity.properties["notebooklm_notebook_id"] = notebook_id
                    entity.properties["notebooklm_sources"] = details["sources"]
                    entity.properties["world_building_aspect"] = aspect

                    kg.add_entity(entity)
                    entities_added += 1

            # Save graph
            project_graph.graph_data = json.loads(kg.to_json())
            db.commit()

            details["entities_added"] = entities_added

        return details

    except Exception as e:
        logger.error(f"Error extracting world building: {e}")
        raise HTTPException(500, f"Failed to extract world building: {str(e)}")


@router.get("/projects/{project_id}/notebooks")
async def get_project_notebooks(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get NotebookLM notebooks configured for this project.

    Returns the notebook URLs and configuration status.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    return {
        "notebooks": project.notebooklm_notebooks or {},
        "config": project.notebooklm_config or {"enabled": False},
        "has_character_research": "character_research" in (project.notebooklm_notebooks or {}),
        "has_world_building": "world_building" in (project.notebooklm_notebooks or {}),
        "has_themes": "themes" in (project.notebooklm_notebooks or {})
    }


@router.post("/projects/{project_id}/configure")
async def configure_notebooklm_notebooks(
    project_id: UUID,
    character_research_url: Optional[str] = Query(None, description="URL to character research notebook"),
    world_building_url: Optional[str] = Query(None, description="URL to world building notebook"),
    themes_url: Optional[str] = Query(None, description="URL to themes/philosophy notebook"),
    auto_query_on_copilot: bool = Query(True, description="Enable NotebookLM context in copilot"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Configure NotebookLM notebooks for project.

    This can be called from wizard OR from project settings page.

    Args:
        project_id: UUID of the project
        character_research_url: URL to character research notebook
        world_building_url: URL to world building notebook
        themes_url: URL to themes/philosophy notebook
        auto_query_on_copilot: Enable automatic NotebookLM queries in copilot

    Returns:
        Configuration status
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Build notebooks dict
    notebooks = {}
    if character_research_url:
        notebooks["character_research"] = character_research_url
    if world_building_url:
        notebooks["world_building"] = world_building_url
    if themes_url:
        notebooks["themes"] = themes_url

    # Update project
    project.notebooklm_notebooks = notebooks
    project.notebooklm_config = {
        "enabled": bool(notebooks),
        "auto_query_on_copilot": auto_query_on_copilot,
        "configured_at": datetime.utcnow().isoformat()
    }

    db.commit()

    return {
        "success": True,
        "notebooks_configured": len(notebooks),
        "notebooklm_enabled": bool(notebooks),
        "auto_query_on_copilot": auto_query_on_copilot
    }
