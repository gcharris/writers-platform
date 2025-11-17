"""Dual Voice Profile System for Beginner Mode.

StarterVoiceProfile: Extracted from personal writing (emails, social media, diary)
NovelVoiceProfile: Extracted from fiction writing (2,500+ words)

This enables beginners to start with personal voice, then upgrade to fiction voice.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from factory.core.voice_extractor import VoiceProfile, MetaphorDomain, AntiPattern, QualityCriteria


@dataclass
class StarterVoiceProfile(VoiceProfile):
    """Voice profile extracted from personal writing (emails, social media, diary).

    Characteristics:
    - Lower confidence ("medium" max, never "high")
    - Based on casual writing, not fiction
    - Includes upgrade threshold (default 2,500 words)
    - Contains warnings about limitations
    """

    # Starter-specific fields
    is_starter: bool = True
    confidence_level: str = "medium"  # "low" or "medium", never "high"
    source_types: List[str] = field(default_factory=list)  # ["email", "social_media", "diary"]
    upgrade_threshold: int = 2500  # Words of fiction needed to upgrade
    total_source_words: int = 0  # Total words of personal writing analyzed
    warnings: List[str] = field(default_factory=lambda: [
        "Based on casual writing, not fiction",
        "May differ from your fiction voice",
        "Upgrade at 2,500 words for better accuracy"
    ])

    def __init__(
        self,
        voice_name: str,
        genre: str,
        primary_characteristics: List[str],
        sentence_structure: Dict[str, Any],
        vocabulary: Dict[str, Any],
        pov_style: Dict[str, Any],
        metaphor_domains: Optional[Dict[str, MetaphorDomain]] = None,
        anti_patterns: Optional[List[AntiPattern]] = None,
        quality_criteria: Optional[QualityCriteria] = None,
        voice_consistency_notes: Optional[List[str]] = None,
        # Starter-specific parameters
        source_types: Optional[List[str]] = None,
        total_source_words: int = 0,
        upgrade_threshold: int = 2500,
        confidence_level: str = "medium"
    ):
        """Initialize starter voice profile.

        Args:
            voice_name: Descriptive name for this voice (e.g., "Casual Direct")
            genre: Target genre for the novel
            primary_characteristics: List of key voice traits
            sentence_structure: Dict with sentence patterns
            vocabulary: Dict with vocab characteristics
            pov_style: Dict with POV characteristics
            metaphor_domains: Optional dict of metaphor domains
            anti_patterns: Optional list of patterns to avoid
            quality_criteria: Optional scoring criteria
            voice_consistency_notes: Optional consistency notes
            source_types: Types of personal writing analyzed
            total_source_words: Total words of personal writing
            upgrade_threshold: Words needed to upgrade (default 2500)
            confidence_level: Confidence level ("low" or "medium")
        """
        # Initialize parent VoiceProfile
        super().__init__(
            voice_name=voice_name,
            genre=genre,
            primary_characteristics=primary_characteristics,
            sentence_structure=sentence_structure,
            vocabulary=vocabulary,
            pov_style=pov_style,
            metaphor_domains=metaphor_domains,
            anti_patterns=anti_patterns,
            quality_criteria=quality_criteria,
            voice_consistency_notes=voice_consistency_notes
        )

        # Starter-specific fields
        self.is_starter = True
        self.confidence_level = confidence_level if confidence_level in ["low", "medium"] else "medium"
        self.source_types = source_types or []
        self.total_source_words = total_source_words
        self.upgrade_threshold = upgrade_threshold
        self.warnings = [
            "Based on casual writing, not fiction",
            "May differ from your fiction voice",
            f"Upgrade at {upgrade_threshold} words for better accuracy"
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            "is_starter": self.is_starter,
            "confidence_level": self.confidence_level,
            "source_types": self.source_types,
            "total_source_words": self.total_source_words,
            "upgrade_threshold": self.upgrade_threshold,
            "warnings": self.warnings
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StarterVoiceProfile':
        """Create StarterVoiceProfile from dictionary."""
        # Extract metaphor domains if present
        metaphor_domains = {}
        if "metaphor_domains" in data:
            for name, md in data["metaphor_domains"].items():
                metaphor_domains[name] = MetaphorDomain(
                    max_percentage=md.get("max_percentage", 20),
                    keywords=md.get("keywords", []),
                    examples=md.get("examples", [])
                )

        # Extract anti-patterns if present
        anti_patterns = []
        if "anti_patterns" in data:
            for ap in data["anti_patterns"]:
                anti_patterns.append(AntiPattern(
                    pattern_id=ap.get("pattern_id", ""),
                    name=ap.get("name", ""),
                    description=ap.get("description", ""),
                    why_avoid=ap.get("why_avoid", ""),
                    detection_method=ap.get("detection_method", ""),
                    severity=ap.get("severity", "medium"),
                    examples=ap.get("examples", []),
                    regex=ap.get("regex"),
                    keywords=ap.get("keywords", [])
                ))

        # Extract quality criteria if present
        quality_criteria = None
        if "quality_criteria" in data and data["quality_criteria"]:
            quality_criteria = QualityCriteria.from_dict(data["quality_criteria"])

        return cls(
            voice_name=data.get("voice_name", "Unknown Voice"),
            genre=data.get("genre", "literary"),
            primary_characteristics=data.get("primary_characteristics", []),
            sentence_structure=data.get("sentence_structure", {}),
            vocabulary=data.get("vocabulary", {}),
            pov_style=data.get("pov_style", {}),
            metaphor_domains=metaphor_domains,
            anti_patterns=anti_patterns,
            quality_criteria=quality_criteria,
            voice_consistency_notes=data.get("voice_consistency_notes", []),
            source_types=data.get("source_types", []),
            total_source_words=data.get("total_source_words", 0),
            upgrade_threshold=data.get("upgrade_threshold", 2500),
            confidence_level=data.get("confidence_level", "medium")
        )


@dataclass
class NovelVoiceProfile(VoiceProfile):
    """Voice profile extracted from fiction writing.

    Characteristics:
    - Higher confidence (can be "high")
    - Based on actual novel prose
    - Tracks fiction word count
    - May include comparison to previous starter voice
    """

    # Novel-specific fields
    is_starter: bool = False
    confidence_level: str = "high"  # Can be "medium" or "high"
    fiction_word_count: int = 0  # Words of fiction analyzed
    created_from_upgrade: bool = False  # True if upgraded from starter
    previous_starter: Optional[StarterVoiceProfile] = None  # Previous starter voice if upgraded
    voice_evolution: Optional[Dict[str, Any]] = None  # Comparison to starter voice
    upgrade_date: Optional[str] = None  # ISO timestamp of upgrade

    def __init__(
        self,
        voice_name: str,
        genre: str,
        primary_characteristics: List[str],
        sentence_structure: Dict[str, Any],
        vocabulary: Dict[str, Any],
        pov_style: Dict[str, Any],
        metaphor_domains: Optional[Dict[str, MetaphorDomain]] = None,
        anti_patterns: Optional[List[AntiPattern]] = None,
        quality_criteria: Optional[QualityCriteria] = None,
        voice_consistency_notes: Optional[List[str]] = None,
        # Novel-specific parameters
        fiction_word_count: int = 0,
        confidence_level: str = "high",
        created_from_upgrade: bool = False,
        previous_starter: Optional[StarterVoiceProfile] = None,
        voice_evolution: Optional[Dict[str, Any]] = None
    ):
        """Initialize novel voice profile.

        Args:
            voice_name: Descriptive name for this voice
            genre: Genre of the novel
            primary_characteristics: List of key voice traits
            sentence_structure: Dict with sentence patterns
            vocabulary: Dict with vocab characteristics
            pov_style: Dict with POV characteristics
            metaphor_domains: Optional dict of metaphor domains
            anti_patterns: Optional list of patterns to avoid
            quality_criteria: Optional scoring criteria
            voice_consistency_notes: Optional consistency notes
            fiction_word_count: Words of fiction analyzed
            confidence_level: Confidence level ("medium" or "high")
            created_from_upgrade: True if upgraded from starter
            previous_starter: Previous starter voice profile
            voice_evolution: Dict describing voice changes
        """
        # Initialize parent VoiceProfile
        super().__init__(
            voice_name=voice_name,
            genre=genre,
            primary_characteristics=primary_characteristics,
            sentence_structure=sentence_structure,
            vocabulary=vocabulary,
            pov_style=pov_style,
            metaphor_domains=metaphor_domains,
            anti_patterns=anti_patterns,
            quality_criteria=quality_criteria,
            voice_consistency_notes=voice_consistency_notes
        )

        # Novel-specific fields
        self.is_starter = False
        self.confidence_level = confidence_level
        self.fiction_word_count = fiction_word_count
        self.created_from_upgrade = created_from_upgrade
        self.previous_starter = previous_starter
        self.voice_evolution = voice_evolution
        self.upgrade_date = datetime.now().isoformat() if created_from_upgrade else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            "is_starter": self.is_starter,
            "confidence_level": self.confidence_level,
            "fiction_word_count": self.fiction_word_count,
            "created_from_upgrade": self.created_from_upgrade,
            "voice_evolution": self.voice_evolution,
            "upgrade_date": self.upgrade_date
        })

        # Include previous starter if available (but not full object, just summary)
        if self.previous_starter:
            base_dict["previous_starter_summary"] = {
                "voice_name": self.previous_starter.voice_name,
                "source_types": self.previous_starter.source_types,
                "total_source_words": self.previous_starter.total_source_words
            }

        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NovelVoiceProfile':
        """Create NovelVoiceProfile from dictionary."""
        # Extract metaphor domains if present
        metaphor_domains = {}
        if "metaphor_domains" in data:
            for name, md in data["metaphor_domains"].items():
                metaphor_domains[name] = MetaphorDomain(
                    max_percentage=md.get("max_percentage", 20),
                    keywords=md.get("keywords", []),
                    examples=md.get("examples", [])
                )

        # Extract anti-patterns if present
        anti_patterns = []
        if "anti_patterns" in data:
            for ap in data["anti_patterns"]:
                anti_patterns.append(AntiPattern(
                    pattern_id=ap.get("pattern_id", ""),
                    name=ap.get("name", ""),
                    description=ap.get("description", ""),
                    why_avoid=ap.get("why_avoid", ""),
                    detection_method=ap.get("detection_method", ""),
                    severity=ap.get("severity", "medium"),
                    examples=ap.get("examples", []),
                    regex=ap.get("regex"),
                    keywords=ap.get("keywords", [])
                ))

        # Extract quality criteria if present
        quality_criteria = None
        if "quality_criteria" in data and data["quality_criteria"]:
            quality_criteria = QualityCriteria.from_dict(data["quality_criteria"])

        return cls(
            voice_name=data.get("voice_name", "Unknown Voice"),
            genre=data.get("genre", "literary"),
            primary_characteristics=data.get("primary_characteristics", []),
            sentence_structure=data.get("sentence_structure", {}),
            vocabulary=data.get("vocabulary", {}),
            pov_style=data.get("pov_style", {}),
            metaphor_domains=metaphor_domains,
            anti_patterns=anti_patterns,
            quality_criteria=quality_criteria,
            voice_consistency_notes=data.get("voice_consistency_notes", []),
            fiction_word_count=data.get("fiction_word_count", 0),
            confidence_level=data.get("confidence_level", "high"),
            created_from_upgrade=data.get("created_from_upgrade", False),
            previous_starter=None,  # Don't reconstruct full object
            voice_evolution=data.get("voice_evolution")
        )


def compare_voices(
    starter: StarterVoiceProfile,
    novel: NovelVoiceProfile
) -> Dict[str, Any]:
    """Compare starter and novel voice profiles to show evolution.

    Args:
        starter: The original starter voice profile
        novel: The new novel voice profile

    Returns:
        Dictionary describing voice evolution with insights
    """
    evolution = {
        "sentence_length_change": _compare_sentence_length(starter, novel),
        "metaphor_change": _compare_metaphors(starter, novel),
        "formality_shift": _compare_formality(starter, novel),
        "pov_depth_change": _compare_pov_depth(starter, novel),
        "improvements": [],
        "summary": ""
    }

    # Generate improvement insights
    improvements = []

    # Check sentence structure evolution
    if "longer" in evolution["sentence_length_change"].lower():
        improvements.append("More varied sentence structure in fiction")

    # Check metaphor evolution
    if "increase" in evolution["metaphor_change"].lower():
        improvements.append("Richer metaphor usage in fiction")

    # Check formality shift
    if "literary" in evolution["formality_shift"].lower():
        improvements.append("More literary voice in fiction")

    # Check POV depth
    if "deeper" in evolution["pov_depth_change"].lower():
        improvements.append("Deeper POV immersion in fiction")

    evolution["improvements"] = improvements

    # Generate summary
    evolution["summary"] = (
        f"Your fiction voice has evolved from '{starter.voice_name}' "
        f"(based on {', '.join(starter.source_types)}) to '{novel.voice_name}'. "
        f"You've developed a distinct fiction voice!"
    )

    return evolution


def _compare_sentence_length(starter: StarterVoiceProfile, novel: NovelVoiceProfile) -> str:
    """Compare average sentence lengths."""
    starter_length = starter.sentence_structure.get("typical_length", "12 words")
    novel_length = novel.sentence_structure.get("typical_length", "18 words")

    # Extract numeric values
    try:
        starter_num = int(''.join(filter(str.isdigit, str(starter_length))))
        novel_num = int(''.join(filter(str.isdigit, str(novel_length))))
        diff = novel_num - starter_num

        if diff > 0:
            return f"+{diff} words average (longer, more varied)"
        elif diff < 0:
            return f"{diff} words average (tighter, more compressed)"
        else:
            return "Similar sentence length"
    except (ValueError, TypeError):
        return f"{starter_length} → {novel_length}"


def _compare_metaphors(starter: StarterVoiceProfile, novel: NovelVoiceProfile) -> str:
    """Compare metaphor usage."""
    starter_count = len(starter.metaphor_domains)
    novel_count = len(novel.metaphor_domains)

    if novel_count > starter_count:
        increase_pct = ((novel_count - starter_count) / max(starter_count, 1)) * 100
        return f"+{increase_pct:.0f}% increase in metaphor domains"
    elif novel_count < starter_count:
        decrease_pct = ((starter_count - novel_count) / starter_count) * 100
        return f"-{decrease_pct:.0f}% decrease (more focused metaphors)"
    else:
        return "Similar metaphor usage"


def _compare_formality(starter: StarterVoiceProfile, novel: NovelVoiceProfile) -> str:
    """Compare formality levels."""
    starter_formality = starter.vocabulary.get("formality_level", "casual")
    novel_formality = novel.vocabulary.get("formality_level", "neutral")

    formality_order = ["casual", "neutral", "formal", "literary"]

    try:
        starter_idx = formality_order.index(starter_formality.lower())
        novel_idx = formality_order.index(novel_formality.lower())

        if novel_idx > starter_idx:
            return f"{starter_formality} → {novel_formality} (more literary)"
        elif novel_idx < starter_idx:
            return f"{starter_formality} → {novel_formality} (more casual)"
        else:
            return f"Consistent {novel_formality} tone"
    except (ValueError, AttributeError):
        return f"{starter_formality} → {novel_formality}"


def _compare_pov_depth(starter: StarterVoiceProfile, novel: NovelVoiceProfile) -> str:
    """Compare POV depth."""
    starter_depth = starter.pov_style.get("depth", "shallow")
    novel_depth = novel.pov_style.get("depth", "medium")

    depth_order = ["shallow", "medium", "deep"]

    try:
        starter_idx = depth_order.index(starter_depth.lower())
        novel_idx = depth_order.index(novel_depth.lower())

        if novel_idx > starter_idx:
            return f"{starter_depth} → {novel_depth} (deeper immersion)"
        elif novel_idx < starter_idx:
            return f"{starter_depth} → {novel_depth} (more distant)"
        else:
            return f"Consistent {novel_depth} POV"
    except (ValueError, AttributeError):
        return f"{starter_depth} → {novel_depth}"
