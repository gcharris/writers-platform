import psycopg2
import os

# Read migration file
with open('backend/migrations/add_community_badges.sql', 'r') as f:
    migration_sql = f.read()

# Connect to database
conn = psycopg2.connect(os.environ['DATABASE_URL'])
conn.autocommit = True
cursor = conn.cursor()

try:
    # Execute migration
    cursor.execute(migration_sql)
    print("✓ Migration completed successfully")
except Exception as e:
    print(f"✗ Migration failed: {e}")
finally:
    cursor.close()
    conn.close()
