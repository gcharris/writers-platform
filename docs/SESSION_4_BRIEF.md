# Session 4: Import AI Setup Wizard
## Claude Cloud Task Brief

**Objective**: Import and integrate the AI Setup Wizard from writers-factory-core into writers-platform

**Time**: 6-8 hours
**Budget**: ~$250
**Priority**: HIGH (critical for January course)

---

## What to Import

### Source Location
```
/Users/gch2024/Documents/Documents - Mac Mini/Explant drafts current/factory/
```

### Files to Copy

**Backend** (5 files):
1. `factory/ai/setup_wizard_agent.py` → `backend/app/services/setup_wizard_agent.py`
2. `factory/templates/category_templates.py` → `backend/app/services/category_templates.py`
3. `factory/ai/model_router.py` → `backend/app/services/model_router.py`
4. `webapp/backend/routes/wizard.py` → `backend/app/routes/wizard.py`
5. Create `backend/app/models/category.py` (new model for category storage)

**Frontend** (4 files):
1. `webapp/frontend-v2/src/pages/AIWizard.jsx` → `factory-frontend/src/pages/AIWizard.jsx`
2. `webapp/frontend-v2/src/features/wizard/ChatMessage.jsx` → `factory-frontend/src/features/wizard/ChatMessage.jsx`
3. `webapp/frontend-v2/src/features/wizard/ProgressSteps.jsx` → `factory-frontend/src/features/wizard/ProgressSteps.jsx`
4. Update `factory-frontend/src/App.jsx` to add wizard route

---

## Integration Steps

### Step 1: Backend Setup (2 hours)

1. **Copy files** from factory-core to writers-platform:
```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-platform"

# Copy backend files
mkdir -p backend/app/services
cp "../Explant drafts current/factory/ai/setup_wizard_agent.py" backend/app/services/
cp "../Explant drafts current/factory/templates/category_templates.py" backend/app/services/
cp "../Explant drafts current/factory/ai/model_router.py" backend/app/services/
cp "../Explant drafts current/webapp/backend/routes/wizard.py" backend/app/routes/
```

2. **Add WebSocket dependency** to `requirements.txt`:
```
websockets>=12.0
```

3. **Create Category model** in `backend/app/models/category.py`:
```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    category_type = Column(String(50), nullable=False)  # Characters, Story_Structure, etc.
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

4. **Register wizard route** in `backend/app/main.py`:
```python
from app.routes import wizard  # Add to imports

app.include_router(wizard.router, prefix=settings.API_PREFIX)  # Add after other routers
```

5. **Run database migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add categories table for wizard"
alembic upgrade head
```

### Step 2: Frontend Setup (2 hours)

1. **Copy frontend files**:
```bash
cd "/Users/gch2024/Documents/Documents - Mac Mini/writers-platform"

# Copy wizard components
mkdir -p factory-frontend/src/pages
mkdir -p factory-frontend/src/features/wizard

cp "../Explant drafts current/webapp/frontend-v2/src/pages/AIWizard.jsx" \
   factory-frontend/src/pages/

cp "../Explant drafts current/webapp/frontend-v2/src/features/wizard/ChatMessage.jsx" \
   factory-frontend/src/features/wizard/

cp "../Explant drafts current/webapp/frontend-v2/src/features/wizard/ProgressSteps.jsx" \
   factory-frontend/src/features/wizard/
```

2. **Add wizard route** to `factory-frontend/src/App.jsx`:
```jsx
import AIWizard from './pages/AIWizard';

// Add to routes:
<Route path="/wizard" element={<AIWizard />} />
```

3. **Update Dashboard** to link to wizard (`factory-frontend/src/pages/Dashboard.tsx`):
```jsx
// Add button in dashboard header:
<button
  onClick={() => navigate('/wizard')}
  className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
>
  <SparklesIcon className="h-5 w-5 mr-2" />
  AI Setup Wizard
</button>
```

4. **Add WebSocket API** to `factory-frontend/src/api/factory.ts`:
```typescript
// Wizard API
export const wizardApi = {
  startSession: async (projectId: string) => {
    const response = await apiClient.post('/wizard/start', { project_id: projectId });
    return response.data;
  },

  connectWebSocket: (sessionId: string) => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    return new WebSocket(`${wsUrl}/wizard/chat/${sessionId}`);
  },

  getProgress: async (sessionId: string) => {
    const response = await apiClient.get(`/wizard/progress/${sessionId}`);
    return response.data;
  },
};
```

