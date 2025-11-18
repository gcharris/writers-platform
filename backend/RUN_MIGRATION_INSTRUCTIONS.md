# Database Migration Instructions

## Quick Start (Railway - Recommended)

The migration needs to run on Railway where your database is hosted.

### Option 1: Railway Dashboard (Easiest - 2 minutes)

1. Go to https://railway.app/dashboard
2. Select your `writers-platform-production` project
3. Click on the PostgreSQL database service
4. Click "Query" tab
5. Copy and paste the entire contents of `migrations/MANUSCRIPT_MIGRATION.sql`
6. Click "Run Query"
7. ✅ Done! Tables created.

### Option 2: Railway CLI (if authenticated)

```bash
cd backend
railway login  # If not already logged in
railway run python migrate.py
```

### Option 3: Local Connection to Railway DB

1. Get DATABASE_URL from Railway:
   ```bash
   railway variables --service writers-platform-production
   ```

2. Create `backend/.env`:
   ```
   DATABASE_URL=postgresql://...  # paste from Railway
   SECRET_KEY=your-secret-key
   ```

3. Run migration:
   ```bash
   cd backend
   source venv/bin/activate  # If using venv
   python migrate.py
   ```

## What Gets Created

This migration creates 4 new tables:

### 1. `manuscript_acts`
- Stores acts in novels (Act 1, Act 2, Act 3)
- Links to projects table
- Supports multi-volume works

### 2. `manuscript_chapters`
- Stores chapters within acts
- Hierarchical structure: Act → Chapter
- Automatic word count calculation

### 3. `manuscript_scenes`
- Stores actual prose content
- Metadata includes: generation context, AI model used, prompts, KB queries
- Full-text content with word count

### 4. `reference_files`
- Knowledge base files (characters, world-building, plot, etc.)
- **GIN index** for fast full-text search
- Supports categories and subcategories
- Metadata stores NotebookLM URLs, tags, version info

## Verification

After running the migration, verify with:

```sql
-- Check tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('manuscript_acts', 'manuscript_chapters', 'manuscript_scenes', 'reference_files');

-- Check indexes (should show GIN index on reference_files)
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename IN ('manuscript_acts', 'manuscript_chapters', 'manuscript_scenes', 'reference_files');
```

Expected output:
- 4 tables
- 7+ indexes including `idx_reference_files_search` (GIN type)

## Troubleshooting

### "relation already exists"
- Tables were created previously
- Safe to ignore if you see this message
- The `IF NOT EXISTS` clause prevents errors

### "permission denied"
- Ensure you're connected to the correct Railway database
- Check that your database user has CREATE TABLE permissions

### "module not found"
- Install dependencies: `pip install sqlalchemy psycopg2-binary pydantic-settings`

## Next Steps After Migration

1. ✅ Seed reference files with knowledge base template
2. ✅ Test workflow API with Ollama
3. ✅ Implement real cloud AI agents
4. ✅ Build UI components

See: `docs/ARCHITECTURE_GAP_ANALYSIS.md` for complete roadmap
