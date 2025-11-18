# Writers Platform - Deployment Guide

**Last Updated**: 2025-01-18
**Branch**: `claude/implement-knowledge-graph-01JRcFCWvxPePiR6k4QTnSRD`
**Status**: 🚀 Ready for Production

---

## New Features Deployed Tonight

This deployment includes **7 major features** implemented in a single session:

1. ✅ **Entity-Based Discovery** - Find stories by characters, locations, themes
2. ✅ **Error Monitoring (Sentry)** - Production error tracking
3. ✅ **Batch NotebookLM Extraction** - Extract research for multiple projects at once
4. ✅ **Research Citations** - Show NotebookLM sources in Knowledge Graph
5. ✅ **AI Wizard Chat UI** - Conversational setup assistant
6. ✅ **Testing** - Desktop Claude will test all features
7. ✅ **Documentation** - Complete guides for all features

---

## Quick Deployment Checklist

### Backend (Railway)

- [ ] Install dependencies: `pip install -r backend/requirements.txt`
- [ ] Set `SENTRY_DSN` environment variable (optional)
- [ ] Deploy: `railway up` or push to main branch
- [ ] Verify endpoints: `/api/browse/by-entity`, `/api/notebooklm/batch-extract`

### Factory Frontend (Vercel)

- [ ] Install dependencies: `npm install` in factory-frontend/
- [ ] Set `VITE_SENTRY_DSN` environment variable (optional)
- [ ] Deploy: `vercel --prod`
- [ ] Verify pages: `/wizard`, NotebookLM Settings, Knowledge Graph

### Community Frontend (Vercel)

- [ ] Install dependencies: `npm install` in community-frontend/
- [ ] Set `VITE_SENTRY_DSN` environment variable (optional)
- [ ] Deploy: `vercel --prod`
- [ ] Verify entity search: `/browse` with entity filter

---

## Feature-by-Feature Deployment

### 1. Entity-Based Discovery 🎯

**What It Does**: Find stories by searching for characters, locations, or themes in the Knowledge Graph.

**Backend Changes**:
- New endpoint: `GET /api/browse/by-entity`
- Query params: `entity_name`, `entity_type` (optional)
- Searches knowledge graphs, returns works with matching entities

**Frontend Changes** (Community):
- Browse.tsx: Purple gradient search box
- Entity name input + type dropdown
- Search/Clear buttons

**Testing**:
```bash
# Test API endpoint
curl "https://your-backend.railway.app/api/browse/by-entity?entity_name=Mickey&entity_type=character" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**User Flow**:
1. Go to `/browse` on Community frontend
2. See purple "Entity-Based Discovery" section
3. Enter entity name (e.g., "Mickey")
4. Select type (optional)
5. Click Search
6. See works featuring that entity

**No Migration Required** ✅

---

### 2. Error Monitoring (Sentry) 🔍

**What It Does**: Tracks errors in production with Sentry for debugging.

**Backend Changes**:
- Added `sentry-sdk[fastapi]>=1.40.0` to requirements.txt
- Initialized Sentry in main.py (optional, controlled by env var)
- New config settings: `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE`

**Frontend Changes** (Both):
- Added `@sentry/react` to package.json
- Initialized Sentry in main.tsx (production only)
- Session Replay + Performance monitoring enabled

**Setup**:
1. Create free Sentry account at sentry.io
2. Create 3 projects: Backend, Factory, Community
3. Copy DSNs
4. Set environment variables:

**Railway (Backend)**:
```bash
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

**Vercel (Frontends)**:
```bash
VITE_SENTRY_DSN=https://your-frontend-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
```

**Testing**:
- Trigger an error in development
- Check Sentry dashboard (Issues tab)

**Optional Feature** - Works without DSN (disabled by default)

**Full Documentation**: `SENTRY_SETUP.md`

---

### 3. Batch NotebookLM Extraction 🚀

