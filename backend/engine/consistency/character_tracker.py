"""
Character State Tracker

Tracks character state evolution across scenes to detect inconsistencies.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict

from .models import (
    CharacterState,
    RelationshipState,
    ConsistencyIssue,
    IssueSeverity,
    IssueCategory
)


class CharacterStateTracker:
    """
    Tracks character states across scenes to detect evolution inconsistencies.

    Builds timelines of:
    - Character psychological states
    - Abilities and capabilities
    - Relationship dynamics
    - Story-specific attributes (addiction status, etc.)
    """

    def __init__(self):
        """Initialize character tracker."""
        self.character_timeline: Dict[str, List[CharacterState]] = defaultdict(list)
        self.relationship_timeline: Dict[str, List[RelationshipState]] = defaultdict(list)

        # Known characters (Volume 1 focus)
        self.known_characters = [
            "Mickey Bardot",
            "Noni",
            "Sadie",
            "Dr. Webb",
            "Ken",
            "Jillian",
            "Vance"
        ]

    def add_character_state(self, state: CharacterState):
        """
        Add a character state to the timeline.

        Args:
            state: CharacterState for a specific scene
        """
        self.character_timeline[state.character_name].append(state)

        # Sort by scene ID (assumes format like "1.3.2")
        self.character_timeline[state.character_name].sort(
            key=lambda s: self._scene_sort_key(s.scene_id)
        )

    def add_relationship_state(self, state: RelationshipState):
        """
        Add a relationship state to the timeline.

        Args:
            state: RelationshipState for a specific scene
        """
        key = state.relationship_key
        self.relationship_timeline[key].append(state)

        # Sort by scene ID
        self.relationship_timeline[key].sort(
            key=lambda s: self._scene_sort_key(s.scene_id)
        )

    def _scene_sort_key(self, scene_id: str) -> Tuple[int, ...]:
        """
        Convert scene ID to sortable tuple.

        Examples:
            "1.3.2" → (1, 3, 2)
            "1.15.1" → (1, 15, 1)
            "test-1" → (0, 0, 0)
        """
        try:
            parts = scene_id.split('.')
            return tuple(int(p) for p in parts)
        except (ValueError, AttributeError):
            return (0, 0, 0)

    def get_character_timeline(self, character_name: str) -> List[CharacterState]:
        """Get chronological timeline for a character."""
        return self.character_timeline.get(character_name, [])

    def get_relationship_timeline(self, char_a: str, char_b: str) -> List[RelationshipState]:
        """Get chronological timeline for a relationship."""
        chars = sorted([char_a, char_b])
        key = f"{chars[0]} ↔ {chars[1]}"
        return self.relationship_timeline.get(key, [])

    def check_character_consistency(self, character_name: str) -> List[ConsistencyIssue]:
        """
        Check a character's timeline for inconsistencies.

        Args:
            character_name: Character to check

        Returns:
            List of consistency issues found
        """
        issues = []
        timeline = self.get_character_timeline(character_name)

        if len(timeline) < 2:
            return issues  # Need at least 2 states to compare

        # Check for attribute inconsistencies
        issues.extend(self._check_attribute_progression(character_name, timeline))

        # Check for ability inconsistencies
        issues.extend(self._check_ability_consistency(character_name, timeline))

        # Check for psychological regression without cause
        issues.extend(self._check_psychological_coherence(character_name, timeline))

        return issues

    def _check_attribute_progression(self, character_name: str,
                                    timeline: List[CharacterState]) -> List[ConsistencyIssue]:
        """Check for illogical attribute changes (e.g., addiction recovery then relapse without cause)."""
        issues = []

        # Mickey-specific: Addiction tracking
        if character_name == "Mickey Bardot":
            sobriety_timeline = []

            for state in timeline:
                if 'sobriety_days' in state.attributes:
                    sobriety_timeline.append((
                        state.scene_id,
                        state.attributes['sobriety_days']
                    ))

            # Check for illogical sobriety counts
            for i in range(1, len(sobriety_timeline)):
                prev_scene, prev_days = sobriety_timeline[i-1]
                curr_scene, curr_days = sobriety_timeline[i]

                # If sobriety count decreased without reset to 0, that's suspicious
                if curr_days < prev_days and curr_days > 0:
                    issues.append(ConsistencyIssue(
                        category=IssueCategory.CHARACTER_STATE,
                        severity=IssueSeverity.MODERATE,
                        description=f"{character_name} Sobriety Count Inconsistency",
                        scenes_affected=[prev_scene, curr_scene],
                        problem_details=f"Scene {prev_scene} shows {prev_days} days sober, "
                                       f"but later scene {curr_scene} shows {curr_days} days sober. "
                                       f"Regression without narrative cause (expected reset to 0 or progression).",
                        recommendation=f"Verify timeline: either fix sobriety count progression or "
                                      f"add relapse scene between {prev_scene} and {curr_scene}"
                    ))

        # Noni-specific: Ability progression checks
        elif character_name == "Noni":
            ability_timeline = []

            for state in timeline:
                if 'morphic_resonance_range' in state.attributes:
                    ability_timeline.append((
                        state.scene_id,
                        state.attributes['morphic_resonance_range'],
                        state.story_phase
                    ))

            # Check for sudden ability jumps
            for i in range(1, len(ability_timeline)):
                prev_scene, prev_range, prev_phase = ability_timeline[i-1]
                curr_scene, curr_range, curr_phase = ability_timeline[i]

                # Convert range strings to numeric values for comparison
                range_values = {
                    "touch": 0,
                    "close": 1,
                    "medium": 2,
                    "far": 3
                }

                prev_val = range_values.get(prev_range, -1)
                curr_val = range_values.get(curr_range, -1)

                # Flag if ability jumps more than 1 level suddenly
                if curr_val > prev_val + 1:
                    issues.append(ConsistencyIssue(
                        category=IssueCategory.CHARACTER_STATE,
                        severity=IssueSeverity.MODERATE,
                        description=f"{character_name} Ability Jump Without Progression",
                        scenes_affected=[prev_scene, curr_scene],
                        problem_details=f"Scene {prev_scene} shows morphic resonance range '{prev_range}', "
                                       f"but scene {curr_scene} shows '{curr_range}'. "
                                       f"This is a significant jump that may need justification.",
                        recommendation=f"Verify ability progression is earned/explained, or add intermediate "
                                      f"scene showing growth between {prev_scene} and {curr_scene}"
                    ))

        return issues

    def _check_ability_consistency(self, character_name: str,
                                   timeline: List[CharacterState]) -> List[ConsistencyIssue]:
        """Check for characters losing abilities without explanation."""
        issues = []

        # Track which abilities appear in each scene
        ability_history = []

        for state in timeline:
            ability_history.append((state.scene_id, set(state.abilities)))

        # Check for lost abilities
        for i in range(1, len(ability_history)):
            prev_scene, prev_abilities = ability_history[i-1]
            curr_scene, curr_abilities = ability_history[i]

            lost_abilities = prev_abilities - curr_abilities

            if lost_abilities:
                issues.append(ConsistencyIssue(
                    category=IssueCategory.CHARACTER_STATE,
                    severity=IssueSeverity.MODERATE,
                    description=f"{character_name} Lost Abilities Without Explanation",
                    scenes_affected=[prev_scene, curr_scene],
                    problem_details=f"Scene {prev_scene} shows abilities: {list(lost_abilities)}, "
                                   f"but these are missing in later scene {curr_scene} without explanation.",
                    recommendation=f"Verify if {character_name} should still have these abilities in {curr_scene}, "
                                  f"or add narrative explanation for why abilities were lost"
                ))

        return issues

    def _check_psychological_coherence(self, character_name: str,
                                      timeline: List[CharacterState]) -> List[ConsistencyIssue]:
        """Check for sudden psychological shifts without cause."""
        issues = []

        # This is more heuristic - flag major emotional state changes
        emotional_keywords = {
            'positive': ['hopeful', 'optimistic', 'happy', 'content', 'peaceful'],
            'negative': ['desperate', 'hopeless', 'depressed', 'cynical', 'angry'],
            'neutral': ['focused', 'analytical', 'calm', 'professional']
        }

        def categorize_emotion(emotional_state: str) -> str:
            """Categorize emotional state."""
            state_lower = emotional_state.lower()
            for category, keywords in emotional_keywords.items():
                if any(kw in state_lower for kw in keywords):
                    return category
            return 'unknown'

        emotional_timeline = []
        for state in timeline:
            if state.emotional_state:
                category = categorize_emotion(state.emotional_state)
                emotional_timeline.append((state.scene_id, category, state.emotional_state))

        # Flag sudden positive to negative or vice versa without intermediate
        for i in range(1, len(emotional_timeline)):
            prev_scene, prev_category, prev_state = emotional_timeline[i-1]
            curr_scene, curr_category, curr_state = emotional_timeline[i]

            # Check for dramatic shift
            if (prev_category == 'positive' and curr_category == 'negative') or \
               (prev_category == 'negative' and curr_category == 'positive'):

                issues.append(ConsistencyIssue(
                    category=IssueCategory.CHARACTER_STATE,
                    severity=IssueSeverity.MINOR,
                    description=f"{character_name} Sudden Emotional Shift",
                    scenes_affected=[prev_scene, curr_scene],
                    problem_details=f"Scene {prev_scene} shows {character_name} as '{prev_state}', "
                                   f"but scene {curr_scene} shows '{curr_state}'. "
                                   f"Verify this dramatic shift is narratively justified.",
                    recommendation=f"Review emotional progression between {prev_scene} and {curr_scene} "
                                  f"to ensure shift is earned/explained"
                ))

        return issues

    def check_relationship_consistency(self, char_a: str, char_b: str) -> List[ConsistencyIssue]:
        """
        Check relationship timeline for inconsistencies.

        Args:
            char_a: First character
            char_b: Second character

        Returns:
            List of consistency issues found
        """
        issues = []
        timeline = self.get_relationship_timeline(char_a, char_b)

        if len(timeline) < 2:
            return issues

        # Check for sudden intimacy jumps
        issues.extend(self._check_intimacy_progression(char_a, char_b, timeline))

        # Check for trust level reversals
        issues.extend(self._check_trust_consistency(char_a, char_b, timeline))

        return issues

    def _check_intimacy_progression(self, char_a: str, char_b: str,
                                   timeline: List[RelationshipState]) -> List[ConsistencyIssue]:
        """Check for sudden relationship intimacy changes."""
        issues = []

        # Track trust level progression
        trust_levels = {
            'none': 0,
            'low': 1,
            'medium': 2,
            'high': 3,
            'complete': 4
        }

        trust_timeline = []
        for state in timeline:
            trust_val = trust_levels.get(state.trust_level.lower(), -1)
            trust_timeline.append((state.scene_id, trust_val, state.trust_level))

        # Flag sudden trust jumps (more than 1 level)
        for i in range(1, len(trust_timeline)):
            prev_scene, prev_val, prev_trust = trust_timeline[i-1]
            curr_scene, curr_val, curr_trust = trust_timeline[i]

            if curr_val > prev_val + 1:
                issues.append(ConsistencyIssue(
                    category=IssueCategory.RELATIONSHIP,
                    severity=IssueSeverity.MODERATE,
                    description=f"{char_a}/{char_b} Sudden Intimacy Jump",
                    scenes_affected=[prev_scene, curr_scene],
                    problem_details=f"Scene {prev_scene} shows trust level '{prev_trust}', "
                                   f"but scene {curr_scene} shows '{curr_trust}'. "
                                   f"This jump may need intermediate development.",
                    recommendation=f"Add scene(s) showing relationship development between "
                                  f"{prev_scene} and {curr_scene}, or reduce trust level in {curr_scene}"
                ))

        return issues

    def _check_trust_consistency(self, char_a: str, char_b: str,
                                timeline: List[RelationshipState]) -> List[ConsistencyIssue]:
        """Check for trust reversals without cause."""
        issues = []

        # Flag any trust level decreases (should have narrative cause)
        trust_levels = {
            'none': 0,
            'low': 1,
            'medium': 2,
            'high': 3,
            'complete': 4
        }

        for i in range(1, len(timeline)):
            prev = timeline[i-1]
            curr = timeline[i]

            prev_val = trust_levels.get(prev.trust_level.lower(), -1)
            curr_val = trust_levels.get(curr.trust_level.lower(), -1)

            # Trust decrease should be noted
            if curr_val < prev_val:
                issues.append(ConsistencyIssue(
                    category=IssueCategory.RELATIONSHIP,
                    severity=IssueSeverity.MINOR,
                    description=f"{char_a}/{char_b} Trust Reversal",
                    scenes_affected=[prev.scene_id, curr.scene_id],
                    problem_details=f"Trust decreased from '{prev.trust_level}' to '{curr.trust_level}'. "
                                   f"Verify this is intentional and has narrative cause.",
                    recommendation=f"Review scenes between {prev.scene_id} and {curr.scene_id} "
                                  f"to ensure trust decrease is justified"
                ))

        return issues

    def generate_character_timeline_markdown(self, character_name: str) -> str:
        """Generate markdown table of character state timeline."""
        timeline = self.get_character_timeline(character_name)

        if not timeline:
            return f"No timeline data for {character_name}"

        lines = [
            f"### {character_name} Timeline",
            "",
            "| Scene | Phase | Emotional State | Abilities | Key Attributes |",
            "|-------|-------|-----------------|-----------|----------------|"
        ]

        for state in timeline:
            abilities_str = ", ".join(state.abilities) if state.abilities else "-"
            attrs_str = ", ".join(f"{k}={v}" for k, v in list(state.attributes.items())[:3])
            if not attrs_str:
                attrs_str = "-"

            lines.append(
                f"| {state.scene_id} | {state.story_phase} | "
                f"{state.emotional_state or '-'} | {abilities_str} | {attrs_str} |"
            )

        return '\n'.join(lines)

    def generate_relationship_timeline_markdown(self, char_a: str, char_b: str) -> str:
        """Generate markdown table of relationship timeline."""
        timeline = self.get_relationship_timeline(char_a, char_b)

        if not timeline:
            return f"No timeline data for {char_a} ↔ {char_b}"

        lines = [
            f"### {char_a} ↔ {char_b} Relationship Timeline",
            "",
            "| Scene | Phase | Type | Dynamic | Trust Level | Notes |",
            "|-------|-------|------|---------|-------------|-------|"
        ]

        for state in timeline:
            lines.append(
                f"| {state.scene_id} | {state.story_phase} | "
                f"{state.relationship_type} | {state.dynamic} | "
                f"{state.trust_level} | {state.notes[:50] if state.notes else '-'} |"
            )

        return '\n'.join(lines)