### Step 3: Integration Testing (2 hours)

1. **Test backend WebSocket**:
```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# In another terminal, test WebSocket:
wscat -c ws://localhost:8000/api/wizard/chat/test-session-id
```

2. **Test frontend wizard**:
```bash
# Start frontend
cd factory-frontend
npm run dev

# Open browser to http://localhost:5173
# Navigate to /wizard
# Verify:
# - Chat interface loads
# - Can send messages
# - Progress steps show 8 categories
# - WebSocket connection works
```

3. **Test end-to-end flow**:
   - Click "AI Setup Wizard" from dashboard
   - Answer questions about project
   - Verify category files are created
   - Check that project is saved with categories
   - Confirm user can continue to dashboard

### Step 4: Deploy (2 hours)

1. **Commit changes**:
```bash
git add .
git commit -m "Add AI Setup Wizard

- Import wizard backend (WebSocket, agent, templates)
- Import wizard frontend (chat UI, progress tracker)
- Add Category model for knowledge storage
- Add wizard route and API endpoints
- Integrate with project creation flow

Session 4 complete - AI wizard now available"
git push origin main
```

2. **Wait for Railway deployment** (~3 minutes)
   - Verify WebSocket endpoint works: `wss://writers-platform-production.up.railway.app/api/wizard/chat/{session_id}`

3. **Wait for Vercel deployment** (~2 minutes)
   - Verify wizard accessible: `https://writers-platform.vercel.app/wizard`

4. **Test production**:
   - Visit https://writers-platform.vercel.app
   - Login
   - Click "AI Setup Wizard"
   - Complete one category
   - Verify data saved

---

## Expected Outcomes

After Session 4 completion:

✅ AI Setup Wizard accessible from dashboard
✅ Chat interface works with WebSocket connection
✅ 8 category progress tracker visible
✅ System can query NotebookLM (placeholder queries for now - Session 5 will connect real API)
✅ Category files saved to database
✅ Project created with structured knowledge

---

## Important Notes

1. **NotebookLM Placeholder**: For Session 4, wizard will use placeholder NotebookLM queries. Session 5 will connect the real NotebookLM client.

2. **Model Selection**: For now, wizard uses Claude Sonnet 4.5 by default. Session 5 will add Ollama/Llama 3.3 for free option.

3. **Error Handling**: Add try-catch around WebSocket operations and show user-friendly errors.

4. **Environment Variables**: Make sure Railway has these set:
   - `ANTHROPIC_API_KEY` (for wizard)
   - Frontend needs `VITE_WS_URL=wss://writers-platform-production.up.railway.app`

5. **Database**: Railway PostgreSQL must have the new `categories` table after migration.

---

## Testing Checklist

After implementation, verify:

- [ ] Backend starts without errors
- [ ] WebSocket endpoint accessible
- [ ] Frontend wizard page loads
- [ ] Can start new wizard session
- [ ] Chat messages send and receive
- [ ] Progress tracker updates
- [ ] Category data saves to database
- [ ] Can complete wizard and return to dashboard
- [ ] Production deployment works
- [ ] No console errors

---

## Success Criteria

**Session 4 is complete when**:
1. User can access wizard from dashboard
2. Chat interface is functional and responsive
3. Wizard processes all 8 categories
4. Data is saved to database
5. Deployed to production (Railway + Vercel)

---

## Troubleshooting

**If WebSocket fails**:
- Check Railway WebSocket support enabled
- Verify `websockets` package installed
- Test with `wscat` or Postman

**If chat doesn't respond**:
- Check Claude API key set
- Verify `setup_wizard_agent.py` imported correctly
- Check backend logs for errors

**If categories don't save**:
- Verify Category model migrated
- Check database connection
- Look for errors in `/wizard/start` endpoint

**If frontend won't build**:
- Check all imports correct
- Verify wizard components copied
- Run `npm install` to ensure dependencies

---

## After Session 4

**Next steps** (Session 5):
1. Import NotebookLM client (replace placeholders)
2. Add Ollama/Llama 3.3 integration (free AI)
3. Add model selection in wizard
4. Test cost savings with local AI

See `SESSION_5_BRIEF.md` for details.

---

*Created: 2025-01-17*
*For: Claude Cloud Session 4*
*Status: Ready to execute*
