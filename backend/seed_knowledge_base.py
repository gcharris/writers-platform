#!/usr/bin/env python3
"""
Seed the reference_files table with The-Explants knowledge base template.
This populates the knowledge base so AI agents have context for scene generation.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List
import re

def count_words(text: str) -> int:
    """Count words in text."""
    return len(re.findall(r'\w+', text))

def extract_category_from_path(file_path: Path, template_root: Path) -> tuple[str, str]:
    """
    Extract category and subcategory from file path.

    Examples:
        Characters/Core_Cast/Mickey.md → ('characters', 'core_cast')
        World_Building/Technology/Devices.md → ('world_building', 'technology')
        Story_Structure/Scene_Arc_Map.md → ('story_structure', '')
    """
    # Get relative path from template root
    rel_path = file_path.relative_to(template_root)

    parts = list(rel_path.parts[:-1])  # Exclude filename

    if not parts:
        return ('general', '')

    # Category is first directory, normalized
    category = parts[0].lower().replace(' ', '_').replace('-', '_')

    # Subcategory is second directory if it exists
    subcategory = ''
    if len(parts) > 1:
        subcategory = parts[1].lower().replace(' ', '_').replace('-', '_')

    return (category, subcategory)

def scan_reference_files(template_dir: Path) -> List[Dict]:
    """
    Scan template directory for markdown files.
    Returns list of file metadata dictionaries.
    """
    files = []

    # Find all .md files recursively
    for md_file in template_dir.rglob('*.md'):
        # Skip certain files
        if md_file.name.startswith('_') or md_file.name.startswith('.'):
            continue
        if 'README' in md_file.name.upper():
            continue

        # Read content
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Skipping {md_file.name}: {e}")
            continue

        # Extract category/subcategory
        category, subcategory = extract_category_from_path(md_file, template_dir)

        files.append({
            'filename': md_file.name,
            'category': category,
            'subcategory': subcategory,
            'content': content,
            'word_count': count_words(content),
            'source_path': str(md_file.relative_to(template_dir))
        })

    return files

def seed_database(project_id: str, template_dir: Path, dry_run: bool = False):
    """
    Seed database with reference files from template.

    Args:
        project_id: UUID of project to seed
        template_dir: Path to reference template directory
        dry_run: If True, only print what would be inserted
    """
    # Scan files
    print(f"📂 Scanning: {template_dir}")
    files = scan_reference_files(template_dir)

    print(f"📝 Found {len(files)} reference files")
    print()

    # Group by category
    by_category = {}
    for f in files:
        cat = f['category']
        by_category.setdefault(cat, []).append(f)

    print("📊 Files by category:")
    for cat, items in sorted(by_category.items()):
        total_words = sum(f['word_count'] for f in items)
        print(f"   {cat:25s} {len(items):3d} files, {total_words:8,d} words")
    print()

    if dry_run:
        print("🔍 DRY RUN - No changes will be made")
        print()
        print("Sample files:")
        for f in files[:5]:
            print(f"   • {f['category']:20s} / {f['subcategory']:15s} / {f['filename']}")
        print(f"   ... and {len(files) - 5} more")
        return True

    # Insert into database
    try:
        from sqlalchemy import create_engine, text
        from uuid import UUID

        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set in environment")
            return False

        # Validate project_id is UUID
        try:
            UUID(project_id)
        except ValueError:
            print(f"❌ Invalid project_id (not a UUID): {project_id}")
            return False

        print(f"🔌 Connecting to database...")
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Check if project exists
            result = conn.execute(
                text("SELECT id, title FROM projects WHERE id = :pid"),
                {"pid": project_id}
            )
            project = result.first()

            if not project:
                print(f"❌ Project not found: {project_id}")
                print()
                print("Available projects:")
                result = conn.execute(text("SELECT id, title FROM projects LIMIT 10"))
                for p in result:
                    print(f"   {p[0]} - {p[1]}")
                return False

            print(f"✅ Project found: {project[1]}")
            print()

            # Insert files
            print(f"📥 Inserting {len(files)} files...")
            inserted = 0
            skipped = 0

            for f in files:
                try:
                    conn.execute(text("""
                        INSERT INTO reference_files
                            (project_id, category, subcategory, filename, content, word_count, metadata)
                        VALUES
                            (:project_id, :category, :subcategory, :filename, :content, :word_count, :metadata)
                        ON CONFLICT (project_id, category, subcategory, filename) DO UPDATE SET
                            content = EXCLUDED.content,
                            word_count = EXCLUDED.word_count,
                            updated_at = CURRENT_TIMESTAMP
                    """), {
                        'project_id': project_id,
                        'category': f['category'],
                        'subcategory': f['subcategory'],
                        'filename': f['filename'],
                        'content': f['content'],
                        'word_count': f['word_count'],
                        'metadata': '{"source": "' + f['source_path'] + '"}'
                    })
                    inserted += 1

                except Exception as e:
                    print(f"   ⚠️  Failed: {f['filename']}: {e}")
                    skipped += 1

            conn.commit()

            print()
            print("=" * 70)
            print(f"✅ SUCCESS - Seeded knowledge base")
            print(f"   Inserted: {inserted} files")
            if skipped > 0:
                print(f"   Skipped:  {skipped} files")
            print(f"   Total words: {sum(f['word_count'] for f in files):,}")
            print("=" * 70)

            return True

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install: pip install sqlalchemy psycopg2-binary")
        return False

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Seed knowledge base with reference files')
    parser.add_argument('--project-id', required=False,
                        help='UUID of project to seed (or set PROJECT_ID env var)')
    parser.add_argument('--template-dir', default='app/templates/project_template/reference',
                        help='Path to reference template directory')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be inserted without actually inserting')

    args = parser.parse_args()

    # Get project ID
    project_id = args.project_id or os.getenv('PROJECT_ID')

    if not project_id and not args.dry_run:
        print("❌ ERROR: --project-id required (or set PROJECT_ID environment variable)")
        print()
        print("Usage:")
        print("  python seed_knowledge_base.py --project-id YOUR-PROJECT-UUID")
        print("  python seed_knowledge_base.py --dry-run  # Preview without inserting")
        return 1

    # Get template directory
    template_dir = Path(__file__).parent / args.template_dir

    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        return 1

    print("=" * 70)
    print("Writers Platform - Knowledge Base Seeding")
    print("=" * 70)
    print()

    success = seed_database(project_id, template_dir, dry_run=args.dry_run)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
