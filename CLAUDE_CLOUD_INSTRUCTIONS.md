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
   - Create job queue for long-running analyses

4. **backend/app/services/badge_engine.py**
   - detect_ai_authorship(text) -> confidence score
   - assign_badges(work, analysis_results) -> Badge[]
   - Badge types: AI-Analyzed, Human-Verified, Human-Self, Community

5. **backend/app/services/file_parser.py**
   - parse_docx(file) -> chapters/scenes
   - parse_pdf(file) -> chapters/scenes
   - parse_txt(file) -> chapters/scenes

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

- Railway deployment config
- Environment variables
- Database migration
- Test all endpoints

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
