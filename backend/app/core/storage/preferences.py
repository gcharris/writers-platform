"""User preferences management."""

import logging
import json
from pathlib import Path
from typing import Optional

import aiofiles

from .models import Preferences

logger = logging.getLogger(__name__)


class PreferencesManager:
    """Manages user preferences with file-based storage."""

    def __init__(self, session_path: Path):
        """Initialize preferences manager.

        Args:
            session_path: Path to .session directory
        """
        self.session_path = Path(session_path)
        self.prefs_file = self.session_path / "preferences.json"

        # Load existing preferences
        self.data = self._load_or_create()

    def _load_or_create(self) -> Preferences:
        """Load existing preferences or create defaults."""
        if self.prefs_file.exists():
            try:
                with open(self.prefs_file, 'r') as f:
                    data_dict = json.load(f)
                    return Preferences(**data_dict)
            except Exception as e:
                logger.error(f"Failed to load preferences: {e}. Using defaults.")

        return Preferences()

    async def save(self) -> bool:
        """Save preferences to disk."""
        try:
            temp_path = self.prefs_file.with_suffix('.tmp')
            async with aiofiles.open(temp_path, 'w') as f:
                await f.write(self.data.model_dump_json(indent=2))
            temp_path.replace(self.prefs_file)
            return True
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False

    def get_model_for_stage(self, stage: str) -> str:
        """Get preferred model for stage."""
        return self.data.model_preferences.get(stage, "claude-sonnet-4.5")

    def set_model_for_stage(self, stage: str, model: str):
        """Set preferred model for stage."""
        self.data.model_preferences[stage] = model

    def get_auto_save_interval(self) -> int:
        """Get auto-save interval in seconds."""
        return self.data.auto_save_interval
