"""
Google File Store Indexer

Creates and maintains a searchable index of all story assets in Google Cloud Storage.
Enables fast keyword searching and semantic queries across the entire project.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from google.cloud import storage
from google.oauth2 import service_account
import re

from .config import GoogleStoreConfig


class StoryIndex:
    """Searchable index of story assets."""

    def __init__(self):
        self.index = {
            'metadata': {
                'created': None,
                'last_updated': None,
                'total_files': 0,
                'categories': {}
            },
            'files': [],
            'keywords': {},
            'character_mentions': {},
            'scene_connections': {}
        }

    def add_file(self, category: str, filename: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a file to the index.

        Args:
            category: File category (characters, worldbuilding, etc.)
            filename: Name of the file
            content: File content
            metadata: Additional metadata
        """
        file_entry = {
            'category': category,
            'filename': filename,
            'path': f"{category}/{filename}",
            'word_count': len(content.split()),
            'keywords': self._extract_keywords(content),
            'character_mentions': self._extract_character_names(content),
            'metadata': metadata or {}
        }

        self.index['files'].append(file_entry)

        # Update keyword index
        for keyword in file_entry['keywords']:
            if keyword not in self.index['keywords']:
                self.index['keywords'][keyword] = []
            self.index['keywords'][keyword].append(file_entry['path'])

        # Update character mentions index
        for character in file_entry['character_mentions']:
            if character not in self.index['character_mentions']:
                self.index['character_mentions'][character] = []
            self.index['character_mentions'][character].append(file_entry['path'])

        # Update category counts
        if category not in self.index['metadata']['categories']:
            self.index['metadata']['categories'][category] = 0
        self.index['metadata']['categories'][category] += 1

        self.index['metadata']['total_files'] += 1

    def _extract_keywords(self, content: str, min_length: int = 4) -> Set[str]:
        """Extract important keywords from content."""
        # Simple keyword extraction (can be enhanced with NLP)
        words = re.findall(r'\b[a-z]+\b', content.lower())

        # Common stop words to exclude
        stop_words = {
            'that', 'this', 'with', 'from', 'have', 'will', 'what', 'when',
            'where', 'they', 'their', 'them', 'there', 'these', 'those',
            'would', 'could', 'should', 'about', 'which', 'been'
        }

        keywords = {
            word for word in words
            if len(word) >= min_length and word not in stop_words
        }

        # Limit to most frequent keywords
        return set(sorted(keywords)[:100])

    def _extract_character_names(self, content: str) -> Set[str]:
        """Extract character names (proper nouns) from content."""
        # Simple proper noun extraction
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)

        # Filter out common false positives
        false_positives = {'The', 'Chapter', 'Scene', 'Part'}
        return {name for name in set(proper_nouns) if name not in false_positives}

    def search(self, query: str, categories: Optional[List[str]] = None) -> List[Dict]:
        """
        Search the index for files matching the query.

        Args:
            query: Search query (keywords)
            categories: Optional list of categories to search within

        Returns:
            List of matching file entries
        """
        query_words = set(query.lower().split())
        matches = []

        for file_entry in self.index['files']:
            # Filter by category if specified
            if categories and file_entry['category'] not in categories:
                continue

            # Check for keyword matches
            matching_keywords = query_words & file_entry['keywords']

            if matching_keywords:
                match_score = len(matching_keywords)
                matches.append({
                    **file_entry,
                    'match_score': match_score,
                    'matching_keywords': list(matching_keywords)
                })

        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches

    def find_by_character(self, character_name: str) -> List[str]:
        """
        Find all files that mention a specific character.

        Args:
            character_name: Name of the character

        Returns:
            List of file paths
        """
        return self.index['character_mentions'].get(character_name, [])

    def to_dict(self) -> Dict:
        """Convert index to dictionary for serialization."""
        return self.index

    def from_dict(self, data: Dict):
        """Load index from dictionary."""
        self.index = data


