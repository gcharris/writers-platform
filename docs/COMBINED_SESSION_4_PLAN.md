# Session 4: Combined Implementation Plan
## Merging Cloud Claude (Architecture) + Desktop Claude (Import) Approaches

**Created**: 2025-01-17
**Status**: READY TO EXECUTE
**Priority**: HIGH (Critical for January course)

---

## Executive Summary

After comparing two parallel Session 4 plans, here's the **optimal combined approach**:

### Cloud Claude's Approach (ARCHITECTURE.md)
- ✅ **Strength**: Comprehensive architecture documentation
- ✅ **Strength**: Detailed system design and technology stack
- ❌ **Issue**: Started building from scratch (Ollama integration)
- ❌ **Issue**: Would rebuild ~3,200 lines of existing code

### Desktop Claude's Approach (SESSION_4_BRIEF.md)
- ✅ **Strength**: Practical "copy existing files" strategy
- ✅ **Strength**: Knows exact source paths in factory-core
- ✅ **Strength**: Files are battle-tested (100,000 lines, 17 sprints)
- ❌ **Issue**: Less architectural documentation

### ⭐ COMBINED APPROACH
**Use Desktop Claude's import strategy + Cloud Claude's architecture docs**

1. **Import** existing files from factory-core (don't rebuild!)
2. **Keep** ARCHITECTURE.md for system documentation
3. **Adapt** imported files to writers-platform structure
4. **Test** end-to-end with existing battle-tested code

---

## Key Insight: Don't Rebuild What Exists!

The files we need **already exist** in `writers-factory-core`:

```
/Users/gch2024/Documents/Documents - Mac Mini/Explant drafts current/factory/
├── ai/
│   ├── setup_wizard_agent.py        # ✅ EXISTS (~800 lines)
│   ├── model_router.py              # ✅ EXISTS (~200 lines)
│   └── ollama_setup.py              # ✅ EXISTS (~150 lines)
├── templates/
│   └── category_templates.py        # ✅ EXISTS (~1,500 lines)
└── webapp/
    ├── backend/routes/wizard.py     # ✅ EXISTS (~400 lines)
    └── frontend-v2/src/
        ├── pages/AIWizard.jsx       # ✅ EXISTS (~300 lines)
        └── features/wizard/         # ✅ EXISTS (~200 lines)
```

**Total**: ~3,550 lines of battle-tested code from 17 sprints

Cloud Claude started rebuilding `ollama_setup.py` from scratch - **STOP!** Let's copy the existing file instead.

---

## Comparison of Approaches

| Aspect | Cloud Claude | Desktop Claude | COMBINED |
|--------|-------------|----------------|----------|
| **Strategy** | Build from scratch | Copy existing files | Copy + Adapt |
| **Architecture Docs** | ✅ Excellent (ARCHITECTURE.md) | ❌ Missing | ✅ Keep Cloud's docs |
| **Implementation** | ❌ Rebuilding (~8h) | ✅ Copy (~2h) | ✅ Copy (~2h) |
| **Code Quality** | ⚠️ Untested | ✅ Battle-tested | ✅ Battle-tested |
| **Integration** | ⚠️ From requirements | ✅ Known paths | ✅ Known paths |
| **Timeline** | ~8 hours | ~6 hours | ~5 hours |
| **Cost** | ~$250 | ~$250 | ~$200 |

**Winner**: Desktop Claude's copy strategy + Cloud Claude's architecture docs

---

## Combined Plan: Session 4 Implementation

### Phase 1: Import Backend (2 hours)

**1.1: Copy AI Services** (45 min)

```bash
# User needs to provide these files from factory-core
# Desktop Claude knows the paths:
SOURCE="/Users/gch2024/Documents/Documents - Mac Mini/Explant drafts current/factory/"

# Copy to writers-platform:
mkdir -p backend/app/services/wizard
mkdir -p backend/app/services/ai

cp "$SOURCE/ai/setup_wizard_agent.py" backend/app/services/wizard/
cp "$SOURCE/templates/category_templates.py" backend/app/services/wizard/
cp "$SOURCE/ai/model_router.py" backend/app/services/ai/
cp "$SOURCE/ai/ollama_setup.py" backend/app/services/ai/
cp "$SOURCE/webapp/backend/routes/wizard.py" backend/app/routes/
```

**1.2: Adapt Imports** (30 min)

Update imports to match writers-platform structure:

```python
# In all imported files, change:
from factory.ai.* → from app.services.ai.*
from factory.templates.* → from app.services.wizard.*
from webapp.backend.* → from app.*
```

**1.3: Add Category Model** (15 min)

```python
# backend/app/models/category.py
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    category_type = Column(String(50), nullable=False)
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**1.4: Register Routes** (15 min)

```python
# backend/app/main.py
from app.routes import wizard  # Add import

# Register wizard WebSocket route
app.include_router(wizard.router, prefix=settings.API_PREFIX)
```

**1.5: Database Migration** (15 min)

```bash
cd backend
alembic revision --autogenerate -m "Add categories table for wizard"
alembic upgrade head
```

### Phase 2: Import Frontend (1.5 hours)

**2.1: Copy Wizard Components** (30 min)

```bash
SOURCE_FE="$SOURCE/webapp/frontend-v2/src/"

mkdir -p factory-frontend/src/pages
mkdir -p factory-frontend/src/features/wizard

cp "$SOURCE_FE/pages/AIWizard.jsx" factory-frontend/src/pages/
cp "$SOURCE_FE/features/wizard/ChatMessage.jsx" factory-frontend/src/features/wizard/
cp "$SOURCE_FE/features/wizard/ProgressSteps.jsx" factory-frontend/src/features/wizard/
```

**2.2: Convert JSX to TypeScript** (45 min)

Factory frontend uses TypeScript - convert the JSX files:

```bash
# Rename and adapt:
mv factory-frontend/src/pages/AIWizard.jsx factory-frontend/src/pages/AIWizard.tsx
mv factory-frontend/src/features/wizard/ChatMessage.jsx factory-frontend/src/features/wizard/ChatMessage.tsx
mv factory-frontend/src/features/wizard/ProgressSteps.jsx factory-frontend/src/features/wizard/ProgressSteps.tsx
```

Add TypeScript types for props and state.

**2.3: Add Wizard Route** (15 min)

```typescript
// factory-frontend/src/App.tsx
import AIWizard from './pages/AIWizard';

// Add route:
<Route path="/wizard" element={<AIWizard />} />
```

### Phase 3: Integration (1.5 hours)

**3.1: Wizard API Client** (30 min)

```typescript
// factory-frontend/src/api/factory.ts

export const wizardApi = {
  startSession: async (projectId: string) => {
    const response = await apiClient.post('/wizard/start', { project_id: projectId });
    return response.data;
  },

  connectWebSocket: (sessionId: string) => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    return new WebSocket(`${wsUrl}/api/wizard/chat/${sessionId}`);
  },

  getProgress: async (sessionId: string) => {
    const response = await apiClient.get(`/wizard/progress/${sessionId}`);
    return response.data;
  },

  saveCategory: async (sessionId: string, category: string, data: any) => {
    const response = await apiClient.post(`/wizard/save`, {
      session_id: sessionId,
      category,
      data,
    });
    return response.data;
  },
};
```

**3.2: Dashboard Integration** (30 min)

```typescript
// factory-frontend/src/pages/Dashboard.tsx

