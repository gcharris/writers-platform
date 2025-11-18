"""Smart knowledge routing system.

Routes queries to appropriate knowledge systems:
- Database Full-Text Search (local reference files) - Always available
- NotebookLM (external analysis) - Opt-in, configured in preferences

Knowledge is queried from the project's reference files using PostgreSQL
full-text search for fast, accurate retrieval.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of knowledge queries."""
    FACTUAL = "factual"  # Specific facts (use Cognee)
    CONCEPTUAL = "conceptual"  # Concepts and relationships (use Cognee)
    ANALYTICAL = "analytical"  # Complex analysis (use NotebookLM if available)
    GENERAL = "general"  # General queries (use Cognee)


class KnowledgeSource(Enum):
    """Available knowledge sources (internal only - not user-facing)."""
    DATABASE = "database"  # PostgreSQL full-text search on reference files
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
    - Database (local) for most queries via PostgreSQL full-text search
    - NotebookLM (external) for analytical queries if configured

    Users never see implementation details - they just ask questions.
    """

    def __init__(
        self,
        db: Session,
        project_id: UUID,
        notebooklm_enabled: bool = False,
        notebooklm_notebook_id: Optional[str] = None,
        enable_caching: bool = True
    ):
        """Initialize knowledge router.

        Args:
            db: Database session for querying reference files
            project_id: Project UUID to query reference files for
            notebooklm_enabled: Whether NotebookLM is configured
            notebooklm_notebook_id: NotebookLM notebook ID if enabled
            enable_caching: Enable query result caching
        """
        self.db = db
        self.project_id = project_id
        self.notebooklm_enabled = notebooklm_enabled
        self.notebooklm_notebook_id = notebooklm_notebook_id
        self.enable_caching = enable_caching

        # Query cache (simple in-memory for now)
        self._cache: Dict[str, QueryResult] = {}

        logger.info(f"Initialized knowledge router for project {project_id} (NotebookLM: {notebooklm_enabled})")

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

        # All other queries go to local database (PostgreSQL full-text search)
        logger.debug(f"Routing {query_type.value} query to database: {query[:50]}")
        return KnowledgeSource.DATABASE

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
        # Check cache first
        cache_key = f"{query}:{max_results}"
        if self.enable_caching and cache_key in self._cache:
            logger.debug(f"Returning cached result for: {query[:50]}")
            return self._cache[cache_key]

        # Determine source
        if force_source:
            source = KnowledgeSource(force_source)
        else:
            source = self.route_query(query)

        logger.info(f"Routing query to {source.value}: {query[:50]}...")

        # Execute query
        try:
            result = await self._execute_query(source, query, max_results)

            # Cache result
            if self.enable_caching:
                self._cache[cache_key] = result

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
        if source == KnowledgeSource.DATABASE:
            return await self._query_database(query, max_results)
        elif source == KnowledgeSource.NOTEBOOKLM:
            return await self._query_notebooklm(query, max_results)
        else:
            raise ValueError(f"Unknown knowledge source: {source}")

    async def _query_database(self, query: str, max_results: int) -> QueryResult:
        """Query reference files using PostgreSQL full-text search.

        Uses the GIN index on reference_files.content for fast full-text search.

        Args:
            query: Query text
            max_results: Maximum results to return

        Returns:
            QueryResult from database search
        """
        from app.models.manuscript import ReferenceFile

        logger.debug(f"Querying database for project {self.project_id}: {query[:50]}")

        try:
            # PostgreSQL full-text search using ts_vector
            # The migration created: CREATE INDEX idx_reference_files_search ON reference_files
            #     USING GIN (to_tsvector('english', content));

            # Build search query - convert query to tsquery format
            search_query = func.to_tsquery('english', func.plainto_tsquery('english', query))

            # Query reference files with full-text search ranked by relevance
            results = (
                self.db.query(ReferenceFile)
                .filter(ReferenceFile.project_id == self.project_id)
                .filter(func.to_tsvector('english', ReferenceFile.content).op('@@')(search_query))
                .order_by(
                    func.ts_rank(
                        func.to_tsvector('english', ReferenceFile.content),
                        search_query
                    ).desc()
                )
                .limit(max_results)
                .all()
            )

            if not results:
                # No results found - return empty result
                logger.info(f"No knowledge base results found for query: {query[:50]}")
                return QueryResult(
                    source=KnowledgeSource.DATABASE,
                    answer="No relevant information found in the knowledge base for this query.",
                    confidence=0.0,
                    references=[],
                    metadata={
                        "source": "database",
                        "query": query,
                        "results_count": 0
                    }
                )

            # Build answer from results
            answer_parts = []
            references = []

            for ref_file in results:
                # Add reference
                ref_path = f"{ref_file.category}/{ref_file.subcategory}/{ref_file.filename}".strip('/')
                references.append(ref_path)

                # Extract relevant snippet (first 200 chars of content)
                snippet = ref_file.content[:200] + "..." if len(ref_file.content) > 200 else ref_file.content
                answer_parts.append(f"**{ref_file.filename}**: {snippet}")

            # Combine into answer
            answer = "Based on your knowledge base:\n\n" + "\n\n".join(answer_parts)

            # Calculate confidence based on number of results
            confidence = min(0.95, 0.5 + (len(results) * 0.1))

            logger.info(f"Found {len(results)} knowledge base results for query")

            return QueryResult(
                source=KnowledgeSource.DATABASE,
                answer=answer,
                confidence=confidence,
                references=references,
                metadata={
                    "source": "database",
                    "query": query,
                    "results_count": len(results),
                    "search_type": "postgresql_fulltext"
                }
            )

        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

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
        # If NotebookLM failed, try database
        if failed_source == KnowledgeSource.NOTEBOOKLM:
            try:
                logger.info("NotebookLM failed, falling back to database")
                result = await self._query_database(query, max_results)
                return result
            except Exception as e:
                logger.error(f"Database fallback also failed: {e}")
                raise Exception(f"All knowledge sources failed for query: {query}")

        # If database failed and NotebookLM is enabled, try it
        if failed_source == KnowledgeSource.DATABASE and self.notebooklm_enabled:
            try:
                logger.info("Database failed, falling back to NotebookLM")
                result = await self._query_notebooklm(query, max_results)
                return result
            except Exception as e:
                logger.error(f"NotebookLM fallback also failed: {e}")
                raise Exception(f"All knowledge sources failed for query: {query}")

        # No fallback available
        raise Exception(f"Knowledge source {failed_source.value} failed and no fallback available")
