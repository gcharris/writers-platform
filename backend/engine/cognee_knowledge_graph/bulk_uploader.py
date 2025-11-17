"""
Bulk uploader for The Explants corpus to Cognee Knowledge Graph.

Handles:
- Automatic metadata extraction from file paths
- Batch processing with progress tracking
- Resume capability for interrupted uploads
- Volume, category, status, scene number tagging
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import json

try:
    import cognee
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False

from .config import CogneeConfig
from .cognee_graph import CogneeKnowledgeGraph


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        elif "chapter" in path_lower or "act" in path_lower:
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
        Phase 3: Volume 2 (Escalation)
        Phase 4: Volume 3 (Resolution)
        """
        if volume == 1:
            if chapter and chapter <= 10:
                return 1
            elif chapter and chapter >= 11:
                return 2
            else:
                return 1  # Default to Phase 1 for Volume 1
        elif volume == 2:
            return 3
        elif volume == 3:
            return 4

        return None

    @classmethod
    def extract_all_metadata(cls, path: Path) -> Dict[str, any]:
        """
        Extract all metadata from a file path.

        Returns:
            Dictionary with all extracted metadata
        """
        volume = cls.extract_volume(path)
        chapter = cls.extract_chapter_number(path)

        metadata = {
            'file_path': str(path),
            'filename': path.name,
            'volume': volume,
            'chapter': chapter,
            'category': cls.extract_category(path),
            'status': cls.extract_status(path),
            'scene_number': cls.extract_scene_number(path),
            'story_phase': cls.infer_story_phase(volume, chapter),
        }

        return metadata


