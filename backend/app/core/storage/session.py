"""Session management with auto-save and crash recovery."""

import asyncio
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import aiofiles

from .models import SessionData, CurrentState, OpenFile, RecentQuery

logger = logging.getLogger(__name__)


class Session:
    """Manages session state with auto-save and crash recovery.

    Features:
    - Auto-save every 30s (configurable, non-blocking)
    - Atomic writes (never corrupt session files)
    - Crash recovery (detect interrupted sessions)
    - Change tracking (only save when dirty)
    - File-based storage (no database needed)
    """

    def __init__(self, project_path: Path, auto_save_interval: int = 30):
        """Initialize session.

        Args:
            project_path: Path to project root (contains .session/)
            auto_save_interval: Auto-save interval in seconds
        """
        self.project_path = Path(project_path)
        self.session_path = self.project_path / ".session"
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.auto_save_interval = auto_save_interval
        self._auto_save_task: Optional[asyncio.Task] = None
        self._saving = False  # Prevent concurrent saves

        # Load or create session
        self.data = self._load_or_create()

        logger.info(
            f"Session initialized: {self.data.session_id} "
            f"(project: {self.data.project_name})"
        )

    def _generate_session_id(self) -> str:
        """Generate unique session ID: YYYY-MM-DD-HHMMSS."""
        return datetime.now().strftime("%Y-%m-%d-%H%M%S")

    def _load_or_create(self) -> SessionData:
        """Load existing session or create new one."""
        current_file = self.session_path / "current.json"

        if current_file.exists():
            try:
                with open(current_file, 'r') as f:
                    data_dict = json.load(f)
                    # Convert ISO strings back to datetime
                    if 'created_at' in data_dict:
                        data_dict['created_at'] = datetime.fromisoformat(
                            data_dict['created_at']
                        )
                    if 'last_activity' in data_dict:
                        data_dict['last_activity'] = datetime.fromisoformat(
                            data_dict['last_activity']
                        )
                    if 'last_save_time' in data_dict and data_dict['last_save_time']:
                        data_dict['last_save_time'] = datetime.fromisoformat(
                            data_dict['last_save_time']
                        )

                    # Convert recent_queries timestamps
                    if 'recent_queries' in data_dict:
                        for query in data_dict['recent_queries']:
                            if 'timestamp' in query:
                                query['timestamp'] = datetime.fromisoformat(
                                    query['timestamp']
                                )

                    return SessionData(**data_dict)
            except Exception as e:
                logger.error(f"Failed to load session: {e}. Creating new session.")
                # Backup corrupted file
                backup_path = current_file.with_suffix('.corrupted')
                current_file.rename(backup_path)
                logger.info(f"Backed up corrupted session to {backup_path}")

        # Create new session
        session_id = self._generate_session_id()
        return SessionData(
            session_id=session_id,
            project_name=self.project_path.name,
            created_at=datetime.now(),
            current_state=CurrentState(
                stage="creation",
                screen="dashboard",
                breadcrumb=["Home"]
            )
        )

    def was_interrupted(self) -> bool:
        """Check if previous session was interrupted (crashed).

        Returns:
            True if session was not cleanly closed
        """
        if self.data.completed_at is not None:
            return False  # Was cleanly closed

        # If last activity > 5 minutes ago, likely interrupted
        if self.data.last_activity:
            time_since_activity = datetime.now() - self.data.last_activity
            return time_since_activity > timedelta(minutes=5)

        return False

    async def save(self) -> bool:
        """Save session to disk (atomic write).

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.data.dirty and self.data.total_saves > 0:
            logger.debug("Session unchanged, skipping save")
            return True  # No changes to save

        if self._saving:
            logger.debug("Save already in progress, skipping")
            return True  # Don't queue up multiple saves

        self._saving = True
        try:
            await self._atomic_write(
                self.session_path / "current.json",
                self.data.model_dump_json(indent=2)
            )
            self.data.mark_clean()
            logger.debug(f"Session saved (total saves: {self.data.total_saves})")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False
        finally:
            self._saving = False

    async def _atomic_write(self, file_path: Path, content: str):
        """Write to temp file, then rename (atomic on POSIX).

        Args:
            file_path: Target file path
            content: Content to write
        """
        temp_path = file_path.with_suffix('.tmp')
        try:
            async with aiofiles.open(temp_path, 'w') as f:
                await f.write(content)
            # Atomic rename
            temp_path.replace(file_path)
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise e

    def start_auto_save(self):
        """Start auto-save background task."""
        if self._auto_save_task is None or self._auto_save_task.done():
            self._auto_save_task = asyncio.create_task(self._auto_save_worker())
            logger.info(f"Auto-save started (interval: {self.auto_save_interval}s)")

    def stop_auto_save(self):
        """Stop auto-save background task."""
        if self._auto_save_task and not self._auto_save_task.done():
            self._auto_save_task.cancel()
            logger.info("Auto-save stopped")

    async def _auto_save_worker(self):
        """Background worker for auto-save."""
        try:
            while True:
                await asyncio.sleep(self.auto_save_interval)
                await self.save()
        except asyncio.CancelledError:
            logger.debug("Auto-save worker cancelled")
            raise

    async def close(self):
        """Close session cleanly."""
        self.stop_auto_save()

        # Mark as completed
        self.data.completed_at = datetime.now()
        self.data.mark_dirty()

        # Final save
        await self.save()

        logger.info(f"Session closed: {self.data.session_id}")

    # Convenience methods for updating state

    def set_stage(self, stage: str):
        """Set current stage."""
        self.data.current_state.stage = stage
        self.data.mark_dirty()

    def set_screen(self, screen: str):
        """Set current screen."""
        self.data.current_state.screen = screen
        self.data.mark_dirty()

    def set_breadcrumb(self, breadcrumb: list[str]):
        """Set breadcrumb trail."""
        self.data.current_state.breadcrumb = breadcrumb
        self.data.mark_dirty()

    def add_open_file(self, path: str, cursor_line: int = 0, cursor_col: int = 0):
        """Add an open file."""
        # Check if already open
        for file in self.data.open_files:
            if file.path == path:
                file.cursor_line = cursor_line
                file.cursor_col = cursor_col
                self.data.mark_dirty()
                return

        # Add new file
        self.data.open_files.append(
            OpenFile(path=path, cursor_line=cursor_line, cursor_col=cursor_col)
        )
        self.data.mark_dirty()

    def remove_open_file(self, path: str):
        """Remove an open file."""
        self.data.open_files = [
            f for f in self.data.open_files if f.path != path
        ]
        self.data.mark_dirty()

    def add_recent_query(self, query: str, source: str, answer: Optional[str] = None):
        """Add a recent query."""
        recent_query = RecentQuery(
            query=query,
            timestamp=datetime.now(),
            source=source,
            answer=answer
        )
        self.data.recent_queries.insert(0, recent_query)

        # Keep only last 10
        if len(self.data.recent_queries) > 10:
            self.data.recent_queries = self.data.recent_queries[:10]

        self.data.mark_dirty()

    def set_model_preference(self, stage: str, model: str):
        """Set model preference for a stage."""
        self.data.model_preferences[stage] = model
        self.data.mark_dirty()

    def get_model_preference(self, stage: str) -> str:
        """Get model preference for a stage."""
        return self.data.model_preferences.get(stage, "claude-sonnet-4.5")

    def get_time_since_save(self) -> Optional[timedelta]:
        """Get time since last save."""
        if self.data.last_save_time:
            return datetime.now() - self.data.last_save_time
        return None

    def get_save_status(self) -> str:
        """Get human-readable save status."""
        if self._saving:
            return "Saving..."

        if self.data.dirty:
            return "Unsaved changes"

        time_since = self.get_time_since_save()
        if time_since:
            seconds = int(time_since.total_seconds())
            if seconds < 60:
                return f"Auto-saved {seconds}s ago"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"Auto-saved {minutes}m ago"
            else:
                hours = seconds // 3600
                return f"Auto-saved {hours}h ago"

        return "Not saved yet"
