# Writers Platform: Master Roadmap
## Consolidating All Integration Plans

**Created**: 2025-01-17
**Status**: Phase 1 Complete, Phase 2-4 Planned
**Total Budget**: $1,000-1,200 (24-48 hours)

---

## Overview: Two Parallel Tracks

We're building a unified platform with TWO frontends:

### Track A: Writers Factory (Private Workspace)
**Domain**: writersfactory.app
**Purpose**: Write, analyze, improve with AI
**Status**: Deployed ✅, needs enhanced onboarding

### Track B: Writers Community (Public Showcase)
**Domain**: writerscommunity.app
**Purpose**: Publish, validate, discover works
**Status**: Needs migration to Vercel

---

## Phase 1: Foundation & Bug Fixes ✅ COMPLETE

**Duration**: 4 hours
**Cost**: ~$50
**Status**: DONE

### Completed:
- ✅ Backend deployed to Railway
- ✅ Factory frontend deployed to Vercel
- ✅ Bug #1: Added `/auth/me` endpoint
- ✅ Bug #2: Login returns user object
- ✅ Bug #3: Fixed localStorage JSON parsing
- ✅ Documentation created

### Pending Bug Fixes:
- 🔄 Bug #4: API key environment variable support (discovered, not yet fixed)
- 🔄 Upload testing

---

## Phase 2: Community Platform Migration (SESSION 3)

**Duration**: 6-8 hours
**Cost**: $200-300
**Priority**: HIGH (complete public platform)
**Status**: PLANNED

### Claude Cloud's Plan (SESSION_3_INTEGRATION.md):

**2.1: Migrate Community to Vercel** (2 hours)
- Copy community-frontend from old repo
- Update API client to point to Railway backend
- Add `vercel.json` configuration
- Deploy to writerscommunity.app

**2.2: Add Badge System** (2 hours)
- Update WorkCard component with badges
- Display 4 badge types:
  - `ai_analyzed`: From Factory analysis
  - `human_verified`: AI detection passed
  - `human_self`: Self-certified human
  - `community`: Standard upload
- Show badge metadata (scores, models used)

**2.3: Direct Upload Flow** (2 hours)
- Create UploadWork page
- File upload with DOCX/PDF/TXT support
- Optional "claim human-authored" checkbox
- Backend auto-analysis and badge assignment
- CTA to Factory for professional feedback

**2.4: Factory Integration CTAs** (1 hour)
- Add Factory analysis results on work pages
- "Get AI Feedback" CTA for non-Factory works
- Link back to Factory projects

**2.5: Landing Page Updates** (1 hour)
- Badge explainer section
- "Discover AI-Validated Fiction" hero
- Featured works showcase

**2.6: Browse Filters** (1 hour)
- Filter by badge type
- Updated API with `badge_type` parameter

**Deliverable**:
```
✅ Community migrated to Vercel
✅ Badge system live
✅ Direct upload working
✅ Factory ↔ Community integration complete
```

---

## Phase 3: AI Setup Wizard (SESSION 4)

**Duration**: 6-8 hours
**Cost**: $250-300
**Priority**: HIGH (course onboarding)
**Status**: PLANNED

### Our Plan (UNIFIED_PLATFORM_INTEGRATION_PLAN.md):

**3.1: Import Wizard Backend** (3 hours)
- Copy `setup_wizard_agent.py` - Conversation agent
- Copy `category_templates.py` - 8 knowledge categories
- Copy `model_router.py` - Model selection
- Add WebSocket endpoint `wizard.py`
- Create Category database model

**3.2: Import Wizard Frontend** (2 hours)
- Copy `AIWizard.jsx` - Main wizard page
- Copy `ChatMessage.jsx` - Message display
- Copy `ProgressSteps.jsx` - Progress tracker
- Add route and navigation

**3.3: Integration** (2 hours)
- Database migration for categories table
- Test WebSocket connection
- Verify 8-category flow
- Placeholder NotebookLM queries (real integration in Phase 4)

**3.4: Dashboard Integration** (1 hour)
- Add "AI Setup Wizard" button
- Route to wizard from project creation
- Update project creation to use wizard output

**Deliverable**:
```
✅ AI wizard accessible from Factory dashboard
✅ Chat-based onboarding (not form-based)
✅ 8 categories of knowledge extracted
✅ Professional UX with real-time updates
```

---

## Phase 4: Cost Optimization (SESSION 5)

**Duration**: 3-4 hours
**Cost**: $150-200
**Priority**: MEDIUM (course cost savings)
**Status**: PLANNED

### 4.1: Ollama/Llama 3.3 Integration (2 hours)
- Import `ollama_client.py`
- Update `model_router.py` with local AI option
- Test wizard with Llama 3.3 (FREE)
- Add model selection UI: "Free (Local)" vs "Premium (Claude)"

### 4.2: Fallback to Chinese Models (1 hour)
- Add DeepSeek V3 configuration ($0.14 per 1M tokens)
- Test as Ollama alternative
- Document both options for course

### 4.3: Documentation (1 hour)
- "How to use free local AI" guide
- System requirements for Ollama
- Cost comparison table

