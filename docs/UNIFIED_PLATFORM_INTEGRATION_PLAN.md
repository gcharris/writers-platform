# Writers Platform: Unified Integration Plan
## Consolidating writers-factory-core into writers-platform

**Created**: 2025-01-17
**Status**: In Progress (Phase 1 Complete - Bug Hunting)
**Timeline**: 24 hours, $800 budget, 3-6 sessions remaining
**Current Branch**: `main` (deployed to Railway + Vercel)

---

## Executive Summary

We are consolidating **writers-factory-core** (100,000 lines, 17 sprints) into **writers-platform** (current deployment) to create one unified ecosystem:

- **Writers Factory** (private workspace): Write, analyze, improve with AI
- **Writers Community** (public platform): Publish, validate, earn badges
- **Shared Backend**: One database, one API, one AI engine

**Why One Platform?**
1. Shared authentication and user data
2. Seamless Factory → Community publishing flow
3. Unified AI analysis engine and badge system
4. Single deployment, single maintenance
5. Consistent data models across private/public modes

---

## Current State: What We Have

### ✅ Writers Platform (Deployed & Working)

**Backend** (FastAPI on Railway):
- `app/routes/auth.py` - Authentication (register, login, /me)
- `app/routes/projects.py` - Factory projects (CRUD, upload, scenes)
- `app/routes/analysis.py` - AI analysis jobs
- `app/routes/works.py` - Community published works
- `app/routes/comments.py` - Community comments
- `app/routes/ratings.py` - Community ratings
- `app/routes/professional.py` - Badge system
- `app/routes/factory.py` - Factory→Community bridge
- `engine/orchestration/` - Tournament system (multi-agent AI)
- `engine/agents/` - 5 AI integrations (Claude, GPT, Gemini, Grok, DeepSeek)

**Frontend** (React on Vercel):
- Factory UI: Dashboard, upload, editor, analysis
- Simple project management
- Basic AI analysis triggering

**Database** (PostgreSQL on Railway):
- Users, Projects, Scenes, Works, Comments, Ratings, Badges
- Shared data models across Factory & Community

### ❌ What We're Missing from writers-factory-core

**Priority 1: AI Setup Wizard** (~3,183 lines)
- `factory/ai/setup_wizard_agent.py` - Conversation agent (not form-based)
- `factory/templates/category_templates.py` - 8 knowledge categories:
  1. Characters (4 sections, 15+ fields)
  2. Story_Structure
  3. World_Building
  4. Themes_and_Philosophy
  5. Voice_and_Craft
  6. Antagonism_and_Conflict
  7. Key_Beats_and_Pacing
  8. Research_and_Setting_Specifics
- `webapp/backend/routes/wizard.py` - WebSocket endpoint
- `webapp/frontend-v2/src/pages/AIWizard.jsx` - Chat UI
- `webapp/frontend-v2/src/features/wizard/` - Chat components

**Priority 2: Cost-Effective AI** (~599 lines)
- `factory/ai/model_router.py` - Intelligent model routing
- `factory/ai/ollama_setup.py` - Local Llama 3.3 integration
- **Value**: FREE setup wizard (currently costs $2-5 per user)
- **Fallback**: Chinese models (DeepSeek, Qwen, Kimi) if Ollama issues

**Priority 3: Enhanced Welcome Flow** (~830 lines)
- `webapp/frontend-v2/src/features/welcome/PathSelectionStep.jsx` - 3 paths:
  - Experienced Writer (has manuscript)
  - Prepared Writer (has NotebookLM) ⭐ RECOMMENDED
  - New Writer (needs guidance)
- `webapp/frontend-v2/src/features/welcome/NotebookLMGuide.jsx` - Setup guide
- **Value**: Better onboarding, NotebookLM integration guidance

**Priority 4: Knowledge Graph** (Future - only 25% complete in factory-core)
- `factory/core/cognee_knowledge_graph/` - Entity extraction, graph management
- **Issue**: Web deployment challenges, large dependencies
- **Strategy**: Import when stable, consider alternatives if needed

