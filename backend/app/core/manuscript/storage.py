"""Manuscript storage and persistence with file-based scene storage.

NEW ARCHITECTURE (Sprint 9):
- manifest.json: Structure and metadata only (NO content)
- Individual .md files: One file per scene
- Directory structure: manuscript/ACT_1/CHAPTER_1/scene-id.md
- Direct file editing: Compatible with any text editor (VS Code, Cursor AI, etc.)
"""

import json
import shutil
import re
from pathlib import Path
from typing import Optional
from datetime import datetime

from factory.core.manuscript.structure import Manuscript, Scene


class ManuscriptStorage:
    """Handles manuscript persistence with file-based scene storage.

    NEW Storage format (Sprint 9):
    - manifest.json: Structure + metadata (NO scene content)
    - scenes/: Individual .md files organized by act/chapter
      Example: scenes/ACT_1/CHAPTER_1/scene-abc123.md

    Attributes:
        storage_path: Path to storage directory
        backup_enabled: Whether to create backup before saving
    """

    MANIFEST_FILE = "manifest.json"
    BACKUP_SUFFIX = ".backup"
    SCENES_DIR = "scenes"

    def __init__(self, storage_path: Path, backup_enabled: bool = True):
        """Initialize manuscript storage.

        Args:
            storage_path: Directory for manuscript storage
            backup_enabled: Create backup before each save
        """
        self.storage_path = Path(storage_path)
        self.backup_enabled = backup_enabled

    def save(self, manuscript: Manuscript) -> bool:
        """Save manuscript with file-based scene storage.

        NEW BEHAVIOR (Sprint 9):
        - Saves manifest.json WITHOUT scene content
        - Saves each scene to individual .md file
        - Organizes files by act/chapter directories

        Args:
            manuscript: Manuscript to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure storage directory exists
            self.storage_path.mkdir(parents=True, exist_ok=True)

            # Save each scene to individual .md file
            scenes_dir = self.storage_path / self.SCENES_DIR
            scenes_dir.mkdir(parents=True, exist_ok=True)

            # First, save all scene files and update file_paths
            for act in manuscript.acts:
                act_dir_name = self._sanitize_dirname(f"{act.id}")
                act_dir = scenes_dir / act_dir_name

                for chapter in act.chapters:
                    chapter_dir_name = self._sanitize_dirname(f"{chapter.id}")
                    chapter_dir = act_dir / chapter_dir_name
                    chapter_dir.mkdir(parents=True, exist_ok=True)

                    for scene in chapter.scenes:
                        # Generate file path
                        scene_file = chapter_dir / f"{scene.id}.md"
                        scene_file_relative = scene_file.relative_to(self.storage_path)

                        # Update scene's file_path
                        scene.file_path = str(scene_file_relative)

                        # Save scene content to file
                        self._save_scene_file(scene, scene_file, act.title, chapter.title)

            # Now save manifest WITHOUT content
            manifest_path = self.storage_path / self.MANIFEST_FILE

            # Create backup if file exists
            if self.backup_enabled and manifest_path.exists():
                self._create_backup(manifest_path)

            # Convert to dictionary WITHOUT content
            data = manuscript.to_dict(include_content=False)

            # Add metadata
            data["_metadata"] = {
                "saved_at": datetime.now().isoformat(),
                "version": "2.0",  # New version for file-based storage
                "storage_type": "file_based",
            }

            # Atomic write: write to temp file, then rename
            temp_path = self.storage_path / f"{self.MANIFEST_FILE}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic rename
            temp_path.replace(manifest_path)

            return True

        except Exception as e:
            print(f"Error saving manuscript: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load(self) -> Optional[Manuscript]:
        """Load manuscript from file-based storage.

        NEW BEHAVIOR (Sprint 9):
        - Loads manifest.json (structure only)
        - Loads scene content from individual .md files
        - Falls back to content in manifest if file doesn't exist (backward compatible)

        Returns:
            Manuscript instance if successful, None otherwise
        """
        try:
            manifest_path = self.storage_path / self.MANIFEST_FILE

            if not manifest_path.exists():
                return None

            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Remove internal metadata before creating manuscript
            metadata = data.pop("_metadata", {})
            storage_type = metadata.get("storage_type", "embedded")  # For backward compatibility

            # Create manuscript from structure
            manuscript = Manuscript.from_dict(data)

            # Load scene content from files if using file-based storage
            if storage_type == "file_based":
                for act in manuscript.acts:
                    for chapter in act.chapters:
                        for scene in chapter.scenes:
                            if scene.file_path:
                                # Load scene content from file
                                scene_file = self.storage_path / scene.file_path
                                if scene_file.exists():
                                    content = scene_file.read_text(encoding="utf-8")
                                    # Extract actual content (skip metadata header if present)
                                    scene.content = self._extract_content_from_md(content)
                                    scene.update_content(scene.content)  # Recalculate word count

            return manuscript

        except Exception as e:
            print(f"Error loading manuscript: {e}")
            import traceback
            traceback.print_exc()

            # Try to load from backup
            if self.backup_enabled:
                return self._load_from_backup()

            return None

    def save_scene(self, manuscript: Manuscript, scene_id: str, content: str) -> bool:
        """Save a single scene's content to its file.

        NEW METHOD (Sprint 9): Direct file editing support

        Args:
            manuscript: Manuscript containing the scene
            scene_id: Scene identifier
            content: New content for the scene

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the scene
            scene = manuscript.get_scene(scene_id)
            if not scene:
                print(f"Scene {scene_id} not found")
                return False

            # Update scene content
            scene.update_content(content)

            # Save to file
            if scene.file_path:
                scene_file = self.storage_path / scene.file_path

                # Find act and chapter for metadata
                act_title = None
                chapter_title = None
                for act in manuscript.acts:
                    for chapter in act.chapters:
                        if scene in chapter.scenes:
                            act_title = act.title
                            chapter_title = chapter.title
                            break
                    if act_title:
                        break

                self._save_scene_file(scene, scene_file, act_title or "", chapter_title or "")

                # Update manifest with new word count
                self.save(manuscript)

                return True

            return False

        except Exception as e:
            print(f"Error saving scene: {e}")
            return False

    def load_scene(self, scene_id: str, file_path: str) -> Optional[str]:
        """Load a single scene's content from its file.

        NEW METHOD (Sprint 9): Direct file reading

        Args:
            scene_id: Scene identifier
            file_path: Relative path to scene file

        Returns:
            Scene content if successful, None otherwise
        """
        try:
            scene_file = self.storage_path / file_path
            if scene_file.exists():
                content = scene_file.read_text(encoding="utf-8")
                return self._extract_content_from_md(content)
            return None

        except Exception as e:
            print(f"Error loading scene {scene_id}: {e}")
            return None

    def _save_scene_file(self, scene: Scene, file_path: Path, act_title: str, chapter_title: str) -> None:
        """Save scene content to markdown file with metadata header.

        Args:
            scene: Scene to save
            file_path: Path to scene file
            act_title: Title of containing act
            chapter_title: Title of containing chapter
        """
        # Create markdown with metadata header
        lines = [
            "---",
            f"id: {scene.id}",
            f"title: {scene.title}",
            f"act: {act_title}",
            f"chapter: {chapter_title}",
            f"word_count: {scene.word_count}",
            "---",
            "",
        ]

        if scene.notes:
            lines.extend([
                "## Notes",
                "",
                scene.notes,
                "",
                "---",
                "",
            ])

        lines.append(scene.content)

        file_path.write_text("\n".join(lines), encoding="utf-8")

    def _extract_content_from_md(self, markdown: str) -> str:
        """Extract scene content from markdown file (skip metadata header).

        Args:
            markdown: Full markdown file content

        Returns:
            Scene content only
        """
        # Split by metadata delimiter
        parts = markdown.split("---")

        if len(parts) >= 3:
            # Format: --- metadata --- content
            content = "---".join(parts[2:]).strip()

            # Check if there's a notes section
            if "## Notes" in content:
                # Split at last --- before actual content
                content_parts = content.split("---")
                if len(content_parts) > 1:
                    content = content_parts[-1].strip()

            return content

        # No metadata found, return as-is
        return markdown.strip()

    def _sanitize_dirname(self, name: str) -> str:
        """Sanitize directory name to be filesystem-safe.

        Args:
            name: Original name

        Returns:
            Sanitized name
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        return sanitized or "unnamed"

    def exists(self) -> bool:
        """Check if manuscript file exists.

        Returns:
            True if manifest file exists
        """
        manifest_path = self.storage_path / self.MANIFEST_FILE
        return manifest_path.exists()

    def delete(self) -> bool:
        """Delete manuscript and all associated files.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.storage_path.exists():
                shutil.rmtree(self.storage_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting manuscript: {e}")
            return False

    def _create_backup(self, manifest_path: Path) -> None:
        """Create backup of manifest file.

        Args:
            manifest_path: Path to manifest file
        """
        backup_path = Path(str(manifest_path) + self.BACKUP_SUFFIX)
        shutil.copy2(manifest_path, backup_path)

    def _load_from_backup(self) -> Optional[Manuscript]:
        """Attempt to load from backup file.

        Returns:
            Manuscript instance if successful, None otherwise
        """
        try:
            backup_path = self.storage_path / (self.MANIFEST_FILE + self.BACKUP_SUFFIX)

            if not backup_path.exists():
                return None

            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            data.pop("_metadata", None)
            return Manuscript.from_dict(data)

        except Exception as e:
            print(f"Error loading from backup: {e}")
            return None

    @classmethod
    def create_new(cls, storage_path: Path, title: str, author: str = "") -> "ManuscriptStorage":
        """Create new manuscript storage with empty manuscript.

        Args:
            storage_path: Directory for storage
            title: Manuscript title
            author: Author name

        Returns:
            ManuscriptStorage instance with saved empty manuscript
        """
        storage = cls(storage_path)
        manuscript = Manuscript(title=title, author=author)
        storage.save(manuscript)
        return storage
