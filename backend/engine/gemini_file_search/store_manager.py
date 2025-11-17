"""
File Search Store Manager

Creates and manages Gemini File Search stores (semantic knowledge graphs).
"""

import os
from typing import Optional, Dict
from google import genai
from google.genai import types

from .config import GeminiFileSearchConfig


class FileSearchStoreManager:
    """Manage Gemini File Search stores."""

    def __init__(self, config: Optional[GeminiFileSearchConfig] = None):
        """
        Initialize store manager.

        Args:
            config: Configuration instance
        """
        self.config = config or GeminiFileSearchConfig()

        if not self.config.validate_api_key():
            raise ValueError("Google API key not configured")

        self.client = genai.Client(api_key=self.config.get_google_api_key())

    def create_store(self,
                    project_name: str = "The-Explants",
                    display_name: str = "The Explants Story Knowledge Graph",
                    corpus_name: str = "explants-trilogy") -> str:
        """
        Create a new File Search store.

        Args:
            project_name: Project name (for saving to config)
            display_name: Human-readable store name
            corpus_name: Corpus identifier

        Returns:
            Store ID (name)
        """
        print("=" * 80)
        print("CREATING GEMINI FILE SEARCH STORE")
        print("=" * 80)
        print(f"Project: {project_name}")
        print(f"Display Name: {display_name}")
        print(f"Corpus: {corpus_name}")
        print()

        try:
            # Create file search corpus
            corpus = self.client.files.create_corpus(
                display_name=display_name,
                name=corpus_name
            )

            store_id = corpus.name
            print(f"✓ Store created successfully")
            print(f"  Store ID: {store_id}")
            print()

            # Save to config
            self.config.set_file_search_store_id(store_id, project_name)
            print(f"✓ Store ID saved to config")
            print()

            print("=" * 80)
            print("STORE CREATION COMPLETE")
            print("=" * 80)
            print()
            print(f"Store ID: {store_id}")
            print()
            print("Next steps:")
            print("1. Bulk upload files:")
            print(f"   python3 framework/gemini_file_search/bulk_upload.py --store-id {store_id}")
            print("2. Test queries:")
            print(f"   python3 test_knowledge_graph.py")
            print()

            return store_id

        except Exception as e:
            print(f"Error creating store: {e}")
            raise

    def get_store(self, store_id: str) -> types.Corpus:
        """
        Get store information.

        Args:
            store_id: Store ID

        Returns:
            Corpus object
        """
        try:
            corpus = self.client.files.get_corpus(name=store_id)
            return corpus
        except Exception as e:
            print(f"Error getting store: {e}")
            raise

    def delete_store(self, store_id: str):
        """
        Delete a File Search store.

        Args:
            store_id: Store ID to delete
        """
        print(f"Deleting store: {store_id}")

        try:
            self.client.files.delete_corpus(name=store_id)
            print("✓ Store deleted")
        except Exception as e:
            print(f"Error deleting store: {e}")
            raise

    def list_stores(self):
        """List all File Search stores."""
        try:
            corpora = self.client.files.list_corpora()
            print("File Search Stores:")
            for corpus in corpora:
                print(f"  - {corpus.display_name}: {corpus.name}")
        except Exception as e:
            print(f"Error listing stores: {e}")


def main():
    """Command-line interface for store management."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage Gemini File Search stores"
    )
    parser.add_argument('action', choices=['create', 'list', 'delete', 'info'],
                       help="Action to perform")
    parser.add_argument('--store-id', help="Store ID (for delete/info)")
    parser.add_argument('--project', default="The-Explants",
                       help="Project name (default: The-Explants)")
    parser.add_argument('--display-name',
                       default="The Explants Story Knowledge Graph",
                       help="Display name for new store")
    parser.add_argument('--corpus-name', default="explants-trilogy",
                       help="Corpus name for new store")

    args = parser.parse_args()

    manager = FileSearchStoreManager()

    if args.action == 'create':
        store_id = manager.create_store(
            project_name=args.project,
            display_name=args.display_name,
            corpus_name=args.corpus_name
        )

    elif args.action == 'list':
        manager.list_stores()

    elif args.action == 'delete':
        if not args.store_id:
            print("Error: --store-id required for delete action")
            return
        manager.delete_store(args.store_id)

    elif args.action == 'info':
        if not args.store_id:
            print("Error: --store-id required for info action")
            return
        corpus = manager.get_store(args.store_id)
        print(f"Store: {corpus.display_name}")
        print(f"ID: {corpus.name}")
        print(f"Create time: {corpus.create_time}")
        print(f"Update time: {corpus.update_time}")


if __name__ == "__main__":
    main()
