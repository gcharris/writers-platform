"""
Bulk Upload with Intelligent Auto-Tagging

Uploads all markdown files from The Explants Series with automatically detected metadata.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from google import genai
from google.genai import types

from .config import GeminiFileSearchConfig


class FileMetadataExtractor:
    """Extract metadata from file paths and names."""

    @staticmethod
    def extract_volume(path: Path) -> Optional[int]:
        """Extract volume number from path."""
        path_str = str(path)

        if "Volume 1" in path_str or "volume 1" in path_str.lower():
            return 1
        elif "Volume 2" in path_str or "volume 2" in path_str.lower():
            return 2
        elif "Volume 3" in path_str or "volume 3" in path_str.lower():
            return 3

        return None

    @staticmethod
    def extract_category(path: Path) -> str:
        """Extract content category from path."""
        path_lower = str(path).lower()

        if "character" in path_lower:
            return "character"
        elif "world" in path_lower or "mechanics" in path_lower:
            return "worldbuilding"
        elif "chapter" in path_lower or "act" in path_lower.lower():
            return "chapter"
        elif "scene" in path_lower:
            return "scene"
        elif "outline" in path_lower:
            return "outline"
        elif "reference" in path_lower or "knowledge_base" in path_lower:
            return "reference"
        elif "voice" in path_lower or "style" in path_lower:
            return "voice"
        elif "skill" in path_lower:
            return "skill"
        elif "backup" in path_lower or "archive" in path_lower:
            return "archive"
        else:
            return "unknown"

    @staticmethod
    def extract_status(path: Path) -> str:
        """Extract file status from path and name."""
        path_str = str(path)
        filename = path.stem.lower()

        if "draft" in filename:
            return "draft"
        elif "final" in filename.lower() or "FINAL" in path.stem:
            return "final"
        elif "archive" in path_str.lower() or "backup" in path_str.lower():
            return "archived"
        elif "old" in path_str.lower():
            return "old"
        elif "Volume 1" in path_str or "Volume 2" in path_str:
            # Files in main Volume directories considered canon
            return "canon"
        else:
            return "unknown"

    @staticmethod
    def extract_scene_number(path: Path) -> Optional[str]:
        """Extract scene number (e.g., 2.3.6) from filename."""
        filename = path.stem

        # Pattern: X.Y.Z (volume.chapter.scene)
        match = re.search(r'(\d+)\.(\d+)\.(\d+)', filename)
        if match:
            return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"

        return None

    @staticmethod
    def extract_chapter_number(path: Path) -> Optional[int]:
        """Extract chapter number from path."""
        path_str = str(path)

        # Pattern: Chapter X or Chapter_X
        match = re.search(r'Chapter[_\s](\d+)', path_str, re.IGNORECASE)
        if match:
            return int(match.group(1))

        return None

    @staticmethod
    def infer_story_phase(volume: Optional[int], chapter: Optional[int]) -> Optional[int]:
        """
        Infer story phase from volume and chapter.

        Phase 1: Volume 1, Chapters 1-10 (Setup)
        Phase 2: Volume 1, Chapters 11-28 (Development)
        Phase 3: Volume 2 (Deepening)
        Phase 4: Volume 3 (Resolution)
        """
        if volume is None:
            return None

        if volume == 1:
            if chapter is not None:
                return 1 if chapter <= 10 else 2
            else:
                return 1
        elif volume == 2:
            return 3
        elif volume == 3:
            return 4

        return None

    @classmethod
    def extract_all_metadata(cls, file_path: Path, root: Path) -> Dict:
        """
        Extract all metadata from file.

        Args:
            file_path: Path to file
            root: Root directory (for relative path)

        Returns:
            Metadata dictionary
        """
        rel_path = file_path.relative_to(root)

        volume = cls.extract_volume(file_path)
        category = cls.extract_category(file_path)
        status = cls.extract_status(file_path)
        scene_number = cls.extract_scene_number(file_path)
        chapter_number = cls.extract_chapter_number(file_path)
        story_phase = cls.infer_story_phase(volume, chapter_number)

        metadata = {
            "relative_path": str(rel_path),
            "filename": file_path.name,
            "category": category,
            "status": status
        }

        if volume is not None:
            metadata["volume"] = volume
        if scene_number is not None:
            metadata["scene_number"] = scene_number
        if chapter_number is not None:
            metadata["chapter_number"] = chapter_number
        if story_phase is not None:
            metadata["story_phase"] = story_phase

        return metadata


class BulkUploader:
    """Bulk upload markdown files to Gemini File Search store."""

    def __init__(self,
                 store_id: str,
                 config: Optional[GeminiFileSearchConfig] = None):
        """
        Initialize uploader.

        Args:
            store_id: File Search store ID (corpus name)
            config: Configuration instance
        """
        self.config = config or GeminiFileSearchConfig()
        self.store_id = store_id

        if not self.config.validate_api_key():
            raise ValueError("Google API key not configured")

        self.client = genai.Client(api_key=self.config.get_google_api_key())
        self.extractor = FileMetadataExtractor()

    def upload_file(self, file_path: Path, root: Path) -> bool:
        """
        Upload a single file with metadata.

        Args:
            file_path: Path to file
            root: Root directory (for relative path)

        Returns:
            True if successful
        """
        # Extract metadata
        metadata = self.extractor.extract_all_metadata(file_path, root)

        try:
            # Upload file
            uploaded_file = self.client.files.upload(
                path=str(file_path),
                config=types.UploadFileConfig(
                    display_name=file_path.name,
                    corpus_name=self.store_id
                )
            )

            # Add to corpus with metadata
            document = self.client.files.create_document(
                corpus_name=self.store_id,
                display_name=file_path.name,
                files=[uploaded_file.name],
                metadata=metadata
            )

            return True

        except Exception as e:
            print(f"  Error: {e}")
            return False

    def upload_directory(self,
                        root_dir: Optional[Path] = None,
                        file_pattern: str = "*.md",
                        exclude_patterns: Optional[List[str]] = None,
                        dry_run: bool = False) -> Tuple[int, int, List]:
        """
        Upload all matching files from directory recursively.

        Args:
            root_dir: Root directory (default: from config)
            file_pattern: File glob pattern (default: *.md)
            exclude_patterns: Patterns to exclude
            dry_run: If True, don't actually upload

        Returns:
            Tuple of (success_count, error_count, error_list)
        """
        if root_dir is None:
            root_dir = self.config.get_story_root_path()

        if not root_dir.exists():
            raise ValueError(f"Root directory not found: {root_dir}")

        print("=" * 80)
        print("BULK UPLOAD TO GEMINI FILE SEARCH")
        print("=" * 80)
        print(f"Root directory: {root_dir}")
        print(f"Store ID: {self.store_id}")
        print(f"File pattern: {file_pattern}")
        if dry_run:
            print("DRY RUN - No files will be uploaded")
        print()

        # Find all matching files
        all_files = list(root_dir.rglob(file_pattern))

        # Apply exclusions
        exclude_patterns = exclude_patterns or [
            "*/.git/*",
            "*/node_modules/*",
            "*/__pycache__/*",
            "*/venv/*",
            "*/output/*",
            "*/.DS_Store"
        ]

        files_to_upload = []
        for file_path in all_files:
            excluded = False
            for pattern in exclude_patterns:
                if file_path.match(pattern):
                    excluded = True
                    break

            if not excluded:
                files_to_upload.append(file_path)

        print(f"Found {len(files_to_upload)} files to upload")
        print()

        if dry_run:
            print("DRY RUN - Showing first 20 files with metadata:")
            print()
            for file_path in files_to_upload[:20]:
                metadata = self.extractor.extract_all_metadata(file_path, root_dir)
                print(f"File: {file_path.name}")
                print(f"  Path: {metadata['relative_path']}")
                print(f"  Category: {metadata['category']}")
                print(f"  Status: {metadata['status']}")
                if 'volume' in metadata:
                    print(f"  Volume: {metadata['volume']}")
                if 'scene_number' in metadata:
                    print(f"  Scene: {metadata['scene_number']}")
                print()

            print(f"Total files to upload: {len(files_to_upload)}")
            return 0, 0, []

        # Upload files
        success_count = 0
        error_count = 0
        errors = []

        start_time = datetime.now()

        for i, file_path in enumerate(files_to_upload, 1):
            try:
                # Show progress
                if i % 10 == 0 or i == 1:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    rate = i / elapsed if elapsed > 0 else 0
                    remaining = (len(files_to_upload) - i) / rate if rate > 0 else 0
                    print(f"Progress: {i}/{len(files_to_upload)} "
                          f"({i/len(files_to_upload)*100:.1f}%) "
                          f"- {rate:.1f} files/sec "
                          f"- ETA: {remaining/60:.1f} min")

                # Upload file
                success = self.upload_file(file_path, root_dir)

                if success:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append((str(file_path), "Upload failed"))

            except Exception as e:
                error_count += 1
                errors.append((str(file_path), str(e)))
                print(f"  ✗ {file_path.name}: {e}")

        # Summary
        elapsed = (datetime.now() - start_time).total_seconds()
        print()
        print("=" * 80)
        print("UPLOAD COMPLETE")
        print("=" * 80)
        print(f"✓ Successfully uploaded: {success_count} files")
        print(f"✗ Errors: {error_count} files")
        print(f"Time elapsed: {elapsed/60:.1f} minutes")
        print(f"Average rate: {success_count/elapsed:.1f} files/sec")
        print()

        if errors:
            print("Errors encountered:")
            for file_path, error in errors[:10]:  # Show first 10
                print(f"  - {Path(file_path).name}: {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
            print()

        return success_count, error_count, errors


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Bulk upload files to Gemini File Search store"
    )
    parser.add_argument('--store-id', required=True,
                       help="File Search store ID (corpus name)")
    parser.add_argument('--root-dir',
                       help="Root directory (default: from config)")
    parser.add_argument('--pattern', default="*.md",
                       help="File pattern (default: *.md)")
    parser.add_argument('--dry-run', action='store_true',
                       help="Show what would be uploaded without uploading")
    parser.add_argument('--exclude', nargs='+',
                       help="Additional exclude patterns")

    args = parser.parse_args()

    # Initialize uploader
    config = GeminiFileSearchConfig()
    uploader = BulkUploader(store_id=args.store_id, config=config)

    # Set root directory
    root_dir = Path(args.root_dir) if args.root_dir else None

    # Upload
    success, errors, error_list = uploader.upload_directory(
        root_dir=root_dir,
        file_pattern=args.pattern,
        exclude_patterns=args.exclude,
        dry_run=args.dry_run
    )

    if not args.dry_run:
        print(f"Upload complete: {success} succeeded, {errors} failed")


if __name__ == "__main__":
    main()
