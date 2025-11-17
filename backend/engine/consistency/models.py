"""
Data models for consistency checking.

Defines structured reports for consistency analysis results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class IssueSeverity(Enum):
    """Severity levels for consistency issues."""
    CRITICAL = "critical"  # Must fix before publication
    MODERATE = "moderate"  # Should fix, impacts quality
    MINOR = "minor"        # Nice to fix, minor polish


class IssueCategory(Enum):
    """Categories of consistency issues."""
    CHARACTER_STATE = "character_state"
    RELATIONSHIP = "relationship"
    WORLDBUILDING = "worldbuilding"
    TIMELINE = "timeline"
    BACKSTORY = "backstory"
    VOICE = "voice"
    MECHANICS = "mechanics"


@dataclass
class ConsistencyIssue:
    """A single consistency issue found in a scene."""

    category: IssueCategory
    severity: IssueSeverity
    description: str
    scenes_affected: List[str]
    problem_details: str
    canonical_reference: Optional[str] = None  # From NotebookLM
    recommendation: str = ""
    file_paths: List[str] = field(default_factory=list)
    line_numbers: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'category': self.category.value,
            'severity': self.severity.value,
            'description': self.description,
            'scenes_affected': self.scenes_affected,
            'problem_details': self.problem_details,
            'canonical_reference': self.canonical_reference,
            'recommendation': self.recommendation,
            'file_paths': self.file_paths,
            'line_numbers': self.line_numbers
        }

    def to_markdown(self) -> str:
        """Convert to markdown report section."""
        lines = [
            f"### {self.description}",
            f"**Scenes affected:** {', '.join(self.scenes_affected)}",
            f"**Category:** {self.category.value.replace('_', ' ').title()}",
            f"**Severity:** {self.severity.value.upper()}",
            f"**Problem:** {self.problem_details}",
        ]

        if self.canonical_reference:
            lines.append(f"**Canonical Reference:** {self.canonical_reference}")

        if self.recommendation:
            lines.append(f"**Recommendation:** {self.recommendation}")

        if self.file_paths:
            lines.append("**Files:**")
            for path in self.file_paths:
                lines.append(f"  - `{path}`")

        return '\n'.join(lines)


@dataclass
class ConsistencyReport:
    """Consistency report for a single scene."""

    scene_id: str
    scene_path: str
    story_phase: int
    checked_at: datetime = field(default_factory=datetime.now)

    issues: List[ConsistencyIssue] = field(default_factory=list)

    character_states: Dict[str, 'CharacterState'] = field(default_factory=dict)
    relationship_states: Dict[str, 'RelationshipState'] = field(default_factory=dict)

    @property
    def critical_issues(self) -> List[ConsistencyIssue]:
        """Get critical issues only."""
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]

    @property
    def moderate_issues(self) -> List[ConsistencyIssue]:
        """Get moderate issues only."""
        return [i for i in self.issues if i.severity == IssueSeverity.MODERATE]

    @property
    def minor_issues(self) -> List[ConsistencyIssue]:
        """Get minor issues only."""
        return [i for i in self.issues if i.severity == IssueSeverity.MINOR]

    @property
    def has_issues(self) -> bool:
        """Check if scene has any issues."""
        return len(self.issues) > 0

    @property
    def consistency_score(self) -> int:
        """Calculate consistency score (0-100)."""
        if not self.issues:
            return 100

        # Deduct points based on severity
        deductions = 0
        deductions += len(self.critical_issues) * 15
        deductions += len(self.moderate_issues) * 5
        deductions += len(self.minor_issues) * 2

        return max(0, 100 - deductions)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'scene_id': self.scene_id,
            'scene_path': self.scene_path,
            'story_phase': self.story_phase,
            'checked_at': self.checked_at.isoformat(),
            'consistency_score': self.consistency_score,
            'issue_counts': {
                'critical': len(self.critical_issues),
                'moderate': len(self.moderate_issues),
                'minor': len(self.minor_issues),
                'total': len(self.issues)
            },
            'issues': [issue.to_dict() for issue in self.issues],
            'character_states': {k: v.to_dict() for k, v in self.character_states.items()},
            'relationship_states': {k: v.to_dict() for k, v in self.relationship_states.items()}
        }


@dataclass
class VolumeConsistencyReport:
    """Consistency report for an entire volume."""

    volume_name: str
    volume_path: str
    checked_at: datetime = field(default_factory=datetime.now)

    scenes_checked: int = 0
    scene_reports: List[ConsistencyReport] = field(default_factory=list)

    critical_issues: List[ConsistencyIssue] = field(default_factory=list)
    moderate_issues: List[ConsistencyIssue] = field(default_factory=list)
    minor_issues: List[ConsistencyIssue] = field(default_factory=list)

    character_timelines: Dict[str, List['CharacterState']] = field(default_factory=dict)
    relationship_timelines: Dict[str, List['RelationshipState']] = field(default_factory=dict)

    @property
    def total_issues(self) -> int:
        """Total number of issues found."""
        return len(self.critical_issues) + len(self.moderate_issues) + len(self.minor_issues)

    @property
    def consistency_score(self) -> int:
        """Overall consistency score (0-100)."""
        if not self.scene_reports:
            return 0

        # Average of all scene scores
        total = sum(report.consistency_score for report in self.scene_reports)
        return int(total / len(self.scene_reports))

    @property
    def grade(self) -> str:
        """Letter grade for consistency."""
        score = self.consistency_score
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 87:
            return "A-"
        elif score >= 83:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 77:
            return "B-"
        elif score >= 73:
            return "C+"
        elif score >= 70:
            return "C"
        else:
            return "F"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'volume_name': self.volume_name,
            'volume_path': self.volume_path,
            'checked_at': self.checked_at.isoformat(),
            'scenes_checked': self.scenes_checked,
            'consistency_score': self.consistency_score,
            'grade': self.grade,
            'issue_counts': {
                'critical': len(self.critical_issues),
                'moderate': len(self.moderate_issues),
                'minor': len(self.minor_issues),
                'total': self.total_issues
            },
            'scene_reports': [report.to_dict() for report in self.scene_reports],
            'critical_issues': [issue.to_dict() for issue in self.critical_issues],
            'moderate_issues': [issue.to_dict() for issue in self.moderate_issues],
            'minor_issues': [issue.to_dict() for issue in self.minor_issues]
        }

    def to_markdown(self) -> str:
        """Generate comprehensive markdown report."""
        lines = [
            f"# {self.volume_name} Consistency Report",
            f"Generated: {self.checked_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            "",
            f"- **Scenes checked:** {self.scenes_checked}",
            f"- **Critical issues:** {len(self.critical_issues)}",
            f"- **Moderate issues:** {len(self.moderate_issues)}",
            f"- **Minor issues:** {len(self.minor_issues)}",
            f"- **Overall consistency:** {self.grade} ({self.consistency_score}/100)",
            ""
        ]

        # Critical issues section
        if self.critical_issues:
            lines.extend([
                "## Critical Issues (Must Fix)",
                "",
                "*These issues must be resolved before publication.*",
                ""
            ])

            for i, issue in enumerate(self.critical_issues, 1):
                lines.append(f"### Issue {i}: {issue.description}")
                lines.append(issue.to_markdown())
                lines.append("")

        # Moderate issues section
        if self.moderate_issues:
            lines.extend([
                "## Moderate Issues (Should Fix)",
                "",
                "*These issues impact quality and should be addressed.*",
                ""
            ])

            for i, issue in enumerate(self.moderate_issues, 1):
                lines.append(f"### Issue {i}: {issue.description}")
                lines.append(issue.to_markdown())
                lines.append("")

        # Minor issues section
        if self.minor_issues:
            lines.extend([
                "## Minor Issues (Nice to Fix)",
                "",
                "*These are polish items that can be addressed as time permits.*",
                ""
            ])

            # Only show first 10 minor issues to avoid overwhelming report
            for i, issue in enumerate(self.minor_issues[:10], 1):
                lines.append(f"### Issue {i}: {issue.description}")
                lines.append(issue.to_markdown())
                lines.append("")

            if len(self.minor_issues) > 10:
                lines.append(f"*... and {len(self.minor_issues) - 10} more minor issues*")
                lines.append("")

        # Recommendations section
        lines.extend([
            "## Recommendations by Priority",
            "",
            "### Immediate (Critical):",
        ])

        if self.critical_issues:
            for i, issue in enumerate(self.critical_issues, 1):
                lines.append(f"{i}. {issue.recommendation}")
        else:
            lines.append("✅ No critical issues found!")

        lines.extend([
            "",
            "### Short-term (Moderate):"
        ])

        if self.moderate_issues[:5]:  # Top 5
            for i, issue in enumerate(self.moderate_issues[:5], 1):
                lines.append(f"{i}. {issue.recommendation}")
        else:
            lines.append("✅ No moderate issues found!")

        lines.extend([
            "",
            "### Long-term (Minor):"
        ])

        if self.minor_issues[:5]:  # Top 5
            for i, issue in enumerate(self.minor_issues[:5], 1):
                lines.append(f"{i}. {issue.recommendation}")
        else:
            lines.append("✅ No minor issues found!")

        # Files to review section
        lines.extend([
            "",
            "## Files to Review",
            "",
            "Priority order for manual review:",
            ""
        ])

        # Collect all files with critical/moderate issues
        priority_files = []
        for issue in self.critical_issues + self.moderate_issues:
            for file_path in issue.file_paths:
                if file_path not in [f[1] for f in priority_files]:
                    severity_label = "CRITICAL" if issue.severity == IssueSeverity.CRITICAL else "MODERATE"
                    priority_files.append((issue.severity, file_path, issue.description, severity_label))

        # Sort by severity
        priority_files.sort(key=lambda x: 0 if x[0] == IssueSeverity.CRITICAL else 1)

        for i, (_, file_path, desc, label) in enumerate(priority_files[:20], 1):  # Top 20
            lines.append(f"{i}. `{file_path}` - {label}: {desc}")

        if len(priority_files) > 20:
            lines.append(f"... and {len(priority_files) - 20} more files")

        return '\n'.join(lines)


@dataclass
class CharacterState:
    """Character state at a specific point in the story."""

    character_name: str
    scene_id: str
    story_phase: int

    # Psychological state
    psychological_notes: str = ""
    emotional_state: str = ""

    # Capabilities
    abilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    # Specific attributes (vary by character)
    attributes: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'character_name': self.character_name,
            'scene_id': self.scene_id,
            'story_phase': self.story_phase,
            'psychological_notes': self.psychological_notes,
            'emotional_state': self.emotional_state,
            'abilities': self.abilities,
            'limitations': self.limitations,
            'attributes': self.attributes
        }


@dataclass
class RelationshipState:
    """Relationship state between two characters at a specific point."""

    character_a: str
    character_b: str
    scene_id: str
    story_phase: int

    relationship_type: str  # "romantic", "professional", "familial", etc.
    dynamic: str  # Description of power dynamic, intimacy level, etc.
    trust_level: str  # "high", "medium", "low", "conflicted"

    notes: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'character_a': self.character_a,
            'character_b': self.character_b,
            'scene_id': self.scene_id,
            'story_phase': self.story_phase,
            'relationship_type': self.relationship_type,
            'dynamic': self.dynamic,
            'trust_level': self.trust_level,
            'notes': self.notes
        }

    @property
    def relationship_key(self) -> str:
        """Get canonical key for this relationship (alphabetical order)."""
        chars = sorted([self.character_a, self.character_b])
        return f"{chars[0]} ↔ {chars[1]}"
