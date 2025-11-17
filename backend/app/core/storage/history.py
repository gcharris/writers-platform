"""Session history tracking."""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List

import aiofiles

from .models import SessionHistory, SessionHistoryEntry

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manages session history (last 20 sessions)."""

    def __init__(self, session_path: Path):
        """Initialize history manager.

        Args:
            session_path: Path to .session directory
        """
        self.session_path = Path(session_path)
        self.history_file = self.session_path / "history.json"

        # Load existing history
        self.data = self._load_or_create()

    def _load_or_create(self) -> SessionHistory:
        """Load existing history or create new."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data_dict = json.load(f)

                    # Convert timestamps
                    if 'entries' in data_dict:
                        for entry in data_dict['entries']:
                            if 'started_at' in entry:
                                entry['started_at'] = datetime.fromisoformat(
                                    entry['started_at']
                                )
                            if 'ended_at' in entry and entry['ended_at']:
                                entry['ended_at'] = datetime.fromisoformat(
                                    entry['ended_at']
                                )

                    return SessionHistory(**data_dict)
            except Exception as e:
                logger.error(f"Failed to load history: {e}. Creating new.")

        return SessionHistory()

    async def save(self) -> bool:
        """Save history to disk."""
        try:
            temp_path = self.history_file.with_suffix('.tmp')
            async with aiofiles.open(temp_path, 'w') as f:
                await f.write(self.data.model_dump_json(indent=2))
            temp_path.replace(self.history_file)
            return True
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False

    async def add_session(self, entry: SessionHistoryEntry):
        """Add a session to history."""
        self.data.add_entry(entry)
        await self.save()

    def get_recent_sessions(self, count: int = 5) -> List[SessionHistoryEntry]:
        """Get recent sessions."""
        return self.data.get_recent(count)
