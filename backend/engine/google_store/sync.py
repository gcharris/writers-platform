"""
Google File Store Sync System

Upload and download files between local filesystem and Google Cloud Storage.
Maintains the standardized folder structure for creative writing projects.
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict
from google.cloud import storage
from google.oauth2 import service_account

from .config import GoogleStoreConfig


class GoogleStoreSync:
    """Sync files between local filesystem and Google Cloud Storage."""

    STANDARD_CATEGORIES = [
        'characters',
        'worldbuilding',
        'chapters',
        'scenes',
        'motifs',
        'research',
        'references'
    ]

    def __init__(self, project_name: str, config: Optional[GoogleStoreConfig] = None):
        """
        Initialize sync system for a specific project.

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

    def create_bucket(self, location: str = "US") -> bool:
        """
        Create the Google Cloud Storage bucket for this project.

        Args:
            location: Bucket location (default: US)

        Returns:
            True if bucket created or already exists, False on error
        """
        try:
            # Check if bucket already exists
            if self.bucket.exists():
                print(f"Bucket {self.bucket_name} already exists")
                return True

            # Create new bucket
            bucket = self.client.create_bucket(self.bucket_name, location=location)
            print(f"Created bucket {bucket.name} in {location}")

            # Create standard folder structure
            self._create_folder_structure()

            return True
        except Exception as e:
            print(f"Error creating bucket: {e}")
            return False

    def _create_folder_structure(self):
        """Create standard folder structure in the bucket."""
        for category in self.STANDARD_CATEGORIES:
            # Create a placeholder file to establish the directory
            blob = self.bucket.blob(f"{category}/.gitkeep")
            blob.upload_from_string("")

        print(f"Created standard folder structure: {', '.join(self.STANDARD_CATEGORIES)}")

    def upload_file(self, local_path: str, category: str,
                   remote_name: Optional[str] = None) -> bool:
        """
        Upload a single file to Google Cloud Storage.

        Args:
            local_path: Path to local file
            category: Category folder (characters, worldbuilding, etc.)
            remote_name: Optional custom name for remote file

        Returns:
            True if upload successful, False otherwise
        """
        local_path = Path(local_path)

        if not local_path.exists():
            print(f"Error: File not found: {local_path}")
            return False

        if category not in self.STANDARD_CATEGORIES:
            print(f"Warning: Non-standard category '{category}'. Consider using: {self.STANDARD_CATEGORIES}")

        # Determine remote file name
        if remote_name is None:
            remote_name = local_path.name

        remote_path = f"{category}/{remote_name}"

        try:
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(str(local_path))
            print(f"Uploaded: {local_path} -> gs://{self.bucket_name}/{remote_path}")
            return True
        except Exception as e:
            print(f"Error uploading {local_path}: {e}")
            return False

    def upload_directory(self, local_dir: str, category: str,
                        file_extensions: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Upload all files from a local directory to a category.

        Args:
            local_dir: Path to local directory
            category: Category folder (characters, worldbuilding, etc.)
            file_extensions: List of file extensions to include (e.g., ['.md', '.json'])
                           If None, uploads all files

        Returns:
            Dictionary with upload statistics
        """
        local_dir = Path(local_dir)

        if not local_dir.is_dir():
            print(f"Error: Directory not found: {local_dir}")
            return {'success': 0, 'failed': 0}

        stats = {'success': 0, 'failed': 0}

        # Get all files
        files = []
        if file_extensions:
            for ext in file_extensions:
                files.extend(local_dir.glob(f"*{ext}"))
        else:
            files = [f for f in local_dir.iterdir() if f.is_file()]

        print(f"Uploading {len(files)} files from {local_dir} to {category}/")

        for file_path in files:
            if self.upload_file(str(file_path), category):
                stats['success'] += 1
            else:
                stats['failed'] += 1

        print(f"Upload complete: {stats['success']} successful, {stats['failed']} failed")
        return stats

    def upload_project_structure(self, project_root: str,
                                 categories: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Upload entire project structure with standardized folders.

        Expected local structure:
        project_root/
        ├── characters/
        ├── worldbuilding/
        ├── chapters/
        └── ...

        Args:
            project_root: Root directory of the project
            categories: List of categories to upload (default: all standard categories)

        Returns:
            Dictionary with upload statistics
        """
        project_root = Path(project_root)
        categories = categories or self.STANDARD_CATEGORIES

        total_stats = {'success': 0, 'failed': 0}

        for category in categories:
            category_dir = project_root / category

            if not category_dir.exists():
                print(f"Skipping {category}/ (directory not found)")
                continue

            stats = self.upload_directory(str(category_dir), category)
            total_stats['success'] += stats['success']
            total_stats['failed'] += stats['failed']

        print(f"\nTotal upload: {total_stats['success']} files uploaded, {total_stats['failed']} failed")
        return total_stats

    def download_file(self, category: str, remote_name: str,
                     local_path: Optional[str] = None) -> bool:
        """
        Download a single file from Google Cloud Storage.

        Args:
            category: Category folder
            remote_name: Name of file in GCS
            local_path: Optional local path to save to

        Returns:
            True if download successful, False otherwise
        """
        remote_path = f"{category}/{remote_name}"

        if local_path is None:
            local_path = remote_name

        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            blob = self.bucket.blob(remote_path)
            blob.download_to_filename(str(local_path))
            print(f"Downloaded: gs://{self.bucket_name}/{remote_path} -> {local_path}")
            return True
        except Exception as e:
            print(f"Error downloading {remote_path}: {e}")
            return False

    def download_category(self, category: str, local_dir: str) -> Dict[str, int]:
        """
        Download all files from a category to a local directory.

        Args:
            category: Category folder to download
            local_dir: Local directory to save files to

        Returns:
            Dictionary with download statistics
        """
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        stats = {'success': 0, 'failed': 0}

        blobs = self.bucket.list_blobs(prefix=f"{category}/")

        for blob in blobs:
            # Skip directory markers
            if blob.name.endswith('/') or blob.name.endswith('.gitkeep'):
                continue

            # Extract filename
            filename = Path(blob.name).name
            local_path = local_dir / filename

            try:
                blob.download_to_filename(str(local_path))
                print(f"Downloaded: {blob.name} -> {local_path}")
                stats['success'] += 1
            except Exception as e:
                print(f"Error downloading {blob.name}: {e}")
                stats['failed'] += 1

        print(f"Download complete: {stats['success']} successful, {stats['failed']} failed")
        return stats

    def download_all(self, local_root: str,
                    categories: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Download entire project structure from Google Cloud Storage.

        Args:
            local_root: Local root directory to download to
            categories: List of categories to download (default: all)

        Returns:
            Dictionary with download statistics
        """
        local_root = Path(local_root)
        categories = categories or self.STANDARD_CATEGORIES

        total_stats = {'success': 0, 'failed': 0}

        for category in categories:
            category_dir = local_root / category
            stats = self.download_category(category, str(category_dir))
            total_stats['success'] += stats['success']
            total_stats['failed'] += stats['failed']

        print(f"\nTotal download: {total_stats['success']} files downloaded, {total_stats['failed']} failed")
        return total_stats

    def list_files(self, category: Optional[str] = None) -> List[str]:
        """
        List all files in the bucket or a specific category.

        Args:
            category: Optional category to list (lists all if None)

        Returns:
            List of file paths
        """
        prefix = f"{category}/" if category else ""
        blobs = self.bucket.list_blobs(prefix=prefix)

        files = []
        for blob in blobs:
            if not blob.name.endswith('/') and not blob.name.endswith('.gitkeep'):
                files.append(blob.name)

        return files

    def sync_bidirectional(self, local_root: str,
                          categories: Optional[List[str]] = None,
                          direction: str = "upload") -> Dict[str, int]:
        """
        Sync files between local and cloud storage.

        Args:
            local_root: Local root directory
            categories: Categories to sync
            direction: 'upload', 'download', or 'both'

        Returns:
            Dictionary with sync statistics
        """
        if direction not in ['upload', 'download', 'both']:
            raise ValueError("direction must be 'upload', 'download', or 'both'")

        stats = {'success': 0, 'failed': 0}

        if direction in ['upload', 'both']:
            print("\n=== Uploading to Google Cloud Storage ===")
            upload_stats = self.upload_project_structure(local_root, categories)
            stats['success'] += upload_stats['success']
            stats['failed'] += upload_stats['failed']

        if direction in ['download', 'both']:
            print("\n=== Downloading from Google Cloud Storage ===")
            download_stats = self.download_all(local_root, categories)
            stats['success'] += download_stats['success']
            stats['failed'] += download_stats['failed']

        return stats

    def delete_file(self, category: str, remote_name: str) -> bool:
        """
        Delete a file from Google Cloud Storage.

        Args:
            category: Category folder
            remote_name: Name of file to delete

        Returns:
            True if deletion successful, False otherwise
        """
        remote_path = f"{category}/{remote_name}"

        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            print(f"Deleted: gs://{self.bucket_name}/{remote_path}")
            return True
        except Exception as e:
            print(f"Error deleting {remote_path}: {e}")
            return False


def main():
    """Command-line interface for sync operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Sync files with Google Cloud Storage")
    parser.add_argument('--project', required=True, help="Project name")
    parser.add_argument('--action', choices=['upload', 'download', 'list', 'create-bucket'],
                       required=True, help="Action to perform")
    parser.add_argument('--local-dir', help="Local directory path")
    parser.add_argument('--category', help="Category to sync")
    parser.add_argument('--categories', nargs='+', help="Multiple categories to sync")

    args = parser.parse_args()

    # Initialize sync system
    sync = GoogleStoreSync(args.project)

    if args.action == 'create-bucket':
        sync.create_bucket()

    elif args.action == 'upload':
        if args.local_dir:
            if args.categories:
                sync.upload_project_structure(args.local_dir, args.categories)
            elif args.category:
                sync.upload_directory(args.local_dir, args.category)
            else:
                sync.upload_project_structure(args.local_dir)
        else:
            print("Error: --local-dir required for upload")

    elif args.action == 'download':
        if args.local_dir:
            if args.categories:
                sync.download_all(args.local_dir, args.categories)
            elif args.category:
                sync.download_category(args.category, args.local_dir)
            else:
                sync.download_all(args.local_dir)
        else:
            print("Error: --local-dir required for download")

    elif args.action == 'list':
        files = sync.list_files(args.category)
        print(f"\nFiles in {args.category or 'all categories'}:")
        for file in files:
            print(f"  {file}")


if __name__ == "__main__":
    main()
