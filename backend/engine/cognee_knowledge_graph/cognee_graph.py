"""
Main Cognee Knowledge Graph interface for The Explants.

This module provides the primary interface for querying the knowledge graph,
building context for AI agents, and extracting semantic relationships across
the trilogy corpus.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import json

# Cognee imports (will be installed via pip install cognee)
try:
    import cognee
    from cognee.modules.search.types import SearchType
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    SearchType = None

from factory.core.cognee_knowledge_graph.config import CogneeConfig


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result from a knowledge graph query."""
    answer: str
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    source_documents: List[str]
    confidence: float
    query: str
    search_type: str


@dataclass
class EntityInfo:
    """Information about an entity in the knowledge graph."""
    name: str
    type: str  # character, location, concept, event, etc.
    attributes: Dict[str, Any]
    related_entities: List[str]
    documents: List[str]


@dataclass
class RelationshipInfo:
    """Information about a relationship between entities."""
    source: str
    target: str
    relationship_type: str
    attributes: Dict[str, Any]
    documents: List[str]


class CogneeKnowledgeGraph:
    """
    Main interface for The Explants knowledge graph using Cognee.

    This class provides high-level methods for:
    - Querying the knowledge graph with natural language
    - Extracting entity and relationship information
    - Building rich context for AI agents
    - Traversing the graph for connected concepts

    Example:
        >>> kg = CogneeKnowledgeGraph()
        >>> await kg.initialize()
        >>> result = await kg.query("Show Mickey's addiction arc in Volume 1")
        >>> print(result.answer)
    """

    def __init__(self, config: Optional[CogneeConfig] = None):
        """
        Initialize the knowledge graph interface.

        Args:
            config: CogneeConfig instance (creates default if not provided)
        """
        if not COGNEE_AVAILABLE:
            raise ImportError(
                "Cognee is not installed. Install with: pip install cognee\n"
                "For specific database support, use: pip install cognee[neo4j,postgres]"
            )

        self.config = config or CogneeConfig()
        self.initialized = False

        # Validate configuration
        is_valid, errors = self.config.validate()
        if not is_valid:
            logger.warning("Configuration validation errors:")
            for error in errors:
                logger.warning(f"  - {error}")

    async def initialize(self):
        """
        Initialize Cognee with configuration.

        Sets up environment variables and prepares the system for queries.
        Must be called before using the knowledge graph.
        """
        if self.initialized:
            logger.info("Knowledge graph already initialized")
            return

        # Set environment variables for Cognee
        env_vars = self.config.get_env_variables()
        import os
        for key, value in env_vars.items():
            os.environ[key] = value

        # Reset Cognee to pick up new configuration
        try:
            await cognee.prune.prune_data()
            await cognee.prune.prune_system()
            logger.info("Cognee system reset complete")
        except Exception as e:
            logger.warning(f"Could not reset Cognee (might be first run): {e}")

        self.initialized = True
        logger.info(f"Cognee Knowledge Graph initialized: {self.config}")

    async def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a single document to the knowledge graph.

        Args:
            content: Document text content
            metadata: Optional metadata (file path, volume, chapter, etc.)
        """
        if not self.initialized:
            await self.initialize()

        try:
            await cognee.add(content, metadata=metadata)
            logger.info(f"Added document: {metadata.get('file_path', 'unknown')}")
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise

    async def cognify(self):
        """
        Process all added documents to build the knowledge graph.

        This extracts entities, relationships, embeddings, and summaries.
        Should be called after adding documents and before querying.
        """
        if not self.initialized:
            await self.initialize()

        logger.info("Starting cognify process (building knowledge graph)...")
        try:
            await cognee.cognify()
            logger.info("Knowledge graph built successfully")
        except Exception as e:
            logger.error(f"Error during cognify: {e}")
            raise

    async def query(
        self,
        question: str,
        search_type: str = "INSIGHTS",
        volume: Optional[int] = None,
        story_phase: Optional[int] = None,
        categories: Optional[List[str]] = None,
    ) -> QueryResult:
        """
        Query the knowledge graph with natural language.

        Args:
            question: Natural language query
            search_type: Type of search (INSIGHTS, SUMMARIES, CHUNKS)
            volume: Filter by volume (1, 2, or 3)
            story_phase: Filter by story phase (1-4)
            categories: Filter by categories (character, worldbuilding, etc.)

        Returns:
            QueryResult with answer, entities, relationships, and sources

        Example:
            >>> result = await kg.query("What is Mickey's relationship with Noni?")
            >>> print(result.answer)
        """
        if not self.initialized:
            await self.initialize()

        # Build metadata filter
        metadata_filter = {}
        if volume:
            metadata_filter['volume'] = volume
        if story_phase:
            metadata_filter['story_phase'] = story_phase
        if categories:
            metadata_filter['categories'] = categories

        # Perform search
        try:
            search_type_enum = getattr(SearchType, search_type.upper(), SearchType.INSIGHTS)

            results = await cognee.search(
                query_text=question,
                query_type=search_type_enum,
            )

            # Parse results
            answer = ""
            entities = []
            relationships = []
            source_docs = []
            confidence = 0.0

            if isinstance(results, list):
                for result in results:
                    if isinstance(result, dict):
                        answer += result.get('text', '') + "\n\n"
                        source_docs.extend(result.get('sources', []))
                        entities.extend(result.get('entities', []))
                        relationships.extend(result.get('relationships', []))
                        confidence = max(confidence, result.get('confidence', 0.0))
                    else:
                        answer += str(result) + "\n\n"

            return QueryResult(
                answer=answer.strip(),
                entities=entities,
                relationships=relationships,
                source_documents=list(set(source_docs)),
                confidence=confidence,
                query=question,
                search_type=search_type,
            )

        except Exception as e:
            logger.error(f"Error during query: {e}")
            raise

    async def get_character_context(
        self,
        character_name: str,
        story_phase: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive context for a character.

        Args:
            character_name: Name of the character
            story_phase: Filter by story phase (1-4)

        Returns:
            Dictionary with:
            - psychological_state: Character's mental/emotional state
            - relationships: Connections to other characters
            - abilities: Powers or skills
            - arc: Character development trajectory
            - key_scenes: Important scenes featuring this character

        Example:
            >>> context = await kg.get_character_context("Mickey Bardot", story_phase=1)
            >>> print(context['psychological_state'])
        """
        if not self.initialized:
            await self.initialize()

        # Query for different aspects of the character
        queries = {
            'psychological_state': f"What is {character_name}'s psychological and emotional state?",
            'relationships': f"What are {character_name}'s relationships with other characters?",
            'abilities': f"What abilities or powers does {character_name} have?",
            'arc': f"What is {character_name}'s character development arc?",
            'backstory': f"What is {character_name}'s backstory and history?",
        }

        context = {}
        for aspect, query_text in queries.items():
            try:
                result = await self.query(query_text, story_phase=story_phase)
                context[aspect] = result.answer
            except Exception as e:
                logger.warning(f"Could not get {aspect} for {character_name}: {e}")
                context[aspect] = ""

        return context

    async def get_worldbuilding_context(
        self,
        topics: List[str],
        story_phase: Optional[int] = None,
    ) -> Dict[str, str]:
        """
        Get worldbuilding context for specific topics.

        Args:
            topics: List of worldbuilding topics (e.g., "bi-location", "The Line")
            story_phase: Filter by story phase (1-4)

        Returns:
            Dictionary mapping topics to their descriptions

        Example:
            >>> context = await kg.get_worldbuilding_context(["bi-location", "The Line"])
            >>> print(context['bi-location'])
        """
        if not self.initialized:
            await self.initialize()

        context = {}
        for topic in topics:
            query_text = f"Explain the worldbuilding concept: {topic}"
            try:
                result = await self.query(query_text, story_phase=story_phase)
                context[topic] = result.answer
            except Exception as e:
                logger.warning(f"Could not get worldbuilding for {topic}: {e}")
                context[topic] = ""

        return context

    async def get_chapter_context(
        self,
        volume: int,
        chapter: int,
    ) -> Dict[str, Any]:
        """
        Get context for a specific chapter.

        Args:
            volume: Volume number (1, 2, or 3)
            chapter: Chapter number

        Returns:
            Dictionary with:
            - summary: Chapter summary
            - key_events: Important events in the chapter
            - characters: Characters appearing in the chapter
            - themes: Thematic elements

        Example:
            >>> context = await kg.get_chapter_context(1, 4)
            >>> print(context['summary'])
        """
        if not self.initialized:
            await self.initialize()

        chapter_id = f"{volume}.{chapter}"

        queries = {
            'summary': f"Summarize chapter {chapter_id}",
            'key_events': f"What are the key events in chapter {chapter_id}?",
            'characters': f"Which characters appear in chapter {chapter_id}?",
            'themes': f"What are the main themes in chapter {chapter_id}?",
        }

        context = {}
        for aspect, query_text in queries.items():
            try:
                result = await self.query(query_text, volume=volume)
                context[aspect] = result.answer
            except Exception as e:
                logger.warning(f"Could not get {aspect} for chapter {chapter_id}: {e}")
                context[aspect] = ""

        return context

    async def build_scene_context(
        self,
        scene_outline: str,
        characters: List[str],
        worldbuilding_topics: List[str],
        story_phase: Optional[int] = None,
        previous_scenes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build comprehensive context for writing a scene.

        This is the primary method used by the tournament system to gather
        all necessary context before generating a scene.

        Args:
            scene_outline: Brief description of the scene to be written
            characters: List of character names in the scene
            worldbuilding_topics: List of worldbuilding elements needed
            story_phase: Story phase (1-4)
            previous_scenes: List of previous scene IDs for continuity

        Returns:
            Dictionary with:
            - characters: Character contexts
            - worldbuilding: Worldbuilding contexts
            - related_scenes: Similar scenes from the corpus
            - previous_context: Context from previous scenes
            - outline: The scene outline

        Example:
            >>> context = await kg.build_scene_context(
            ...     "Mickey confronts Ken about the leverage",
            ...     ["Mickey Bardot", "Ken"],
            ...     ["bi-location", "The Line"],
            ...     story_phase=3
            ... )
        """
        if not self.initialized:
            await self.initialize()

        context = {
            'outline': scene_outline,
            'characters': {},
            'worldbuilding': {},
            'related_scenes': "",
            'previous_context': "",
        }

        # Get character contexts
        for character in characters:
            try:
                char_context = await self.get_character_context(character, story_phase)
                context['characters'][character] = char_context
            except Exception as e:
                logger.warning(f"Could not get context for {character}: {e}")

        # Get worldbuilding contexts
        try:
            wb_context = await self.get_worldbuilding_context(worldbuilding_topics, story_phase)
            context['worldbuilding'] = wb_context
        except Exception as e:
            logger.warning(f"Could not get worldbuilding context: {e}")

        # Find related scenes
        try:
            related_query = f"Find scenes similar to: {scene_outline}"
            result = await self.query(related_query, story_phase=story_phase)
            context['related_scenes'] = result.answer
        except Exception as e:
            logger.warning(f"Could not find related scenes: {e}")

        # Get previous scene context if provided
        if previous_scenes:
            prev_contexts = []
            for scene_id in previous_scenes:
                try:
                    query = f"Summarize scene {scene_id}"
                    result = await self.query(query, story_phase=story_phase)
                    prev_contexts.append(f"Scene {scene_id}: {result.answer}")
                except Exception as e:
                    logger.warning(f"Could not get context for scene {scene_id}: {e}")

            context['previous_context'] = "\n\n".join(prev_contexts)

        return context

    def format_context_for_agent(self, context: Dict[str, Any]) -> str:
        """
        Format context dictionary as a prompt-ready string for AI agents.

        Args:
            context: Context dictionary from build_scene_context()

        Returns:
            Formatted string ready to be included in agent prompts

        Example:
            >>> context = await kg.build_scene_context(...)
            >>> prompt_text = kg.format_context_for_agent(context)
        """
        sections = []

        # Scene outline
        sections.append(f"## Scene Outline\n\n{context.get('outline', 'No outline provided')}")

        # Characters
        if context.get('characters'):
            sections.append("## Character Context\n")
            for char_name, char_data in context['characters'].items():
                sections.append(f"### {char_name}\n")
                for aspect, info in char_data.items():
                    if info:
                        sections.append(f"**{aspect.replace('_', ' ').title()}**: {info}\n")

        # Worldbuilding
        if context.get('worldbuilding'):
            sections.append("## Worldbuilding Context\n")
            for topic, description in context['worldbuilding'].items():
                if description:
                    sections.append(f"**{topic}**: {description}\n")

        # Related scenes
        if context.get('related_scenes'):
            sections.append(f"## Related Scenes\n\n{context['related_scenes']}")

        # Previous context
        if context.get('previous_context'):
            sections.append(f"## Previous Scenes\n\n{context['previous_context']}")

        return "\n\n".join(sections)

    async def get_entity_info(self, entity_name: str) -> Optional[EntityInfo]:
        """
        Get detailed information about a specific entity.

        Args:
            entity_name: Name of the entity

        Returns:
            EntityInfo object or None if not found
        """
        # This would query Cognee's graph database directly
        # Implementation depends on Cognee's API for entity extraction
        logger.warning("get_entity_info not yet implemented - requires Cognee graph API")
        return None

    async def get_relationship_info(
        self,
        source_entity: str,
        target_entity: str,
    ) -> Optional[RelationshipInfo]:
        """
        Get information about the relationship between two entities.

        Args:
            source_entity: Source entity name
            target_entity: Target entity name

        Returns:
            RelationshipInfo object or None if not found
        """
        # This would query Cognee's graph database directly
        # Implementation depends on Cognee's API for relationship extraction
        logger.warning("get_relationship_info not yet implemented - requires Cognee graph API")
        return None

    async def traverse_graph(
        self,
        start_entity: str,
        max_depth: int = 2,
        relationship_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Traverse the knowledge graph starting from an entity.

        Args:
            start_entity: Starting entity name
            max_depth: Maximum traversal depth
            relationship_types: Filter by relationship types

        Returns:
            Dictionary representing the subgraph
        """
        # This would use Cognee's graph traversal capabilities
        # Implementation depends on Cognee's API for graph queries
        logger.warning("traverse_graph not yet implemented - requires Cognee graph API")
        return {}

    async def reset(self):
        """
        Reset the knowledge graph (clear all data).

        Warning: This deletes all documents and graph data!
        """
        logger.warning("Resetting knowledge graph - all data will be lost!")
        try:
            await cognee.prune.prune_data()
            await cognee.prune.prune_system()
            logger.info("Knowledge graph reset complete")
        except Exception as e:
            logger.error(f"Error resetting knowledge graph: {e}")
            raise


# Helper function for synchronous context
def create_knowledge_graph(config: Optional[CogneeConfig] = None) -> CogneeKnowledgeGraph:
    """
    Create a CogneeKnowledgeGraph instance.

    Args:
        config: Optional CogneeConfig

    Returns:
        CogneeKnowledgeGraph instance
    """
    return CogneeKnowledgeGraph(config)


if __name__ == "__main__":
    # Test basic functionality
    async def test():
        kg = CogneeKnowledgeGraph()
        await kg.initialize()

        # Add a test document
        await kg.add_document(
            "Mickey Bardot is a quantum gambler with bi-location abilities.",
            metadata={'volume': 1, 'chapter': 1}
        )

        # Build the graph
        await kg.cognify()

        # Query
        result = await kg.query("Who is Mickey Bardot?")
        print(f"Answer: {result.answer}")

    asyncio.run(test())
