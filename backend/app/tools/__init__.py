"""Tools for Writers Factory.

This module provides user-facing tools that wrap workflows and provide
enhanced functionality:
- Model comparison with visual diffs
- Preference tracking
- Side-by-side output display
- Manuscript importing from existing files
"""

from .model_comparison import ModelComparisonTool, ComparisonResult
from .manuscript_importer import (
    ManuscriptImporter,
    import_explants_volume_1,
    import_from_directory,
)

__all__ = [
    "ModelComparisonTool",
    "ComparisonResult",
    "ManuscriptImporter",
    "import_explants_volume_1",
    "import_from_directory",
]