class GoogleStoreIndexer:
    """Build and maintain searchable index of Google Cloud Storage files."""

    def __init__(self, project_name: str, config: Optional[GoogleStoreConfig] = None):
        """
        Initialize indexer for a specific project.

        Args:
            project_name: Name of the writing project
            config: GoogleStoreConfig instance
        """
        self.project_name = project_name
        self.config = config or GoogleStoreConfig()

        if not self.config.validate():
            raise ValueError("Invalid Google Cloud configuration")

        self.bucket_name = self.config.get_bucket_name(project_name)
        if not self.bucket_name:
            raise ValueError(f"No bucket configured for project: {project_name}")

        self.client = self._init_storage_client()
        self.bucket = self.client.bucket(self.bucket_name)

    def _init_storage_client(self) -> storage.Client:
        """Initialize Google Cloud Storage client."""
        creds_path = self.config.get_google_credentials_path()
        project_id = self.config.get_project_id()

        credentials = service_account.Credentials.from_service_account_file(creds_path)
        return storage.Client(project=project_id, credentials=credentials)

    def build_index(self, categories: Optional[List[str]] = None) -> StoryIndex:
        """
        Build a complete index of all files in the bucket.

        Args:
            categories: List of categories to index (default: all)

        Returns:
            StoryIndex object
        """
        index = StoryIndex()
        index.index['metadata']['created'] = datetime.now().isoformat()
        index.index['metadata']['last_updated'] = datetime.now().isoformat()

        print(f"Building index for project: {self.project_name}")

        # Get all blobs
        blobs = list(self.bucket.list_blobs())

        for blob in blobs:
            # Skip directories and gitkeep files
            if blob.name.endswith('/') or blob.name.endswith('.gitkeep'):
                continue

            # Extract category from path
            parts = blob.name.split('/')
            if len(parts) < 2:
                continue

            category = parts[0]
            filename = parts[-1]

            # Filter by categories if specified
            if categories and category not in categories:
                continue

            try:
                # Download content
                content = blob.download_as_text()

                # Extract metadata
                metadata = {
                    'size': blob.size,
                    'updated': blob.updated.isoformat() if blob.updated else None,
                    'content_type': blob.content_type
                }

                # Add to index
                index.add_file(category, filename, content, metadata)
                print(f"Indexed: {blob.name}")

            except Exception as e:
                print(f"Error indexing {blob.name}: {e}")

        print(f"\nIndex complete: {index.index['metadata']['total_files']} files indexed")
        print(f"Categories: {dict(index.index['metadata']['categories'])}")

        return index

    def save_index(self, index: StoryIndex, filename: str = "index.json"):
        """
        Save index to Google Cloud Storage.

        Args:
            index: StoryIndex object to save
            filename: Name of index file (default: index.json)
        """
        index_data = index.to_dict()

        # Upload to root of bucket
        blob = self.bucket.blob(filename)
        blob.upload_from_string(
            json.dumps(index_data, indent=2),
            content_type='application/json'
        )

        print(f"Index saved to gs://{self.bucket_name}/{filename}")

    def load_index(self, filename: str = "index.json") -> Optional[StoryIndex]:
        """
        Load index from Google Cloud Storage.

        Args:
            filename: Name of index file

        Returns:
            StoryIndex object or None if not found
        """
        try:
            blob = self.bucket.blob(filename)
            content = blob.download_as_text()
            data = json.loads(content)

            index = StoryIndex()
            index.from_dict(data)

            print(f"Index loaded from gs://{self.bucket_name}/{filename}")
            print(f"Total files: {index.index['metadata']['total_files']}")

            return index
        except Exception as e:
            print(f"Error loading index: {e}")
            return None

    def rebuild_and_save(self, categories: Optional[List[str]] = None):
        """
        Rebuild index from scratch and save to cloud storage.

        Args:
            categories: List of categories to index
        """
        print("Rebuilding index...")
        index = self.build_index(categories)
        self.save_index(index)
        return index


def main():
    """Command-line interface for indexing operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Build searchable index of story assets")
    parser.add_argument('--project', required=True, help="Project name")
    parser.add_argument('--action', choices=['build', 'search', 'find-character'],
                       required=True, help="Action to perform")
    parser.add_argument('--query', help="Search query")
    parser.add_argument('--character', help="Character name to find")
    parser.add_argument('--categories', nargs='+', help="Categories to index/search")

    args = parser.parse_args()

    indexer = GoogleStoreIndexer(args.project)

    if args.action == 'build':
        indexer.rebuild_and_save(args.categories)

    elif args.action == 'search':
        if not args.query:
            print("Error: --query required for search")
            return

        # Load existing index
        index = indexer.load_index()
        if not index:
            print("No index found. Run with --action build first.")
            return

        # Perform search
        results = index.search(args.query, args.categories)
        print(f"\nFound {len(results)} matches for '{args.query}':")
        for result in results[:10]:  # Show top 10
            print(f"\n  {result['path']}")
            print(f"    Match score: {result['match_score']}")
            print(f"    Matching keywords: {', '.join(result['matching_keywords'])}")

    elif args.action == 'find-character':
        if not args.character:
            print("Error: --character required")
            return

        index = indexer.load_index()
        if not index:
            print("No index found. Run with --action build first.")
            return

        files = index.find_by_character(args.character)
        print(f"\nFiles mentioning '{args.character}':")
        for file_path in files:
            print(f"  {file_path}")


if __name__ == "__main__":
    main()
