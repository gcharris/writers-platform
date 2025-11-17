# Instructions for Claude Cloud Agent

## IMPORTANT: Repository to Use

**GitHub Repository:**
```
https://github.com/gcharris/writers-platform
```

**This is the ONLY repository you need to work with.**

All code has been migrated here by Cursor AI. You'll find:
- Community backend in `backend/`
- Factory engine in `backend/engine/`
- Placeholder files for new features

## Repository Status

✅ **READY TO BUILD** - All foundation code has been migrated by Cursor AI.

## What's Already Done

1. ✅ Community backend copied to `writers-platform/backend/`
2. ✅ Factory engine copied to `writers-platform/backend/engine/`
3. ✅ Placeholder files created for new routes/services
4. ✅ Requirements merged
5. ✅ Documentation written

## Your Task: Build the Missing Pieces

### PRIORITY 1: Backend API Routes & Services

**Files to implement:**

1. **backend/app/routes/projects.py**
   - POST /api/projects/ - Create project (upload file or new)
   - GET /api/projects/ - List user's projects
   - GET /api/projects/{id} - Get project details
   - PUT /api/projects/{id} - Update project
   - DELETE /api/projects/{id} - Delete project

2. **backend/app/routes/analysis.py**
   - POST /api/analysis/run - Trigger analysis on project
   - GET /api/analysis/{job_id}/status - Check progress
   - GET /api/analysis/{job_id}/results - Get results

3. **backend/app/services/orchestrator.py**
   - Import from: backend.engine.orchestration.tournament
   - Wrap tournament.py for async web use
   - **CRITICAL:** Create background job system for long-running AI analyses
   - **Options:** Use FastAPI BackgroundTasks (simple), or Celery + Redis (production)
   - **Why:** AI tournaments can take 5-10 minutes, can't block HTTP requests
   - **Must return:** Job ID immediately, allow polling for status/results

4. **backend/app/services/badge_engine.py**
   - detect_ai_authorship(text) -> confidence score
   - assign_badges(work, analysis_results) -> Badge[]
   - Badge types: AI-Analyzed, Human-Verified, Human-Self, Community

5. **backend/app/services/file_parser.py**
   - parse_docx(file) -> chapters/scenes
   - parse_pdf(file) -> chapters/scenes
   - parse_txt(file) -> chapters/scenes
   - **File Storage:** Use Railway volumes or integrate S3-compatible storage
   - **Not local filesystem** - must work in cloud environment

### PRIORITY 2: Database Models

**Files to create:**

1. **backend/app/models/project.py**
   ```python
   class Project(Base):
       id, user_id, title, status, created_at, updated_at
   ```

2. **backend/app/models/scene.py**
   ```python
   class Scene(Base):
       id, project_id, content, chapter_num, scene_num, sequence
   ```

3. **backend/app/models/analysis_result.py**
   ```python
   class AnalysisResult(Base):
       id, project_id, model, scores_json, feedback, timestamp
   ```

4. **backend/app/models/badge.py**
   ```python
   class Badge(Base):
       id, work_id, badge_type, verified, metadata_json, created_at
   ```

### PRIORITY 3: Update Existing Code

**backend/app/routes/works.py**
- Add badge assignment on work creation
- Add direct upload flow with auto-analysis
- Add support for factory_project_id linking

**backend/app/main.py**
- Import new routes (projects, analysis)
- Add CORS for writersfactory.app
- Update API docs

### PRIORITY 4: Deploy Backend

**CRITICAL: Cloud-First Architecture**

This is NOT a local CLI tool. This is a web-based SaaS product.

**Requirements:**
- ✅ Deploy to Railway (cloud hosting)
- ✅ PostgreSQL database (Railway addon)
- ✅ File storage (Railway volumes or S3)
- ✅ Background jobs (FastAPI BackgroundTasks minimum, Celery preferred)
- ✅ Environment variables (all secrets in Railway config, not in code)
- ✅ HTTPS endpoints (accessible from anywhere)
- ✅ CORS for writersfactory.app and writerscommunity.app

**NOT acceptable:**
- ❌ Local file system paths
- ❌ Blocking HTTP requests for long AI processing
- ❌ Hardcoded API keys in code
- ❌ "Run locally" as primary deployment

**Deployment Steps:**
1. Create Railway project
2. Add PostgreSQL addon
3. Configure environment variables (API keys, JWT secret, etc.)
4. Deploy backend
5. Run database migrations
6. Test all endpoints via HTTPS

## Important Notes

**Don't Modify:**
- `backend/engine/` - This is Factory's analysis code, use as-is
- Existing Community routes - Only extend, don't break

**Do Import:**
- Use `from backend.engine.orchestration import tournament` for AI analysis
- Use existing models where possible

**Dependencies:**
- Add to requirements.txt: python-docx, PyPDF2 (for file parsing)
- Add AI detection library of your choice

## Testing Checklist

Before considering backend complete, verify:
- [ ] User can register/login (existing)
- [ ] User can create project via upload
- [ ] User can create project from scratch
- [ ] User can trigger analysis on project
- [ ] Analysis runs successfully (even just 1 model for MVP)
- [ ] User can view analysis results
- [ ] User can publish project to Community
- [ ] Published work has correct badges
- [ ] Community direct upload works with auto-analysis

## Budget

Session 1 Budget: $500 max for backend

## Success Criteria

✅ Backend API deployed to Railway
✅ All endpoints documented in /docs
✅ Can create project, analyze, publish workflow end-to-end
✅ Database schema extended correctly
✅ Factory engine integration working

---

**After Session 1 completes, notify user for Session 2: Factory Frontend**
