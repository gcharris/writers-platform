"""Manuscript importer for converting existing files to manuscript structure.

Supports importing from various formats:
- Markdown files with naming conventions (e.g., "1.2.3 Scene Title.md")
- Directory-based organization (PART 1/, PART 2/, etc.)
- Automatic structure detection
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import logging

from factory.core.manuscript import Manuscript, Act, Chapter, Scene

logger = logging.getLogger(__name__)


class ManuscriptImporter:
    """Import existing manuscript files into structured format.

    Supports:
    - Parsing numbered scene files (e.g., "1.2.3 Scene Title.md")
    - Organizing by acts/parts (e.g., "PART 1/", "PART 2/")
    - Extracting content from markdown files
    - Preserving scene order and hierarchy
    """

    # Regex patterns for file parsing
    SCENE_FILE_PATTERN = r"^(\d+)\.(\d+)\.(\d+)\s+(.+)\.md$"
    PART_DIR_PATTERN = r"^PART\s+(\d+)$"

    def __init__(self, source_path: Path):
        """Initialize importer.

        Args:
            source_path: Root directory containing manuscript files
        """
        self.source_path = Path(source_path)

        if not self.source_path.exists():
            raise ValueError(f"Source path does not exist: {source_path}")

        if not self.source_path.is_dir():
            raise ValueError(f"Source path is not a directory: {source_path}")

    def import_manuscript(
        self,
        title: str,
        author: str = "",
        act_prefix: str = "Act",
        chapter_prefix: str = "Chapter",
    ) -> Manuscript:
        """Import entire manuscript from source directory.

        Args:
            title: Manuscript title
            author: Author name
            act_prefix: Prefix for act titles (e.g., "Act" → "Act 1")
            chapter_prefix: Prefix for chapter titles (e.g., "Chapter" → "Chapter 1")

        Returns:
            Manuscript with imported content
        """
        logger.info(f"Importing manuscript from {self.source_path}")

        manuscript = Manuscript(title=title, author=author)

        # Find all part/act directories
        part_dirs = self._find_part_directories()

        if not part_dirs:
            # No part directories, try flat structure
            logger.warning("No PART directories found, trying flat structure")
            scenes = self._find_scene_files(self.source_path)
            if scenes:
                act = manuscript.add_act(title=f"{act_prefix} 1", act_id="act-1")
                self._import_scenes_to_act(act, scenes, chapter_prefix)
        else:
            # Import each part as an act
            for part_num, part_dir in sorted(part_dirs.items()):
                logger.info(f"Importing {part_dir.name} as {act_prefix} {part_num}")

                act = manuscript.add_act(
                    title=f"{act_prefix} {part_num}",
                    act_id=f"act-{part_num}",
                )

                scenes = self._find_scene_files(part_dir)
                self._import_scenes_to_act(act, scenes, chapter_prefix)

        logger.info(
            f"Import complete: {len(manuscript.acts)} acts, "
            f"{manuscript.structure_summary['chapters']} chapters, "
            f"{manuscript.structure_summary['scenes']} scenes, "
            f"{manuscript.structure_summary['words']} words"
        )

        return manuscript

    def _find_part_directories(self) -> Dict[int, Path]:
        """Find all PART directories.

        Returns:
            Dictionary mapping part number to directory path
        """
        part_dirs = {}

        for item in self.source_path.iterdir():
            if not item.is_dir():
                continue

            match = re.match(self.PART_DIR_PATTERN, item.name, re.IGNORECASE)
            if match:
                part_num = int(match.group(1))
                part_dirs[part_num] = item

        return part_dirs

    def _find_scene_files(self, directory: Path) -> List[Tuple[int, int, int, str, Path]]:
        """Find all scene files in directory.

        Args:
            directory: Directory to search

        Returns:
            List of tuples: (act_num, chapter_num, scene_num, title, file_path)
        """
        scenes = []

        for item in directory.rglob("*.md"):
            if not item.is_file():
                continue

            match = re.match(self.SCENE_FILE_PATTERN, item.name)
            if match:
                act_num = int(match.group(1))
                chapter_num = int(match.group(2))
                scene_num = int(match.group(3))
                title = match.group(4).strip()

                scenes.append((act_num, chapter_num, scene_num, title, item))

        return scenes

    def _import_scenes_to_act(
        self,
        act: Act,
        scenes: List[Tuple[int, int, int, str, Path]],
        chapter_prefix: str,
    ) -> None:
        """Import scenes into an act, organizing by chapters.

        Args:
            act: Act to import into
            scenes: List of scene tuples
            chapter_prefix: Prefix for chapter titles
        """
        # Group scenes by chapter
        chapters_dict: Dict[int, List[Tuple[int, str, Path]]] = {}

        for act_num, chapter_num, scene_num, title, file_path in scenes:
            if chapter_num not in chapters_dict:
                chapters_dict[chapter_num] = []

            chapters_dict[chapter_num].append((scene_num, title, file_path))

        # Create chapters and import scenes
        for chapter_num in sorted(chapters_dict.keys()):
            chapter = act.add_chapter(
                title=f"{chapter_prefix} {chapter_num}",
                chapter_id=f"chapter-{act.id}-{chapter_num}",
            )

            # Import scenes in order
            for scene_num, title, file_path in sorted(chapters_dict[chapter_num]):
                self._import_scene_to_chapter(
                    chapter,
                    title,
                    file_path,
                    scene_id=f"scene-{act.id}-{chapter.id}-{scene_num}",
                )

    def _import_scene_to_chapter(
        self,
        chapter: Chapter,
        title: str,
        file_path: Path,
        scene_id: str,
    ) -> Scene:
        """Import a single scene into a chapter.

        Args:
            chapter: Chapter to import into
            title: Scene title
            file_path: Path to scene markdown file
            scene_id: Scene identifier

        Returns:
            Created Scene instance
        """
        # Read file content
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            content = f"[Error reading file: {e}]"

        # Clean content (remove any metadata headers, etc.)
        content = self._clean_scene_content(content)

        # Create scene
        scene = chapter.add_scene(
            title=title,
            content=content,
            scene_id=scene_id,
        )

        logger.debug(f"Imported scene: {title} ({scene.word_count} words)")

        return scene

    def _clean_scene_content(self, content: str) -> str:
        """Clean and normalize scene content.

        Removes common metadata, extra whitespace, etc.

        Args:
            content: Raw file content

        Returns:
            Cleaned content
        """
        # Remove common metadata patterns
        # (e.g., front matter, comments, etc.)

        # For now, just strip leading/trailing whitespace
        # Can be extended based on actual file format
        content = content.strip()

        return content


def import_explants_volume_1(
    source_dir: Path,
    title: str = "The Explants - Volume 1",
    author: str = "",
) -> Manuscript:
    """Import The Explants Volume 1 from markdown files.

    Convenience function for importing the Explants manuscript.

    Args:
        source_dir: Path to "Volume 1" directory
        title: Manuscript title
        author: Author name

    Returns:
        Manuscript with imported content
    """
    importer = ManuscriptImporter(source_dir)
    return importer.import_manuscript(title=title, author=author)


def import_from_directory(
    source_dir: Path,
    title: str,
    author: str = "",
    act_prefix: str = "Act",
    chapter_prefix: str = "Chapter",
) -> Manuscript:
    """Import manuscript from any directory structure.

    Generic import function that can be used for any project.

    Args:
        source_dir: Root directory containing manuscript files
        title: Manuscript title
        author: Author name
        act_prefix: Prefix for act titles
        chapter_prefix: Prefix for chapter titles

    Returns:
        Manuscript with imported content
    """
    importer = ManuscriptImporter(source_dir)
    return importer.import_manuscript(
        title=title,
        author=author,
        act_prefix=act_prefix,
        chapter_prefix=chapter_prefix,
    )