**Deliverable**:
```
✅ FREE setup wizard option (Ollama)
✅ $0 onboarding for course students
✅ Cheap fallback (DeepSeek) if Ollama unavailable
```

---

## Phase 5: Enhanced Welcome Flow (SESSION 6)

**Duration**: 3-4 hours
**Cost**: $150-200
**Priority**: MEDIUM (polish)
**Status**: PLANNED

### 5.1: Path Selection (2 hours)
- Import `PathSelectionStep.jsx` - 3-path chooser:
  - **Experienced Writer**: Has manuscript → Upload
  - **Prepared Writer**: Has NotebookLM → Wizard ⭐ RECOMMENDED
  - **New Writer**: Needs guidance → NotebookLM Guide
- Import `PathOption.jsx` - Path cards
- Import `NotebookLMRecommendation.jsx` - Modal for new writers

### 5.2: NotebookLM Guide (1 hour)
- Import `NotebookLMGuide.jsx` - 5-step setup guide
- Downloadable markdown guide
- Return-to-app flow

### 5.3: Real NotebookLM Integration (1 hour)
- Copy `notebooklm_client.py` from factory-core
- Replace placeholder queries in wizard
- Test knowledge extraction

**Deliverable**:
```
✅ Clear 3-path onboarding
✅ NotebookLM setup guidance
✅ Real knowledge extraction (not placeholders)
```

---

## Phase 6: Knowledge Graph (FUTURE)

**Duration**: TBD (4-8 hours when ready)
**Cost**: $200-400
**Priority**: LOW (only 25% complete in factory-core)
**Status**: DEFERRED

### When factory-core Sprint 17 completes:

**6.1: Cognee Integration** (2 hours)
- Test Cognee on Railway (heavy dependencies)
- If fails: Build lightweight alternative with NetworkX

**6.2: Entity Extraction** (2 hours)
- Extract entities on scene completion
- Update knowledge graph automatically

**6.3: Export System** (2 hours)
- Generate summaries for NotebookLM upload
- Development docs logging

**Alternative Plan** (if Cognee fails):
- Custom knowledge graph with NetworkX + LLMs
- Vector database (Pinecone/Chroma)
- Hybrid approach (basic graph + vector search)

**Deliverable**: TBD based on factory-core progress

---

## Bug Fixes (Ongoing)

### Current Known Bugs:

**Bug #4: API Key Environment Variables** ⚠️ CRITICAL
- **Issue**: Tournament system expects `credentials.json` file
- **Impact**: AI analysis will fail on Railway (uses env vars)
- **Fix Required**: Add environment variable fallback to `GoogleStoreConfig`
- **Priority**: Fix before Session 3 or 4
- **Estimated Time**: 30 minutes

**Bug #5: Upload Testing** 🔄 PENDING
- **Status**: Needs user testing
- **Expected**: Should work after Bug #1-3 fixes
- **If Fails**: Will debug based on error message

---

## Consolidated Timeline

| Phase | Duration | Cost | Status | Dependencies |
|-------|----------|------|--------|--------------|
| Phase 1: Foundation | 4h | $50 | ✅ Done | None |
| **Bug #4 Fix** | 0.5h | $20 | ⚠️ Critical | Before Phase 2/3 |
| Phase 2: Community | 8h | $250 | 📋 Ready | Bug #4 fixed |
| Phase 3: AI Wizard | 8h | $250 | 📋 Ready | Phase 2 optional |
| Phase 4: Local AI | 4h | $150 | 📋 Ready | Phase 3 done |
| Phase 5: Welcome Flow | 4h | $150 | 📋 Ready | Phase 3-4 done |
| Phase 6: Knowledge Graph | 8h | $300 | 🔮 Future | factory-core Sprint 17 |
| **Total** | **36.5h** | **$1,170** | **5 phases ready** | |

---

## Execution Strategy

### Parallel vs Sequential

**Can Run in Parallel** (2 sessions simultaneously):
- Phase 2 (Community) + Phase 3 (AI Wizard)
  - Different frontends, no conflicts
  - Both use same backend API
  - Can deploy independently

**Must Run Sequentially**:
- Phase 3 → Phase 4 → Phase 5 (wizard dependencies)
- Bug #4 must be fixed before any AI analysis work

### Recommended Order:

**Option A: Fast Track (24 hours, $670)**
1. Fix Bug #4 (30 min)
2. Phase 3: AI Wizard (8h) ← For January course
3. Phase 4: Local AI (4h) ← Cost savings for course
4. Phase 5: Welcome Flow (4h) ← Polish for course
5. **Skip Phase 2** temporarily (Community can wait)

**Option B: Complete Platform (36 hours, $1,170)**
1. Fix Bug #4 (30 min)
2. **Parallel Session**:
   - Phase 2: Community (8h)
   - Phase 3: AI Wizard (8h)
3. Phase 4: Local AI (4h)
4. Phase 5: Welcome Flow (4h)

**Option C: Prioritize Community (20 hours, $620)**
1. Fix Bug #4 (30 min)
2. Phase 2: Community (8h) ← Public platform complete
3. Phase 3: AI Wizard (8h) ← Factory onboarding
4. **Defer Phases 4-5** to post-course

