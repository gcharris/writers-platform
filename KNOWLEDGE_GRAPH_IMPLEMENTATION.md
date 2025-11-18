# Knowledge Graph Implementation: Complete Gold Standard

**Goal**: Build a production-grade knowledge graph system that auto-extracts entities and relationships from scenes, provides rich context to AI agents, and enables powerful querying and visualization.

**Philosophy**: No shortcuts. Build it right the first time. Modular, scalable, and battle-tested.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE GRAPH LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐        ┌──────────────┐      ┌─────────────┐ │
│  │  NetworkX    │        │  PostgreSQL  │      │   Neo4j     │ │
│  │  (In-Memory) │───────▶│  (Persist)   │──────│  (Future)   │ │
│  │              │        │              │      │             │ │
│  │  • Fast      │        │  • JSONB     │      │  • Scale    │ │
│  │  • Analysis  │        │  • Backup    │      │  • Cypher   │ │
│  │  • Prototype │        │  • Query     │      │  • Advanced │ │
│  └──────────────┘        └──────────────┘      └─────────────┘ │
│         ↑                        ↑                      ↑        │
│         │                        │                      │        │
│         └────────────────────────┴──────────────────────┘        │
│                    Unified Graph Service                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Entity & Relationship Extraction             │  │
│  │  • LLM-based (Claude, GPT for quality)                   │  │
│  │  • NER fallback (spaCy for speed)                        │  │
│  │  • Relationship inference (LLM reasoning)                │  │
│  │  • Attribute extraction (traits, descriptions)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│         ↑                                                         │
│         │ Triggered by                                           │
│         │                                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                Scene Completion Events                    │  │
│  │  • Automatic extraction on scene save                    │  │
│  │  • Background job processing                             │  │
│  │  • Incremental graph updates                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
│  • REST endpoints for graph queries                             │
│  • WebSocket for real-time graph updates                        │
│  • Export endpoints (JSON, GraphML, NotebookLM)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                              │
│  • Interactive graph visualization (D3.js, vis.js)              │
│  • Entity browser and search                                     │
│  • Relationship explorer                                         │
│  • Timeline view (events over narrative time)                   │
│  • Export and sharing tools                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Core Graph Engine (NetworkX Foundation)

### 1.1: Graph Data Models

**File**: `backend/app/services/knowledge_graph/models.py`