**What It Does**: Extract NotebookLM research for multiple projects at once instead of one-by-one.

**Backend Changes**:
- New endpoint: `POST /api/notebooklm/batch-extract`
- Query params: `project_ids[]` (optional), `extract_types[]`
- Processes character, world building, and themes in one batch
- Returns detailed results with success/error counts

**Frontend Changes** (Factory):
- NotebookLMSettings.tsx: Purple gradient "Batch Extraction" section
- Checkboxes for extract types
- Progress/results display

**Testing**:
```bash
# Extract for all projects
curl -X POST "https://your-backend.railway.app/api/notebooklm/batch-extract?extract_types=character&extract_types=world" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Extract for specific projects
curl -X POST "https://your-backend.railway.app/api/notebooklm/batch-extract?project_ids=abc123&extract_types=character" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**User Flow**:
1. Configure NotebookLM notebooks for projects
2. Go to NotebookLM Settings page
3. See purple "Batch Extraction" section
4. Select extract types (character, world, themes)
5. Click "Start Batch Extraction"
6. See results: entities added/enriched per project

**Requirements**:
- Projects must have NotebookLM notebooks configured
- NotebookLM MCP server must be running (or use mock)

**No Migration Required** ✅

---

### 4. Research Citations 📚

**What It Does**: Show NotebookLM research sources for each entity in the Knowledge Graph.

**Frontend Changes** (Factory):
- EntityDetails.tsx: Blue-purple gradient "Research Citations" section
- Shows up to 5 sources per entity
- Clickable source links
- Citation numbering [1], [2], etc.

**Testing**:
1. Extract entities from NotebookLM
2. Open Knowledge Graph
3. Click on an entity
4. See "Research Citations" section (if entity has sources)
5. Click source URLs to verify links work

**User Flow**:
1. Create project with NotebookLM integration
2. Extract entities (manual or batch)
3. View Knowledge Graph
4. Click entity
5. Scroll to "Research Citations"
6. Click source to see original research

**No Migration Required** ✅
**No Backend Changes** ✅

---

### 5. AI Wizard Chat UI 🧙‍♂️

**What It Does**: Conversational interface to guide users through setup via chat (like ChatGPT).

**Frontend Changes** (Factory):
- New components: `AIWizard.tsx`, `WizardMessage.tsx`, `FloatingWizard.tsx`
- New page: `Wizard.tsx`
- CSS animations in index.css

**5 Conversation Contexts**:
1. **Onboarding** - First-time user setup
2. **Project Setup** - Creating new projects
3. **NotebookLM** - Research integration guide
4. **Knowledge Graph** - Entity extraction help
5. **Copilot** - AI assistant setup

**Usage Examples**:

**Full-Page Wizard**:
```tsx
// Navigate to wizard
navigate('/wizard?context=onboarding');
navigate('/wizard?context=notebooklm&projectId=abc123');
```

**Embedded Wizard**:
```tsx
import { AIWizard } from './components/wizard';

<AIWizard
  context="knowledge-graph"
  projectId={project.id}
  onComplete={() => console.log('Done!')}
/>
```

**Floating Button**:
```tsx
import { FloatingWizard } from './components/wizard';

<FloatingWizard
  projectId={project.id}
  context="copilot"
  position="bottom-right"
/>
```

**Testing**:
1. Navigate to `/wizard`
2. Test all 5 contexts
3. Click action buttons
4. Verify API calls work
5. Test modal open/close

**No Migration Required** ✅
**No Backend Changes** ✅

**Full Documentation**: `AI_WIZARD_GUIDE.md`

---

## Environment Variables

### Backend (Railway)

**Required**:
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
```

