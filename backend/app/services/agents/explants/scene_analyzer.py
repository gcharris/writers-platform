"""Native Scene Analyzer Agent for Explants craft standards.

This module provides a Python-native implementation of the Explants Scene Analyzer,
which scores scenes based on voice authenticity, character consistency, metaphor
discipline, anti-pattern compliance, and phase appropriateness.

Sprint 12 - Task 12-03
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import re
from pathlib import Path


@dataclass
class SceneScore:
    """Complete scene scoring breakdown.

    Attributes:
        total_score: Overall score (0-100)
        category_scores: Breakdown by category
        quality_tier: Quality assessment (Gold Standard, A+, A, etc.)
        fixes: List of suggested improvements
        details: Detailed analysis per category
    """
    total_score: int
    category_scores: Dict[str, int] = field(default_factory=dict)
    quality_tier: str = ""
    fixes: List[Dict[str, Any]] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_score": self.total_score,
            "category_scores": self.category_scores,
            "quality_tier": self.quality_tier,
            "fixes": self.fixes,
            "details": self.details
        }


class SceneAnalyzerAgent:
    """Native Python implementation of Explants Scene Analyzer.

    This agent analyzes scenes against Explants craft standards and provides
    detailed scoring with specific improvement suggestions.

    Scoring Framework (100 points):
    - Voice Authenticity: 30 points
    - Character Consistency: 20 points
    - Metaphor Discipline: 20 points
    - Anti-Pattern Compliance: 15 points
    - Phase Appropriateness: 15 points
    """

    def __init__(self, knowledge_path: Optional[Path] = None):
        """Initialize Scene Analyzer Agent.

        Args:
            knowledge_path: Path to reference knowledge materials
        """
        self.knowledge_path = knowledge_path
        self.anti_patterns = self._compile_anti_patterns()
        self.metaphor_domains = self._load_metaphor_domains()

    def _compile_anti_patterns(self) -> Dict[str, re.Pattern]:
        """Compile anti-pattern regex patterns.

        Returns:
            Dictionary of pattern name to compiled regex
        """
        return {
            # Zero-tolerance violations (-2 points each)
            "first_person_italics": re.compile(r'\*[^*]*\b(we|I)\b[^*]*\*', re.IGNORECASE),
            "with_precision": re.compile(r'\bwith \w+ precision\b', re.IGNORECASE),
            "computer_psychology": re.compile(
                r'\b(processed|downloaded|uploaded|computed)\b.*\b(emotion|thought|feeling)\b',
                re.IGNORECASE
            ),

            # Formulaic patterns (-1 point each)
            "with_adjective_noun": re.compile(
                r'\bwith (the |a |an )?([\w]+) ([\w]+)\b',
                re.IGNORECASE
            ),
            "weak_similes": re.compile(
                r'\b(like (a|an|the)|as if|resembled|seemed like)\b',
                re.IGNORECASE
            ),
            "formulaic_walking": re.compile(r'\bwalked \w+ly\b', re.IGNORECASE),
            "academic_tone": re.compile(
                r'\b(furthermore|moreover|in conclusion|therefore|thus|hence)\b',
                re.IGNORECASE
            ),
            "gerund_walking": re.compile(r'\bwalking \w+\b', re.IGNORECASE),
            "body_part_subject": re.compile(
                r'\b(his|her|their) (hand|hands|eyes|fingers|arm|arms)\b \w+ (reached|moved|grabbed|touched)',
                re.IGNORECASE
            )
        }

    def _load_metaphor_domains(self) -> Dict[str, List[str]]:
        """Load metaphor domain classifications.

        Returns:
            Dictionary of domains to keywords
        """
        # Simplified domain keywords for native implementation
        # Full implementation would load from knowledge files
        return {
            "computational": ["process", "download", "upload", "compute", "program", "algorithm"],
            "medical": ["diagnose", "symptom", "treatment", "surgery", "prescription"],
            "military": ["attack", "defend", "strategy", "tactical", "weapon", "battle"],
            "architectural": ["foundation", "structure", "framework", "scaffold", "pillar"],
            "mechanical": ["mechanism", "engine", "gear", "cog", "lever", "spring"],
            "economic": ["invest", "profit", "cost", "value", "transaction", "currency"]
        }

    async def execute(
        self,
        scene_content: str,
        mode: str = "detailed",
        reference_files: Optional[List[str]] = None,
        phase: str = "phase2"
    ) -> Dict[str, Any]:
        """Execute scene analysis (MCP-compatible entry point).

        Args:
            scene_content: Scene text to analyze
            mode: Analysis mode (detailed, quick, variant_comparison)
            reference_files: Optional reference documents
            phase: Story phase (phase1, phase2, phase3)

        Returns:
            MCP-formatted response with scoring data
        """
        try:
            score = await self._score_scene(scene_content, phase)

            return {
                "status": "success",
                "data": score.to_dict(),
                "metadata": {
                    "provider": "native_python",
                    "agent": "scene_analyzer",
                    "mode": mode
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": {
                    "code": "ANALYSIS_ERROR",
                    "message": str(e)
                },
                "metadata": {
                    "provider": "native_python",
                    "agent": "scene_analyzer"
                }
            }

    async def _score_scene(self, scene_content: str, phase: str) -> SceneScore:
        """Run complete scene scoring.

        Args:
            scene_content: Scene text
            phase: Story phase

        Returns:
            Complete scene score
        """
        score = SceneScore(total_score=0)

        # Score each category
        voice_score, voice_details = self._score_voice_authenticity(scene_content)
        char_score, char_details = self._score_character_consistency(scene_content)
        metaphor_score, metaphor_details = self._score_metaphor_discipline(scene_content)
        antipattern_score, antipattern_details, fixes = self._score_anti_patterns(scene_content)
        phase_score, phase_details = self._score_phase_appropriateness(scene_content, phase)

        # Compile scores
        score.category_scores = {
            "voice_authenticity": voice_score,
            "character_consistency": char_score,
            "metaphor_discipline": metaphor_score,
            "anti_pattern_compliance": antipattern_score,
            "phase_appropriateness": phase_score
        }

        score.total_score = sum(score.category_scores.values())

        # Determine quality tier
        score.quality_tier = self._get_quality_tier(score.total_score)

        # Compile fixes
        score.fixes = fixes

        # Add detailed breakdowns
        score.details = {
            "voice": voice_details,
            "character": char_details,
            "metaphor": metaphor_details,
            "antipatterns": antipattern_details,
            "phase": phase_details
        }

        return score

    def _score_voice_authenticity(self, scene_content: str) -> tuple[int, Dict]:
        """Score voice authenticity (30 points max).

        Tests:
        - Observer vs Consciousness War check
        - Cognitive Fusion detection
        - Internal thought authenticity

        Args:
            scene_content: Scene text

        Returns:
            Tuple of (score, details)
        """
        score = 30  # Start with max
        issues = []

        # Observer check: Look for direct observation language
        observer_patterns = [
            r'\b(I saw|I noticed|I observed|I watched)\b',
            r'\b(observing|noticing|watching)\b'
        ]
        observer_count = sum(
            len(re.findall(pattern, scene_content, re.IGNORECASE))
            for pattern in observer_patterns
        )

        if observer_count > 3:  # More than 3 instances is problematic
            score -= 5
            issues.append("Excessive observer language (direct observation verbs)")

        # Consciousness War check: Internal thoughts should be integrated
        italics_thoughts = re.findall(r'\*([^*]+)\*', scene_content)
        if italics_thoughts:
            # Check for "I/we" in italics (breaks 3rd person limited)
            first_person_count = sum(
                1 for thought in italics_thoughts
                if re.search(r'\b(I|we)\b', thought, re.IGNORECASE)
            )
            if first_person_count > 0:
                score -= 10
                issues.append("First-person pronouns in internal thoughts (breaks POV)")

        # Cognitive Fusion check: Thoughts should feel immediate
        telling_phrases = [
            r'\bthought to (himself|herself|themselves)\b',
            r'\bwondered if\b',
            r'\brealizing that\b'
        ]
        telling_count = sum(
            len(re.findall(pattern, scene_content, re.IGNORECASE))
            for pattern in telling_phrases
        )

        if telling_count > 2:
            score -= 5
            issues.append("Cognitive distance (telling rather than showing thoughts)")

        details = {
            "score": score,
            "max_score": 30,
            "issues": issues,
            "observer_count": observer_count,
            "first_person_italics": first_person_count if italics_thoughts else 0
        }

        return score, details

    def _score_character_consistency(self, scene_content: str) -> tuple[int, Dict]:
        """Score character consistency (20 points max).

        Tests:
        - Psychology consistency
        - Capability consistency
        - Relationship dynamics

        Args:
            scene_content: Scene text

        Returns:
            Tuple of (score, details)
        """
        score = 20  # Start with max
        issues = []

        # This is a simplified version - full implementation would check against
        # character bible and previous scenes

        # Basic consistency checks
        # Check for contradictory emotional states in same scene
        emotion_shifts = [
            (r'\banger\b.*\bjoy\b', "Rapid emotion shift: anger to joy"),
            (r'\bfear\b.*\bconfidence\b', "Rapid emotion shift: fear to confidence"),
            (r'\bconfusion\b.*\bclarity\b', "Rapid emotion shift: confusion to clarity")
        ]

        for pattern, issue in emotion_shifts:
            if re.search(pattern, scene_content, re.IGNORECASE):
                score -= 3
                issues.append(issue)

        # Check for capability violations (simplified)
        # E.g., suddenly knowing things they shouldn't
        if re.search(r'\bsuddenly (knew|understood|realized)\b', scene_content, re.IGNORECASE):
            score -= 2
            issues.append("Potential capability violation (sudden knowledge)")

        details = {
            "score": score,
            "max_score": 20,
            "issues": issues,
            "note": "Full character bible validation requires context"
        }

        return score, details

    def _score_metaphor_discipline(self, scene_content: str) -> tuple[int, Dict]:
        """Score metaphor discipline (20 points max).

        Tests:
        - Domain rotation (not overusing one domain)
        - Simile elimination (prefer metaphor)
        - Transformation check (dead metaphors)

        Args:
            scene_content: Scene text

        Returns:
            Tuple of (score, details)
        """
        score = 20  # Start with max
        issues = []

        # Check for weak similes
        simile_matches = re.findall(
            r'\b(like (a|an|the)|as if|seemed like)\b',
            scene_content,
            re.IGNORECASE
        )
        if len(simile_matches) > 3:
            score -= 5
            issues.append(f"Excessive similes ({len(simile_matches)} found) - prefer direct metaphor")

        # Check for domain overuse
        domain_counts = {}
        for domain, keywords in self.metaphor_domains.items():
            count = sum(
                len(re.findall(rf'\b{keyword}\b', scene_content, re.IGNORECASE))
                for keyword in keywords
            )
            if count > 0:
                domain_counts[domain] = count

        if domain_counts:
            max_domain = max(domain_counts.values())
            if max_domain > 5:
                score -= 3
                issues.append(f"Metaphor domain overuse (one domain used {max_domain} times)")

        # Check for dead/cliché metaphors
        dead_metaphors = [
            r'\btime will tell\b',
            r'\bonly time will tell\b',
            r'\bat the end of the day\b',
            r'\bpush the envelope\b',
            r'\bthink outside the box\b'
        ]
        for pattern in dead_metaphors:
            if re.search(pattern, scene_content, re.IGNORECASE):
                score -= 2
                issues.append("Dead/cliché metaphor detected")
                break

        details = {
            "score": score,
            "max_score": 20,
            "issues": issues,
            "simile_count": len(simile_matches),
            "domain_usage": domain_counts
        }

        return score, details

    def _score_anti_patterns(self, scene_content: str) -> tuple[int, List, List[Dict]]:
        """Score anti-pattern compliance (15 points max).

        Tests:
        - Zero-tolerance violations (-2 each)
        - Formulaic patterns (-1 each)

        Args:
            scene_content: Scene text

        Returns:
            Tuple of (score, details, fixes)
        """
        score = 15  # Start with max
        violations = []
        fixes = []

        # Check each anti-pattern
        for pattern_name, pattern in self.anti_patterns.items():
            matches = list(pattern.finditer(scene_content))

            if matches:
                # Determine severity
                if pattern_name in ["first_person_italics", "with_precision", "computer_psychology"]:
                    # Zero-tolerance: -2 points per instance
                    penalty = min(len(matches) * 2, 6)  # Cap at -6
                    score -= penalty
                    priority = "high"
                else:
                    # Formulaic: -1 point per instance
                    penalty = min(len(matches), 4)  # Cap at -4
                    score -= penalty
                    priority = "medium"

                violation = {
                    "pattern": pattern_name,
                    "count": len(matches),
                    "penalty": penalty
                }
                violations.append(violation)

                # Generate fixes
                for match in matches[:3]:  # Show first 3 instances
                    fix = {
                        "type": "anti-pattern",
                        "pattern": pattern_name,
                        "old_string": match.group(0),
                        "suggested_fix": self._get_pattern_fix(pattern_name, match.group(0)),
                        "priority": priority,
                        "line_context": self._get_line_context(scene_content, match.start())
                    }
                    fixes.append(fix)

        details = {
            "score": max(0, score),  # Don't go below 0
            "max_score": 15,
            "violations": violations
        }

        return max(0, score), details, fixes

    def _score_phase_appropriateness(self, scene_content: str, phase: str) -> tuple[int, Dict]:
        """Score phase appropriateness (15 points max).

        Tests:
        - Voice complexity matching phase
        - Technical language appropriateness
        - Sentence structure complexity

        Args:
            scene_content: Scene text
            phase: Story phase (phase1, phase2, phase3)

        Returns:
            Tuple of (score, details)
        """
        score = 15  # Start with max
        issues = []

        # Count sentences for complexity analysis
        sentences = re.split(r'[.!?]+', scene_content)
        sentences = [s.strip() for s in sentences if s.strip()]

        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Phase-specific expectations
        if phase == "phase1":
            # Phase 1: Simpler voice (15-20 words/sentence)
            if avg_sentence_length > 25:
                score -= 5
                issues.append("Sentences too complex for Phase 1 (should be 15-20 words)")
        elif phase == "phase2":
            # Phase 2: Moderate complexity (20-25 words/sentence)
            if avg_sentence_length < 15 or avg_sentence_length > 30:
                score -= 3
                issues.append("Sentence complexity doesn't match Phase 2 (should be 20-25 words)")
        elif phase == "phase3":
            # Phase 3: Fuller complexity allowed (25-30 words/sentence)
            if avg_sentence_length < 20:
                score -= 3
                issues.append("Voice too simple for Phase 3 (should be 25-30 words)")

        # Check for technical jargon inappropriateness
        technical_terms = len(re.findall(
            r'\b(algorithm|protocol|interface|parameter|optimization)\b',
            scene_content,
            re.IGNORECASE
        ))

        if technical_terms > 5:  # Too much jargon for fiction
            score -= 4
            issues.append(f"Excessive technical jargon ({technical_terms} instances)")

        details = {
            "score": score,
            "max_score": 15,
            "issues": issues,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "phase": phase
        }

        return score, details

    def _get_quality_tier(self, total_score: int) -> str:
        """Determine quality tier from total score.

        Args:
            total_score: Overall score

        Returns:
            Quality tier description
        """
        if total_score >= 95:
            return "Gold Standard (95-100) - Publishable as-is"
        elif total_score >= 90:
            return "A+ Excellent (90-94) - Minor polish only"
        elif total_score >= 85:
            return "A Strong (85-89) - Enhancement pass recommended"
        elif total_score >= 80:
            return "A- Good (80-84) - 1-2 specific issues"
        elif total_score >= 75:
            return "B+ Acceptable (75-79) - Enhancement required"
        elif total_score >= 70:
            return "B Functional (70-74) - Multiple issues"
        else:
            return "Needs Rework (<70) - Consider multiplier or major revision"

    def _get_pattern_fix(self, pattern_name: str, matched_text: str) -> str:
        """Get suggested fix for anti-pattern.

        Args:
            pattern_name: Name of the pattern
            matched_text: The matched text

        Returns:
            Suggested fix
        """
        fixes = {
            "first_person_italics": "[REWRITE IN 3RD PERSON LIMITED]",
            "with_precision": "[DELETE THIS PHRASE]",
            "computer_psychology": "[REPLACE WITH HUMAN EMOTION METAPHOR]",
            "with_adjective_noun": "[CONSIDER REMOVING OR REWRITING]",
            "weak_similes": "[TRANSFORM TO DIRECT METAPHOR]",
            "formulaic_walking": "[SHOW DON'T TELL - DESCRIBE MOVEMENT]",
            "academic_tone": "[REMOVE ACADEMIC CONNECTOR]",
            "gerund_walking": "[REWRITE WITH ACTIVE VERB]",
            "body_part_subject": "[MAKE CHARACTER THE SUBJECT, NOT BODY PART]"
        }

        return fixes.get(pattern_name, "[REWRITE SUGGESTED]")

    def _get_line_context(self, text: str, position: int, context_chars: int = 80) -> str:
        """Get context around a position in text.

        Args:
            text: Full text
            position: Position of match
            context_chars: Characters of context on each side

        Returns:
            Context string
        """
        start = max(0, position - context_chars)
        end = min(len(text), position + context_chars)

        context = text[start:end]

        # Clean up
        context = context.replace('\n', ' ').strip()

        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context