```python
"""
Knowledge graph data models.
Defines entity types, relationship types, and graph structure.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    """Entity types in the knowledge graph."""
    CHARACTER = "character"
    LOCATION = "location"
    OBJECT = "object"
    CONCEPT = "concept"
    EVENT = "event"
    ORGANIZATION = "organization"
    THEME = "theme"


class RelationType(str, Enum):
    """Relationship types between entities."""
    # Character relationships
    KNOWS = "knows"
    RELATED_TO = "related_to"
    CONFLICTS_WITH = "conflicts_with"
    LOVES = "loves"
    FEARS = "fears"
    WORKS_WITH = "works_with"
    LEADS = "leads"
    FOLLOWS = "follows"

    # Spatial relationships
    LOCATED_IN = "located_in"
    TRAVELS_TO = "travels_to"
    OWNS = "owns"
    RESIDES_IN = "resides_in"

    # Temporal relationships
    OCCURS_BEFORE = "occurs_before"
    OCCURS_DURING = "occurs_during"
    OCCURS_AFTER = "occurs_after"
    CAUSES = "causes"
    RESULTS_IN = "results_in"

    # Conceptual relationships
    REPRESENTS = "represents"
    SYMBOLIZES = "symbolizes"
    RELATES_TO = "relates_to"
    OPPOSES = "opposes"
    SUPPORTS = "supports"

    # Event relationships
    PARTICIPATES_IN = "participates_in"
    WITNESSES = "witnesses"
    TRIGGERS = "triggers"

    # Organizational
    MEMBER_OF = "member_of"
    FOUNDED_BY = "founded_by"
    CONTROLS = "controls"


@dataclass
class Entity:
    """An entity in the knowledge graph."""
    id: str
    name: str
    entity_type: EntityType
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)

    # Tracking
    first_appearance: Optional[str] = None  # scene_id
    appearances: List[str] = field(default_factory=list)  # scene_ids
    mentions: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0  # Extraction confidence
    verified: bool = False  # Human-verified

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.entity_type.value,
            'description': self.description,
            'aliases': self.aliases,
            'attributes': self.attributes,
            'first_appearance': self.first_appearance,
            'appearances': self.appearances,
            'mentions': self.mentions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'confidence': self.confidence,
            'verified': self.verified
        }


@dataclass
class Relationship:
    """A relationship between two entities."""
    source_id: str
    target_id: str
    relation_type: RelationType

    # Context
    description: str = ""
    context: List[str] = field(default_factory=list)  # Textual context
    scenes: List[str] = field(default_factory=list)  # Where relationship appears

    # Attributes
    strength: float = 1.0  # Relationship strength (0-1)
    valence: float = 0.0  # Emotional valence (-1 to 1, negative to positive)
    attributes: Dict[str, Any] = field(default_factory=dict)

    # Temporal
    start_scene: Optional[str] = None
    end_scene: Optional[str] = None

    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'source': self.source_id,
            'target': self.target_id,
            'relation': self.relation_type.value,
            'description': self.description,
            'context': self.context,
            'scenes': self.scenes,
            'strength': self.strength,
            'valence': self.valence,
            'attributes': self.attributes,
            'start_scene': self.start_scene,
            'end_scene': self.end_scene,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'confidence': self.confidence,
            'verified': self.verified
        }


@dataclass
class GraphMetadata:
    """Metadata about the knowledge graph."""
    project_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    last_extracted_scene: Optional[str] = None

    # Statistics
    entity_count: int = 0
    relationship_count: int = 0
    scene_count: int = 0

    # Extraction stats
    total_extractions: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'last_extracted_scene': self.last_extracted_scene,
            'stats': {
                'entities': self.entity_count,
                'relationships': self.relationship_count,
                'scenes': self.scene_count
            },
            'extraction_stats': {
                'total': self.total_extractions,
                'successful': self.successful_extractions,
                'failed': self.failed_extractions,
                'success_rate': (
                    self.successful_extractions / self.total_extractions
                    if self.total_extractions > 0 else 0
                )
            }
        }
```

### 1.2: Core Graph Service

**File**: `backend/app/services/knowledge_graph/graph_service.py`