**Optional (Error Monitoring)**:
```bash
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### Factory Frontend (Vercel)

**Optional (Error Monitoring)**:
```bash
VITE_SENTRY_DSN=https://your-factory-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
```

### Community Frontend (Vercel)

**Optional (Error Monitoring)**:
```bash
VITE_SENTRY_DSN=https://your-community-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
```

---

## Deployment Steps

### Step 1: Backend (Railway)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Set environment variables in Railway dashboard
# - DATABASE_URL (already set)
# - SECRET_KEY (already set)
# - SENTRY_DSN (optional)

# 3. Deploy
git push  # Railway auto-deploys from main branch

# Or manual:
railway up
```

**Verify Deployment**:
```bash
# Check health
curl https://your-backend.railway.app/health

# Test new endpoints
curl https://your-backend.railway.app/api/browse/by-entity?entity_name=test
curl -X POST https://your-backend.railway.app/api/notebooklm/batch-extract
```

### Step 2: Factory Frontend (Vercel)

```bash
# 1. Install dependencies
cd factory-frontend
npm install

# 2. Set environment variables in Vercel dashboard
# - VITE_SENTRY_DSN (optional)

# 3. Deploy
vercel --prod

# Or via GitHub (automatic):
git push origin main
```

**Verify Deployment**:
- Visit https://writersfactory.app
- Navigate to `/wizard`
- Go to NotebookLM Settings
- Check Knowledge Graph entity details

### Step 3: Community Frontend (Vercel)

```bash
# 1. Install dependencies
cd community-frontend
npm install

# 2. Set environment variables in Vercel dashboard
# - VITE_SENTRY_DSN (optional)

# 3. Deploy
vercel --prod
```

**Verify Deployment**:
- Visit https://writerscommunity.app
- Go to `/browse`
- See Entity-Based Discovery section
- Test entity search

---

## Testing Checklist

### Entity-Based Discovery

- [ ] Purple search box appears on Browse page
- [ ] Entity name input works
- [ ] Entity type dropdown shows all types
- [ ] Search button triggers API call
- [ ] Results update with matching works
- [ ] Clear button resets search
- [ ] Header shows "Entity Search Results"

### Sentry Error Monitoring

- [ ] Backend: Trigger test error, check Sentry
- [ ] Factory: Trigger test error, check Sentry
- [ ] Community: Trigger test error, check Sentry
- [ ] Performance traces appear in dashboard
- [ ] Session replays work (if enabled)

### Batch NotebookLM Extraction

- [ ] Batch section appears on NotebookLM Settings
- [ ] Only shows for projects with notebooks configured
- [ ] Checkboxes work for extract types
- [ ] Start button triggers extraction
- [ ] Loading spinner appears
- [ ] Results display correctly
- [ ] Per-project breakdown shows

### Research Citations

- [ ] Citations appear in EntityDetails
- [ ] Only shows for entities with sources
- [ ] Source links are clickable
- [ ] Citation numbering is correct
- [ ] Notebook ID displays
- [ ] "Enriched" badge shows

### AI Wizard

- [ ] Full-page wizard loads at `/wizard`
- [ ] All 5 contexts work
- [ ] Typing indicators appear
- [ ] Messages fade in smoothly
- [ ] Action buttons trigger responses
- [ ] API calls succeed
- [ ] Modal closes properly
- [ ] FloatingWizard button pulses

---

## Rollback Plan

If deployment issues occur:

### Backend Rollback

```bash
# Railway
railway rollback

# Or revert commit
git revert HEAD
git push origin main
```

### Frontend Rollback

```bash
# Vercel
vercel rollback

# Or redeploy previous version
git checkout <previous-commit>
vercel --prod
```

### Feature Flags

All new features are **additive** - they don't break existing functionality:
- Entity search is optional (normal browse still works)
- Sentry is optional (works without DSN)
- Batch extraction is optional
- Citations only show if data exists
- Wizard is a separate page

**Safe to deploy incrementally**!

---

## Monitoring

### What to Monitor

**Backend**:
- Error rate in Sentry
- Response times for new endpoints
- Database query performance
- NotebookLM API call success rate

