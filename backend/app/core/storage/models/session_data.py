"""Pydantic models for session state management."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path


class OpenFile(BaseModel):
    """Represents an open file with cursor position."""

    path: str
    cursor_line: int = 0
    cursor_col: int = 0
    scroll_position: int = 0


class CurrentState(BaseModel):
    """Current UI state."""

    stage: str = "creation"  # creation, writing, enhancing, analyzing, scoring
    screen: str = "dashboard"
    breadcrumb: List[str] = Field(default_factory=lambda: ["Home"])
    context: Dict[str, Any] = Field(default_factory=dict)


class RecentQuery(BaseModel):
    """Recent knowledge base query."""

    query: str
    timestamp: datetime
    source: str  # "notebooklm" (user-facing), internal routing handled by system
    answer: Optional[str] = None
    duration_ms: Optional[int] = None


class SessionData(BaseModel):
    """Complete session state."""

    # Identity
    session_id: str
    project_name: str
    created_at: datetime
    last_activity: datetime = Field(default_factory=datetime.now)
    last_save_time: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Current state
    current_state: CurrentState = Field(default_factory=CurrentState)
    open_files: List[OpenFile] = Field(default_factory=list)

    # Model preferences per stage
    model_preferences: Dict[str, str] = Field(
        default_factory=lambda: {
            "creation": "claude-sonnet-4.5",
            "writing": "claude-sonnet-4.5",
            "enhancing": "gpt-4o",
            "analyzing": "claude-sonnet-4.5",
            "scoring": "claude-sonnet-4.5",
        }
    )

    # Recent queries (last 10)
    recent_queries: List[RecentQuery] = Field(default_factory=list)

    # Metadata
    total_saves: int = 0
    dirty: bool = False  # Has unsaved changes

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Path: lambda v: str(v),
        }

    def mark_dirty(self):
        """Mark session as having unsaved changes."""
        self.dirty = True
        self.last_activity = datetime.now()

    def mark_clean(self):
        """Mark session as saved."""
        self.dirty = False
        self.last_save_time = datetime.now()
        self.total_saves += 1