```python
"""
Core knowledge graph service using NetworkX.
Handles all graph operations, queries, and analysis.
"""

import networkx as nx
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import logging

from .models import Entity, Relationship, EntityType, RelationType, GraphMetadata

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """
    Production knowledge graph service.
    Uses NetworkX for in-memory graph operations with PostgreSQL persistence.
    """

    def __init__(self, project_id: str):
        """Initialize knowledge graph for a project."""
        self.project_id = project_id
        self.graph = nx.MultiDiGraph()
        self.metadata = GraphMetadata(project_id=project_id)
        self._entity_index: Dict[str, Entity] = {}
        self._relationship_index: Dict[Tuple[str, str, str], Relationship] = {}

    # ============================================================================
    # ENTITY OPERATIONS
    # ============================================================================

    def add_entity(self, entity: Entity) -> bool:
        """
        Add entity to graph.

        Returns:
            True if entity was added, False if it already existed (then updated)
        """
        existed = entity.id in self.graph

        # Add to NetworkX graph
        self.graph.add_node(
            entity.id,
            **entity.to_dict()
        )

        # Update index
        self._entity_index[entity.id] = entity

        # Update metadata
        if not existed:
            self.metadata.entity_count += 1
        self.metadata.last_updated = datetime.now()

        logger.info(f"{'Updated' if existed else 'Added'} entity: {entity.name} ({entity.entity_type.value})")
        return not existed

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self._entity_index.get(entity_id)

    def find_entity_by_name(self, name: str, fuzzy: bool = False) -> Optional[Entity]:
        """Find entity by name (exact or fuzzy match)."""
        # Exact match
        for entity in self._entity_index.values():
            if entity.name.lower() == name.lower():
                return entity
            if name.lower() in [alias.lower() for alias in entity.aliases]:
                return entity

        # Fuzzy match (simple contains)
        if fuzzy:
            for entity in self._entity_index.values():
                if name.lower() in entity.name.lower():
                    return entity

        return None

    def query_entities(
        self,
        entity_type: Optional[EntityType] = None,
        min_mentions: int = 0,
        verified_only: bool = False,
        **attribute_filters
    ) -> List[Entity]:
        """
        Query entities with filters.

        Args:
            entity_type: Filter by entity type
            min_mentions: Minimum number of scene mentions
            verified_only: Only return human-verified entities
            **attribute_filters: Filter by specific attributes

        Returns:
            List of matching entities
        """
        results = []

        for entity in self._entity_index.values():
            # Type filter
            if entity_type and entity.entity_type != entity_type:
                continue

            # Mentions filter
            if entity.mentions < min_mentions:
                continue

            # Verified filter
            if verified_only and not entity.verified:
                continue

            # Attribute filters
            if attribute_filters:
                match = all(
                    entity.attributes.get(k) == v
                    for k, v in attribute_filters.items()
                )
                if not match:
                    continue

            results.append(entity)

        return results

    def update_entity(self, entity_id: str, **updates) -> bool:
        """Update entity attributes."""
        entity = self.get_entity(entity_id)
        if not entity:
            return False

        # Update attributes
        for key, value in updates.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
            else:
                entity.attributes[key] = value

        entity.updated_at = datetime.now()

        # Update graph node
        self.graph.nodes[entity_id].update(entity.to_dict())

        self.metadata.last_updated = datetime.now()
        return True

    # ============================================================================
    # RELATIONSHIP OPERATIONS
    # ============================================================================

    def add_relationship(self, relationship: Relationship) -> bool:
        """
        Add relationship to graph.

        Returns:
            True if relationship was added, False if it already existed
        """
        # Check if entities exist
        if relationship.source_id not in self._entity_index:
            logger.warning(f"Source entity not found: {relationship.source_id}")
            return False

        if relationship.target_id not in self._entity_index:
            logger.warning(f"Target entity not found: {relationship.target_id}")
            return False

        # Create relationship key
        key = (relationship.source_id, relationship.target_id, relationship.relation_type.value)
        existed = key in self._relationship_index

        # Add to NetworkX graph
        self.graph.add_edge(
            relationship.source_id,
            relationship.target_id,
            key=relationship.relation_type.value,
            **relationship.to_dict()
        )

        # Update index
        self._relationship_index[key] = relationship

        # Update metadata
        if not existed:
            self.metadata.relationship_count += 1
        self.metadata.last_updated = datetime.now()

        logger.info(
            f"{'Updated' if existed else 'Added'} relationship: "
            f"{relationship.source_id} --[{relationship.relation_type.value}]--> {relationship.target_id}"
        )
        return not existed

    def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[RelationType] = None
    ) -> List[Relationship]:
        """Get relationships matching criteria."""
        results = []

        for (src, tgt, rel), relationship in self._relationship_index.items():
            if source_id and src != source_id:
                continue
            if target_id and tgt != target_id:
                continue
            if relation_type and rel != relation_type.value:
                continue

            results.append(relationship)

        return results

    # ============================================================================
    # GRAPH QUERIES
    # ============================================================================

    def get_connected_entities(
        self,
        entity_id: str,
        max_depth: int = 2,
        relation_types: Optional[List[RelationType]] = None
    ) -> List[Entity]:
        """
        Get all entities connected to this one within max_depth.

        Args:
            entity_id: Starting entity
            max_depth: Maximum traversal depth
            relation_types: Filter by relationship types

        Returns:
            List of connected entities
        """
        if entity_id not in self.graph:
            return []

        # BFS traversal
        visited: Set[str] = set()
        queue: List[Tuple[str, int]] = [(entity_id, 0)]
        connected: List[str] = []

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            if current_id != entity_id:
                connected.append(current_id)

            # Get neighbors
            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in visited:
                    # Check relationship type filter
                    if relation_types:
                        edges = self.graph[current_id][neighbor]
                        has_matching_rel = any(
                            data.get('relation') in [rt.value for rt in relation_types]
                            for edge_key, data in edges.items()
                        )
                        if not has_matching_rel:
                            continue

                    queue.append((neighbor, depth + 1))

        return [self._entity_index[eid] for eid in connected if eid in self._entity_index]

    def find_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find shortest path between two entities."""
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except nx.NetworkXNoPath:
            return None

    def get_central_entities(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get most central entities using PageRank.

        Returns:
            List of (entity_id, centrality_score) tuples
        """
        pagerank = nx.pagerank(self.graph)
        sorted_entities = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        return sorted_entities[:top_n]

    def get_communities(self) -> List[Set[str]]:
        """Detect entity communities using Louvain method."""
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()

        # Use greedy modularity optimization
        from networkx.algorithms import community
        communities = community.greedy_modularity_communities(undirected)

        return [set(c) for c in communities]

    # ============================================================================
    # SERIALIZATION
    # ============================================================================

    def to_json(self) -> str:
        """Serialize entire graph to JSON."""
        data = {
            'metadata': self.metadata.to_dict(),
            'graph': nx.node_link_data(self.graph),
            'entities': {
                eid: entity.to_dict()
                for eid, entity in self._entity_index.items()
            },
            'relationships': [
                rel.to_dict()
                for rel in self._relationship_index.values()
            ]
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'KnowledgeGraphService':
        """Load graph from JSON."""
        data = json.loads(json_str)

        # Create instance
        kg = cls(project_id=data['metadata']['project_id'])

        # Restore graph
        kg.graph = nx.node_link_graph(data['graph'], directed=True, multigraph=True)

        # Restore entities
        for eid, entity_data in data['entities'].items():
            entity = Entity(
                id=entity_data['id'],
                name=entity_data['name'],
                entity_type=EntityType(entity_data['type']),
                description=entity_data.get('description', ''),
                aliases=entity_data.get('aliases', []),
                attributes=entity_data.get('attributes', {}),
                first_appearance=entity_data.get('first_appearance'),
                appearances=entity_data.get('appearances', []),
                mentions=entity_data.get('mentions', 0),
                confidence=entity_data.get('confidence', 1.0),
                verified=entity_data.get('verified', False)
            )
            kg._entity_index[eid] = entity

        # Restore relationships
        for rel_data in data['relationships']:
            relationship = Relationship(
                source_id=rel_data['source'],
                target_id=rel_data['target'],
                relation_type=RelationType(rel_data['relation']),
                description=rel_data.get('description', ''),
                context=rel_data.get('context', []),
                scenes=rel_data.get('scenes', []),
                strength=rel_data.get('strength', 1.0),
                valence=rel_data.get('valence', 0.0),
                attributes=rel_data.get('attributes', {}),
                start_scene=rel_data.get('start_scene'),
                end_scene=rel_data.get('end_scene'),
                confidence=rel_data.get('confidence', 1.0),
                verified=rel_data.get('verified', False)
            )
            key = (relationship.source_id, relationship.target_id, relationship.relation_type.value)
            kg._relationship_index[key] = relationship

        # Restore metadata
        kg.metadata.last_updated = datetime.fromisoformat(data['metadata']['last_updated'])
        kg.metadata.entity_count = len(kg._entity_index)
        kg.metadata.relationship_count = len(kg._relationship_index)

        return kg

    def export_for_visualization(self) -> Dict[str, Any]:
        """
        Export graph in format for D3.js/vis.js visualization.

        Returns:
            Dict with 'nodes' and 'edges' arrays
        """
        nodes = []
        for entity_id, entity in self._entity_index.items():
            nodes.append({
                'id': entity_id,
                'label': entity.name,
                'type': entity.entity_type.value,
                'description': entity.description,
                'mentions': entity.mentions,
                'verified': entity.verified,
                'group': entity.entity_type.value,  # For coloring
                **entity.attributes
            })

        edges = []
        for relationship in self._relationship_index.values():
            edges.append({
                'source': relationship.source_id,
                'target': relationship.target_id,
                'label': relationship.relation_type.value,
                'description': relationship.description,
                'strength': relationship.strength,
                'valence': relationship.valence,
                'type': relationship.relation_type.value
            })

        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': self.metadata.to_dict()
        }

    def export_graphml(self) -> str:
        """Export as GraphML for visualization in tools like Gephi."""
        from io import BytesIO
        buffer = BytesIO()
        nx.write_graphml(self.graph, buffer)
        return buffer.getvalue().decode('utf-8')

    # ============================================================================
    # ANALYSIS METHODS
    # ============================================================================

    def get_entity_stats(self, entity_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for an entity."""
        entity = self.get_entity(entity_id)
        if not entity:
            return {}

        # Degree (connections)
        in_degree = self.graph.in_degree(entity_id)
        out_degree = self.graph.out_degree(entity_id)

        # Centrality
        try:
            betweenness = nx.betweenness_centrality(self.graph).get(entity_id, 0)
            closeness = nx.closeness_centrality(self.graph).get(entity_id, 0)
        except:
            betweenness = 0
            closeness = 0

        # Relationships
        incoming_rels = self.get_relationships(target_id=entity_id)
        outgoing_rels = self.get_relationships(source_id=entity_id)

        return {
            'entity': entity.to_dict(),
            'connections': {
                'incoming': in_degree,
                'outgoing': out_degree,
                'total': in_degree + out_degree
            },
            'centrality': {
                'betweenness': betweenness,
                'closeness': closeness
            },
            'relationships': {
                'incoming': len(incoming_rels),
                'outgoing': len(outgoing_rels),
                'total': len(incoming_rels) + len(outgoing_rels)
            }
        }
```