// Add wizard button:
<button
  onClick={() => navigate('/wizard')}
  className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
>
  <SparklesIcon className="h-5 w-5 mr-2" />
  AI Setup Wizard
</button>
```

**3.3: Environment Variables** (15 min)

```bash
# backend/.env
ANTHROPIC_API_KEY=your_key_here  # For wizard (can use Ollama later)

# factory-frontend/.env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

**3.4: Update Requirements** (15 min)

```txt
# backend/requirements.txt
# WebSocket already included in FastAPI[all]
httpx>=0.24.0  # For Ollama client (if not present)
```

### Phase 4: Testing (1 hour)

**4.1: Backend WebSocket Test** (20 min)

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Test WebSocket (in another terminal)
wscat -c ws://localhost:8000/api/wizard/chat/test-session-id

# Expected: Connection established, can send/receive messages
```

**4.2: Frontend Wizard Test** (20 min)

```bash
cd factory-frontend
npm run dev

# Open http://localhost:5173
# Navigate to /wizard
# Verify:
# - Chat interface loads
# - Can type and send messages
# - Progress tracker shows 8 categories
# - WebSocket connection icon shows "connected"
```

**4.3: End-to-End Flow** (20 min)

Test complete wizard flow:

1. Login to Factory
2. Click "AI Setup Wizard"
3. Answer questions across all 8 categories
4. Verify category data saved to database
5. Return to dashboard
6. Verify project has wizard data

---

## What We're NOT Building

Because Desktop Claude's files already include:

❌ **Don't build** `ollama_setup.py` from scratch (Cloud Claude started this - DISCARD)
❌ **Don't build** category templates (already ~1,500 lines in factory-core)
❌ **Don't build** wizard agent (already ~800 lines in factory-core)
❌ **Don't build** WebSocket endpoint (already ~400 lines in factory-core)
❌ **Don't build** chat UI (already ~300 lines in factory-core)

✅ **Do** import, adapt imports, and integrate into writers-platform structure

---

## Key Architectural Decisions (from Cloud Claude's ARCHITECTURE.md)

### Why This Architecture Works

**1. Dual Frontend Pattern** (from ARCHITECTURE.md)
- Factory frontend: Private workspace for creation
- Community frontend: Public showcase for reading
- Shared backend: Unified API and data models

**2. Cost Optimization Strategy** (from both plans)
- FREE local AI (Llama 3.3 via Ollama) for wizard setup
- Paid cloud APIs (Claude, GPT, etc.) for actual scene analysis
- Estimated savings: $5-10 per project setup → $0

**3. WebSocket for Real-Time Chat** (from SESSION_4_BRIEF.md)
- Smooth conversational experience
- Bi-directional communication
- Session state managed in database

**4. 8-Category Knowledge Structure** (from factory-core)
1. Characters (15+ fields)
2. Story_Structure
3. World_Building
4. Themes_and_Philosophy
5. Voice_and_Craft
6. Antagonism_and_Conflict
7. Key_Beats_and_Pacing
8. Research_and_Setting_Specifics

---

## Database Schema (from ARCHITECTURE.md)

```sql
-- New table for wizard sessions
CREATE TABLE wizard_sessions (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    current_category VARCHAR(50),
    progress JSONB,              -- Category completion status
    conversation_history JSONB,  -- Full chat log
    status VARCHAR(20),          -- in_progress, completed, abandoned
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Categories table (8 types)
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    category_type VARCHAR(50),   -- Characters, Story_Structure, etc.
    data JSONB,                  -- Structured category data
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Timeline & Cost

| Phase | Desktop Plan | Cloud Plan | COMBINED |
|-------|-------------|-----------|----------|
| Backend Import | 2h | 4h (building) | **1.5h** (copying) |
| Frontend Import | 2h | 2h (building) | **1.5h** (copying+TS) |
| Integration | 2h | 2h | **1.5h** |
| Testing | 2h | 2h | **1h** |
| **Total** | **8h** | **10h** | **5.5h** ⭐ |
| **Cost** | **$250** | **$300** | **~$200** ⭐ |

**Savings**: 2.5-4.5 hours by using existing code!

---

## Risk Mitigation

### Risk 1: Files Don't Exist at Expected Paths
**Likelihood**: Low
**Mitigation**: User will provide actual paths from their system

### Risk 2: Import Path Conflicts
**Likelihood**: Medium
**Mitigation**: Systematic find-replace for all imports (30 min)

### Risk 3: TypeScript Conversion Issues
**Likelihood**: Medium
**Mitigation**: Focus on type safety, add `any` temporarily if needed

### Risk 4: WebSocket Not Working on Railway
**Likelihood**: Low
**Mitigation**: Railway supports WebSockets natively

---

## Success Criteria

✅ **Backend**:
- All 5 files imported and imports adapted
- Category model created
- Database migration successful
- WebSocket endpoint accessible

✅ **Frontend**:
- All 3 components imported and converted to TypeScript
- Wizard route added
- Dashboard button works
- Chat interface loads

✅ **Integration**:
- Can start wizard session
- WebSocket connection works
- Messages send/receive
- Progress tracker updates
- Category data saves to database

✅ **End-to-End**:
- User completes 8-category wizard
- Project created with structured knowledge
- Can continue to scene creation

---

## Next Steps (Session 5: Local AI)

**After Session 4 complete**:

1. **Verify Ollama Integration Works** (already imported!)
   - Test with Llama 3.3
   - Measure cost savings

2. **Add Model Selection UI**:
   - "Free (Llama 3.3 Local)"
   - "Premium (Claude Sonnet)"

3. **Document for Course**:
   - "How to Install Ollama"
   - "Using Free Local AI"
   - System requirements

---

## Documentation Strategy

### Keep Cloud Claude's ARCHITECTURE.md ✅
- Comprehensive system architecture
- Technology stack details
- Database schema
- API documentation
- Deployment architecture

### Keep Desktop Claude's UNIFIED_PLATFORM_INTEGRATION_PLAN.md ✅
- High-level integration strategy
- All 6 phases documented
- Budget and timeline
- Risk assessment

### Keep Desktop Claude's MASTER_ROADMAP.md ✅
- Timeline across all sessions
- Parallel vs sequential execution
- Resource allocation

### Add This Document ✅
- Combined approach for Session 4
- Practical implementation steps
- Comparison of both approaches

---

## Handoff Instructions

### For Human (User):
1. **Provide file paths** from factory-core on your system
2. **Approve combined approach** (copy vs rebuild)
3. **Choose next step**: Execute Session 4 or continue planning?

### For Next Claude Session:
1. **Read all docs**:
   - This document (COMBINED_SESSION_4_PLAN.md)
   - ARCHITECTURE.md (for system understanding)
   - SESSION_4_BRIEF.md (for file paths)

2. **Execute import strategy** (not rebuild strategy!)

3. **Focus on adaptation**, not creation:
   - Copy existing files
   - Fix imports
   - Convert JSX → TypeScript
   - Test integration

---

## Conclusion: Best of Both Worlds

**Cloud Claude's Contribution** ✅:
- Comprehensive architecture documentation
- System design and planning
- Understanding of requirements

**Desktop Claude's Contribution** ✅:
- Practical implementation strategy
- Knowledge of existing codebase
- Battle-tested code locations

**Combined Result** ⭐:
- **Copy** battle-tested code (Desktop approach)
- **Document** system architecture (Cloud approach)
- **Save** 2.5-4.5 hours of development time
- **Reduce** risk with proven components
- **Maintain** architectural clarity

---

## Decision Required

**User, please confirm:**

1. ✅ Approve combined approach (copy + adapt vs rebuild)?
2. 📂 Provide actual paths to factory-core files on your system?
3. 🚀 Execute Session 4 now, or continue planning?

---

*Created by: Cloud Claude*
*Based on: Desktop Claude's SESSION_4_BRIEF.md + Cloud Claude's ARCHITECTURE.md*
*Status: Ready for user approval and execution*
