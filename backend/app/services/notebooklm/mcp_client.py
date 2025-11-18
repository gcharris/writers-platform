"""
NotebookLM MCP Client

Singleton service for communicating with NotebookLM via MCP (Model Context Protocol).
Provides methods to query notebooks and extract research-grounded entities.

Note: Requires NotebookLM MCP server to be running locally or accessible.
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel
from uuid import uuid4

logger = logging.getLogger(__name__)


class NotebookInfo(BaseModel):
    """Metadata about a NotebookLM notebook."""
    id: str
    title: str
    description: Optional[str] = None
    source_count: int = 0
    created_at: str
    updated_at: str


class NotebookQuery(BaseModel):
    """Query to send to NotebookLM."""
    notebook_id: str
    query: str
    max_sources: int = 5
    include_citations: bool = True


class NotebookResponse(BaseModel):
    """Response from NotebookLM."""
    answer: str
    sources: List[Dict[str, str]]  # [{"title": "...", "excerpt": "..."}]
    notebook_id: str
    query: str


class NotebookLMMCPClient:
    """
    Singleton MCP client for NotebookLM queries.

    This client manages a persistent connection to the NotebookLM MCP server
    and provides high-level methods for querying notebooks and extracting entities.
    """

    _instance = None
    _process = None
    _initialized = False

    def __new__(cls):
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize MCP client configuration (only once)."""
        if not self._initialized:
            self.config_path = "backend/mcp_config.json"
            self.server_config = None
            self._load_config()
            NotebookLMMCPClient._initialized = True

    def _load_config(self):
        """Load MCP server configuration from file."""
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            self.server_config = config.get("mcpServers", {}).get("notebooklm", {})

            if not self.server_config:
                logger.warning("NotebookLM MCP server not configured in mcp_config.json")
                self.server_config = {
                    "command": "node",
                    "args": ["external/notebooklm-mcp/index.js"],
                    "env": {}
                }

        except FileNotFoundError:
            logger.warning(f"MCP config file not found: {self.config_path}")
            # Use default config
            self.server_config = {
                "command": "node",
                "args": ["external/notebooklm-mcp/index.js"],
                "env": {}
            }
        except Exception as e:
            logger.error(f"Error loading MCP config: {e}")
            self.server_config = {}

    async def ensure_started(self):
        """
        Ensure MCP server is running (start if not).

        This is called automatically before each query to ensure the server
        is available. The server persists between requests for efficiency.
        """
        if self._process and self._process.returncode is None:
            return  # Already running

        if not self.server_config:
            raise RuntimeError("NotebookLM MCP server not configured")

        try:
            # Start MCP server subprocess
            self._process = await asyncio.create_subprocess_exec(
                self.server_config["command"],
                *self.server_config["args"],
                env=self.server_config.get("env", {}),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for server to be ready
            await asyncio.sleep(2)

            logger.info("NotebookLM MCP server started successfully")

        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise RuntimeError(f"Could not start NotebookLM MCP server: {e}")

    async def stop_server(self):
        """Stop the MCP server process."""
        if self._process:
            self._process.terminate()
            await self._process.wait()
            self._process = None
            logger.info("NotebookLM MCP server stopped")

    async def is_available(self) -> bool:
        """Check if NotebookLM MCP server is available."""
        try:
            await self.ensure_started()
            return True
        except Exception as e:
            logger.error(f"NotebookLM MCP server not available: {e}")
            return False

    async def list_notebooks(self) -> List[NotebookInfo]:
        """
        List all available NotebookLM notebooks.

        Returns:
            List of notebook metadata

        Raises:
            RuntimeError: If MCP server is not available
        """
        await self.ensure_started()

        try:
            # Send MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "notebooks/list",
                "params": {}
            }

            self._process.stdin.write(json.dumps(request).encode() + b"\n")
            await self._process.stdin.drain()

            # Read response
            response_line = await self._process.stdout.readline()
            response = json.loads(response_line.decode())

            if "error" in response:
                raise RuntimeError(f"MCP error: {response['error']}")

            notebooks = response.get("result", {}).get("notebooks", [])
            return [NotebookInfo(**nb) for nb in notebooks]

        except Exception as e:
            logger.error(f"Error listing notebooks: {e}")
            return []

    async def query_notebook(
        self,
        notebook_id: str,
        query: str,
        max_sources: int = 5
    ) -> NotebookResponse:
        """
        Query a NotebookLM notebook with a question.

        Args:
            notebook_id: ID or URL of the notebook to query
            query: Question to ask (e.g., "How would Mo Gawdat describe AI in 2035?")
            max_sources: Maximum number of sources to return

        Returns:
            Answer with citations from notebook sources

        Example:
            response = await client.query_notebook(
                notebook_id="abc123",
                query="What are the key themes in this research?",
                max_sources=5
            )
            print(response.answer)
            for source in response.sources:
                print(f"- {source['title']}: {source['excerpt']}")
        """
        await self.ensure_started()

        try:
            # Send MCP query request
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "notebook/query",
                "params": {
                    "notebook_id": notebook_id,
                    "query": query,
                    "max_sources": max_sources,
                    "include_citations": True
                }
            }

            self._process.stdin.write(json.dumps(request).encode() + b"\n")
            await self._process.stdin.drain()

            # Read response
            response_line = await self._process.stdout.readline()
            response = json.loads(response_line.decode())

            if "error" in response:
                raise RuntimeError(f"MCP query error: {response['error']}")

            result = response.get("result", {})

            return NotebookResponse(
                answer=result.get("answer", ""),
                sources=result.get("sources", []),
                notebook_id=notebook_id,
                query=query
            )

        except Exception as e:
            logger.error(f"Error querying notebook {notebook_id}: {e}")
            # Return empty response on error
            return NotebookResponse(
                answer="",
                sources=[],
                notebook_id=notebook_id,
                query=query
            )

    async def extract_character_profile(
        self,
        notebook_id: str,
        character_name: str
    ) -> Dict:
        """
        Extract a character profile from NotebookLM research.

        This method queries the notebook for character-specific information
        and structures it for knowledge graph extraction.

        Args:
            notebook_id: ID of the notebook with character research
            character_name: Name of the character to extract

        Returns:
            Character profile with backstory, voice, arc, etc.

        Example:
            profile = await client.extract_character_profile(
                notebook_id="character-research-123",
                character_name="Mo Gawdat"
            )
            # profile = {
            #     "character_name": "Mo Gawdat",
            #     "profile": "...",
            #     "sources": [...]
            # }
        """
        query = f"""
        If {character_name} were a character in a novel, based on the
        research in this notebook, provide:

        1. **Backstory**: Their background and formative experiences
        2. **Voice**: Their speaking style, vocabulary, and mannerisms
        3. **Core Beliefs**: Their philosophical views and values
        4. **Character Arc**: Potential journey and transformation
        5. **Conflicts**: Internal and external struggles they might face
        6. **Relationships**: How they might relate to other characters

        Use specific examples from the notebook sources.
        Keep response concise but detailed (under 500 words).
        """

        response = await self.query_notebook(
            notebook_id=notebook_id,
            query=query,
            max_sources=10
        )

        return {
            "character_name": character_name,
            "profile": response.answer,
            "sources": response.sources,
            "notebook_id": notebook_id
        }

    async def extract_world_building(
        self,
        notebook_id: str,
        aspect: str
    ) -> Dict:
        """
        Extract world-building details from NotebookLM research.

        Args:
            notebook_id: ID of the notebook with world research
            aspect: Aspect to extract (e.g., "technology in 2035", "social dynamics")

        Returns:
            World-building details with citations

        Example:
            details = await client.extract_world_building(
                notebook_id="world-building-123",
                aspect="AI technology in 2035"
            )
        """
        query = f"""
        Based on the research in this notebook, describe {aspect} for a
        fictional world. Include:

        1. **Key Characteristics**: Defining features and trends
        2. **Concrete Examples**: Specific scenarios and manifestations
        3. **Implications**: How this affects characters and plot
        4. **Conflicts**: Tensions and dilemmas arising from this aspect

        Ground your response in the notebook sources.
        Keep response concise but detailed (under 500 words).
        """

        response = await self.query_notebook(
            notebook_id=notebook_id,
            query=query,
            max_sources=8
        )

        return {
            "aspect": aspect,
            "details": response.answer,
            "sources": response.sources,
            "notebook_id": notebook_id
        }

    async def query_for_context(
        self,
        notebook_id: str,
        entity_name: str,
        entity_type: str
    ) -> str:
        """
        Query notebook for context about a specific entity.

        This is used by the copilot to get research context when
        an entity is mentioned in the current text.

        Args:
            notebook_id: Notebook to query
            entity_name: Name of entity (character, location, etc.)
            entity_type: Type of entity (character, location, object, etc.)

        Returns:
            Brief context about the entity (1-2 paragraphs)
        """
        if entity_type == "character":
            query = f"What are the key traits and characteristics of {entity_name}?"
        elif entity_type == "location":
            query = f"Describe the key features and atmosphere of {entity_name}"
        elif entity_type == "object":
            query = f"What is {entity_name} and how does it work?"
        else:
            query = f"What is important to know about {entity_name}?"

        response = await self.query_notebook(
            notebook_id=notebook_id,
            query=query,
            max_sources=3
        )

        return response.answer


# Global singleton instance
_mcp_client: Optional[NotebookLMMCPClient] = None


def get_mcp_client() -> NotebookLMMCPClient:
    """
    Get or create singleton MCP client.

    Returns:
        NotebookLMMCPClient instance (singleton)

    Example:
        from app.services.notebooklm import get_mcp_client

        client = get_mcp_client()
        response = await client.query_notebook(...)
    """
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = NotebookLMMCPClient()
    return _mcp_client
