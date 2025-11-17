"""Smart knowledge routing system.

Routes queries to appropriate knowledge systems:
- Cognee (local semantic graph) - Always available, uses Gemini internally
- NotebookLM (external analysis) - Opt-in, configured in preferences

IMPORTANT: Gemini File Search is an implementation detail of Cognee,
not a user-facing option. Users just "ask questions" and the system
routes intelligently.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of knowledge queries."""
    FACTUAL = "factual"  # Specific facts (use Cognee)
    CONCEPTUAL = "conceptual"  # Concepts and relationships (use Cognee)
    ANALYTICAL = "analytical"  # Complex analysis (use NotebookLM if available)
    GENERAL = "general"  # General queries (use Cognee)


class KnowledgeSource(Enum):
    """Available knowledge sources (internal only - not user-facing)."""
    COGNEE = "cognee"  # Local semantic graph (uses Gemini internally)
    NOTEBOOKLM = "notebooklm"  # External analysis (opt-in)


@dataclass
class QueryResult:
    """Result from a knowledge query."""
    source: KnowledgeSource
    answer: str
    confidence: float
    references: List[str]
    metadata: Dict[str, Any]


class KnowledgeRouter:
    """Routes knowledge queries to appropriate system.

    Automatically routes queries to:
    - Cognee (local) for most queries
    - NotebookLM (external) for analytical queries if configured

    Users never see "Cognee" or "Gemini" - they just ask questions.
    """

    def __init__(
        self,
        project_path: Optional[Path] = None,
        notebooklm_enabled: bool = False,
        notebooklm_notebook_id: Optional[str] = None,
        enable_caching: bool = True
    ):
        """Initialize knowledge router.

        Args:
            project_path: Path to project (for reading preferences)
            notebooklm_enabled: Whether NotebookLM is configured
            notebooklm_notebook_id: NotebookLM notebook ID if enabled
            enable_caching: Enable query result caching
        """
        self.project_path = project_path
        self.notebooklm_enabled = notebooklm_enabled
        self.notebooklm_notebook_id = notebooklm_notebook_id
        self.enable_caching = enable_caching

        # Initialize systems (mock for now - real integrations in future)
        self._systems = {}
        logger.info(f"Initialized knowledge router (NotebookLM: {notebooklm_enabled})")

    def classify_query(self, query: str) -> QueryType:
        """Classify query type.

        Args:
            query: Query text

        Returns:
            QueryType classification
        """
        query_lower = query.lower()

        # Analytical queries (check first - most specific)
        if any(word in query_lower for word in ["why ", "analyze", "compare", "explain why"]):
            return QueryType.ANALYTICAL

        # Factual queries
        if any(word in query_lower for word in ["what is", "who is", "when", "where"]):
            return QueryType.FACTUAL

        # Conceptual queries
        if any(word in query_lower for word in ["relationship", "connect", "related"]):
            return QueryType.CONCEPTUAL

        return QueryType.GENERAL

    def route_query(self, query: str) -> KnowledgeSource:
        """Determine which knowledge source to use.

        Args:
            query: Query text

        Returns:
            Recommended knowledge source
        """
        query_type = self.classify_query(query)

        # Analytical queries go to NotebookLM if enabled
        if query_type == QueryType.ANALYTICAL and self.notebooklm_enabled:
            logger.debug(f"Routing analytical query to NotebookLM: {query[:50]}")
            return KnowledgeSource.NOTEBOOKLM

        # All other queries go to Cognee (local semantic graph)
        # Note: Cognee may use Gemini File Search internally, but that's
        # an implementation detail hidden from users
        logger.debug(f"Routing {query_type.value} query to Cognee: {query[:50]}")
        return KnowledgeSource.COGNEE

    async def query(
        self,
        query: str,
        max_results: int = 5,
        force_source: Optional[str] = None
    ) -> QueryResult:
        """Execute a knowledge query.

        Args:
            query: Query text
            max_results: Maximum results to return
            force_source: Force specific source (bypass routing)

        Returns:
            QueryResult with answer and metadata
        """
        # Determine source
        if force_source:
            source = KnowledgeSource(force_source)
        else:
            source = self.route_query(query)

        logger.info(f"Routing query to {source.value}: {query[:50]}...")

        # Execute query (mock implementation)
        try:
            result = await self._execute_query(source, query, max_results)
            return result
        except Exception as e:
            logger.error(f"Query failed on {source.value}: {e}")
            # Try fallback chain
            return await self._fallback_query(query, max_results, source)

    async def _execute_query(
        self,
        source: KnowledgeSource,
        query: str,
        max_results: int
    ) -> QueryResult:
        """Execute query on specific source.

        Args:
            source: Knowledge source to query
            query: Query text
            max_results: Maximum results

        Returns:
            QueryResult
        """
        if source == KnowledgeSource.COGNEE:
            return await self._query_cognee(query, max_results)
        elif source == KnowledgeSource.NOTEBOOKLM:
            return await self._query_notebooklm(query, max_results)
        else:
            raise ValueError(f"Unknown knowledge source: {source}")

    async def _query_cognee(self, query: str, max_results: int) -> QueryResult:
        """Query Cognee (local semantic graph).

        TODO: Replace with real Cognee integration
        - Use existing Cognee installation (17MB)
        - Query semantic graph
        - Return results with references

        Args:
            query: Query text
            max_results: Maximum results to return

        Returns:
            QueryResult from Cognee
        """
        # Mock implementation - replace with real Cognee integration
        logger.debug(f"Querying Cognee: {query[:50]}")

        # Simulate semantic search
        answer = f"Based on your story knowledge base, {query.lower()} "
        answer += "is related to the main character's development arc and the "
        answer += "central themes of identity and belonging."

        return QueryResult(
            source=KnowledgeSource.COGNEE,
            answer=answer,
            confidence=0.85,
            references=[
                "story_bible.md",
                "character_profiles/protagonist.md",
                "themes/identity.md"
            ],
            metadata={
                "source": "cognee",
                "query": query,
                "search_type": "semantic_graph"
            }
        )

    async def _query_notebooklm(self, query: str, max_results: int) -> QueryResult:
        """Query NotebookLM (external analysis).

        TODO: Replace with real NotebookLM integration
        - Use notebook ID from preferences
        - Query via NotebookLM API
        - Return results with audio summary option

        Args:
            query: Query text
            max_results: Maximum results to return

        Returns:
            QueryResult from NotebookLM
        """
        if not self.notebooklm_enabled:
            raise Exception("NotebookLM is not enabled. Configure in preferences.")

        # Mock implementation - replace with real NotebookLM integration
        logger.debug(f"Querying NotebookLM: {query[:50]}")

        answer = f"After analyzing your story materials for '{query}', "
        answer += "I've identified several key patterns and connections. "
        answer += "The thematic elements align with your character motivations, "
        answer += "and there are opportunities to strengthen the narrative arc."

        return QueryResult(
            source=KnowledgeSource.NOTEBOOKLM,
            answer=answer,
            confidence=0.90,
            references=[
                "notebooklm_analysis_summary.md",
                "Audio summary available (2:30)"
            ],
            metadata={
                "source": "notebooklm",
                "query": query,
                "notebook_id": self.notebooklm_notebook_id,
                "has_audio": True
            }
        )

    async def _fallback_query(
        self,
        query: str,
        max_results: int,
        failed_source: KnowledgeSource
    ) -> QueryResult:
        """Try fallback sources if primary fails.

        Args:
            query: Query text
            max_results: Maximum results
            failed_source: Source that failed

        Returns:
            QueryResult from fallback source
        """
        # If NotebookLM failed, try Cognee
        if failed_source == KnowledgeSource.NOTEBOOKLM:
            try:
                logger.info("NotebookLM failed, falling back to Cognee")
                result = await self._query_cognee(query, max_results)
                return result
            except Exception as e:
                logger.error(f"Cognee fallback also failed: {e}")
                raise Exception(f"All knowledge sources failed for query: {query}")

        # If Cognee failed and NotebookLM is enabled, try it
        if failed_source == KnowledgeSource.COGNEE and self.notebooklm_enabled:
            try:
                logger.info("Cognee failed, falling back to NotebookLM")
                result = await self._query_notebooklm(query, max_results)
                return result
            except Exception as e:
                logger.error(f"NotebookLM fallback also failed: {e}")
                raise Exception(f"All knowledge sources failed for query: {query}")

        # No fallback available
        raise Exception(f"Knowledge source {failed_source.value} failed and no fallback available")
