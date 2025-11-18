"""
LLM-based entity and relationship extraction.
Uses Claude/GPT for high-quality extraction with reasoning.
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
import re

from app.core.agent_pool_initializer import create_default_agent_pool
from ..models import Entity, Relationship, EntityType, RelationType

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extract entities and relationships using large language models."""

    def __init__(self, model_name: str = "claude-sonnet-4.5"):
        """
        Initialize extractor.

        Args:
            model_name: Which AI model to use for extraction
        """
        self.model_name = model_name
        self.agent_pool = create_default_agent_pool()

    async def extract_entities(
        self,
        scene_content: str,
        scene_id: str,
        existing_entities: Optional[List[Entity]] = None
    ) -> List[Entity]:
        """
        Extract entities from scene text.

        Args:
            scene_content: The scene prose
            scene_id: ID of the scene
            existing_entities: Known entities to help with coreference resolution

        Returns:
            List of extracted Entity objects
        """
        # Build context from existing entities
        context = ""
        if existing_entities:
            entity_list = "\n".join([
                f"- {e.name} ({e.entity_type.value}): {e.description[:100]}"
                for e in existing_entities[:20]  # Top 20 for context
            ])
            context = f"\n\nKnown entities from previous scenes:\n{entity_list}\n"

        prompt = f"""Extract ALL entities from this scene. For each entity found:

1. Identify the entity name
2. Classify the type: character, location, object, concept, event, organization, or theme
3. Write a brief description (1-2 sentences)
4. List any alternative names or aliases
5. Extract key attributes (traits, properties, characteristics)

{context}

Scene text:
{scene_content}

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "name": "Entity Name",
    "type": "character|location|object|concept|event|organization|theme",
    "description": "Brief description",
    "aliases": ["alternative name 1", "alternative name 2"],
    "attributes": {{
      "trait1": "value1",
      "trait2": "value2"
    }}
  }}
]

Be thorough. Extract ALL meaningful entities, including:
- All characters mentioned (even minor ones)
- All locations (specific places, cities, buildings, rooms)
- Important objects (weapons, devices, artifacts)
- Concepts and themes discussed
- Events that occur
- Organizations or groups mentioned
"""

        try:
            agent = self.agent_pool.get_agent(self.model_name)
            result = await agent.generate(
                prompt,
                temperature=0.3,  # Low temperature for consistent extraction
                max_tokens=4000
            )

            # Parse JSON from output
            output = result['output']

            # Extract JSON array (handle markdown code blocks)
            json_match = re.search(r'\[[\s\S]*\]', output)
            if not json_match:
                logger.error(f"No JSON array found in LLM output")
                return []

            entities_data = json.loads(json_match.group(0))

            # Convert to Entity objects
            entities = []
            for data in entities_data:
                try:
                    entity = Entity(
                        id=self._create_entity_id(data['name']),
                        name=data['name'],
                        entity_type=EntityType(data['type']),
                        description=data.get('description', ''),
                        aliases=data.get('aliases', []),
                        attributes=data.get('attributes', {}),
                        first_appearance=scene_id,
                        appearances=[scene_id],
                        mentions=1,
                        confidence=0.9  # LLM extraction has high confidence
                    )
                    entities.append(entity)
                except Exception as e:
                    logger.warning(f"Failed to create entity from {data}: {e}")
                    continue

            logger.info(f"Extracted {len(entities)} entities from scene {scene_id}")
            return entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    async def extract_relationships(
        self,
        scene_content: str,
        scene_id: str,
        entities: List[Entity]
    ) -> List[Relationship]:
        """
        Extract relationships between entities.

        Args:
            scene_content: The scene prose
            scene_id: ID of the scene
            entities: Entities found in this scene

        Returns:
            List of extracted Relationship objects
        """
        if len(entities) < 2:
            return []  # Need at least 2 entities for relationships

        entity_names = [e.name for e in entities]
        entity_types = {e.name: e.entity_type.value for e in entities}

        # Available relationship types
        rel_types = [rt.value for rt in RelationType]

        prompt = f"""Identify ALL relationships between entities in this scene.

Entities found:
{json.dumps([{'name': e.name, 'type': e.entity_type.value} for e in entities], indent=2)}

Available relationship types:
{', '.join(rel_types)}

Scene text:
{scene_content}

For each relationship:
1. Identify source entity (must be from the entities list)
2. Identify target entity (must be from the entities list)
3. Choose appropriate relationship type from the available types
4. Provide context/evidence from the scene
5. Estimate relationship strength (0.0 to 1.0)
6. Estimate emotional valence (-1.0 negative to 1.0 positive)

Return ONLY a valid JSON array:
[
  {{
    "source": "Entity 1 Name",
    "target": "Entity 2 Name",
    "relation": "relationship_type",
    "context": "Evidence from scene showing this relationship",
    "strength": 0.8,
    "valence": 0.5
  }}
]

Be thorough. Extract ALL relationships shown or implied in the scene.
"""

        try:
            agent = self.agent_pool.get_agent(self.model_name)
            result = await agent.generate(
                prompt,
                temperature=0.3,
                max_tokens=3000
            )

            # Parse JSON
            output = result['output']
            json_match = re.search(r'\[[\s\S]*\]', output)
            if not json_match:
                logger.error(f"No JSON array found in relationship extraction")
                return []

            relationships_data = json.loads(json_match.group(0))

            # Convert to Relationship objects
            relationships = []
            entity_id_map = {e.name: e.id for e in entities}

            for data in relationships_data:
                try:
                    source_name = data['source']
                    target_name = data['target']

                    # Validate entities exist
                    if source_name not in entity_id_map or target_name not in entity_id_map:
                        logger.warning(f"Relationship references unknown entity: {source_name} or {target_name}")
                        continue

                    relationship = Relationship(
                        source_id=entity_id_map[source_name],
                        target_id=entity_id_map[target_name],
                        relation_type=RelationType(data['relation']),
                        description=data.get('context', ''),
                        context=[data.get('context', '')],
                        scenes=[scene_id],
                        strength=float(data.get('strength', 1.0)),
                        valence=float(data.get('valence', 0.0)),
                        start_scene=scene_id,
                        confidence=0.85
                    )
                    relationships.append(relationship)
                except Exception as e:
                    logger.warning(f"Failed to create relationship from {data}: {e}")
                    continue

            logger.info(f"Extracted {len(relationships)} relationships from scene {scene_id}")
            return relationships

        except Exception as e:
            logger.error(f"Relationship extraction failed: {e}")
            return []

    def _create_entity_id(self, name: str) -> str:
        """Create normalized entity ID from name."""
        # Normalize: lowercase, remove special chars, replace spaces with underscores
        normalized = re.sub(r'[^a-z0-9\s]', '', name.lower())
        normalized = re.sub(r'\s+', '_', normalized.strip())
        return f"entity_{normalized}"
