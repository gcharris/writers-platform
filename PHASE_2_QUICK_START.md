# Phase 2: Quick Start Guide

**Status**: ✅ Ready to Test
**Estimated Time**: 10 minutes

---

## Prerequisites

- PostgreSQL database running
- `DATABASE_URL` environment variable set
- Backend dependencies installed (`pip install -r backend/requirements.txt`)

---

## Step 1: Run Database Migration (2 minutes)

### Option A: Using Shell Script (Recommended)

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
./test_phase2_migration.sh
```

### Option B: Manual Migration

```bash
psql $DATABASE_URL -f backend/migrations/add_community_badges.sql
```

---

## Step 2: Verify Schema (1 minute)

Check that tables were created:

```sql
psql $DATABASE_URL -c "\d badges"
psql $DATABASE_URL -c "\d works" | grep factory
```

Expected output:
- `badges` table with columns: id, work_id, badge_type, verified, metadata_json, created_at, updated_at
- `works` table with columns: factory_project_id, factory_scores

---

## Step 3: Run API Tests (5 minutes)

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
python3 test_phase2_api.py
```

This will:
1. ✅ Verify database schema
2. ✅ Test badge assignment for 3 scenarios:
   - Community upload (no claim)
   - Human authorship claim (human-like content)
   - Human claim with AI-like content
3. ✅ Test badge queries and filtering
4. ✅ Clean up test data

Expected output:
```
==================================================
All Tests Passed!
==================================================

Phase 2 Migration Summary:
  ✓ Database schema correct
  ✓ Badge assignment working
  ✓ Badge queries functional
```

---

## Step 4: Test Frontend (2 minutes)

### Browse Page Badge Filter

1. Start frontend: `cd community-frontend && npm run dev`
2. Navigate to `/browse`
3. Click "Badge Type" dropdown
4. Select "AI-Analyzed"
5. **Expected**: Only AI-analyzed works appear

### Upload Page Copilot CTA

1. Navigate to `/upload`
2. **Expected**: Purple/blue "Write with FREE AI Copilot" section at top
3. Click "Start Writing with Copilot"
4. **Expected**: Redirects to Factory

### ViewWork Knowledge Graph Tab

1. Create a Factory project with Knowledge Graph
2. Publish to Community (API endpoint)
3. Navigate to work page
4. **Expected**: Two tabs appear: "Read Story" and "Explore Knowledge Graph"

---

## Troubleshooting

### "DATABASE_URL not set"
```bash
export DATABASE_URL="postgresql://user:pass@host:port/database"
```

### "Badges table does not exist"
Run migration:
```bash
psql $DATABASE_URL -f backend/migrations/add_community_badges.sql
```

### "ModuleNotFoundError"
Install backend dependencies:
```bash
cd backend && pip install -r requirements.txt
```

### "Works table missing Factory fields"
The migration should have added these. If not, check PostgreSQL logs for errors during migration.

---

## What's Working Now

After running these tests, you'll have:

✅ **Database**: Badges table created with proper indexes
✅ **Models**: Work and Badge models with relationships
✅ **Badge Assignment**: 4 badge types working (ai_analyzed, human_verified, human_self, community_upload)
✅ **AI Detection**: Heuristic-based detection assigns correct badges
✅ **Frontend**: Badge filter, Copilot CTA, Knowledge Graph tabs

---

## Next Steps

1. **Deploy to Production**
   - Run migration on Railway PostgreSQL
   - Deploy backend to Railway
   - Deploy frontend to Vercel

2. **Test Factory → Community Publishing**
   - Create Factory project
   - Call `/api/works/from-factory/{project_id}` endpoint
   - Verify ai_analyzed badge assigned

3. **Add Research Citations** (Option 2)
   - Show NotebookLM sources on ViewWork page
   - Display research foundation

---

## Quick Verification Queries

Check badge distribution:
```sql
SELECT badge_type, COUNT(*) as count
FROM badges
GROUP BY badge_type;
```

Find works with Factory link:
```sql
SELECT title, factory_project_id, factory_scores->>'best_score' as score
FROM works
WHERE factory_project_id IS NOT NULL;
```

Check badge metadata:
```sql
SELECT badge_type, metadata_json
FROM badges
LIMIT 5;
```

---

**Phase 2 Status**: ✅ Ready for Production Testing

Once these tests pass, Phase 2 Community Platform Migration is complete!
