import psycopg2
import os

conn = psycopg2.connect(os.environ['DATABASE_URL'])
conn.autocommit = True
cursor = conn.cursor()

try:
    # Add Factory linking columns to works table
    cursor.execute("""
        ALTER TABLE works
        ADD COLUMN IF NOT EXISTS factory_project_id UUID REFERENCES projects(id),
        ADD COLUMN IF NOT EXISTS factory_scores JSONB
    """)
    print("✓ Added factory_project_id and factory_scores to works table")
    
    # Create index
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_works_factory_project ON works(factory_project_id)
    """)
    print("✓ Created index on factory_project_id")
    
except Exception as e:
    print(f"✗ Failed: {e}")
finally:
    cursor.close()
    conn.close()
