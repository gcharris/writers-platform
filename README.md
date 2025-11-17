# Writers Platform

**Unified backend for Writers Factory + Writers Community**

## Overview

This repository contains the backend API that powers both:
- **Writers Factory** (writersfactory.app) - AI writing coach workspace
- **Writers Community** (writerscommunity.app) - Public showcase platform

## Architecture

```
writers-platform/
├── backend/
│   ├── app/                  # FastAPI application
│   │   ├── routes/
│   │   │   ├── auth.py       # Authentication (shared)
│   │   │   ├── projects.py   # Factory workspace (TODO)
│   │   │   ├── analysis.py   # AI analysis (TODO)
│   │   │   ├── works.py      # Community works
│   │   │   └── ...           # Other Community routes
│   │   ├── services/
│   │   │   ├── orchestrator.py   # Wraps engine/ (TODO)
│   │   │   ├── badge_engine.py   # Badge assignment (TODO)
│   │   │   └── file_parser.py    # File upload (TODO)
│   │   └── models/           # Database models
│   └── engine/               # Factory AI analysis engine
│       └── (70k+ lines from factory/core/)
├── factory-frontend/         # TODO: React app for Factory
└── community-frontend/       # TODO: Copy from writers-community
```

## What's Copied (Ready to Use)

✅ **Community Backend** - Complete FastAPI app with auth, works, comments, ratings
✅ **Factory Engine** - All AI analysis code from factory/core/
✅ **Merged Dependencies** - requirements.txt combines both

## What Needs Building (For Claude Cloud Agent)

### Backend:
- [ ] `routes/projects.py` - CRUD for Factory projects
- [ ] `routes/analysis.py` - Trigger AI analysis, get results
- [ ] `services/orchestrator.py` - Wrap engine/orchestration/tournament.py
- [ ] `services/badge_engine.py` - AI detection, badge assignment
- [ ] `services/file_parser.py` - Parse DOCX/PDF/TXT uploads
- [ ] Database models - projects, scenes, analysis_results, badges
- [ ] Update `works.py` - Add badge support, direct upload with analysis

### Frontend:
- [ ] Create `factory-frontend/` - writersfactory.app UI
- [ ] Copy `community-frontend/` - Update with badge display
- [ ] Deploy both frontends to Railway

## Database Schema Extensions Needed

```sql
-- New tables for Factory
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(500),
    status VARCHAR(50),  -- draft, analyzing, analyzed, published
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE scenes (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    content TEXT,
    chapter_num INTEGER,
    scene_num INTEGER,
    sequence INTEGER
);

CREATE TABLE analysis_results (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    model VARCHAR(100),  -- claude, gpt4, gemini, etc.
    scores_json JSONB,   -- {voice: 85, pacing: 90, ...}
    feedback TEXT,
    timestamp TIMESTAMP
);

CREATE TABLE badges (
    id UUID PRIMARY KEY,
    work_id UUID REFERENCES works(id),
    badge_type VARCHAR(50),  -- ai_analyzed, human_verified, human_self, community
    verified BOOLEAN,
    metadata_json JSONB,
    created_at TIMESTAMP
);
```

## API Endpoints

### Existing (Community)
- POST /api/auth/register
- POST /api/auth/login
- GET /api/works/
- POST /api/works/
- GET /api/works/{id}
- ... (see backend/app/routes/)

### To Build (Factory)
- POST /api/projects/ - Create project
- GET /api/projects/ - List user's projects
- GET /api/projects/{id} - Get project
- PUT /api/projects/{id} - Update project
- DELETE /api/projects/{id} - Delete project
- POST /api/analysis/run - Trigger AI analysis
- GET /api/analysis/{id}/status - Check status
- GET /api/analysis/{id}/results - Get results
- POST /api/projects/{id}/publish - Publish to Community

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI API Keys (from Factory)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Google Cloud (for Factory engine)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# CORS
FACTORY_FRONTEND_URL=https://writersfactory.app
COMMUNITY_FRONTEND_URL=https://writerscommunity.app
```

## Deployment

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Railway Deployment:**
- Backend: writers-platform-api.railway.app
- Factory Frontend: writersfactory.app
- Community Frontend: writerscommunity.app

## Development Roadmap

### Session 1: Backend Core (Claude Cloud Agent)
- Implement projects routes
- Implement analysis routes
- Create orchestrator service
- Create badge engine service  
- Create file parser service
- Extend database schema
- Deploy to Railway

### Session 2: Factory Frontend (Claude Cloud Agent)
- Build React app for Factory
- Upload interface
- Analysis dashboard
- Publish to Community flow
- Deploy to Railway

### Session 3: Integration & Polish (Claude Cloud Agent)
- Update Community frontend with badges
- Add direct upload with auto-analysis
- Landing pages for both domains
- Testing & bug fixes
- Final deployment

## Original Repositories

This platform merges code from:
- `writers-community/` - Social platform (7k lines)
- `factory/core/` - AI analysis engine (70k lines)

Both original repos remain unchanged for reference.

## License

Private - Writers Platform Product
