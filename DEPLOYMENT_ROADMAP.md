# Writers Platform - Complete Deployment Roadmap

**GitHub:** https://github.com/gcharris/writers-platform

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

Backend (Railway)                    Frontends (Vercel)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                     
┌─────────────────────┐              ┌──────────────────────┐
│   FastAPI Backend   │◄─────────────│  Factory Frontend    │
│                     │              │  writersfactory.app  │
│ PostgreSQL Database │              │                      │
│ Background Jobs     │              │ React + TypeScript   │
│ File Storage        │              │ Tailwind CSS         │
│                     │              │ Vite Build           │
│ writers-platform    │              └──────────────────────┘
│ -production         │              
│ .up.railway.app     │              ┌──────────────────────┐
│                     │◄─────────────│ Community Frontend   │
└─────────────────────┘              │ writerscommunity.app │
                                     │                      │
                                     │ React + TypeScript   │
                                     │ Tailwind CSS         │
                                     │ Vite Build           │
                                     └──────────────────────┘
```

---

## Three-Session Plan

### **Session 1: Backend (Railway)** - $400-500
**Status:** Ready to start
**Specification:** `CLAUDE_CLOUD_INSTRUCTIONS.md`

**What Gets Built:**
- ✅ Projects API (CRUD for Factory workspaces)
- ✅ Analysis API (AI tournament wrapper)
- ✅ Badge engine (AI detection, assignment)
- ✅ File parser (DOCX/PDF/TXT)
- ✅ Background job system
- ✅ Database models (projects, scenes, analysis_results, badges)
- ✅ Deployed to Railway with PostgreSQL

**Deliverable:** Working backend API at Railway URL

---

### **Session 2: Factory Frontend (Vercel)** - $300-400
**Status:** Pending Session 1 completion
**Specification:** `SESSION_2_FACTORY_FRONTEND.md`

**What Gets Built:**
- ✅ Factory homepage (two-column: upload vs. new)
- ✅ Projects dashboard
- ✅ Rich text editor
- ✅ File upload flow
- ✅ Analysis results dashboard
- ✅ Publish to Community flow
- ✅ Deployed to Vercel → writersfactory.app

**Deliverable:** Working Factory frontend connected to Railway backend

---

### **Session 3: Community Integration (Vercel)** - $200-300
**Status:** Pending Session 2 completion
**Specification:** `SESSION_3_INTEGRATION.md`

**What Gets Built:**
- ✅ Migrate Community to Vercel
- ✅ Badge display system
- ✅ Direct upload with auto-analysis
- ✅ Factory CTAs on work pages
- ✅ Filter by badge type
- ✅ Updated landing page
- ✅ Deployed to Vercel → writerscommunity.app

**Deliverable:** Fully integrated platform, both frontends live

---

## Total Budget

**Estimated:** $900-1,200  
**Time Saved by Cursor AI Migration:** ~$200-300  
**Net Investment:** ~$700-900 for complete platform

---

## Deployment Stack

| Component | Technology | Host | Domain |
|-----------|-----------|------|--------|
| Backend API | FastAPI + Python 3.11 | Railway | writers-platform-production.up.railway.app |
| Database | PostgreSQL 14+ | Railway | (internal) |
| File Storage | Railway Volumes or S3 | Railway/AWS | (internal) |
| Background Jobs | FastAPI BackgroundTasks or Celery | Railway | (internal) |
| Factory Frontend | React 19 + Vite + TypeScript | Vercel | writersfactory.app |
| Community Frontend | React 19 + Vite + TypeScript | Vercel | writerscommunity.app |

---

## Key Features Per Platform

### **Writers Factory (writersfactory.app)**
Private workspace for writing and AI analysis

**Features:**
- File upload (DOCX, PDF, TXT)
- Rich text editor
- Project management
- Multi-model AI analysis
- Voice consistency testing
- Scene scoring (7 dimensions)
- Publish to Community

**User Journey:**
1. Upload manuscript or start new
2. Edit content
3. Request AI analysis
4. View tournament results
5. Publish to Community when ready

---

### **Writers Community (writerscommunity.app)**
Public showcase for AI-validated fiction

**Features:**
- Browse published works
- Read-to-rate validation
- Comments and ratings
- Badge system (AI-Analyzed, Human-Authored, etc.)
- Direct upload with auto-analysis
- Filter by badge type
- Factory integration CTAs

**User Journey:**
1. Browse works by badge/genre
2. Read and rate
3. Upload own work (direct or via Factory)
4. Earn credibility through engagement
5. Get discovered by readers/agents

---

## Badge System

| Badge | How Earned | Visual |
|-------|-----------|--------|
| **AI-Analyzed** | Published from Factory after multi-model analysis | ✓ AI-Analyzed (Score: 87/100) |
| **Human-Authored (Verified)** | AI detection confirms no AI usage | 🖋️ Human-Authored (Verified 98%) |
| **Human-Authored (Self)** | Writer self-certifies, no verification | 🖋️ Human-Authored (Self-Certified) |
| **Community Upload** | Direct upload, no analysis | Community Upload |

---

## Environment Variables

### **Backend (Railway)**
```
DATABASE_URL=postgresql://...  (auto-set by Railway)
SECRET_KEY=<generate-random-key>
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
ALLOWED_ORIGINS=https://writersfactory.app,https://writerscommunity.app
```

### **Factory Frontend (Vercel)**
```
VITE_API_URL=https://writers-platform-production.up.railway.app/api
```

### **Community Frontend (Vercel)**
```
VITE_API_URL=https://writers-platform-production.up.railway.app/api
```

---

## Post-Deployment Checklist

After all 3 sessions complete:

### Backend
- [ ] /health endpoint responds
- [ ] /docs shows all API endpoints
- [ ] Database migrations applied
- [ ] CORS allows both Vercel domains
- [ ] Background jobs working
- [ ] File uploads working

### Factory Frontend
- [ ] Accessible at writersfactory.app
- [ ] Can create project
- [ ] Can upload file
- [ ] Can edit content
- [ ] Can trigger analysis
- [ ] Can view results
- [ ] Can publish to Community

### Community Frontend
- [ ] Accessible at writerscommunity.app
- [ ] Can browse works
- [ ] Badges display correctly
- [ ] Can read and rate
- [ ] Can upload directly
- [ ] Factory CTAs visible
- [ ] Filter by badge works

### Integration
- [ ] Factory publish creates work in Community
- [ ] Community shows Factory badges
- [ ] Direct upload auto-analyzes
- [ ] Cross-links work (Factory ↔ Community)

---

## Next Steps

1. **TODAY:** Give `START_HERE.md` to Claude Cloud Agent
2. **Session 1:** Wait for backend deployment (4-6 hours)
3. **Test backend:** Verify all endpoints work
4. **Session 2:** Give `SESSION_2_FACTORY_FRONTEND.md` to Claude Cloud
5. **Session 2:** Wait for Factory frontend (3-5 hours)
6. **Test Factory:** Full workflow (upload → analyze → publish)
7. **Session 3:** Give `SESSION_3_INTEGRATION.md` to Claude Cloud
8. **Session 3:** Wait for Community integration (2-4 hours)
9. **Final testing:** Both platforms fully integrated
10. **Launch! 🚀**

---

**Estimated Total Time:** 10-15 hours of Claude Cloud work across 3 sessions  
**Your Time:** Review each session's output, test, approve next session  
**Target Completion:** Within 48 hours if sessions run back-to-back

---

**STATUS: READY TO LAUNCH SESSION 1** ✅
