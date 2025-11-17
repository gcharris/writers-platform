"""Manuscript structure and storage module.

This module provides data models for organizing a manuscript into
Acts → Chapters → Scenes hierarchy with JSON-based persistence.
"""

from app.core.manuscript.structure import (
    Scene,
    Chapter,
    Act,
    Manuscript,
)
from app.core.manuscript.storage import ManuscriptStorage

__all__ = [
    "Scene",
    "Chapter",
    "Act",
    "Manuscript",
    "ManuscriptStorage",
]