---

## Phase 2: Entity & Relationship Extraction

### 2.1: LLM-Based Extraction

**File**: `backend/app/services/knowledge_graph/extractors/llm_extractor.py`

```python
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
```

### 2.2: NER Fallback Extractor

**File**: `backend/app/services/knowledge_graph/extractors/ner_extractor.py`

```python
"""
Fast NER-based extraction using spaCy.
Fallback for when LLM extraction is too slow/expensive.
"""

import logging
from typing import List, Optional

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from ..models import Entity, EntityType

logger = logging.getLogger(__name__)


class NERExtractor:
    """Fast entity extraction using spaCy NER."""

    def __init__(self):
        """Initialize spaCy model."""
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy not installed. Run: pip install spacy && python -m spacy download en_core_web_lg")

        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            logger.warning("en_core_web_lg not found, downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_lg"])
            self.nlp = spacy.load("en_core_web_lg")

    def extract_entities(self, scene_content: str, scene_id: str) -> List[Entity]:
        """
        Extract entities using spaCy NER.

        Faster than LLM but less accurate. Good for:
        - Quick extraction
        - Large volumes of text
        - Cost-sensitive scenarios
        """
        doc = self.nlp(scene_content)

        entities = []
        seen_names = set()

        for ent in doc.ents:
            # Skip duplicates
            if ent.text in seen_names:
                continue
            seen_names.add(ent.text)

            # Map spaCy types to our types
            entity_type = self._map_spacy_type(ent.label_)
            if not entity_type:
                continue

            entity = Entity(
                id=self._create_entity_id(ent.text),
                name=ent.text,
                entity_type=entity_type,
                description=f"Extracted from scene context",
                first_appearance=scene_id,
                appearances=[scene_id],
                mentions=1,
                confidence=0.7  # Lower confidence for NER
            )
            entities.append(entity)

        logger.info(f"NER extracted {len(entities)} entities from scene {scene_id}")
        return entities

    def _map_spacy_type(self, spacy_label: str) -> Optional[EntityType]:
        """Map spaCy entity labels to our entity types."""
        mapping = {
            'PERSON': EntityType.CHARACTER,
            'GPE': EntityType.LOCATION,  # Geopolitical entity
            'LOC': EntityType.LOCATION,
            'FAC': EntityType.LOCATION,  # Facility
            'ORG': EntityType.ORGANIZATION,
            'EVENT': EntityType.EVENT,
            'PRODUCT': EntityType.OBJECT,
            'WORK_OF_ART': EntityType.OBJECT,
        }
        return mapping.get(spacy_label)

    def _create_entity_id(self, name: str) -> str:
        """Create normalized entity ID."""
        import re
        normalized = re.sub(r'[^a-z0-9\s]', '', name.lower())
        normalized = re.sub(r'\s+', '_', normalized.strip())
        return f"entity_{normalized}"
```

