"""
Volume Consistency Checking Framework

Automated consistency verification for The Explants trilogy to catch:
- Character state inconsistencies
- Relationship dynamic contradictions
- Worldbuilding mechanics violations
- Timeline coherence issues
- Backstory contradictions

Integrates with NotebookLM for canonical reference verification.
"""

from .models import (
    ConsistencyIssue,
    ConsistencyReport,
    VolumeConsistencyReport,
    CharacterState,
    RelationshipState
)

from .character_tracker import CharacterStateTracker

from .volume1_checker import Volume1ConsistencyChecker

__all__ = [
    'ConsistencyIssue',
    'ConsistencyReport',
    'VolumeConsistencyReport',
    'CharacterState',
    'RelationshipState',
    'CharacterStateTracker',
    'Volume1ConsistencyChecker'
]
