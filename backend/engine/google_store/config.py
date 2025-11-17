"""
Google File Store Configuration Manager

Handles credentials, bucket configuration, and project-specific settings
for accessing Google Cloud Storage.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class GoogleStoreConfig:
    """Manages Google File Store configuration and credentials."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to credentials JSON file.
                        Defaults to config/credentials.json
        """
        if config_path is None:
            config_path = self._find_config_path()

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _find_config_path(self) -> str:
        """Find the configuration file in standard locations."""
        possible_paths = [
            Path(__file__).parent.parent / "config" / "credentials.json",
            Path.home() / ".creative-writing-framework" / "credentials.json",
            Path("config/credentials.json"),
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        # Return default path even if it doesn't exist yet
        return str(possible_paths[0])

    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            print(f"Warning: Config file not found at {self.config_path}")
            print("Please create config/credentials.json based on credentials.example.json")
            return {}

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return {}

    def get_google_credentials_path(self) -> Optional[str]:
        """Get path to Google Cloud service account credentials."""
        return self.config.get('google_cloud', {}).get('credentials_path')

    def get_project_id(self) -> Optional[str]:
        """Get Google Cloud project ID."""
        return self.config.get('google_cloud', {}).get('project_id')

    def get_bucket_name(self, project_name: str) -> Optional[str]:
        """
        Get Google Cloud Storage bucket name for a specific project.

        Args:
            project_name: Name of the writing project

        Returns:
            Bucket name or None if not configured
        """
        projects = self.config.get('projects', {})
        return projects.get(project_name, {}).get('bucket_name')

    def get_project_config(self, project_name: str) -> Dict:
        """
        Get full configuration for a specific project.

        Args:
            project_name: Name of the writing project

        Returns:
            Project configuration dictionary
        """
        return self.config.get('projects', {}).get(project_name, {})

    def set_project_bucket(self, project_name: str, bucket_name: str):
        """
        Set or update bucket name for a project.

        Args:
            project_name: Name of the writing project
            bucket_name: Google Cloud Storage bucket name
        """
        if 'projects' not in self.config:
            self.config['projects'] = {}

        if project_name not in self.config['projects']:
            self.config['projects'][project_name] = {}

        self.config['projects'][project_name]['bucket_name'] = bucket_name
        self._save_config()

    def add_project(self, project_name: str, bucket_name: str,
                   description: str = "", metadata: Optional[Dict] = None):
        """
        Add a new project to configuration.

        Args:
            project_name: Name of the writing project
            bucket_name: Google Cloud Storage bucket name
            description: Project description
            metadata: Additional project metadata
        """
        if 'projects' not in self.config:
            self.config['projects'] = {}

        self.config['projects'][project_name] = {
            'bucket_name': bucket_name,
            'description': description,
            'metadata': metadata or {}
        }

        self._save_config()
        print(f"Added project '{project_name}' with bucket '{bucket_name}'")

    def list_projects(self) -> Dict[str, Dict]:
        """
        List all configured projects.

        Returns:
            Dictionary of project configurations
        """
        return self.config.get('projects', {})

    def _save_config(self):
        """Save configuration to JSON file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_ai_api_key(self, platform: str) -> Optional[str]:
        """
        Get API key for a specific AI platform.

        Args:
            platform: Platform name (claude, openai, google, anthropic, xai)

        Returns:
            API key or None if not configured
        """
        return self.config.get('ai_platforms', {}).get(platform, {}).get('api_key')

    def validate(self) -> bool:
        """
        Validate that required configuration is present.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.config:
            print("Error: No configuration loaded")
            return False

        # Check for Google Cloud credentials
        google_config = self.config.get('google_cloud', {})
        if not google_config.get('credentials_path'):
            print("Error: Google Cloud credentials_path not configured")
            return False

        if not google_config.get('project_id'):
            print("Error: Google Cloud project_id not configured")
            return False

        # Check if credentials file exists
        creds_path = Path(google_config['credentials_path'])
        if not creds_path.exists():
            print(f"Error: Credentials file not found at {creds_path}")
            return False

        return True


def create_example_config(output_path: str = "config/credentials.example.json"):
    """Create an example configuration file."""
    example_config = {
        "google_cloud": {
            "project_id": "your-google-cloud-project-id",
            "credentials_path": "config/google-cloud-credentials.json",
            "region": "us-central1"
        },
        "ai_platforms": {
            "claude": {
                "api_key": "your-anthropic-api-key",
                "model": "claude-sonnet-4-5-20250929"
            },
            "openai": {
                "api_key": "your-openai-api-key",
                "model": "gpt-4"
            },
            "google": {
                "api_key": "your-google-api-key",
                "model": "gemini-pro"
            },
            "xai": {
                "api_key": "your-xai-api-key",
                "model": "grok-2"
            }
        },
        "projects": {
            "example-novel": {
                "bucket_name": "example-novel-store",
                "description": "Example novel project",
                "metadata": {
                    "genre": "science-fiction",
                    "target_length": "80000 words"
                }
            }
        }
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(example_config, f, indent=2)

    print(f"Example configuration created at {output_path}")


if __name__ == "__main__":
    # Create example configuration
    create_example_config()

    # Test configuration loading
    config = GoogleStoreConfig()
    if config.validate():
        print("Configuration is valid!")
        print(f"Projects: {list(config.list_projects().keys())}")
    else:
        print("Configuration validation failed")
