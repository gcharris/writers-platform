"""
Knowledge Graph service package.
Provides entity extraction, relationship detection, and graph analysis.
"""

from .models import Entity, Relationship, EntityType, RelationType, GraphMetadata
from .graph_service import KnowledgeGraphService

__all__ = [
    'Entity',
    'Relationship',
    'EntityType',
    'RelationType',
    'GraphMetadata',
    'KnowledgeGraphService',
]
