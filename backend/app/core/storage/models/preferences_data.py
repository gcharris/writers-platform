"""Pydantic models for user preferences."""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class NotebookLMConfig(BaseModel):
    """NotebookLM configuration."""

    enabled: bool = False
    notebook_url: Optional[str] = None
    last_synced: Optional[str] = None


class KeyboardShortcuts(BaseModel):
    """Keyboard shortcut customizations."""

    next_stage: str = "Tab"
    prev_stage: str = "Shift+Tab"
    save: str = "Ctrl+S"
    ask_question: str = "Ctrl+K"
    model_comparison: str = "C"
    quit: str = "Q"


class UIPreferences(BaseModel):
    """UI appearance preferences."""

    theme: str = "dark"  # "dark", "light"
    color_scheme: str = "default"  # "default", "nord", "monokai"
    show_costs: bool = True
    show_tokens: bool = False
    show_timestamps: bool = True


class Preferences(BaseModel):
    """Complete user preferences."""

    # Model preferences per stage (can override defaults)
    model_preferences: Dict[str, str] = Field(
        default_factory=lambda: {
            "creation": "claude-sonnet-4.5",
            "writing": "claude-sonnet-4.5",
            "enhancing": "gpt-4o",
            "analyzing": "claude-sonnet-4.5",
            "scoring": "claude-sonnet-4.5",
        }
    )

    # Knowledge base
    notebooklm: NotebookLMConfig = Field(default_factory=NotebookLMConfig)

    # UI
    ui: UIPreferences = Field(default_factory=UIPreferences)
    keyboard: KeyboardShortcuts = Field(default_factory=KeyboardShortcuts)

    # Auto-save
    auto_save_interval: int = 30  # seconds
    auto_save_enabled: bool = True

    # Budget
    budget_daily: Optional[float] = 5.0
    budget_weekly: Optional[float] = 30.0
    budget_monthly: Optional[float] = 100.0
    budget_warnings_enabled: bool = True

    # Defaults for new files
    default_model_writing: str = "claude-sonnet-4.5"
    default_temperature: float = 0.8
    default_max_tokens: int = 2000
