"""
Real-time AI Copilot for Writing Assistance
Provides inline suggestions, auto-completion, and context-aware assistance
Similar to Cursor AI or GitHub Copilot, but for creative writing
"""

import logging
import json
from typing import Dict, List, Optional, Set
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.services.ai.ollama_setup import get_ollama_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copilot", tags=["copilot"])

# Active WebSocket connections: {project_id: {websocket}}
active_connections: Dict[str, Set[WebSocket]] = {}


# ============================================================================
# Context Management
# ============================================================================

class WritingContextManager:
    """Manages context for real-time writing suggestions"""

    def __init__(self, db: Session):
        self.db = db

    async def get_context(
        self,
        project_id: UUID,
        current_text: str,
        cursor_position: int,
        scene_id: Optional[UUID] = None
    ) -> Dict:
        """
        Gather comprehensive writing context for AI suggestions.

        Context includes:
        - Knowledge graph entities mentioned
        - Character voice/traits
        - Scene location and setting
        - Previous paragraph for continuity
        - POV character
        - NotebookLM research context (Phase 9)
        """
        context = {
            "previous_text": self._get_previous_context(current_text, cursor_position),
            "entities": await self._get_mentioned_entities(project_id, current_text),
            "project_info": await self._get_project_info(project_id),
            "tone": self._analyze_tone(current_text),
            "notebooklm_context": await self._get_notebooklm_context(project_id, current_text),  # NEW
        }

        return context

    def _get_previous_context(self, text: str, cursor_pos: int, words: int = 50) -> str:
        """Get previous N words before cursor for context"""
        text_before = text[:cursor_pos]
        words_list = text_before.split()
        previous = ' '.join(words_list[-words:]) if len(words_list) > words else text_before
        return previous

    async def _get_mentioned_entities(self, project_id: UUID, text: str) -> List[Dict]:
        """Find knowledge graph entities mentioned in text"""
        try:
            # Query knowledge graph for entities
            # This integrates with our Knowledge Graph system!
            from app.services.knowledge_graph.graph_service import KnowledgeGraphService

            graph_service = KnowledgeGraphService(str(project_id))

            # Check if graph exists
            from app.models.knowledge_graph import ProjectGraph
            project_graph = self.db.query(ProjectGraph).filter(
                ProjectGraph.project_id == project_id
            ).first()

            if not project_graph:
                return []

            # Load graph using classmethod from_json()
            kg = KnowledgeGraphService.from_json(project_graph.graph_data)

            # Find entities mentioned in text (query_entities() with no filters = all)
            all_entities = kg.query_entities()
            mentioned = []

            text_lower = text.lower()
            for entity in all_entities:
                if entity.name.lower() in text_lower:
                    mentioned.append({
                        "name": entity.name,
                        "type": entity.entity_type.value,  # Convert enum to string
                        "description": entity.description or "",
                        "attributes": entity.attributes
                    })

            return mentioned[:10]  # Limit to top 10 for context

        except Exception as e:
            logger.error(f"Error getting entities: {e}")
            return []

    async def _get_project_info(self, project_id: UUID) -> Dict:
        """Get project metadata for context"""
        try:
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if project:
                return {
                    "title": project.title,
                    "genre": project.genre,
                    "description": project.description or ""
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting project info: {e}")
            return {}

    def _analyze_tone(self, text: str) -> str:
        """Quick tone analysis of current text"""
        text_lower = text.lower()

        # Simple keyword-based tone detection
        if any(word in text_lower for word in ["screamed", "shouted", "yelled", "furious"]):
            return "intense/angry"
        elif any(word in text_lower for word in ["whispered", "murmured", "softly"]):
            return "quiet/intimate"
        elif any(word in text_lower for word in ["laughed", "grinned", "smiled"]):
            return "lighthearted/joyful"
        elif any(word in text_lower for word in ["dark", "shadow", "ominous", "fear"]):
            return "dark/suspenseful"
        else:
            return "neutral"

    async def _get_notebooklm_context(self, project_id: UUID, text: str) -> Dict:
        """
        Query NotebookLM notebooks for relevant research based on current text.

        Phase 9: NotebookLM MCP Integration
        This enhances copilot suggestions with research-grounded context.

        Example: If writing about "AI in 2035", query world-building notebook
        """
        try:
            # Get project's NotebookLM configuration
            project = self.db.query(Project).filter(Project.id == project_id).first()

            if not project or not project.notebooklm_notebooks:
                return {}

            # Check if NotebookLM auto-query is enabled
            config = project.notebooklm_config or {}
            if not config.get("auto_query_on_copilot", True):
                return {}

            # Get mentioned entities to determine what to query
            mentioned_entities = await self._get_mentioned_entities(project_id, text)

            if not mentioned_entities:
                return {}

            # Query NotebookLM based on entity types
            from app.services.notebooklm import get_mcp_client
            client = get_mcp_client()

            # Check if MCP server is available
            if not await client.is_available():
                return {}

            notebooklm_context = {}

            # If character mentioned, query character research notebook
            characters = [e for e in mentioned_entities if e["type"] == "character"]
            if characters and "character_research" in project.notebooklm_notebooks:
                try:
                    # Query for first mentioned character
                    entity_name = characters[0]["name"]
                    response = await client.query_for_context(
                        notebook_id=project.notebooklm_notebooks["character_research"],
                        entity_name=entity_name,
                        entity_type="character"
                    )

                    if response:
                        notebooklm_context["character_research"] = {
                            "entity": entity_name,
                            "context": response[:300]  # Limit length for copilot
                        }
                except Exception as e:
                    logger.error(f"Error querying character research: {e}")

            # If location/technology mentioned, query world-building notebook
            locations = [e for e in mentioned_entities if e["type"] in ["location", "object", "concept"]]
            if locations and "world_building" in project.notebooklm_notebooks:
                try:
                    entity_name = locations[0]["name"]
                    response = await client.query_for_context(
                        notebook_id=project.notebooklm_notebooks["world_building"],
                        entity_name=entity_name,
                        entity_type=locations[0]["type"]
                    )

                    if response:
                        notebooklm_context["world_building"] = {
                            "entity": entity_name,
                            "context": response[:300]
                        }
                except Exception as e:
                    logger.error(f"Error querying world building: {e}")

            return notebooklm_context

        except Exception as e:
            logger.error(f"Error getting NotebookLM context: {e}")
            return {}


# ============================================================================
# Suggestion Engine
# ============================================================================

class SuggestionEngine:
    """Generates inline suggestions using Ollama (FREE local AI)"""

    def __init__(self):
        self.ollama = get_ollama_client()

    async def generate_suggestion(
        self,
        text_before_cursor: str,
        context: Dict,
        suggestion_type: str = "continuation"
    ) -> Optional[str]:
        """
        Generate writing suggestion using FREE Ollama AI.

        Types:
        - continuation: Continue the current sentence/paragraph
        - completion: Complete the current word/phrase
        - enhancement: Suggest better phrasing
        """

        # Check if Ollama is available
        if not await self.ollama.is_available():
            logger.warning("Ollama not available for suggestions")
            return None

        # Build prompt with context
        prompt = self._build_suggestion_prompt(text_before_cursor, context, suggestion_type)

        try:
            # Generate using FREE Ollama
            suggestion = await self.ollama.generate(
                prompt=text_before_cursor,
                system=prompt,
                temperature=0.7,
                max_tokens=100  # Keep suggestions concise
            )

            # Clean up suggestion
            if suggestion:
                suggestion = suggestion.strip()
                # Ensure it's a continuation, not a repeat
                if suggestion and not text_before_cursor.endswith(suggestion[:20]):
                    return suggestion

            return None

        except Exception as e:
            logger.error(f"Error generating suggestion: {e}")
            return None

    def _build_suggestion_prompt(self, text: str, context: Dict, suggestion_type: str) -> str:
        """Build context-aware prompt for suggestion generation (Phase 9: includes NotebookLM research)"""

        entities_text = ""
        if context.get("entities"):
            entities_text = "\n\nCharacters/entities mentioned:\n"
            for entity in context["entities"][:5]:
                entities_text += f"- {entity['name']} ({entity['type']}): {entity.get('description', '')}\n"

        # NEW: Add NotebookLM research context
        notebooklm_text = ""
        if context.get("notebooklm_context"):
            notebooklm_text = "\n\nResearch context from notebooks:\n"
            for key, value in context["notebooklm_context"].items():
                entity_name = value.get("entity", "")
                research_context = value.get("context", "")
                notebooklm_text += f"- {key.replace('_', ' ').title()} ({entity_name}): {research_context}\n"

        project_info = context.get("project_info", {})
        genre = project_info.get("genre", "fiction")

        tone = context.get("tone", "neutral")

        prompt = f"""You are an expert creative writing assistant for {genre} stories.

Project: {project_info.get('title', 'Untitled')}
Current tone: {tone}
{entities_text}
{notebooklm_text}

Task: Continue the text naturally, matching the established voice and style.

Guidelines:
1. Match the existing tone and pacing
2. Stay consistent with character voices
3. Use research context to ground suggestions in reality
4. Keep suggestions concise (1-2 sentences max)
5. Be creative but maintain story continuity
6. Don't repeat what's already written

Continue the text smoothly from where it left off:"""

        return prompt


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@router.websocket("/{project_id}/stream")
async def copilot_stream(
    websocket: WebSocket,
    project_id: str,
):
    """
    WebSocket endpoint for real-time writing copilot.

    Receives:
    - text: Current editor content
    - cursor: Cursor position
    - event: 'typing' | 'pause' | 'request'

    Sends:
    - type: 'suggestion'
    - text: Suggested completion
    - confidence: 0.0-1.0

    Example client:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/copilot/{project_id}/stream');

    ws.send(JSON.stringify({
        text: "Mickey walked into the",
        cursor: 23,
        event: "pause"
    }));

    ws.onmessage = (event) => {
        const suggestion = JSON.parse(event.data);
        // Show inline suggestion
    };
    ```
    """
    await websocket.accept()

    # Add to active connections
    if project_id not in active_connections:
        active_connections[project_id] = set()
    active_connections[project_id].add(websocket)

    logger.info(f"Copilot connected for project {project_id}")

    # Get database session (simplified - in production, use dependency injection)
    from app.core.database import SessionLocal
    db = SessionLocal()

    try:
        context_manager = WritingContextManager(db)
        suggestion_engine = SuggestionEngine()

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            event_type = data.get("event", "typing")
            text = data.get("text", "")
            cursor_pos = data.get("cursor", len(text))
            scene_id = data.get("scene_id")

            # Only generate suggestions on 'pause' or 'request' events
            # Don't spam suggestions on every keystroke
            if event_type in ["pause", "request"]:
                try:
                    # Get writing context
                    context = await context_manager.get_context(
                        project_id=UUID(project_id),
                        current_text=text,
                        cursor_position=cursor_pos,
                        scene_id=UUID(scene_id) if scene_id else None
                    )

                    # Get text before cursor
                    text_before_cursor = text[:cursor_pos]

                    # Generate suggestion
                    suggestion = await suggestion_engine.generate_suggestion(
                        text_before_cursor=text_before_cursor,
                        context=context,
                        suggestion_type="continuation"
                    )

                    # Send suggestion back
                    if suggestion:
                        await websocket.send_json({
                            "type": "suggestion",
                            "text": suggestion,
                            "confidence": 0.85,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        # No suggestion available
                        await websocket.send_json({
                            "type": "no_suggestion",
                            "reason": "Unable to generate suggestion",
                            "timestamp": datetime.utcnow().isoformat()
                        })

                except Exception as e:
                    logger.error(f"Error processing suggestion request: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })

    except WebSocketDisconnect:
        logger.info(f"Copilot disconnected for project {project_id}")
        active_connections[project_id].discard(websocket)
        if not active_connections[project_id]:
            del active_connections[project_id]

    except Exception as e:
        logger.error(f"Copilot error: {e}", exc_info=True)
        active_connections[project_id].discard(websocket)

    finally:
        # Always close database session to prevent connection leaks
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database session: {e}")


@router.get("/{project_id}/status")
async def copilot_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get copilot status for a project.
    Returns whether Ollama is available and ready.
    """
    ollama = get_ollama_client()

    is_available = await ollama.is_available()
    models = await ollama.list_models() if is_available else []

    return {
        "project_id": project_id,
        "copilot_enabled": is_available,
        "ollama_available": is_available,
        "available_models": models,
        "active_connections": len(active_connections.get(project_id, set())),
        "free": True,  # Ollama is always free!
        "cost_per_suggestion": 0.0
    }
