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
