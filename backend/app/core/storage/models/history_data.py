"""Pydantic models for session history."""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SessionHistoryEntry(BaseModel):
    """Single session history entry."""

    session_id: str
    project_name: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    total_cost: float = 0.0
    total_tokens: int = 0
    files_created: List[str] = Field(default_factory=list)
    files_modified: List[str] = Field(default_factory=list)
    stages_visited: List[str] = Field(default_factory=list)
    operations_count: int = 0
    was_interrupted: bool = False  # Crashed/force quit

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SessionHistory(BaseModel):
    """Complete session history (last 20 sessions)."""

    entries: List[SessionHistoryEntry] = Field(default_factory=list)
    max_entries: int = 20

    def add_entry(self, entry: SessionHistoryEntry):
        """Add new session entry, maintaining max limit."""
        self.entries.insert(0, entry)  # Add to front (most recent first)

        # Trim to max entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[:self.max_entries]

    def get_recent(self, count: int = 5) -> List[SessionHistoryEntry]:
        """Get most recent N sessions."""
        return self.entries[:count]

    def get_total_cost(self) -> float:
        """Get total cost across all sessions."""
        return sum(e.total_cost for e in self.entries)

    def get_total_sessions(self) -> int:
        """Get total number of sessions."""
        return len(self.entries)
