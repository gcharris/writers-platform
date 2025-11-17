# 🚀 START HERE - Give This to Claude Cloud

## For the User (You)

**What just happened:**
Cursor AI migrated your code in 15 minutes, saving ~$300 in Claude Cloud credits.

**What's ready:**
✅ `writers-platform/` repository with all foundation code
✅ Community backend (working)
✅ Factory engine (working)
✅ Placeholder files for new features (ready for Claude Cloud to implement)

---

## Instructions for Claude Cloud Agent

Copy everything below this line and paste into Claude Cloud:

---

# Session 1: Writers Platform Backend Implementation

## Context

I have a new repository `writers-platform` that contains:
- ✅ Complete Community backend (FastAPI, already working)
- ✅ Factory AI engine (70k lines, already working)
- 📝 Placeholder files for NEW features (you need to implement these)

**Repository Path:**
```
/Users/gch2024/Documents/Documents - Mac Mini/writers-platform/
```

**GitHub:**
```
https://github.com/gcharris/writers-platform
```

## Your Task

Build the Writers Factory web interface by implementing 5 new files and updating 2 existing files.

**Read these files first for context:**
1. `README.md` - Full architecture overview
2. `CLAUDE_CLOUD_INSTRUCTIONS.md` - Detailed task breakdown
3. `MIGRATION_COMPLETE.md` - What's already done

## Budget

- **Maximum:** $500 for this session
- **Goal:** Complete backend API, deploy to Railway

## What to Build

### NEW Files to Implement:

1. **backend/app/routes/projects.py**
   - Project CRUD (create, list, get, update, delete)
   - File upload handling (DOCX/PDF/TXT)

2. **backend/app/routes/analysis.py**
   - Trigger AI analysis
   - Check status
   - Get results

3. **backend/app/services/orchestrator.py**
   - Wrap `backend/engine/orchestration/tournament.py`
   - Async job queue for long-running analyses

4. **backend/app/services/badge_engine.py**
   - AI authorship detection
   - Badge assignment (AI-Analyzed, Human-Authored, etc.)

5. **backend/app/services/file_parser.py**
   - Parse DOCX → chapters/scenes
   - Parse PDF → chapters/scenes
   - Parse TXT → chapters/scenes

### Database Models to Create:

- `backend/app/models/project.py`
- `backend/app/models/scene.py`
- `backend/app/models/analysis_result.py`
- `backend/app/models/badge.py`

### Existing Files to Update:

- `backend/app/main.py` - Add new routes, update CORS
- `backend/app/routes/works.py` - Add badge support, factory linking

## Success Criteria

✅ All new endpoints working
✅ Can upload file → create project → analyze → publish to Community
✅ Deployed to Railway
✅ All tests passing
✅ API documentation at /docs

## Important Notes

**DO NOT modify:**
- `backend/engine/` (Factory's AI code - use as-is via imports)
- Original repos: `writers-community/` or `factory/` (they're reference only)

**DO use:**
- Existing Community models where possible
- Import Factory's tournament code: `from backend.engine.orchestration import tournament`

---

## Start Command

```bash
cd /Users/gch2024/Documents/Documents\ -\ Mac\ Mini/writers-platform/
# Read the docs, then start implementing!
```

**When done, notify user for Session 2: Factory Frontend**