**Priority 5: NotebookLM Integration** (Existing in factory-core)
- `factory/research/notebooklm_client.py` - Already exists in factory-core
- Sprint 11 implementation (battle-tested)
- **Action**: Copy to writers-platform

---

## Integration Strategy

### Phase 1: Bug Hunting & Stabilization ✅ IN PROGRESS

**Status**: 3/4 bugs fixed, upload testing pending
**Time**: 2-4 hours
**Cost**: ~$20 (Claude Code session)

**Bugs Fixed**:
- ✅ Bug #1: Missing `/auth/me` endpoint
- ✅ Bug #2: Login response missing user object
- ✅ Bug #3: localStorage JSON parsing crash
- 🔄 Bug #4: File upload (testing now)

**Next**: Test upload, fix any remaining bugs, verify deployment

---

### Phase 2: Import AI Setup Wizard (Session 4)

**Goal**: Intelligent onboarding with conversation-based knowledge extraction

**Files to Import**:
```
writers-platform/
├── backend/
│   ├── app/routes/wizard.py                    # NEW - WebSocket endpoint
│   └── app/services/
│       ├── setup_wizard_agent.py              # NEW - Conversation agent
│       ├── category_templates.py              # NEW - 8 templates
│       └── model_router.py                    # NEW - Model routing
└── factory-frontend/src/
    ├── pages/AIWizard.jsx                     # NEW - Main wizard page
    └── features/wizard/
        ├── ChatMessage.jsx                    # NEW - Message display
        ├── ProgressSteps.jsx                  # NEW - Progress tracker
        └── ChatInput.jsx                      # NEW - User input
```

**Integration Steps**:
1. Copy backend files to `backend/app/services/`
2. Add WebSocket dependency to `requirements.txt`: `websockets>=12.0`
3. Register wizard route in `backend/app/main.py`
4. Copy frontend files to `factory-frontend/src/`
5. Add route to `factory-frontend/src/App.jsx`
6. Test end-to-end wizard flow
7. Update project creation to use wizard

**Expected Result**:
- Users answer questions in chat interface
- AI extracts knowledge from NotebookLM
- System generates 8 structured category files
- Project ready with organized reference library

**Time**: 6-8 hours
**Cost**: ~$250
**Value**: Professional onboarding, structured knowledge extraction

---

### Phase 3: Add Local AI Support (Session 5)

**Goal**: FREE AI for setup wizard (save $2-5 per user, critical for course)

**Files to Import**:
```
writers-platform/
└── backend/
    └── app/services/
        ├── ollama_client.py                   # NEW - Ollama integration
        └── model_router.py                    # UPDATE - Add Ollama option
```

**Integration Steps**:
1. Copy `factory/ai/ollama_setup.py` → `backend/app/services/ollama_client.py`
2. Update `model_router.py` to include Ollama/Llama 3.3
3. Add model selection to wizard: "Free (Llama 3.3)" vs "Premium (Claude)"
4. Test Ollama installation and model download
5. Verify wizard works with Llama 3.3
6. Document for course: "How to use free local AI"

**Fallback Plan** (if Ollama issues):
- Use DeepSeek V3 ($0.14 per 1M tokens - 95% cheaper than Claude)
- Use Qwen Max (similar pricing)
- Still cost-effective for course

**Time**: 3-4 hours
**Cost**: ~$150
**Value**: $0 setup for course students (huge win)

---

### Phase 4: Enhanced Welcome Flow (Session 6)

**Goal**: Guide users to NotebookLM setup for best experience

**Files to Import**:
```
writers-platform/
└── factory-frontend/src/
    ├── components/welcome/
    │   ├── PathSelectionStep.jsx              # NEW - 3-path chooser
    │   ├── PathOption.jsx                     # NEW - Path card component
    │   ├── NotebookLMRecommendation.jsx       # NEW - Recommendation modal
    │   └── NotebookLMGuide.jsx                # NEW - Setup guide
    └── pages/Welcome.jsx                      # UPDATE - Add path selection
```

