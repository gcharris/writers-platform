"""
Bi-location Mechanics and Voice Validation

Validates scenes for:
- Forbidden jargon detection
- Mickey's voice terms (The Line, The Tether, The Shared Vein)
- Bi-location mechanics requirements
- Voice authenticity markers
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Results from bi-location and voice validation."""
    forbidden_jargon_found: List[str]
    correct_terms_used: List[str]
    correct_terms_counts: Dict[str, int]
    bi_location_shown_properly: bool
    validation_score: float  # 0-10
    issues: List[str]
    strengths: List[str]


class BiLocationValidator:
    """Validates bi-location mechanics and Mickey's voice requirements."""

    # Forbidden jargon patterns (case-insensitive)
    FORBIDDEN_PATTERNS = [
        r'quantum\s+link',
        r'bi-?location\s+mode',
        r'split\s+consciousness',
        r'dual\s+consciousness\s+mode',
        r'activated?\s+bi-?location',
        r'entering\s+bi-?location',
        r'QBV\s+integration',
        r'cognitive\s+load',
    ]

    # Mickey's correct terms
    CORRECT_TERMS = [
        "The Line",
        "the Line",
        "The Tether",
        "the Tether",
        "The Shared Vein",
        "the Shared Vein",
    ]

    # Bi-location showing patterns (good indicators)
    BI_LOCATION_INDICATORS = [
        r'shadow\s+split',
        r'temples?\s+puls(?:ed|ing)',
        r'voice\s+desync',
        r'awareness\s+(?:telescop|pivot)',
        r'consciousness\s+stretched',
        r'dual\s+existence',
        r'analog\s+(?:brain|body|reality)',
        r'quantum\s+space',
        r'sleep\s+debt',
        r'phantom\s+fatigue',
    ]

    # Technical announcement patterns (violations)
    TECHNICAL_ANNOUNCEMENTS = [
        r'(?:he|Mickey)\s+(?:split|activated|entered)',
        r'operated?\s+in\s+(?:dual|bi-?location)',
        r'consciousness\s+was\s+split',
        r'mind\s+operated\s+on\s+dual\s+levels',
    ]

    def validate(self, content: str) -> ValidationResult:
        """
        Validate scene content for bi-location mechanics and voice.

        Args:
            content: Scene text to validate

        Returns:
            ValidationResult with findings
        """
        issues = []
        strengths = []

        # Check for forbidden jargon
        forbidden_found = self._find_forbidden_jargon(content)
        if forbidden_found:
            issues.extend([f"Forbidden jargon: '{term}'" for term in forbidden_found])

        # Check for correct terms
        correct_terms_used, correct_counts = self._find_correct_terms(content)
        if correct_terms_used:
            strengths.append(f"Uses Mickey's terms: {', '.join(correct_terms_used)}")

        # Check bi-location showing vs. telling
        bi_location_shown = self._check_bi_location_showing(content)
        if bi_location_shown:
            strengths.append("Shows bi-location through physical strain/symptoms")

        # Check for technical announcements (violations)
        tech_announcements = self._find_technical_announcements(content)
        if tech_announcements:
            issues.extend([f"Technical announcement: '{ann}'" for ann in tech_announcements])

        # Calculate validation score
        score = self._calculate_validation_score(
            forbidden_found=len(forbidden_found),
            correct_terms=len(correct_terms_used),
            bi_location_shown=bi_location_shown,
            tech_announcements=len(tech_announcements)
        )

        return ValidationResult(
            forbidden_jargon_found=forbidden_found,
            correct_terms_used=correct_terms_used,
            correct_terms_counts=correct_counts,
            bi_location_shown_properly=bi_location_shown,
            validation_score=score,
            issues=issues,
            strengths=strengths
        )

    def _find_forbidden_jargon(self, content: str) -> List[str]:
        """Find forbidden jargon in content."""
        found = []
        for pattern in self.FORBIDDEN_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                found.append(match.group(0))
        return list(set(found))  # Remove duplicates

    def _find_correct_terms(self, content: str) -> Tuple[List[str], Dict[str, int]]:
        """Find Mickey's correct terms in content."""
        found_terms = []
        counts = {}

        for term in self.CORRECT_TERMS:
            count = content.count(term)
            if count > 0:
                # Normalize to canonical form
                canonical = term.replace("the ", "The ")
                if canonical not in found_terms:
                    found_terms.append(canonical)
                counts[canonical] = counts.get(canonical, 0) + count

        return found_terms, counts

    def _check_bi_location_showing(self, content: str) -> bool:
        """Check if bi-location is shown through physical symptoms."""
        indicator_count = 0
        for pattern in self.BI_LOCATION_INDICATORS:
            if re.search(pattern, content, re.IGNORECASE):
                indicator_count += 1

        # Need at least 2 indicators to consider it properly shown
        return indicator_count >= 2

    def _find_technical_announcements(self, content: str) -> List[str]:
        """Find technical announcement violations."""
        found = []
        for pattern in self.TECHNICAL_ANNOUNCEMENTS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get surrounding context (up to 50 chars)
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 30)
                context = content[start:end].strip()
                found.append(context)
        return found[:3]  # Limit to first 3 examples

    def _calculate_validation_score(self, forbidden_found: int, correct_terms: int,
                                    bi_location_shown: bool, tech_announcements: int) -> float:
        """Calculate overall validation score (0-10)."""
        score = 10.0

        # Penalties
        score -= forbidden_found * 2.0  # -2 per forbidden term
        score -= tech_announcements * 1.5  # -1.5 per technical announcement

        # Bonuses
        score += min(correct_terms * 1.0, 3.0)  # +1 per correct term (max +3)
        score += 2.0 if bi_location_shown else 0  # +2 for proper showing

        return max(0.0, min(10.0, score))


