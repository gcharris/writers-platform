"""Progress Tracking & Upgrade System - Monitor word count and trigger upgrades.

Tracks cumulative word count for beginner projects and triggers upgrade from
StarterVoiceProfile to NovelVoiceProfile at 2,500 words.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from anthropic import Anthropic
import logging

from factory.core.dual_voice_profiles import (
    StarterVoiceProfile,
    NovelVoiceProfile,
    compare_voices
)
from factory.core.voice_extractor import VoiceProfileExtractor
from factory.core.skill_generator import SkillGenerator

logger = logging.getLogger(__name__)


@dataclass
class UpgradeStatus:
    """Status of upgrade eligibility."""

    ready: bool  # True if eligible for upgrade
    words: int  # Current word count
    threshold: int  # Words needed for upgrade
    progress_pct: float = 0.0  # Progress percentage (0-100)
    message: str = ""  # Status message


@dataclass
class UpgradeResult:
    """Result of upgrade process."""

    success: bool
    novel_voice: Optional[NovelVoiceProfile] = None
    novel_skills: Optional[Dict[str, Any]] = None
    comparison: Optional[Dict[str, Any]] = None  # Voice evolution comparison
    message: str = ""
    error: Optional[str] = None


class ProgressUpgradeSystem:
    """Monitor progress and trigger upgrades from starter to novel skills."""

    def __init__(self, anthropic_client: Anthropic):
        """Initialize progress upgrade system.

        Args:
            anthropic_client: Anthropic client for voice analysis
        """
        self.client = anthropic_client

    async def track_word_count(
        self,
        current_words: int,
        is_starter_mode: bool,
        upgrade_threshold: int = 2500
    ) -> UpgradeStatus:
        """Track cumulative word count and check upgrade eligibility.

        Args:
            current_words: Current total word count
            is_starter_mode: True if project in starter mode
            upgrade_threshold: Words needed for upgrade (default 2500)

        Returns:
            UpgradeStatus with eligibility information
        """
        if not is_starter_mode:
            return UpgradeStatus(
                ready=False,
                words=current_words,
                threshold=upgrade_threshold,
                progress_pct=100.0,
                message="Already upgraded to Novel Skills"
            )

        progress_pct = min((current_words / upgrade_threshold) * 100, 100.0)

        if current_words >= upgrade_threshold:
            logger.info(f"Upgrade threshold reached! {current_words}/{upgrade_threshold} words")
            return UpgradeStatus(
                ready=True,
                words=current_words,
                threshold=upgrade_threshold,
                progress_pct=100.0,
                message="🎉 Ready to upgrade to Novel Skills!"
            )
        else:
            words_remaining = upgrade_threshold - current_words
            logger.debug(f"Progress: {current_words}/{upgrade_threshold} ({progress_pct:.1f}%)")
            return UpgradeStatus(
                ready=False,
                words=current_words,
                threshold=upgrade_threshold,
                progress_pct=progress_pct,
                message=f"{words_remaining} words until Novel Skills upgrade"
            )

    async def perform_upgrade(
        self,
        project_name: str,
        project_id: str,
        genre: str,
        all_scenes_text: str,  # All fiction written so far
        previous_starter: StarterVoiceProfile
    ) -> UpgradeResult:
        """Upgrade from starter to novel skills.

        Process:
        1. Extract NovelVoiceProfile from fiction (2,500+ words)
        2. Generate 6 novel-tuned skills
        3. Compare starter vs novel voice
        4. Return upgrade result

        Args:
            project_name: Name of the project
            project_id: Project identifier
            genre: Genre of the novel
            all_scenes_text: Combined text of all scenes written
            previous_starter: Previous StarterVoiceProfile

        Returns:
            UpgradeResult with novel voice, skills, and comparison
        """
        logger.info(f"Starting upgrade process for project: {project_name}")

        try:
            # Step 1: Extract fiction voice
            logger.info("Extracting fiction voice from written scenes...")
            extractor = VoiceProfileExtractor(self.client)

            # Extract voice profile from fiction
            novel_voice_base = await extractor.extract_voice_profile(
                example_passages=[all_scenes_text],
                uploaded_docs=[],
                notebooklm_context=None
            )

            # Convert to NovelVoiceProfile
            novel_voice = NovelVoiceProfile(
                voice_name=novel_voice_base.voice_name,
                genre=novel_voice_base.genre,
                primary_characteristics=novel_voice_base.primary_characteristics,
                sentence_structure=novel_voice_base.sentence_structure,
                vocabulary=novel_voice_base.vocabulary,
                pov_style=novel_voice_base.pov_style,
                metaphor_domains=novel_voice_base.metaphor_domains,
                anti_patterns=novel_voice_base.anti_patterns,
                quality_criteria=novel_voice_base.quality_criteria,
                voice_consistency_notes=novel_voice_base.voice_consistency_notes,
                fiction_word_count=len(all_scenes_text.split()),
                confidence_level="high",
                created_from_upgrade=True,
                previous_starter=previous_starter
            )

            logger.info(f"Fiction voice extracted: {novel_voice.voice_name}")

            # Step 2: Compare voices
            logger.info("Comparing starter vs novel voice...")
            comparison = compare_voices(previous_starter, novel_voice)
            novel_voice.voice_evolution = comparison

            logger.info(f"Voice evolution: {comparison.get('summary', 'N/A')}")

            # Step 3: Generate novel skills
            logger.info("Generating novel-tuned skills...")
            generator = SkillGenerator(self.client)
            novel_skills = await generator.generate_project_skills(
                project_name=project_name,
                voice_profile=novel_voice,
                notebooklm_context=None  # Could add story context here
            )

            logger.info(f"Generated {len(novel_skills)} novel skills")

            # Convert skills to dict for response
            skills_dict = {}
            for skill_type, skill in novel_skills.items():
                skills_dict[skill_type] = {
                    "skillName": skill.skill_name,
                    "skillType": skill.skill_type,
                    "skillMd": skill.skill_prompt,
                    "references": skill.references
                }

            return UpgradeResult(
                success=True,
                novel_voice=novel_voice,
                novel_skills=skills_dict,
                comparison=comparison,
                message="Successfully upgraded to Novel Skills! 🎉"
            )

        except Exception as e:
            logger.error(f"Upgrade failed: {str(e)}", exc_info=True)
            return UpgradeResult(
                success=False,
                error=str(e),
                message=f"Upgrade failed: {str(e)}"
            )

    def calculate_progress_stats(
        self,
        current_words: int,
        upgrade_threshold: int = 2500
    ) -> Dict[str, Any]:
        """Calculate detailed progress statistics.

        Args:
            current_words: Current total word count
            upgrade_threshold: Words needed for upgrade

        Returns:
            Dict with progress stats for UI display
        """
        progress_pct = min((current_words / upgrade_threshold) * 100, 100.0)
        words_remaining = max(upgrade_threshold - current_words, 0)
        is_ready = current_words >= upgrade_threshold

        # Calculate milestones
        milestones = [
            {"words": 500, "label": "Getting Started", "reached": current_words >= 500},
            {"words": 1000, "label": "Finding Your Voice", "reached": current_words >= 1000},
            {"words": 1500, "label": "Building Momentum", "reached": current_words >= 1500},
            {"words": 2000, "label": "Almost There!", "reached": current_words >= 2000},
            {"words": 2500, "label": "Upgrade Ready!", "reached": current_words >= 2500}
        ]

        return {
            "current_words": current_words,
            "threshold": upgrade_threshold,
            "words_remaining": words_remaining,
            "progress_percentage": round(progress_pct, 1),
            "is_ready_for_upgrade": is_ready,
            "milestones": milestones,
            "encouragement": self._get_encouragement_message(current_words, upgrade_threshold)
        }

    def _get_encouragement_message(self, current_words: int, threshold: int) -> str:
        """Get encouraging message based on progress.

        Args:
            current_words: Current word count
            threshold: Upgrade threshold

        Returns:
            Encouraging message
        """
        progress_pct = (current_words / threshold) * 100

        if progress_pct >= 100:
            return "🎉 Amazing! You've hit the upgrade threshold! Ready to unlock Novel Skills?"
        elif progress_pct >= 90:
            remaining = threshold - current_words
            return f"So close! Just {remaining} more words until you unlock Novel Skills!"
        elif progress_pct >= 75:
            return "You're in the home stretch! Keep that momentum going!"
        elif progress_pct >= 50:
            return "Halfway there! Your fiction voice is taking shape!"
        elif progress_pct >= 25:
            return "Great progress! You're building your story one word at a time."
        elif progress_pct >= 10:
            return "Excellent start! Every word brings you closer to Novel Skills."
        else:
            return "Welcome to your writing journey! Focus on getting words on the page."


class WordCountTracker:
    """Simple word count tracker for scenes."""

    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text.

        Args:
            text: Text to count

        Returns:
            Word count
        """
        if not text:
            return 0
        return len(text.split())

    @staticmethod
    def count_words_in_scenes(scenes: list[Dict[str, Any]]) -> int:
        """Count total words across multiple scenes.

        Args:
            scenes: List of scene dicts with 'content' field

        Returns:
            Total word count
        """
        total = 0
        for scene in scenes:
            content = scene.get("content", "")
            total += WordCountTracker.count_words(content)
        return total

    @staticmethod
    def should_show_upgrade_prompt(
        current_words: int,
        is_starter_mode: bool,
        upgrade_prompted_before: bool,
        threshold: int = 2500
    ) -> bool:
        """Determine if upgrade prompt should be shown.

        Args:
            current_words: Current total word count
            is_starter_mode: True if in starter mode
            upgrade_prompted_before: True if user already saw prompt
            threshold: Upgrade threshold

        Returns:
            True if should show upgrade prompt
        """
        # Only show if:
        # 1. In starter mode
        # 2. Past threshold
        # 3. Haven't been prompted before
        return (
            is_starter_mode and
            current_words >= threshold and
            not upgrade_prompted_before
        )
