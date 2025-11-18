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

    def delete_entity(self, entity_id: str) -> bool:
        """Delete entity and all its relationships."""
        if entity_id not in self._entity_index:
            return False

        # Remove from graph
        self.graph.remove_node(entity_id)

        # Remove from index
        del self._entity_index[entity_id]

        # Remove relationships
        to_remove = [
            key for key in self._relationship_index.keys()
            if key[0] == entity_id or key[1] == entity_id
        ]
        for key in to_remove:
            del self._relationship_index[key]

        # Update metadata
        self.metadata.entity_count -= 1
        self.metadata.relationship_count -= len(to_remove)
        self.metadata.last_updated = datetime.now()

        logger.info(f"Deleted entity: {entity_id}")
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

    def delete_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType
    ) -> bool:
        """Delete a specific relationship."""
        key = (source_id, target_id, relation_type.value)
        if key not in self._relationship_index:
            return False

        # Remove from graph
        self.graph.remove_edge(source_id, target_id, key=relation_type.value)

        # Remove from index
        del self._relationship_index[key]

        # Update metadata
        self.metadata.relationship_count -= 1
        self.metadata.last_updated = datetime.now()

        logger.info(f"Deleted relationship: {source_id} --[{relation_type.value}]--> {target_id}")
        return True

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
        except nx.NodeNotFound:
            return None

    def get_central_entities(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get most central entities using PageRank.

        Returns:
            List of (entity_id, centrality_score) tuples
        """
        if len(self.graph.nodes) == 0:
            return []

        pagerank = nx.pagerank(self.graph)
        sorted_entities = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        return sorted_entities[:top_n]

    def get_communities(self) -> List[Set[str]]:
        """Detect entity communities using Louvain method."""
        if len(self.graph.nodes) == 0:
            return []

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

    def get_stats(self) -> Dict[str, Any]:
        """Get overall graph statistics."""
        return {
            'entities': self.metadata.entity_count,
            'relationships': self.metadata.relationship_count,
            'scenes': self.metadata.scene_count,
            'density': nx.density(self.graph) if len(self.graph.nodes) > 1 else 0,
            'avg_degree': sum(dict(self.graph.degree()).values()) / max(len(self.graph.nodes), 1),
        }
