#!/usr/bin/env python3
"""
Simple migration runner that works both locally and on Railway.
Reads DATABASE_URL from environment and executes the manuscript migration.
"""

import os
import sys

def main():
    # Check for DATABASE_URL
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print()
        print("To run locally, create backend/.env with:")
        print("DATABASE_URL=postgresql://user:pass@host:5432/dbname")
        print()
        print("On Railway, this is automatically provided.")
        return 1

    print("=" * 70)
    print("Writers Platform - Manuscript Tables Migration")
    print("=" * 70)
    print()
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    print()

    try:
        from sqlalchemy import create_engine, text
        from pathlib import Path

        # Read migration SQL
        migration_file = Path(__file__).parent / "migrations" / "MANUSCRIPT_MIGRATION.sql"

        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            return 1

        print(f"📄 Reading: {migration_file.name}")
        migration_sql = migration_file.read_text()

        # Create engine and execute
        print(f"🔌 Connecting to database...")
        engine = create_engine(database_url)

        with engine.connect() as conn:
            print(f"🚀 Executing migration...")
            conn.execute(text(migration_sql))
            conn.commit()

            # Verify
            print(f"✅ Verifying tables...")
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('manuscript_acts', 'manuscript_chapters',
                                   'manuscript_scenes', 'reference_files')
                ORDER BY table_name;
            """))

            tables = [row[0] for row in result]

            print()
            print("=" * 70)
            if len(tables) == 4:
                print("✅ SUCCESS - All 4 tables created:")
                for table in tables:
                    print(f"   ✓ {table}")
                print()
                print("Tables ready for use!")
            else:
                print(f"⚠️  WARNING - Expected 4 tables, found {len(tables)}")
                for table in tables:
                    print(f"   ✓ {table}")
            print("=" * 70)

            return 0 if len(tables) == 4 else 1

    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print()
        print("Install required packages:")
        print("  pip install sqlalchemy psycopg2-binary")
        return 1

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
