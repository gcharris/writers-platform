"""
Project Initialization Script

Initialize a new creative writing project with Google File Store bucket
and configuration.
"""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from google_store import GoogleStoreConfig, GoogleStoreSync


def init_project(project_name: str,
                bucket_name: str,
                description: str = "",
                create_bucket: bool = True,
                local_path: Optional[str] = None):
    """
    Initialize a new writing project.

    Args:
        project_name: Name of the project
        bucket_name: Google Cloud Storage bucket name
        description: Project description
        create_bucket: Whether to create the GCS bucket
        local_path: Optional local directory to initialize
    """
    print("=" * 80)
    print("PROJECT INITIALIZATION")
    print("=" * 80)
    print(f"Project: {project_name}")
    print(f"Bucket: {bucket_name}")
    print()

    # Load configuration
    config = GoogleStoreConfig()

    # Validate Google Cloud credentials
    if not config.validate():
        print("Error: Google Cloud credentials not properly configured")
        print("Please set up config/credentials.json first")
        return False

    # Add project to configuration
    print("Step 1: Adding project to configuration...")
    config.add_project(
        project_name=project_name,
        bucket_name=bucket_name,
        description=description
    )
    print(f"✓ Project '{project_name}' added to config")
    print()

    # Create Google Cloud Storage bucket
    if create_bucket:
        print("Step 2: Creating Google Cloud Storage bucket...")
        try:
            sync = GoogleStoreSync(project_name, config)
            if sync.create_bucket():
                print(f"✓ Bucket '{bucket_name}' created")
            print()
        except Exception as e:
            print(f"Error creating bucket: {e}")
            print("You may need to create the bucket manually")
            print()

    # Create local directory structure if requested
    if local_path:
        print("Step 3: Creating local directory structure...")
        local_path = Path(local_path)
        local_path.mkdir(parents=True, exist_ok=True)

        # Create standard folders
        folders = [
            'characters',
            'worldbuilding',
            'chapters',
            'scenes',
            'motifs',
            'research',
            'references'
        ]

        for folder in folders:
            (local_path / folder).mkdir(exist_ok=True)

        print(f"✓ Created local structure at {local_path}")
        print(f"  Folders: {', '.join(folders)}")
        print()

        # Create project configuration file
        project_config = {
            'project_name': project_name,
            'bucket_name': bucket_name,
            'description': description,
            'framework_path': str(Path(__file__).parent.parent),
            'local_path': str(local_path)
        }

        config_file = local_path / '.framework-config.json'
        with open(config_file, 'w') as f:
            json.dump(project_config, f, indent=2)

        print(f"✓ Created project config: {config_file}")
        print()

    # Create example README
    if local_path:
        readme_path = local_path / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(f"# {project_name}\n\n")
            f.write(f"{description}\n\n")
            f.write("## Project Structure\n\n")
            f.write("This project uses the Creative Writing Agent Framework.\n\n")
            f.write("- `characters/` - Character profiles and development\n")
            f.write("- `worldbuilding/` - World, setting, and technology details\n")
            f.write("- `chapters/` - Completed chapters\n")
            f.write("- `scenes/` - Individual scenes and drafts\n")
            f.write("- `motifs/` - Recurring themes and motifs\n")
            f.write("- `research/` - Reference materials\n\n")
            f.write("## Google File Store\n\n")
            f.write(f"Bucket: `{bucket_name}`\n\n")
            f.write("Sync files:\n")
            f.write("```bash\n")
            f.write(f"python /path/to/framework/google-store/sync.py \\\n")
            f.write(f"  --project {project_name} \\\n")
            f.write(f"  --action upload \\\n")
            f.write(f"  --local-dir .\n")
            f.write("```\n\n")

        print(f"✓ Created README: {readme_path}")
        print()

    print("=" * 80)
    print("INITIALIZATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Add your story assets to the local folders (or existing project)")
    print("2. Sync to Google File Store:")
    print(f"   python google-store/sync.py --project {project_name} --action upload --local-dir <path>")
    print("3. Generate scenes:")
    print(f"   python orchestration/scene-writer.py --project {project_name} --scene 'your scene' --agents claude gemini --output scene.md")
    print()

    return True


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Initialize a new creative writing project"
    )
    parser.add_argument('--name', required=True, help="Project name")
    parser.add_argument('--bucket', required=True, help="Google Cloud Storage bucket name")
    parser.add_argument('--description', default="", help="Project description")
    parser.add_argument('--no-create-bucket', action='store_true',
                       help="Don't create the GCS bucket (use existing)")
    parser.add_argument('--local-path', help="Local directory to initialize")

    args = parser.parse_args()

    success = init_project(
        project_name=args.name,
        bucket_name=args.bucket,
        description=args.description,
        create_bucket=not args.no_create_bucket,
        local_path=args.local_path
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    from typing import Optional
    main()