**Integration Steps**:
1. Copy welcome components from factory-core
2. Update `Welcome.jsx` to include path selection
3. Create downloadable NotebookLM setup guide (markdown)
4. Test all 3 paths:
   - Experienced → Upload manuscript
   - Prepared → Enter NotebookLM URLs → AI Wizard
   - New → NotebookLM Guide → Return later
5. Update routing in `App.jsx`

**Time**: 3-4 hours
**Cost**: ~$150
**Value**: Clear onboarding, NotebookLM adoption

---

### Phase 5: NotebookLM Integration (Session 6 continued)

**Goal**: Connect to existing NotebookLM client from Sprint 11

**Files to Import**:
```
writers-platform/
└── backend/
    └── app/services/
        └── notebooklm_client.py               # COPY from factory-core
```

**Integration Steps**:
1. Copy `factory/research/notebooklm_client.py` → `backend/app/services/`
2. Update `setup_wizard_agent.py` to use real NotebookLM client
3. Replace placeholder queries with actual API calls
4. Add NotebookLM credentials to `.env`
5. Test knowledge extraction from user's notebooks
6. Verify export functionality (if needed)

**Time**: 2 hours
**Cost**: ~$100
**Value**: Real knowledge extraction, not placeholders

---

### Phase 6: Knowledge Graph (Future - When Stable)

**Status**: Only 25% complete in factory-core (Sprint 17)
**Strategy**: Wait until factory-core finishes implementation

**Components to Import Later**:
- `factory/core/cognee_knowledge_graph/` - IF web-compatible
- Entity extraction on scene completion
- Development docs export
- Summary generation for NotebookLM upload

**Challenges**:
- Cognee has heavy dependencies (onnxruntime 500MB+)
- May not work well in web deployment
- Caused Railway timeout issues before

