"""
Entity and relationship query interface for Cognee Knowledge Graph.

This module provides specialized query methods for:
- Finding entities (characters, locations, concepts)
- Exploring relationships between entities
- Tracking entity evolution across story phases
- Analyzing entity networks and connections
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

from factory.core.cognee_knowledge_graph.cognee_graph import CogneeKnowledgeGraph, QueryResult


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EntityEvolution:
    """Track how an entity changes over time."""
    entity_name: str
    phases: Dict[int, str]  # Phase number -> description
    key_changes: List[str]
    documents: List[str]


@dataclass
class RelationshipEvolution:
    """Track how a relationship changes over time."""
    entity_a: str
    entity_b: str
    phases: Dict[int, str]  # Phase number -> relationship description
    key_changes: List[str]
    documents: List[str]


class EntityQuerier:
    """
    Specialized queries for entities and relationships in the knowledge graph.

    This class provides methods for:
    - Character analysis (psychological state, abilities, relationships)
    - Relationship tracking (evolution, conflicts, alliances)
    - Entity networks (who is connected to whom)
    - Temporal analysis (how entities change across story phases)
    """

    def __init__(self, knowledge_graph: CogneeKnowledgeGraph):
        """
        Initialize entity querier.

        Args:
            knowledge_graph: CogneeKnowledgeGraph instance
        """
        self.kg = knowledge_graph

    async def get_all_characters(
        self,
        volume: Optional[int] = None,
    ) -> List[str]:
        """
        Get list of all character names in the corpus.

        Args:
            volume: Filter by volume (1, 2, or 3)

        Returns:
            List of character names

        Example:
            >>> characters = await querier.get_all_characters(volume=1)
            >>> print(characters)
            ['Mickey Bardot', 'Noni', 'Ken', 'Sadie']
        """
        query = "List all character names in the story"
        result = await self.kg.query(query, volume=volume)

        # Parse character names from result
        # This is a simple implementation - could be enhanced with NER
        characters = []
        lines = result.answer.split('\n')
        for line in lines:
            # Look for names (capitalized words)
            words = line.strip().split()
            for i, word in enumerate(words):
                if word[0].isupper() and len(word) > 2:
                    # Could be a name
                    if i + 1 < len(words) and words[i+1][0].isupper():
                        # Two capitalized words = likely full name
                        name = f"{word} {words[i+1]}"
                        if name not in characters:
                            characters.append(name)
                    elif word not in characters and word not in ['The', 'A', 'An']:
                        characters.append(word)

        return characters

    async def get_character_psychology(
        self,
        character_name: str,
        story_phase: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get deep psychological analysis of a character.

        Args:
            character_name: Name of the character
            story_phase: Filter by story phase (1-4)

        Returns:
            Dictionary with:
            - emotional_state: Current emotional condition
            - mental_state: Psychological condition
            - motivations: What drives the character
            - fears: What the character fears
            - desires: What the character wants
            - internal_conflicts: Inner struggles

        Example:
            >>> psych = await querier.get_character_psychology("Mickey Bardot", story_phase=1)
            >>> print(psych['motivations'])
        """
        queries = {
            'emotional_state': f"What is {character_name}'s emotional state?",
            'mental_state': f"What is {character_name}'s mental and psychological condition?",
            'motivations': f"What motivates {character_name}?",
            'fears': f"What does {character_name} fear?",
            'desires': f"What does {character_name} desire or want?",
            'internal_conflicts': f"What internal conflicts does {character_name} experience?",
        }

        psychology = {}
        for aspect, query_text in queries.items():
            try:
                result = await self.kg.query(query_text, story_phase=story_phase)
                psychology[aspect] = result.answer
            except Exception as e:
                logger.warning(f"Could not get {aspect} for {character_name}: {e}")
                psychology[aspect] = ""

        return psychology

    async def get_character_abilities(
        self,
        character_name: str,
        story_phase: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get information about a character's abilities and powers.

        Args:
            character_name: Name of the character
            story_phase: Filter by story phase (1-4)

        Returns:
            Dictionary with:
            - abilities: List of abilities/powers
            - limitations: Limitations of their abilities
            - development: How abilities develop over time

        Example:
            >>> abilities = await querier.get_character_abilities("Mickey Bardot")
            >>> print(abilities['abilities'])
        """
        queries = {
            'abilities': f"What abilities or powers does {character_name} have?",
            'limitations': f"What are the limitations of {character_name}'s abilities?",
            'development': f"How do {character_name}'s abilities develop over time?",
        }

        abilities_info = {}
        for aspect, query_text in queries.items():
            try:
                result = await self.kg.query(query_text, story_phase=story_phase)
                abilities_info[aspect] = result.answer
            except Exception as e:
                logger.warning(f"Could not get {aspect} for {character_name}: {e}")
                abilities_info[aspect] = ""

        return abilities_info

    async def get_relationship(
        self,
        character_a: str,
        character_b: str,
        story_phase: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get detailed information about the relationship between two characters.

        Args:
            character_a: First character name
            character_b: Second character name
            story_phase: Filter by story phase (1-4)

        Returns:
            Dictionary with:
            - dynamic: Overall relationship dynamic
            - trust_level: Level of trust between them
            - conflicts: Areas of conflict
            - alliances: Areas of alliance or cooperation
            - history: Relationship history

        Example:
            >>> rel = await querier.get_relationship("Mickey Bardot", "Noni")
            >>> print(rel['dynamic'])
        """
        queries = {
            'dynamic': f"What is the relationship dynamic between {character_a} and {character_b}?",
            'trust_level': f"What is the trust level between {character_a} and {character_b}?",
            'conflicts': f"What conflicts exist between {character_a} and {character_b}?",
            'alliances': f"How do {character_a} and {character_b} cooperate or work together?",
            'history': f"What is the history between {character_a} and {character_b}?",
        }

        relationship = {}
        for aspect, query_text in queries.items():
            try:
                result = await self.kg.query(query_text, story_phase=story_phase)
                relationship[aspect] = result.answer
            except Exception as e:
                logger.warning(f"Could not get {aspect} for relationship: {e}")
                relationship[aspect] = ""

        return relationship

    async def track_entity_evolution(
        self,
        entity_name: str,
        phases: Optional[List[int]] = None,
    ) -> EntityEvolution:
        """
        Track how an entity evolves across story phases.

        Args:
            entity_name: Name of the entity (character, concept, etc.)
            phases: List of phases to track (defaults to all 4)

        Returns:
            EntityEvolution object with phase-by-phase descriptions

        Example:
            >>> evolution = await querier.track_entity_evolution("Mickey Bardot")
            >>> print(evolution.phases[1])  # Phase 1 description
            >>> print(evolution.phases[2])  # Phase 2 description
        """
        if phases is None:
            phases = [1, 2, 3, 4]

        phase_descriptions = {}
        all_documents = []

        for phase in phases:
            query = f"Describe {entity_name} in story phase {phase}"
            try:
                result = await self.kg.query(query, story_phase=phase)
                phase_descriptions[phase] = result.answer
                all_documents.extend(result.source_documents)
            except Exception as e:
                logger.warning(f"Could not get phase {phase} for {entity_name}: {e}")
                phase_descriptions[phase] = ""

        # Analyze key changes between phases
        key_changes = []
        for i in range(len(phases) - 1):
            phase_a, phase_b = phases[i], phases[i+1]
            desc_a = phase_descriptions.get(phase_a, "")
            desc_b = phase_descriptions.get(phase_b, "")

            if desc_a and desc_b:
                query = f"What are the key changes in {entity_name} between phase {phase_a} and phase {phase_b}?"
                try:
                    result = await self.kg.query(query)
                    key_changes.append(f"Phase {phase_a}→{phase_b}: {result.answer}")
                except Exception as e:
                    logger.warning(f"Could not identify changes for {entity_name}: {e}")

        return EntityEvolution(
            entity_name=entity_name,
            phases=phase_descriptions,
            key_changes=key_changes,
            documents=list(set(all_documents)),
        )

    async def track_relationship_evolution(
        self,
        entity_a: str,
        entity_b: str,
        phases: Optional[List[int]] = None,
    ) -> RelationshipEvolution:
        """
        Track how a relationship evolves across story phases.

        Args:
            entity_a: First entity name
            entity_b: Second entity name
            phases: List of phases to track (defaults to all 4)

        Returns:
            RelationshipEvolution object with phase-by-phase descriptions

        Example:
            >>> evolution = await querier.track_relationship_evolution("Mickey Bardot", "Noni")
            >>> print(evolution.phases[1])  # Phase 1 relationship
        """
        if phases is None:
            phases = [1, 2, 3, 4]

        phase_descriptions = {}
        all_documents = []

        for phase in phases:
            query = f"Describe the relationship between {entity_a} and {entity_b} in story phase {phase}"
            try:
                result = await self.kg.query(query, story_phase=phase)
                phase_descriptions[phase] = result.answer
                all_documents.extend(result.source_documents)
            except Exception as e:
                logger.warning(f"Could not get phase {phase} relationship: {e}")
                phase_descriptions[phase] = ""

        # Analyze key changes
        key_changes = []
        for i in range(len(phases) - 1):
            phase_a, phase_b = phases[i], phases[i+1]
            if phase_descriptions.get(phase_a) and phase_descriptions.get(phase_b):
                query = f"How does the relationship between {entity_a} and {entity_b} change from phase {phase_a} to phase {phase_b}?"
                try:
                    result = await self.kg.query(query)
                    key_changes.append(f"Phase {phase_a}→{phase_b}: {result.answer}")
                except Exception as e:
                    logger.warning(f"Could not identify relationship changes: {e}")

        return RelationshipEvolution(
            entity_a=entity_a,
            entity_b=entity_b,
            phases=phase_descriptions,
            key_changes=key_changes,
            documents=list(set(all_documents)),
        )

    async def get_entity_network(
        self,
        entity_name: str,
        max_connections: int = 10,
    ) -> Dict[str, List[str]]:
        """
        Get the network of entities connected to a given entity.

        Args:
            entity_name: Name of the central entity
            max_connections: Maximum number of connections to return

        Returns:
            Dictionary mapping connection types to entity lists

        Example:
            >>> network = await querier.get_entity_network("Mickey Bardot")
            >>> print(network['allies'])
            >>> print(network['enemies'])
        """
        queries = {
            'allies': f"Who are {entity_name}'s allies or friends?",
            'enemies': f"Who are {entity_name}'s enemies or antagonists?",
            'family': f"Who are {entity_name}'s family members?",
            'mentors': f"Who are {entity_name}'s mentors or teachers?",
            'students': f"Who are {entity_name}'s students or proteges?",
        }

        network = {}
        for connection_type, query_text in queries.items():
            try:
                result = await self.kg.query(query_text)
                # Parse entity names from result (simple implementation)
                entities = []
                for line in result.answer.split('\n'):
                    words = line.strip().split()
                    for i, word in enumerate(words):
                        if word[0].isupper() and len(word) > 2:
                            if i + 1 < len(words) and words[i+1][0].isupper():
                                name = f"{word} {words[i+1]}"
                                if name not in entities and name != entity_name:
                                    entities.append(name)

                network[connection_type] = entities[:max_connections]
            except Exception as e:
                logger.warning(f"Could not get {connection_type} for {entity_name}: {e}")
                network[connection_type] = []

        return network

    async def find_similar_entities(
        self,
        entity_name: str,
        entity_type: Optional[str] = None,
        limit: int = 5,
    ) -> List[str]:
        """
        Find entities similar to the given entity.

        Args:
            entity_name: Name of the entity
            entity_type: Type filter (character, location, concept)
            limit: Maximum number of results

        Returns:
            List of similar entity names

        Example:
            >>> similar = await querier.find_similar_entities("Mickey Bardot")
            >>> print(similar)  # Other gamblers or quantum users
        """
        type_filter = f"{entity_type}s" if entity_type else "entities"
        query = f"Find {type_filter} similar to {entity_name}"

        try:
            result = await self.kg.query(query)

            # Parse entity names
            entities = []
            for line in result.answer.split('\n'):
                words = line.strip().split()
                for i, word in enumerate(words):
                    if word[0].isupper() and len(word) > 2:
                        if i + 1 < len(words) and words[i+1][0].isupper():
                            name = f"{word} {words[i+1]}"
                            if name not in entities and name != entity_name:
                                entities.append(name)
                        elif word not in entities and word != entity_name:
                            entities.append(word)

            return entities[:limit]

        except Exception as e:
            logger.error(f"Could not find similar entities: {e}")
            return []

    async def get_worldbuilding_mechanics(
        self,
        topic: str,
    ) -> Dict[str, Any]:
        """
        Get detailed worldbuilding mechanics for a specific topic.

        Args:
            topic: Worldbuilding topic (e.g., "bi-location", "The Line")

        Returns:
            Dictionary with:
            - description: What it is
            - rules: How it works
            - limitations: What its limits are
            - examples: Examples of its use
            - violations: What happens when rules are broken

        Example:
            >>> mechanics = await querier.get_worldbuilding_mechanics("bi-location")
            >>> print(mechanics['rules'])
        """
        queries = {
            'description': f"What is {topic}?",
            'rules': f"What are the rules governing {topic}?",
            'limitations': f"What are the limitations of {topic}?",
            'examples': f"What are examples of {topic} being used?",
            'violations': f"What happens when {topic} rules are violated?",
        }

        mechanics = {}
        for aspect, query_text in queries.items():
            try:
                result = await self.kg.query(query_text, categories=['worldbuilding'])
                mechanics[aspect] = result.answer
            except Exception as e:
                logger.warning(f"Could not get {aspect} for {topic}: {e}")
                mechanics[aspect] = ""

        return mechanics

    async def analyze_character_arc(
        self,
        character_name: str,
    ) -> Dict[str, Any]:
        """
        Analyze a character's complete arc across the entire trilogy.

        Args:
            character_name: Name of the character

        Returns:
            Dictionary with:
            - arc_type: Type of character arc (growth, fall, transformation)
            - starting_point: Character at story beginning
            - turning_points: Major turning points
            - ending_point: Character at story end (if available)
            - themes: Thematic elements of the arc

        Example:
            >>> arc = await querier.analyze_character_arc("Mickey Bardot")
            >>> print(arc['turning_points'])
        """
        queries = {
            'arc_type': f"What type of character arc does {character_name} have?",
            'starting_point': f"Describe {character_name} at the beginning of the story",
            'turning_points': f"What are the major turning points in {character_name}'s arc?",
            'ending_point': f"Describe {character_name} at the end of the story",
            'themes': f"What themes are explored through {character_name}'s arc?",
        }

        arc = {}
        for aspect, query_text in queries.items():
            try:
                result = await self.kg.query(query_text)
                arc[aspect] = result.answer
            except Exception as e:
                logger.warning(f"Could not get {aspect} for {character_name}'s arc: {e}")
                arc[aspect] = ""

        return arc


if __name__ == "__main__":
    # Test entity queries
    import asyncio
    from factory.core.cognee_knowledge_graph.cognee_graph import CogneeKnowledgeGraph

    async def test():
        kg = CogneeKnowledgeGraph()
        await kg.initialize()

        querier = EntityQuerier(kg)

        # Test character psychology
        psych = await querier.get_character_psychology("Mickey Bardot", story_phase=1)
        print("Psychology:", psych)

        # Test relationship
        rel = await querier.get_relationship("Mickey Bardot", "Noni")
        print("Relationship:", rel)

    asyncio.run(test())
