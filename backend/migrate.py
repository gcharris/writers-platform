#!/usr/bin/env python3
"""
Simple migration runner that works both locally and on Railway.
Reads DATABASE_URL from environment and executes migrations.
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    # Load .env file if it exists (for local development)
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print(f"📄 Loaded environment from {env_path}")
    except ImportError:
        pass  # dotenv not installed, will use system env vars

    # Parse arguments
    parser = argparse.ArgumentParser(description='Run database migrations')
    parser.add_argument('--migration-file', type=str, help='Path to migration SQL file')
    parser.add_argument('--verify-tables', type=str, nargs='+', help='Tables to verify after migration')
    args = parser.parse_args()

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

    # Determine migration file
    from pathlib import Path
    if args.migration_file:
        migration_file = Path(args.migration_file)
        migration_name = migration_file.stem
    else:
        migration_file = Path(__file__).parent / "migrations" / "MANUSCRIPT_MIGRATION.sql"
        migration_name = "Manuscript Tables"

    print("=" * 70)
    print(f"Writers Platform - {migration_name} Migration")
    print("=" * 70)
    print()
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    print()

    try:
        from sqlalchemy import create_engine, text

        # Read migration SQL

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

            # Verify tables if specified
            if args.verify_tables:
                print(f"✅ Verifying tables...")
                table_list = "', '".join(args.verify_tables)
                result = conn.execute(text(f"""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('{table_list}')
                    ORDER BY table_name;
                """))

                tables = [row[0] for row in result]

                print()
                print("=" * 70)
                expected_count = len(args.verify_tables)
                if len(tables) == expected_count:
                    print(f"✅ SUCCESS - All {expected_count} tables created:")
                    for table in tables:
                        print(f"   ✓ {table}")
                    print()
                    print("Tables ready for use!")
                else:
                    print(f"⚠️  WARNING - Expected {expected_count} tables, found {len(tables)}")
                    for table in tables:
                        print(f"   ✓ {table}")
                print("=" * 70)

                return 0 if len(tables) == expected_count else 1
            else:
                print()
                print("=" * 70)
                print("✅ SUCCESS - Migration executed")
                print("=" * 70)
                return 0

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