**Alternative Options** (if Cognee doesn't work):
1. **Build custom knowledge graph** using:
   - NetworkX (already in requirements.txt)
   - Simple entity extraction with LLMs
   - JSON storage instead of heavy graph DB
2. **Use vector database** instead:
   - Pinecone (cloud)
   - Chroma (local)
   - Simpler integration, faster queries
3. **Hybrid approach**:
   - Basic graph for structure (characters, locations, timeline)
   - Vector DB for semantic search
   - LLM for entity extraction

**Decision Point**: Test Cognee integration first, pivot if issues

**Time**: TBD (4-8 hours when ready)
**Cost**: TBD (~$200-300)

---

## Architectural Changes

### New Directory Structure

```
writers-platform/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── auth.py                        # ✅ Existing
│   │   │   ├── projects.py                    # ✅ Existing
│   │   │   ├── analysis.py                    # ✅ Existing
│   │   │   ├── works.py                       # ✅ Existing (Community)
│   │   │   ├── wizard.py                      # 🆕 NEW - WebSocket wizard
│   │   │   └── knowledge.py                   # 🆕 NEW - Knowledge graph
│   │   ├── services/
│   │   │   ├── setup_wizard_agent.py         # 🆕 NEW - AI wizard
│   │   │   ├── category_templates.py         # 🆕 NEW - Templates
│   │   │   ├── model_router.py               # 🆕 NEW - Model selection
│   │   │   ├── ollama_client.py              # 🆕 NEW - Local AI
│   │   │   ├── notebooklm_client.py          # 🆕 NEW - NotebookLM
│   │   │   ├── file_parser.py                # ✅ Existing
│   │   │   └── orchestrator.py               # ✅ Existing
│   │   └── models/
│   │       ├── user.py                        # ✅ Existing
│   │       ├── project.py                     # ✅ Existing
│   │       ├── scene.py                       # ✅ Existing
│   │       ├── work.py                        # ✅ Existing (Community)
│   │       └── category.py                    # 🆕 NEW - Knowledge categories
│   └── engine/
│       ├── orchestration/                     # ✅ Existing - Tournament
│       ├── agents/                            # ✅ Existing - AI integrations
│       └── knowledge/                         # 🆕 NEW - Knowledge graph
├── factory-frontend/
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.jsx                  # ✅ Existing
│       │   ├── Upload.jsx                     # ✅ Existing
│       │   ├── Editor.jsx                     # ✅ Existing
│       │   ├── AIWizard.jsx                   # 🆕 NEW - Wizard UI
│       │   └── Welcome.jsx                    # 🆕 UPDATE - Add paths
│       ├── features/
│       │   ├── wizard/                        # 🆕 NEW - Wizard components
│       │   └── welcome/                       # 🆕 NEW - Welcome components
│       └── api/
│           └── factory.ts                     # 🆕 UPDATE - Add wizard APIs
└── community-frontend/                        # ✅ Existing (if separate)
```

### Database Schema Additions

**New Tables**:

```sql
-- Knowledge categories (8 types from templates)
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- Characters, Story_Structure, etc.
    data JSONB NOT NULL,         -- Structured category data
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Wizard session tracking
CREATE TABLE wizard_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    status VARCHAR(20),          -- in_progress, completed, abandoned
    current_category VARCHAR(50),
    progress JSONB,              -- Category completion status
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Knowledge graph entities (if Cognee alternative)
CREATE TABLE entities (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    entity_type VARCHAR(50),     -- character, location, plot_thread, motif
    name VARCHAR(255),
    description TEXT,
    attributes JSONB,
    created_at TIMESTAMP
);

-- Entity relationships
CREATE TABLE entity_relationships (
    id UUID PRIMARY KEY,
    from_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    to_entity_id UUID REFERENCES entities(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50),
    strength FLOAT,              -- 0.0 to 1.0
    context TEXT
);
```

### API Additions

**New Endpoints**:

```
POST   /api/wizard/start                      # Start new wizard session
WS     /api/wizard/chat/{session_id}          # WebSocket chat
GET    /api/wizard/progress/{session_id}      # Get progress
POST   /api/wizard/reset/{session_id}         # Reset session

GET    /api/categories/{project_id}           # List categories
GET    /api/categories/{project_id}/{type}    # Get specific category
PUT    /api/categories/{project_id}/{type}    # Update category

GET    /api/models/available                  # List available models
GET    /api/models/cost-estimate              # Estimate cost

POST   /api/notebooklm/query                  # Query NotebookLM
GET    /api/notebooklm/notebooks              # List user's notebooks

GET    /api/knowledge/entities/{project_id}   # List entities
GET    /api/knowledge/graph/{project_id}      # Get full graph
POST   /api/knowledge/extract                 # Extract from scene
```

---

## Cost Breakdown

### Budget: $800 for 24 hours

**Session 4: AI Setup Wizard** (~$250)
- Import wizard backend (~4 hours)
- Import wizard frontend (~2 hours)
- Integration testing (~2 hours)
- Total: 8 hours @ ~$31/hour

**Session 5: Local AI** (~$150)
- Import Ollama integration (~2 hours)
- Test with wizard (~1 hour)
- Fallback to Chinese models if needed (~1 hour)
- Total: 4 hours @ ~$37/hour

**Session 6: Welcome Flow + NotebookLM** (~$250)
- Import welcome components (~2 hours)
- Import NotebookLM client (~2 hours)
- Integration testing (~2 hours)
- Total: 6 hours @ ~$42/hour

**Buffer**: ~$150 for bug fixes and polish

---

## Risk Mitigation

### Risk 1: Cognee Knowledge Graph Won't Deploy on Railway
**Likelihood**: Medium (heavy dependencies, caused issues before)
**Impact**: Medium (nice-to-have, not critical)
**Mitigation**:
1. Test Cognee integration in separate Railway service first
2. If fails, build lightweight alternative with NetworkX + LLMs
3. If that fails, use vector DB (Pinecone/Chroma)
4. Worst case: Skip knowledge graph for v1, add later

### Risk 2: Ollama Local AI Doesn't Work Well
**Likelihood**: Low (well-tested in factory-core)
**Impact**: Medium (affects cost savings)
**Mitigation**:
1. Test Ollama on various systems (Mac, Windows, Linux)
2. Document system requirements clearly
3. Fallback to DeepSeek V3 ($0.14 per 1M tokens)
4. Provide both options: "Free (local)" vs "Cheap (DeepSeek)" vs "Premium (Claude)"

### Risk 3: NotebookLM API Changes or Breaks
**Likelihood**: Low (stable API)
**Impact**: High (critical for onboarding)
**Mitigation**:
1. Test NotebookLM client thoroughly
2. Add error handling and fallbacks
3. If API unavailable, allow manual category entry
4. Document workaround for course

### Risk 4: WebSocket Connection Issues in Production
**Likelihood**: Low (standard tech)
**Impact**: Medium (wizard degraded experience)
**Mitigation**:
1. Add WebSocket health checks
2. Fallback to HTTP polling if WebSocket fails
3. Test on Railway production environment
4. Configure Railway for WebSocket support

---

## Success Metrics

### Phase 1: Bug Hunting ✅
- ✅ All critical bugs fixed
- ✅ Upload works end-to-end
- ✅ Analysis can be triggered
- ✅ No console errors

### Phase 2: AI Wizard
- ✅ Users can complete wizard in 10-15 minutes
- ✅ 8 category files generated with structured data
- ✅ NotebookLM integration works (queries return relevant data)
- ✅ Chat interface is responsive and smooth

### Phase 3: Local AI
- ✅ Ollama/Llama 3.3 works on Mac/Linux
- ✅ Setup wizard costs $0 with local AI
- ✅ Fallback to DeepSeek works if Ollama unavailable
- ✅ Course documentation explains both options

### Phase 4: Welcome Flow
- ✅ All 3 paths work correctly
- ✅ NotebookLM guide is clear and downloadable
- ✅ "Prepared Writer" path is marked as recommended
- ✅ Users can navigate between paths smoothly

### Phase 5: NotebookLM Integration
- ✅ Real queries to NotebookLM return valid data
- ✅ No placeholder responses
- ✅ Error handling works for invalid notebooks
- ✅ Multiple notebook sources supported

### Phase 6: Knowledge Graph (Future)
- ✅ Entity extraction works on scene completion
- ✅ Graph queries return relevant information
- ✅ Export summaries for NotebookLM
- ✅ Performance acceptable on web deployment

---

## Testing Plan

### Automated Tests (Post-Integration)
```bash
# Backend tests
pytest backend/tests/test_wizard.py
pytest backend/tests/test_models.py
pytest backend/tests/test_notebooklm.py

# Frontend tests
npm test -- wizard
npm test -- welcome
```

### Manual Testing Checklist

**Setup Wizard**:
- [ ] Start new wizard session
- [ ] Answer questions in chat
- [ ] Navigate through all 8 categories
- [ ] System queries NotebookLM correctly
- [ ] Category files generated with correct structure
- [ ] Project created successfully

**Local AI**:
- [ ] Select "Free (Llama 3.3)" option
- [ ] Ollama downloads model automatically
- [ ] Wizard works with local AI
- [ ] Response quality acceptable
- [ ] Fallback to DeepSeek works

**Welcome Flow**:
- [ ] Path selection shows 3 options clearly
- [ ] "Prepared Writer" marked as recommended
- [ ] NotebookLM guide is comprehensive
- [ ] Guide downloads as markdown
- [ ] Each path routes correctly

**NotebookLM**:
- [ ] Can enter notebook URLs
- [ ] Queries return relevant data
- [ ] Multiple notebooks supported
- [ ] Error handling for invalid URLs
- [ ] Category extraction works

**End-to-End**:
- [ ] New user → Welcome → Prepared path → Wizard → Project created
- [ ] User can upload manuscript after wizard
- [ ] Analysis works on wizard-created project
- [ ] Can publish from Factory to Community

---

## Documentation Updates Needed

### For Developers
1. **ARCHITECTURE.md** - Update with new components
2. **API_REFERENCE.md** - Document new endpoints
3. **DEPLOYMENT.md** - Add Ollama setup instructions
4. **CONTRIBUTING.md** - Update with wizard development guidelines

### For Users/Course
1. **QUICK_START.md** - New onboarding flow
2. **NOTEBOOKLM_GUIDE.md** - How to set up NotebookLM
3. **LOCAL_AI_SETUP.md** - Installing Ollama/Llama 3.3
4. **FAQ.md** - Common wizard/setup questions

---

## Deployment Checklist

### Railway Backend
- [ ] WebSocket support enabled
- [ ] Environment variables set:
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `GOOGLE_API_KEY`
  - `DEEPSEEK_API_KEY` (fallback)
  - `NOTEBOOKLM_API_KEY` (if needed)
- [ ] Database migrations run
- [ ] Health check passes

### Vercel Frontend
- [ ] Environment variables set:
  - `VITE_API_URL=https://writers-platform-production.up.railway.app/api`
  - `VITE_WS_URL=wss://writers-platform-production.up.railway.app`
- [ ] Build passes
- [ ] All routes accessible

---

## Timeline Summary

| Phase | Time | Cost | Status |
|-------|------|------|--------|
| Phase 1: Bug Hunting | 2-4 hrs | ~$20 | ✅ In Progress |
| Phase 2: AI Wizard | 8 hrs | ~$250 | 📋 Planned |
| Phase 3: Local AI | 4 hrs | ~$150 | 📋 Planned |
| Phase 4: Welcome Flow | 4 hrs | ~$150 | 📋 Planned |
| Phase 5: NotebookLM | 2 hrs | ~$100 | 📋 Planned |
| Phase 6: Knowledge Graph | TBD | TBD | 🔮 Future |
| **Total** | **20-22 hrs** | **~$670** | **3 sessions** |

**Buffer**: $130 remaining for unexpected issues

---

## Next Actions (Immediate)

1. ✅ **Continue bug hunting** (you + Claude Code now)
2. 📋 **Prepare Session 4 brief** for Claude Cloud:
   - Import AI wizard (backend + frontend)
   - Test WebSocket connection
   - Verify category generation
3. 📋 **Test current deployment** after bug fixes
4. 📋 **Document Session 4 requirements** for handoff

---

## Long-Term Vision

### v1.0 (Next 24 hours)
- ✅ Factory + Community unified platform
- ✅ AI Setup Wizard with 8 categories
- ✅ Local AI support (free)
- ✅ NotebookLM integration
- ✅ Enhanced welcome flow

### v1.1 (Post-Course)
- Knowledge graph with entity extraction
- Advanced analysis features
- Model comparison UI
- Voice profile extraction

### v2.0 (Future)
- Collaborative writing
- Real-time co-editing
- Advanced badge system
- Professional marketplace

---

## Questions for Decision

1. **Knowledge Graph**: Start with Cognee or build custom from day 1?
   - **Recommendation**: Try Cognee first, pivot if issues

2. **Local AI**: Ollama required or optional?
   - **Recommendation**: Optional with DeepSeek fallback

3. **Welcome Flow**: All 3 paths or just "Prepared Writer"?
   - **Recommendation**: All 3 paths for flexibility

4. **Testing**: Automated tests now or after course?
   - **Recommendation**: Manual testing now, automate later

---

## Contact & Collaboration

**Current Session**: Claude Code (Bug hunting)
**Next Sessions**: Claude Cloud (Feature integration)
**Coordination**: Update this document after each session
**Git Branch Strategy**: Feature branches → `main` after testing

---

*Last Updated: 2025-01-17 (Phase 1 - Bug Hunting)*