---

## Success Metrics

### Phase 2 Success:
- [ ] Community deployed to writerscommunity.app
- [ ] Users can browse works with badges
- [ ] Direct upload works with auto-analysis
- [ ] Factory ↔ Community bridge functional

### Phase 3 Success:
- [ ] AI wizard accessible from Factory dashboard
- [ ] Users complete 8-category knowledge extraction
- [ ] Projects created with structured reference library
- [ ] WebSocket chat interface responsive

### Phase 4 Success:
- [ ] Ollama/Llama 3.3 works on target platforms
- [ ] Setup wizard costs $0 with local AI
- [ ] Fallback to DeepSeek documented and tested

### Phase 5 Success:
- [ ] 3 onboarding paths clearly presented
- [ ] NotebookLM guide comprehensive and downloadable
- [ ] Real NotebookLM integration working

---

## Resource Allocation

### Budget: $1,000-1,200 available

**Critical Path** (must do for January course):
- Bug #4: $20
- Phase 3: $250 (AI wizard)
- Phase 4: $150 (local AI)
- Phase 5: $150 (welcome flow)
- **Subtotal**: $570 (leaves $430 buffer)

**Nice to Have**:
- Phase 2: $250 (Community platform)
- Buffer: $180 (unexpected issues)

**Deferred**:
- Phase 6: $300 (knowledge graph - wait for factory-core)

---

## Risk Assessment

### High Risk:
1. **Bug #4 not fixed**: AI analysis will fail on Railway
   - **Mitigation**: Fix immediately (30 min)
2. **Ollama deployment issues**: Local AI may not work everywhere
   - **Mitigation**: DeepSeek fallback ($0.14 per 1M tokens)

### Medium Risk:
1. **WebSocket connection issues**: Railway WebSocket support
   - **Mitigation**: HTTP polling fallback
2. **NotebookLM API changes**: External dependency
   - **Mitigation**: Manual category entry fallback

### Low Risk:
1. **Vercel deployment**: Well-tested platform
2. **Community migration**: Straightforward copy

---

## Decision Points

### Decision 1: Parallel or Sequential?
**Recommendation**: Run Phase 2 & 3 in parallel IF:
- Two separate Claude sessions available
- Budget allows $500 simultaneously
- Want both platforms done fast

Otherwise: Sequential (Phase 3 → 2)

### Decision 2: Community First or Wizard First?
**For January course**: Wizard first (Phase 3-4-5)
**For public launch**: Community first (Phase 2)

### Decision 3: Skip Phases 4-5?
**If tight budget**: Can defer to post-course
**If $800+ available**: Do all phases for complete experience

---

## Handoff Instructions

### For Claude Cloud (Community - Phase 2):
- **Read**: `SESSION_3_INTEGRATION.md` (root directory)
- **Branch**: Create new branch from `main`
- **Focus**: Community frontend migration + badges
- **Test**: Both frontends work independently

### For Claude Cloud (Wizard - Phase 3):
- **Read**: `docs/SESSION_4_BRIEF.md`
- **Branch**: Create new branch from `main`
- **Focus**: AI wizard import + integration
- **Test**: Wizard completes 8-category flow

### For Current Session (Bug Fixes):
- **Priority**: Fix Bug #4 (API keys)
- **Test**: Upload and analysis features
- **Document**: Any new bugs found

---

## Communication Protocol

### After Each Phase:
1. Update this document with completion status
2. Document any issues or deviations
3. Test deployed features
4. Get user approval before next phase

### If Blocked:
1. Document blocker in this file
2. Propose alternative approach
3. Get user decision before proceeding

---

## Final Architecture (Target State)

```
┌─────────────────────────────────────────────────────────────┐
│                   WRITERS PLATFORM                          │
│              (Unified Backend on Railway)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│ WRITERS FACTORY  │        │ WRITERS COMMUNITY│
│ (Vercel)         │        │ (Vercel)         │
├──────────────────┤        ├──────────────────┤
│ writersfactory   │        │ writerscommunity │
│     .app         │        │     .app         │
├──────────────────┤        ├──────────────────┤
│ • AI Wizard ✨   │        │ • Browse Works   │
│ • Setup Guide    │        │ • Badge System   │
│ • Write Scenes   │        │ • Direct Upload  │
│ • AI Analysis    │───Publish─────▶ • Discovery      │
│ • Tournament     │        │ • Comments       │
│ • Local AI       │◀──Validated────│ • Ratings        │
│ • NotebookLM     │        │ • Reading Lists  │
└──────────────────┘        └──────────────────┘
```

---

## Version History

**v1.0** (2025-01-17): Initial master roadmap consolidating:
- SESSION_3_INTEGRATION.md (Claude Cloud's Community plan)
- UNIFIED_PLATFORM_INTEGRATION_PLAN.md (Our Wizard plan)
- Bug hunting results (Bug #1-4)

**Next Update**: After Phase 2 or 3 completion

---

*Created by: Claude Code & Claude Cloud*
*Maintained by: Writers Platform Team*
*Last Updated: 2025-01-17 21:00 UTC*