---

## Phase 3: Database Integration

### 3.1: Database Models

**File**: `backend/app/models/knowledge_graph.py`

```python
"""
SQLAlchemy models for knowledge graph persistence.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ProjectGraph(Base):
    """
    Stores serialized knowledge graph for each project.
    Main persistence mechanism for NetworkX graphs.
    """
    __tablename__ = "project_graphs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Serialized NetworkX graph (full graph as JSON)
    graph_data = Column(JSONB, nullable=False)

    # Metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_extracted_scene = Column(UUID(as_uuid=True), nullable=True)

    # Statistics
    entity_count = Column(Integer, default=0)
    relationship_count = Column(Integer, default=0)
    scene_count = Column(Integer, default=0)

    # Extraction stats
    total_extractions = Column(Integer, default=0)
    successful_extractions = Column(Integer, default=0)
    failed_extractions = Column(Integer, default=0)

    # Relationship to project
    project = relationship("Project", back_populates="knowledge_graph")


class ExtractionJob(Base):
    """
    Tracks entity/relationship extraction jobs.
    Useful for monitoring and debugging.
    """
    __tablename__ = "extraction_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    scene_id = Column(UUID(as_uuid=True), ForeignKey('manuscript_scenes.id', ondelete='CASCADE'), nullable=False)

    # Job info
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    extractor_type = Column(String(20), nullable=False)  # llm, ner, hybrid
    model_name = Column(String(50), nullable=True)  # claude-sonnet-4.5, spacy, etc.

    # Results
    entities_extracted = Column(Integer, default=0)
    relationships_extracted = Column(Integer, default=0)

    # Timing
    started_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Cost tracking (for LLM extraction)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
```

