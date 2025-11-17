"""
Configuration for Gemini File Search Integration

Manages API keys, store IDs, and project settings.
"""

import os
import json
from pathlib import Path
from typing import Optional


class GeminiFileSearchConfig:
    """Configuration for Gemini File Search API."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to credentials.json (default: framework/config/credentials.json)
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "credentials.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            print(f"Warning: Config file not found at {self.config_path}")
            return {}

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return {}

    def get_google_api_key(self) -> Optional[str]:
        """
        Get Google API key for Gemini.

        Tries in order:
        1. Environment variable: GOOGLE_API_KEY
        2. Config file: ai_platforms.google.api_key
        3. Config file: google_cloud.api_key

        Returns:
            API key or None
        """
        # Try environment variable first
        if 'GOOGLE_API_KEY' in os.environ:
            return os.environ['GOOGLE_API_KEY']

        # Try config file
        if 'ai_platforms' in self.config:
            google_config = self.config['ai_platforms'].get('google', {})
            if 'api_key' in google_config:
                return google_config['api_key']

        # Try google_cloud section
        if 'google_cloud' in self.config:
            if 'api_key' in self.config['google_cloud']:
                return self.config['google_cloud']['api_key']

        return None

    def get_file_search_store_id(self, project_name: str = "The-Explants") -> Optional[str]:
        """
        Get File Search store ID for a project.

        Args:
            project_name: Project name

        Returns:
            Store ID or None
        """
        if 'projects' not in self.config:
            return None

        project = self.config['projects'].get(project_name, {})
        return project.get('file_search_store_id')

    def set_file_search_store_id(self, store_id: str, project_name: str = "The-Explants"):
        """
        Save File Search store ID to config.

        Args:
            store_id: Store ID from Gemini API
            project_name: Project name
        """
        if 'projects' not in self.config:
            self.config['projects'] = {}

        if project_name not in self.config['projects']:
            self.config['projects'][project_name] = {}

        self.config['projects'][project_name]['file_search_store_id'] = store_id

        # Save to file
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        print(f"✓ Saved store ID to config: {store_id}")

    def get_story_root_path(self) -> Path:
        """
        Get root path to story files.

        Returns:
            Path to "The Explants Series" directory
        """
        # Default path
        repo_root = Path(__file__).parent.parent.parent
        story_path = repo_root / "The Explants Series"

        if story_path.exists():
            return story_path

        # Try alternative locations
        alt_paths = [
            Path.home() / "Documents" / "The Explants Series",
            Path("/Users/gch2024/Documents/Documents - Mac Mini/Explant drafts current/The Explants Series"),
        ]

        for path in alt_paths:
            if path.exists():
                return path

        # Default to repo location
        return story_path

    def validate_api_key(self) -> bool:
        """
        Validate that Google API key is configured.

        Returns:
            True if API key is available
        """
        api_key = self.get_google_api_key()
        if not api_key:
            print("Error: Google API key not configured")
            print("Set GOOGLE_API_KEY environment variable or add to credentials.json")
            return False
        return True