class VoiceValidator:
    """Validates Enhanced Mickey Bardot voice characteristics."""

    # Voice markers (positive indicators)
    VOICE_MARKERS = [
        # Compressed phrasing
        r'\w+ed\s+(?:himself|herself|themselves)',  # "geometried himself"
        r'\w+\s+(?:refused|demanded|required)\s+to',

        # Direct metaphors
        r'like\s+\w+\s+(?:he|she|they)',
        r'deeper\s+than\s+\w+\s+(?:reached|transformed)',

        # Present-tense urgency
        r'(?:temples?|shadow|voice|awareness)\s+(?:puls|split|pivot|telescope)',
    ]

    # Anti-patterns (voice violations)
    ANTI_PATTERNS = [
        r'it\s+was\s+clear\s+that',
        r'he\s+realized\s+that',
        r'she\s+understood\s+that',
        r'obviously,',
        r'clearly,',
    ]

    def validate_voice(self, content: str) -> Dict[str, any]:
        """
        Validate voice characteristics.

        Returns:
            Dictionary with voice analysis
        """
        voice_markers_found = 0
        anti_patterns_found = 0

        for pattern in self.VOICE_MARKERS:
            if re.search(pattern, content, re.IGNORECASE):
                voice_markers_found += 1

        for pattern in self.ANTI_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                anti_patterns_found += 1

        # Calculate voice authenticity score (0-10)
        base_score = 7.0  # Neutral baseline
        base_score += min(voice_markers_found * 0.5, 3.0)
        base_score -= anti_patterns_found * 1.0

        voice_score = max(0.0, min(10.0, base_score))

        return {
            'voice_markers_found': voice_markers_found,
            'anti_patterns_found': anti_patterns_found,
            'voice_authenticity_score': voice_score,
            'has_compressed_phrasing': voice_markers_found > 0,
            'has_anti_patterns': anti_patterns_found > 0
        }


def validate_scene(content: str) -> Dict:
    """
    Comprehensive scene validation.

    Args:
        content: Scene text

    Returns:
        Combined validation results
    """
    bi_location = BiLocationValidator()
    voice = VoiceValidator()

    bi_result = bi_location.validate(content)
    voice_result = voice.validate_voice(content)

    return {
        'bi_location': {
            'forbidden_jargon_found': bi_result.forbidden_jargon_found,
            'correct_terms_used': bi_result.correct_terms_used,
            'correct_terms_counts': bi_result.correct_terms_counts,
            'bi_location_shown_properly': bi_result.bi_location_shown_properly,
            'validation_score': bi_result.validation_score,
            'issues': bi_result.issues,
            'strengths': bi_result.strengths
        },
        'voice': voice_result,
        'overall_validation_score': (bi_result.validation_score + voice_result['voice_authenticity_score']) / 2
    }