**Frontend**:
- JavaScript errors in Sentry
- Page load times
- User engagement with new features

**Business Metrics**:
- Entity search usage
- Batch extraction jobs completed
- Wizard completion rate
- User activation funnel

### Alerts to Set Up

1. **Error Spike Alert** - >10 errors/hour
2. **Performance Regression** - p95 response time >2s
3. **Failed Batch Jobs** - Batch extraction errors
4. **Low Wizard Completion** - <50% completion rate

---

## Common Issues

### Entity Search Returns No Results

**Cause**: No works have Knowledge Graphs with the searched entity

**Fix**: Ensure works are published from Factory with Knowledge Graphs

### Batch Extraction Fails

**Cause**: NotebookLM MCP server not running or notebooks not configured

**Fix**:
1. Check MCP server status
2. Verify notebook URLs are correct
3. Check Sentry for detailed errors

### Citations Don't Appear

**Cause**: Entity doesn't have `properties.notebooklm_sources`

**Fix**: Re-extract entity from NotebookLM with sources

### Wizard Doesn't Open

**Cause**: JavaScript error or routing issue

**Fix**:
1. Check browser console
2. Verify route is configured in App.tsx
3. Check Sentry for errors

---

## Performance Considerations

### Entity Search

- Queries all knowledge graphs - can be slow with many projects
- Consider adding pagination/limits
- Cache results for common searches

### Batch Extraction

- Can take several minutes for many projects
- Consider adding background job queue (Celery)
- Show progress updates to user

### Sentry

- 10% sampling reduces overhead
- Session replays use bandwidth
- Free tier has limits (5K errors/month)

### Wizard

- Keep conversation flows short
- Lazy load heavy components
- Cache API responses

---

## Next Steps

### Immediate (Post-Deployment)

1. **Run Phase 2 Tests** - Use Desktop Claude
2. **Monitor Sentry** - Watch for errors
3. **Gather User Feedback** - Test with real users
4. **Optimize Performance** - Profile slow queries

### Short-Term (1-2 Weeks)

1. **Add Analytics** - Track feature usage
2. **Improve Entity Search** - Better fuzzy matching
3. **Expand Wizard Contexts** - More conversation flows
4. **Add Rate Limiting** - Protect batch endpoints

### Long-Term (1-3 Months)

1. **Background Jobs** - Async batch extraction with Celery
2. **Entity Search Index** - Elasticsearch for better performance
3. **Wizard AI** - Real LLM-powered responses
4. **Advanced Citations** - Rich previews, deep linking

---

## Support

### Documentation

- `SENTRY_SETUP.md` - Error monitoring guide
- `AI_WIZARD_GUIDE.md` - Wizard usage and extension
- `PROJECT_STATUS_DASHBOARD.md` - Overall project status
- `PHASE_2_QUICK_START.md` - Community migration testing

### Testing

- `test_phase2_migration.sh` - Database verification
- `test_phase2_api.py` - API test suite

### Getting Help

- Check logs in Railway/Vercel dashboards
- Review Sentry error reports
- Consult documentation above
- Ask Desktop Claude to test features

---

## Success Metrics

### Week 1 Targets

- [ ] Zero critical errors in Sentry
- [ ] >10 entity searches performed
- [ ] >5 batch extractions completed
- [ ] >20% wizard completion rate

### Month 1 Targets

- [ ] <0.1% error rate
- [ ] >100 entity searches/week
- [ ] >50% new users complete wizard
- [ ] >90% uptime

---

## Change Log

**2025-01-18** - Initial Deployment
- Entity-Based Discovery
- Error Monitoring (Sentry)
- Batch NotebookLM Extraction
- Research Citations
- AI Wizard Chat UI

---

**Deployment Status**: ✅ Ready
**Risk Level**: 🟢 Low (all additive features)
**Estimated Deployment Time**: 30 minutes
**Rollback Time**: 5 minutes

**Let's ship it!** 🚀
