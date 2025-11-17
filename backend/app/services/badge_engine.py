"""
Badge Engine Service
====================

Assigns badges to works based on analysis results and content detection.

Badge Types:
- ai_analyzed: Work analyzed by Factory engine
- human_verified: AI detection confirmed human authorship (>80% confidence)
- human_self: User self-declared human authorship
- community_upload: Direct upload to Community (no Factory analysis)
"""

from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
import uuid

from app.models.badge import Badge
from app.models.work import Work
from app.models.analysis_result import AnalysisResult


class BadgeEngine:
    """Manages badge assignment and AI authorship detection."""

    # Badge type constants
    BADGE_AI_ANALYZED = "ai_analyzed"
    BADGE_HUMAN_VERIFIED = "human_verified"
    BADGE_HUMAN_SELF = "human_self"
    BADGE_COMMUNITY_UPLOAD = "community_upload"

    # Detection confidence threshold
    HUMAN_CONFIDENCE_THRESHOLD = 0.80  # 80% confidence for verification

    def __init__(self, db: Session, ai_client=None):
        """
        Initialize badge engine.

        Args:
            db: Database session
            ai_client: Optional AI client for content detection (Claude or GPT)
        """
        self.db = db
        self.ai_client = ai_client

    async def detect_ai_authorship(self, text: str, use_ai_detection: bool = True) -> Tuple[bool, float]:
        """
        Detect if text is AI-authored.

        Uses heuristic patterns and optionally AI-based detection.

        Args:
            text: Text to analyze
            use_ai_detection: Whether to use AI-based detection (costs $)

        Returns:
            Tuple of (is_ai_authored: bool, confidence: float)
            - is_ai_authored: True if likely AI-generated
            - confidence: 0.0-1.0 confidence score
        """
        # Heuristic checks (fast, free)
        heuristic_score = self._heuristic_ai_detection(text)

        # If heuristic is very confident, return that
        if heuristic_score > 0.9 or heuristic_score < 0.1:
            is_ai = heuristic_score > 0.5
            return is_ai, heuristic_score if is_ai else (1.0 - heuristic_score)

        # Optionally use AI-based detection (slower, costs money)
        if use_ai_detection and self.ai_client:
            try:
                ai_score = await self._ai_based_detection(text)
                # Average heuristic and AI scores
                combined_score = (heuristic_score + ai_score) / 2
                is_ai = combined_score > 0.5
                return is_ai, combined_score if is_ai else (1.0 - combined_score)
            except Exception as e:
                print(f"AI detection failed: {e}, falling back to heuristic")

        # Fallback to heuristic
        is_ai = heuristic_score > 0.5
        return is_ai, heuristic_score if is_ai else (1.0 - heuristic_score)

    def _heuristic_ai_detection(self, text: str) -> float:
        """
        Heuristic-based AI detection using patterns.

        Checks for:
        - Overly formal/perfect grammar
        - Generic phrases common in AI text
        - Lack of personal voice/quirks
        - Repetitive sentence structures

        Returns:
            Score 0.0-1.0 (higher = more likely AI)
        """
        ai_indicators = 0
        total_checks = 0

        # Convert to lowercase for matching
        text_lower = text.lower()

        # 1. Check for common AI phrases
        ai_phrases = [
            "it's important to note that",
            "it's worth noting that",
            "in conclusion",
            "in summary",
            "furthermore",
            "moreover",
            "additionally",
            "as an ai",
            "i don't have personal opinions",
            "delve into",
            "navigate the complexities",
        ]

        phrase_count = sum(1 for phrase in ai_phrases if phrase in text_lower)
        if phrase_count > 3:
            ai_indicators += 1
        total_checks += 1

        # 2. Check sentence length variation (AI tends to be more uniform)
        sentences = text.split('.')
        if len(sentences) > 5:
            lengths = [len(s.split()) for s in sentences if s.strip()]
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
                # Low variance = more AI-like
                if variance < 20:
                    ai_indicators += 1
            total_checks += 1

        # 3. Check for overly perfect grammar (heuristic: lack of fragments)
        # Human writing often has fragments, questions, exclamations
        has_questions = '?' in text
        has_exclamations = '!' in text
        has_fragments = any(len(s.split()) < 3 for s in sentences if s.strip())

        if not (has_questions or has_exclamations or has_fragments):
            ai_indicators += 1
        total_checks += 1

        # 4. Check for personal pronouns (human writing more personal)
        personal_pronouns = ['i ', 'my ', 'me ', 'we ', 'our ']
        pronoun_count = sum(text_lower.count(p) for p in personal_pronouns)
        word_count = len(text.split())

        if word_count > 100:
            pronoun_ratio = pronoun_count / word_count
            if pronoun_ratio < 0.01:  # Very low personal pronoun usage
                ai_indicators += 0.5
            total_checks += 1

        # Calculate score
        if total_checks == 0:
            return 0.5  # Neutral

        score = ai_indicators / total_checks
        return score

    async def _ai_based_detection(self, text: str) -> float:
        """
        AI-based detection using Claude or GPT.

        Asks AI to analyze writing patterns and assess likelihood of AI authorship.

        Returns:
            Score 0.0-1.0 (higher = more likely AI)
        """
        # This would use Claude/GPT API to analyze the text
        # For MVP, we'll skip this to save costs
        # In production, implement using:
        # - Anthropic Claude API
        # - OpenAI GPT API
        # - Specialized AI detection service

        prompt = """Analyze this text and determine if it was likely written by an AI or a human.

Consider:
- Writing style (natural vs. formulaic)
- Vocabulary choices (varied vs. predictable)
- Personal voice and quirks
- Sentence structure variation
- Authentic human imperfections

Text to analyze:
\"\"\"
{text}
\"\"\"

Respond with ONLY a number between 0.0 and 1.0, where:
- 0.0 = definitely human-written
- 1.0 = definitely AI-generated

Score:"""

        # In production, call AI API here
        # For now, return heuristic fallback
        return self._heuristic_ai_detection(text)

    def assign_badge_ai_analyzed(
        self,
        work_id: uuid.UUID,
        analysis_result_id: uuid.UUID,
        metadata: Optional[Dict] = None
    ) -> Badge:
        """
        Assign AI-Analyzed badge to a work.

        Args:
            work_id: Work UUID
            analysis_result_id: AnalysisResult UUID
            metadata: Optional metadata (scores, models used, etc.)

        Returns:
            Badge instance
        """
        badge = Badge(
            work_id=work_id,
            badge_type=self.BADGE_AI_ANALYZED,
            verified=True,
            metadata_json=metadata or {}
        )

        # Add analysis_result_id to metadata
        if metadata is None:
            badge.metadata_json = {}
        badge.metadata_json['analysis_result_id'] = str(analysis_result_id)

        self.db.add(badge)
        self.db.commit()
        self.db.refresh(badge)

        return badge

    async def assign_badge_human_verified(
        self,
        work_id: uuid.UUID,
        text: str,
        use_ai_detection: bool = True
    ) -> Optional[Badge]:
        """
        Assign Human-Verified badge if AI detection confirms human authorship.

        Args:
            work_id: Work UUID
            text: Work content to analyze
            use_ai_detection: Whether to use AI-based detection

        Returns:
            Badge instance if verified as human, None otherwise
        """
        is_ai, confidence = await self.detect_ai_authorship(text, use_ai_detection)

        # If AI-authored or low confidence, don't assign badge
        if is_ai:
            return None

        if confidence < self.HUMAN_CONFIDENCE_THRESHOLD:
            return None

        # Assign verified badge
        badge = Badge(
            work_id=work_id,
            badge_type=self.BADGE_HUMAN_VERIFIED,
            verified=True,
            metadata_json={
                'confidence': confidence,
                'detection_method': 'ai' if use_ai_detection else 'heuristic'
            }
        )

        self.db.add(badge)
        self.db.commit()
        self.db.refresh(badge)

        return badge

    def assign_badge_human_self(
        self,
        work_id: uuid.UUID,
        user_declaration: str = "User declares human authorship"
    ) -> Badge:
        """
        Assign Human-Self badge (user self-declaration).

        Args:
            work_id: Work UUID
            user_declaration: Optional declaration text

        Returns:
            Badge instance
        """
        badge = Badge(
            work_id=work_id,
            badge_type=self.BADGE_HUMAN_SELF,
            verified=False,  # Not verified, just declared
            metadata_json={
                'declaration': user_declaration
            }
        )

        self.db.add(badge)
        self.db.commit()
        self.db.refresh(badge)

        return badge

    def assign_badge_community_upload(self, work_id: uuid.UUID) -> Badge:
        """
        Assign Community Upload badge (direct upload, no Factory analysis).

        Args:
            work_id: Work UUID

        Returns:
            Badge instance
        """
        badge = Badge(
            work_id=work_id,
            badge_type=self.BADGE_COMMUNITY_UPLOAD,
            verified=False,
            metadata_json={}
        )

        self.db.add(badge)
        self.db.commit()
        self.db.refresh(badge)

        return badge

    def get_work_badges(self, work_id: uuid.UUID) -> List[Badge]:
        """
        Get all badges for a work.

        Args:
            work_id: Work UUID

        Returns:
            List of Badge instances
        """
        return self.db.query(Badge).filter(Badge.work_id == work_id).all()

    def remove_badge(self, badge_id: uuid.UUID):
        """
        Remove a badge.

        Args:
            badge_id: Badge UUID
        """
        badge = self.db.query(Badge).filter(Badge.id == badge_id).first()
        if badge:
            self.db.delete(badge)
            self.db.commit()