class BulkUploader:
    """
    Bulk upload The Explants corpus to Cognee Knowledge Graph.

    Handles:
    - Finding all markdown files in the project
    - Extracting metadata automatically
    - Batch processing with progress tracking
    - Resume capability
    - Statistics and reporting
    """

    def __init__(
        self,
        knowledge_graph: CogneeKnowledgeGraph,
        project_root: Path,
    ):
        """
        Initialize bulk uploader.

        Args:
            knowledge_graph: CogneeKnowledgeGraph instance
            project_root: Root directory of The Explants project
        """
        self.kg = knowledge_graph
        self.project_root = project_root
        self.metadata_extractor = FileMetadataExtractor()

        # Statistics
        self.stats = {
            'total_files': 0,
            'uploaded': 0,
            'skipped': 0,
            'errors': 0,
            'by_volume': {1: 0, 2: 0, 3: 0, None: 0},
            'by_category': {},
            'by_status': {},
        }

        # State file for resume capability
        self.state_file = project_root / '.cognee_upload_state.json'

    def find_markdown_files(self, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
        """
        Find all markdown files in the project.

        Args:
            exclude_patterns: List of path patterns to exclude

        Returns:
            List of Path objects
        """
        if exclude_patterns is None:
            exclude_patterns = [
                'node_modules',
                '.git',
                'venv',
                '__pycache__',
                '.cognee',
            ]

        markdown_files = []
        for md_file in self.project_root.rglob('*.md'):
            # Check if file should be excluded
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(md_file):
                    should_exclude = True
                    break

            if not should_exclude:
                markdown_files.append(md_file)

        logger.info(f"Found {len(markdown_files)} markdown files")
        return markdown_files

    def load_state(self) -> Dict[str, any]:
        """Load upload state from disk."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {'uploaded_files': []}

    def save_state(self, uploaded_files: List[str]):
        """Save upload state to disk."""
        state = {
            'uploaded_files': uploaded_files,
            'timestamp': datetime.now().isoformat(),
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    async def upload_file(self, file_path: Path) -> bool:
        """
        Upload a single file to the knowledge graph.

        Args:
            file_path: Path to the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip empty files
            if not content.strip():
                logger.warning(f"Skipping empty file: {file_path}")
                self.stats['skipped'] += 1
                return False

            # Extract metadata
            metadata = self.metadata_extractor.extract_all_metadata(file_path)

            # Add to knowledge graph
            await self.kg.add_document(content, metadata=metadata)

            # Update statistics
            self.stats['uploaded'] += 1
            volume = metadata.get('volume')
            self.stats['by_volume'][volume] = self.stats['by_volume'].get(volume, 0) + 1

            category = metadata.get('category', 'unknown')
            self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1

            status = metadata.get('status', 'unknown')
            self.stats['by_status'][status] = self.stats['by_status'].get(status, 0) + 1

            logger.info(f"✓ Uploaded: {file_path.name}")
            return True

        except Exception as e:
            logger.error(f"✗ Error uploading {file_path}: {e}")
            self.stats['errors'] += 1
            return False

    async def upload_all(
        self,
        exclude_patterns: Optional[List[str]] = None,
        batch_size: int = 10,
        resume: bool = True,
    ) -> Dict[str, any]:
        """
        Upload all markdown files to the knowledge graph.

        Args:
            exclude_patterns: List of path patterns to exclude
            batch_size: Number of files to process before saving state
            resume: Whether to resume from previous upload

        Returns:
            Statistics dictionary
        """
        # Find all files
        files = self.find_markdown_files(exclude_patterns)
        self.stats['total_files'] = len(files)

        # Load state for resume
        uploaded_files = []
        if resume:
            state = self.load_state()
            uploaded_files = state.get('uploaded_files', [])
            logger.info(f"Resuming upload, {len(uploaded_files)} files already uploaded")

        # Filter out already uploaded files
        files_to_upload = [f for f in files if str(f) not in uploaded_files]
        logger.info(f"Uploading {len(files_to_upload)} files...")

        # Upload in batches
        for i in range(0, len(files_to_upload), batch_size):
            batch = files_to_upload[i:i+batch_size]

            logger.info(f"\nProcessing batch {i//batch_size + 1}/{(len(files_to_upload)-1)//batch_size + 1}")

            for file_path in batch:
                success = await self.upload_file(file_path)
                if success:
                    uploaded_files.append(str(file_path))

            # Save state after each batch
            self.save_state(uploaded_files)

            # Small delay to avoid overwhelming the system
            await asyncio.sleep(0.5)

        logger.info("\n" + "="*60)
        logger.info("Upload complete! Now run cognify to build the knowledge graph.")
        logger.info("="*60)

        return self.stats

    async def upload_and_cognify(
        self,
        exclude_patterns: Optional[List[str]] = None,
        batch_size: int = 10,
        resume: bool = True,
    ) -> Dict[str, any]:
        """
        Upload all files and then run cognify to build the knowledge graph.

        This is the recommended method for a complete setup.

        Args:
            exclude_patterns: List of path patterns to exclude
            batch_size: Number of files to process before saving state
            resume: Whether to resume from previous upload

        Returns:
            Statistics dictionary
        """
        # Upload all files
        stats = await self.upload_all(exclude_patterns, batch_size, resume)

        # Build the knowledge graph
        logger.info("\nBuilding knowledge graph (this may take several minutes)...")
        await self.kg.cognify()

        logger.info("\n" + "="*60)
        logger.info("Knowledge graph ready!")
        logger.info("="*60)

        return stats

    def print_statistics(self):
        """Print upload statistics."""
        print("\n" + "="*60)
        print("UPLOAD STATISTICS")
        print("="*60)
        print(f"Total files found: {self.stats['total_files']}")
        print(f"Successfully uploaded: {self.stats['uploaded']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")

        print("\nBy Volume:")
        for volume, count in sorted(self.stats['by_volume'].items()):
            vol_name = f"Volume {volume}" if volume else "No volume"
            print(f"  {vol_name}: {count}")

        print("\nBy Category:")
        for category, count in sorted(self.stats['by_category'].items()):
            print(f"  {category}: {count}")

        print("\nBy Status:")
        for status, count in sorted(self.stats['by_status'].items()):
            print(f"  {status}: {count}")

        print("="*60)


async def bulk_upload_project(
    project_root: Path,
    config: Optional[CogneeConfig] = None,
    exclude_patterns: Optional[List[str]] = None,
    cognify: bool = True,
) -> Dict[str, any]:
    """
    Convenience function to bulk upload The Explants project.

    Args:
        project_root: Root directory of The Explants project
        config: CogneeConfig (creates default if not provided)
        exclude_patterns: List of path patterns to exclude
        cognify: Whether to run cognify after upload (recommended)

    Returns:
        Statistics dictionary

    Example:
        >>> from pathlib import Path
        >>> stats = await bulk_upload_project(Path("/home/user/The-Explants"))
        >>> print(f"Uploaded {stats['uploaded']} files")
    """
    # Create knowledge graph
    kg = CogneeKnowledgeGraph(config)
    await kg.initialize()

    # Create uploader
    uploader = BulkUploader(kg, project_root)

    # Upload
    if cognify:
        stats = await uploader.upload_and_cognify(exclude_patterns)
    else:
        stats = await uploader.upload_all(exclude_patterns)

    # Print statistics
    uploader.print_statistics()

    return stats


if __name__ == "__main__":
    # Test bulk upload
    import sys

    async def main():
        project_root = Path("/home/user/The-Explants")

        if len(sys.argv) > 1:
            project_root = Path(sys.argv[1])

        logger.info(f"Starting bulk upload from: {project_root}")

        stats = await bulk_upload_project(
            project_root,
            cognify=True,  # Build knowledge graph after upload
        )

        print(f"\n✓ Successfully uploaded {stats['uploaded']} files")

    asyncio.run(main())
