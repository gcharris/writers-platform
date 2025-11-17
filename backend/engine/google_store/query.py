"""
Google File Store Query System

Enables AI agents to autonomously query and retrieve contextual information
from Google Cloud Storage before writing scenes, chapters, or dialogue.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from google.cloud import storage
from google.oauth2 import service_account

from .config import GoogleStoreConfig


@dataclass
class ContextPackage:
    """Package of context information retrieved for an agent."""
    characters: List[Dict[str, Any]]
    worldbuilding: List[Dict[str, Any]]
    previous_chapters: List[Dict[str, Any]]
    scenes: List[Dict[str, Any]]
    motifs: List[Dict[str, Any]]
    research: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    def to_prompt_context(self) -> str:
        """Convert context package to a formatted string for AI prompts."""
        sections = []

        if self.characters:
            sections.append("## CHARACTERS\n")
            for char in self.characters:
                sections.append(f"### {char.get('name', 'Unknown')}\n")
                sections.append(f"{char.get('description', '')}\n")

        if self.worldbuilding:
            sections.append("\n## WORLDBUILDING\n")
            for item in self.worldbuilding:
                sections.append(f"### {item.get('title', 'Unknown')}\n")
                sections.append(f"{item.get('content', '')}\n")

        if self.previous_chapters:
            sections.append("\n## PREVIOUS CHAPTERS\n")
            for chapter in self.previous_chapters:
                sections.append(f"### Chapter {chapter.get('number', '?')}: {chapter.get('title', '')}\n")
                sections.append(f"{chapter.get('summary', chapter.get('content', ''))}\n")

        if self.motifs:
            sections.append("\n## RECURRING MOTIFS & THEMES\n")
            for motif in self.motifs:
                sections.append(f"- {motif.get('name', '')}: {motif.get('description', '')}\n")

        if self.research:
            sections.append("\n## RESEARCH & REFERENCES\n")
            for item in self.research:
                sections.append(f"- {item.get('title', '')}\n")

        return "\n".join(sections)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'characters': self.characters,
            'worldbuilding': self.worldbuilding,
            'previous_chapters': self.previous_chapters,
            'scenes': self.scenes,
            'motifs': self.motifs,
            'research': self.research,
            'metadata': self.metadata
        }


class GoogleStoreQuerier:
    """Query Google Cloud Storage for story context."""

    def __init__(self, project_name: str, config: Optional[GoogleStoreConfig] = None):
        """
        Initialize querier for a specific project.

        Args:
            project_name: Name of the writing project
            config: GoogleStoreConfig instance (creates new if None)
        """
        self.project_name = project_name
        self.config = config or GoogleStoreConfig()

        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid Google Cloud configuration")

        # Get project bucket
        self.bucket_name = self.config.get_bucket_name(project_name)
        if not self.bucket_name:
            raise ValueError(f"No bucket configured for project: {project_name}")

        # Initialize Google Cloud Storage client
        self.client = self._init_storage_client()
        self.bucket = self.client.bucket(self.bucket_name)

    def _init_storage_client(self) -> storage.Client:
        """Initialize Google Cloud Storage client with credentials."""
        creds_path = self.config.get_google_credentials_path()
        project_id = self.config.get_project_id()

        credentials = service_account.Credentials.from_service_account_file(creds_path)

        return storage.Client(project=project_id, credentials=credentials)

    def query_characters(self, character_names: Optional[List[str]] = None) -> List[Dict]:
        """
        Query character information.

        Args:
            character_names: List of specific character names to retrieve.
                           If None, retrieves all characters.

        Returns:
            List of character data dictionaries
        """
        characters = []
        prefix = "characters/"

        blobs = self.bucket.list_blobs(prefix=prefix)

        for blob in blobs:
            # Skip directories
            if blob.name.endswith('/'):
                continue

            # If specific characters requested, filter
            if character_names:
                blob_name = Path(blob.name).stem
                if not any(name.lower() in blob_name.lower() for name in character_names):
                    continue

            # Download and parse
            try:
                content = blob.download_as_text()

                # Handle JSON files
                if blob.name.endswith('.json'):
                    data = json.loads(content)
                # Handle markdown files
                elif blob.name.endswith('.md'):
                    data = {
                        'name': Path(blob.name).stem,
                        'description': content
                    }
                else:
                    data = {
                        'name': Path(blob.name).stem,
                        'content': content
                    }

                characters.append(data)
            except Exception as e:
                print(f"Error loading character {blob.name}: {e}")

        return characters

    def query_worldbuilding(self, topics: Optional[List[str]] = None) -> List[Dict]:
        """
        Query worldbuilding information.

        Args:
            topics: List of specific topics to retrieve.
                   If None, retrieves all worldbuilding content.

        Returns:
            List of worldbuilding data dictionaries
        """
        worldbuilding = []
        prefix = "worldbuilding/"

        blobs = self.bucket.list_blobs(prefix=prefix)

        for blob in blobs:
            if blob.name.endswith('/'):
                continue

            # Filter by topics if specified
            if topics:
                blob_name = Path(blob.name).stem
                if not any(topic.lower() in blob_name.lower() for topic in topics):
                    continue

            try:
                content = blob.download_as_text()

                if blob.name.endswith('.json'):
                    data = json.loads(content)
                else:
                    data = {
                        'title': Path(blob.name).stem,
                        'content': content
                    }

                worldbuilding.append(data)
            except Exception as e:
                print(f"Error loading worldbuilding {blob.name}: {e}")

        return worldbuilding

    def query_chapters(self, chapter_numbers: Optional[List[int]] = None,
                      limit: Optional[int] = None) -> List[Dict]:
        """
        Query chapter information.

        Args:
            chapter_numbers: Specific chapters to retrieve (e.g., [1, 2, 3])
            limit: Maximum number of recent chapters to retrieve

        Returns:
            List of chapter data dictionaries
        """
        chapters = []
        prefix = "chapters/"

        blobs = list(self.bucket.list_blobs(prefix=prefix))

        for blob in blobs:
            if blob.name.endswith('/'):
                continue

            # Filter by chapter number if specified
            if chapter_numbers:
                # Extract chapter number from filename
                import re
                match = re.search(r'chapter[-_]?(\d+)', blob.name, re.IGNORECASE)
                if match:
                    chapter_num = int(match.group(1))
                    if chapter_num not in chapter_numbers:
                        continue

            try:
                content = blob.download_as_text()

                if blob.name.endswith('.json'):
                    data = json.loads(content)
                else:
                    # Extract chapter metadata from filename
                    import re
                    match = re.search(r'chapter[-_]?(\d+)', blob.name, re.IGNORECASE)
                    chapter_num = int(match.group(1)) if match else None

                    data = {
                        'number': chapter_num,
                        'title': Path(blob.name).stem,
                        'content': content,
                        'summary': content[:500] + "..." if len(content) > 500 else content
                    }

                chapters.append(data)
            except Exception as e:
                print(f"Error loading chapter {blob.name}: {e}")

        # Sort by chapter number
        chapters.sort(key=lambda x: x.get('number', 0))

        # Apply limit if specified
        if limit:
            chapters = chapters[-limit:]

        return chapters

    def query_motifs(self) -> List[Dict]:
        """Query recurring motifs and themes."""
        motifs = []
        prefix = "motifs/"

        blobs = self.bucket.list_blobs(prefix=prefix)

        for blob in blobs:
            if blob.name.endswith('/'):
                continue

            try:
                content = blob.download_as_text()

                if blob.name.endswith('.json'):
                    data = json.loads(content)
                    # If it's a list of motifs
                    if isinstance(data, list):
                        motifs.extend(data)
                    else:
                        motifs.append(data)
                else:
                    motifs.append({
                        'name': Path(blob.name).stem,
                        'description': content
                    })
            except Exception as e:
                print(f"Error loading motifs {blob.name}: {e}")

        return motifs

    def query_research(self, keywords: Optional[List[str]] = None) -> List[Dict]:
        """Query research and reference materials."""
        research = []
        prefix = "research/"

        blobs = self.bucket.list_blobs(prefix=prefix)

        for blob in blobs:
            if blob.name.endswith('/'):
                continue

            # Filter by keywords if specified
            if keywords:
                blob_name = Path(blob.name).stem.lower()
                if not any(keyword.lower() in blob_name for keyword in keywords):
                    continue

            try:
                content = blob.download_as_text()

                if blob.name.endswith('.json'):
                    data = json.loads(content)
                else:
                    data = {
                        'title': Path(blob.name).stem,
                        'content': content
                    }

                research.append(data)
            except Exception as e:
                print(f"Error loading research {blob.name}: {e}")

        return research

    def build_context_package(self,
                             scene_outline: str,
                             character_names: Optional[List[str]] = None,
                             worldbuilding_topics: Optional[List[str]] = None,
                             include_recent_chapters: int = 3,
                             include_motifs: bool = True) -> ContextPackage:
        """
        Build a comprehensive context package for writing a scene.

        This is the main method agents use to get context before writing.

        Args:
            scene_outline: Brief description of the scene to be written
            character_names: Characters involved in the scene
            worldbuilding_topics: Relevant worldbuilding topics
            include_recent_chapters: Number of recent chapters to include
            include_motifs: Whether to include recurring motifs

        Returns:
            ContextPackage with all relevant information
        """
        print(f"Building context package for: {scene_outline}")

        # Query all relevant information
        characters = self.query_characters(character_names) if character_names else []
        worldbuilding = self.query_worldbuilding(worldbuilding_topics) if worldbuilding_topics else []
        chapters = self.query_chapters(limit=include_recent_chapters)
        motifs = self.query_motifs() if include_motifs else []

        # For now, we'll leave scenes and research empty unless specifically needed
        scenes = []
        research = []

        metadata = {
            'project': self.project_name,
            'scene_outline': scene_outline,
            'query_timestamp': str(Path.cwd())  # Placeholder
        }

        package = ContextPackage(
            characters=characters,
            worldbuilding=worldbuilding,
            previous_chapters=chapters,
            scenes=scenes,
            motifs=motifs,
            research=research,
            metadata=metadata
        )

        print(f"Context package built: {len(characters)} characters, "
              f"{len(worldbuilding)} worldbuilding items, {len(chapters)} chapters")

        return package

    def search_content(self, query: str, categories: Optional[List[str]] = None) -> List[Dict]:
        """
        Search for content across all categories.

        Args:
            query: Search query string
            categories: List of categories to search (characters, worldbuilding, etc.)
                       If None, searches all categories

        Returns:
            List of matching items with their content
        """
        if categories is None:
            categories = ['characters', 'worldbuilding', 'chapters', 'scenes', 'motifs', 'research']

        results = []

        for category in categories:
            blobs = self.bucket.list_blobs(prefix=f"{category}/")

            for blob in blobs:
                if blob.name.endswith('/'):
                    continue

                try:
                    content = blob.download_as_text()

                    # Simple text search (can be enhanced with better indexing)
                    if query.lower() in content.lower():
                        results.append({
                            'category': category,
                            'file': blob.name,
                            'content': content,
                            'name': Path(blob.name).stem
                        })
                except Exception as e:
                    print(f"Error searching {blob.name}: {e}")

        return results


def example_usage():
    """Example of how to use the querier."""
    # Initialize querier for a project
    querier = GoogleStoreQuerier("the-explants")

    # Build context for a specific scene
    context = querier.build_context_package(
        scene_outline="Mickey confronts the corporate AI overseer about her neural implant",
        character_names=["Mickey", "AI Overseer"],
        worldbuilding_topics=["neural implants", "corporate control"],
        include_recent_chapters=3,
        include_motifs=True
    )

    # Convert to prompt-ready format
    prompt_context = context.to_prompt_context()
    print(prompt_context)

    # Or search for specific content
    results = querier.search_content("consciousness war")
    print(f"Found {len(results)} items about consciousness war")


if __name__ == "__main__":
    example_usage()