### 3.2: Migration Script

**File**: `backend/migrations/add_knowledge_graph_tables.sql`

```sql
-- Knowledge Graph Tables Migration
-- Creates tables for storing knowledge graphs and extraction jobs

-- Main graph storage table
CREATE TABLE IF NOT EXISTS project_graphs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Serialized graph data (NetworkX JSON format)
    graph_data JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_extracted_scene UUID,

    -- Statistics
    entity_count INTEGER DEFAULT 0,
    relationship_count INTEGER DEFAULT 0,
    scene_count INTEGER DEFAULT 0,

    -- Extraction tracking
    total_extractions INTEGER DEFAULT 0,
    successful_extractions INTEGER DEFAULT 0,
    failed_extractions INTEGER DEFAULT 0,

    -- One graph per project
    CONSTRAINT unique_graph_per_project UNIQUE (project_id)
);

CREATE INDEX idx_project_graphs_project_id ON project_graphs(project_id);
CREATE INDEX idx_project_graphs_last_updated ON project_graphs(last_updated);

-- Extraction jobs tracking
CREATE TABLE IF NOT EXISTS extraction_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scene_id UUID NOT NULL REFERENCES manuscript_scenes(id) ON DELETE CASCADE,

    -- Job details
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    extractor_type VARCHAR(20) NOT NULL CHECK (extractor_type IN ('llm', 'ner', 'hybrid')),
    model_name VARCHAR(50),

    -- Results
    entities_extracted INTEGER DEFAULT 0,
    relationships_extracted INTEGER DEFAULT 0,

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds FLOAT,

    -- Error tracking
    error_message TEXT,

    -- Cost tracking
    tokens_used INTEGER,
    cost FLOAT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_extraction_jobs_project_id ON extraction_jobs(project_id);
CREATE INDEX idx_extraction_jobs_scene_id ON extraction_jobs(scene_id);
CREATE INDEX idx_extraction_jobs_status ON extraction_jobs(status);
CREATE INDEX idx_extraction_jobs_created_at ON extraction_jobs(created_at DESC);

-- Comments
COMMENT ON TABLE project_graphs IS 'Stores knowledge graphs (NetworkX format) for each project';
COMMENT ON TABLE extraction_jobs IS 'Tracks entity/relationship extraction jobs with timing and cost data';

COMMENT ON COLUMN project_graphs.graph_data IS 'Serialized NetworkX graph in node-link JSON format';
COMMENT ON COLUMN extraction_jobs.extractor_type IS 'Type of extractor used: llm (Claude/GPT), ner (spaCy), or hybrid';
```

---

*This document continues in Part 2 with API endpoints, background jobs, frontend visualization, and complete integration instructions.*

**Total Length**: 30,000+ words across complete implementation
**Files to Create**: 25+ Python files, 10+ React components, API endpoints, tests
**Estimated Implementation**: Gold standard, production-ready system

Should I continue with Part 2 covering API layer, background jobs, frontend visualization, and deployment?
