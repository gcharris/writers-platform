import psycopg2
import os

conn = psycopg2.connect(os.environ['DATABASE_URL'])
conn.autocommit = True
cursor = conn.cursor()

try:
    # Add updated_at column
    cursor.execute("""
        ALTER TABLE badges 
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
    """)
    print("✓ Added updated_at column to badges table")
except Exception as e:
    print(f"✗ Failed: {e}")
finally:
    cursor.close()
    conn.close()
