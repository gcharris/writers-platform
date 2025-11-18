#!/usr/bin/env python3
"""
Run database migration for manuscript tables.
This script connects to the Railway PostgreSQL database and executes the migration SQL.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    """Execute the manuscript migration SQL file."""

    # Read migration SQL
    migration_file = Path(__file__).parent / "migrations" / "MANUSCRIPT_MIGRATION.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"📄 Reading migration from: {migration_file}")
    migration_sql = migration_file.read_text()

    # Connect and execute
    print(f"🔌 Connecting to database...")

    try:
        with engine.connect() as conn:
            # Execute migration
            print(f"🚀 Executing migration...")
            conn.execute(text(migration_sql))
            conn.commit()

            # Verify tables were created
            print(f"\n✅ Migration complete! Verifying tables...")

            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('manuscript_acts', 'manuscript_chapters', 'manuscript_scenes', 'reference_files')
                ORDER BY table_name;
            """))

            tables = [row[0] for row in result]

            if len(tables) == 4:
                print(f"✅ All 4 tables created successfully:")
                for table in tables:
                    print(f"   ✓ {table}")

                # Check indexes
                result = conn.execute(text("""
                    SELECT indexname
                    FROM pg_indexes
                    WHERE tablename IN ('manuscript_acts', 'manuscript_chapters', 'manuscript_scenes', 'reference_files')
                    AND indexname LIKE 'idx_%'
                    ORDER BY indexname;
                """))

                indexes = [row[0] for row in result]
                print(f"\n✅ Created {len(indexes)} indexes:")
                for idx in indexes[:5]:  # Show first 5
                    print(f"   ✓ {idx}")
                if len(indexes) > 5:
                    print(f"   ... and {len(indexes) - 5} more")

                return True
            else:
                print(f"⚠️  Expected 4 tables, found {len(tables)}: {tables}")
                return False

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Writers Platform - Database Migration")
    print("Creating manuscript structure tables")
    print("=" * 60)
    print()

    success = run_migration()

    print()
    print("=" * 60)
    if success:
        print("✅ MIGRATION SUCCESSFUL")
        print("Next steps:")
        print("  1. Seed reference files with knowledge base")
        print("  2. Test workflow API")
    else:
        print("❌ MIGRATION FAILED")
        print("Please check error messages above")
    print("=" * 60)

    sys.exit(0 if success else 1)
