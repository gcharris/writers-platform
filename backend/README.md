# Writers Platform - Backend API

## Overview

Unified backend for Writers Community (social platform) and Writers Factory (AI writing workspace).

**Built with:**
- FastAPI (Python web framework)
- PostgreSQL + SQLAlchemy (database)
- JWT authentication
- Background job processing
- Factory Engine integration (AI tournament system)

## Architecture

```
writers-platform/backend/
├── app/
│   ├── core/           # Config, database, security
│   ├── models/         # SQLAlchemy models
│   │   ├── user.py, work.py, comment.py, ...  # Community models
│   │   ├── project.py  # Factory workspace projects
│   │   ├── scene.py    # Project scenes/chapters
│   │   ├── analysis_result.py  # AI analysis jobs
│   │   └── badge.py    # Authenticity badges
│   ├── routes/         # API endpoints
│   │   ├── auth.py, works.py, reading.py, ...  # Community routes
│   │   ├── projects.py  # Factory project CRUD + upload
│   │   └── analysis.py  # AI analysis jobs
│   ├── services/       # Business logic
│   │   ├── file_parser.py      # Parse DOCX/PDF/TXT
│   │   ├── badge_engine.py     # AI detection + badges
│   │   ├── orchestrator.py     # Wrap tournament.py for web
│   │   └── notifications.py    # Push notifications
│   └── main.py         # FastAPI app
├── engine/             # Factory AI analysis engine
│   ├── orchestration/
│   │   └── tournament.py  # Multi-agent scene tournament
│   ├── agents/         # AI agent implementations
│   │   ├── claude_agent.py
│   │   ├── gemini_agent.py
│   │   ├── chatgpt_agent.py
│   │   └── grok_agent.py
│   └── utils/          # Scoring, validation
└── requirements.txt    # Python dependencies
```

## Features

### Community Platform (Existing)
- User authentication (JWT)
- Work publishing & reading
- Comments, ratings, bookmarks
- Social features (follows, reading lists)
- Discovery & recommendations
- Professional pipeline (talent scouts, events)

### Factory Integration (New - Session 1)
- **Project Management**
  - Create projects from scratch or upload files
  - Support for DOCX, PDF, TXT formats
  - Automatic chapter/scene detection
  - Scene-level editing

- **AI Analysis**
  - Multi-agent tournament system (5 AI models)
  - Async job processing (returns immediately)
  - Score scenes across 7 criteria
  - Generate hybrid scenes from best elements
  - Full tournament results with costs

- **Badge System**
  - AI-Analyzed (Factory analysis completed)
  - Human-Verified (AI detection confirms human authorship)
  - Human-Self (user declaration)
  - Community-Upload (direct upload, no analysis)

## API Endpoints

### Authentication
```
POST /api/auth/register        # Create account
POST /api/auth/login           # Get JWT token
GET  /api/auth/me              # Get current user
```

### Factory Projects
```
POST   /api/projects/              # Create new project
POST   /api/projects/upload        # Upload file (DOCX/PDF/TXT)
GET    /api/projects/              # List user's projects
GET    /api/projects/{id}          # Get project details
PUT    /api/projects/{id}          # Update project
DELETE /api/projects/{id}          # Delete project
GET    /api/projects/{id}/scenes   # Get project scenes
POST   /api/projects/{id}/scenes   # Add scene to project
```

### AI Analysis
```
POST /api/analysis/run?project_id={id}
  Body: {
    "scene_outline": "Mickey confronts Vance",
    "chapter": "2.3.6",
    "context_requirements": ["Mickey Bardot", "bi-location"],
    "agents": ["claude-sonnet-4-5", "gpt-4o", "gemini-1-5-pro"],
    "synthesize": true
  }
  Returns: { "job_id": "...", "status": "pending" }

GET  /api/analysis/{job_id}/status     # Check progress
GET  /api/analysis/{job_id}/results    # Get full results
GET  /api/analysis/project/{id}/analyses  # List all analyses
GET  /api/analysis/models              # List available AI models
```

### Community Works
```
POST /api/works/          # Publish to Community
GET  /api/works/          # Browse works
GET  /api/works/{id}      # Read work
POST /api/works/{id}/comments  # Add comment
... (50+ Community endpoints)
```

## Database Models

### Factory Models (New)

**Project**
```python
id, user_id, title, description, genre, status,
word_count, scene_count, original_filename,
created_at, updated_at
```

**Scene**
```python
id, project_id, content, title, chapter_number,
scene_number, sequence, word_count, scene_type,
parent_scene_id
```

**AnalysisResult**
```python
id, project_id, scene_id, status, scene_outline,
results_json, best_agent, best_score, hybrid_score,
total_cost, total_tokens, error_message,
started_at, completed_at
```

**Badge**
```python
id, work_id, badge_type, verified, metadata_json,
created_at
```

### Community Models (Existing)
User, Work, Section, Comment, Rating, Bookmark, Follow, ReadingSession, ReadingHistory, ReadingList, Notification, ProfessionalProfile, TalentScout, TalentEvent, Report

## Development

### Local Setup

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://localhost/writers_platform
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Provider Keys
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key
GOOGLE_API_KEY=your-key
XAI_API_KEY=your-key
EOF

# Create database
createdb writers_platform

# Run migrations
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start server
uvicorn app.main:app --reload --port 8000

# View docs
open http://localhost:8000/api/docs
```

### Testing Workflow

1. **Register user**
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"test","email":"test@example.com","password":"test123"}'
   ```

2. **Login**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test123"}'
   # Returns: {"access_token": "..."}
   ```

3. **Create project**
   ```bash
   curl -X POST http://localhost:8000/api/projects/ \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"My Novel","genre":"sci-fi"}'
   ```

4. **Upload file**
   ```bash
   curl -X POST http://localhost:8000/api/projects/upload \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@manuscript.docx" \
     -F "title=My Novel" \
     -F "genre=sci-fi"
   ```

5. **Trigger analysis**
   ```bash
   curl -X POST "http://localhost:8000/api/analysis/run?project_id=PROJECT_ID" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "scene_outline": "Opening scene where protagonist discovers the truth",
       "chapter": "1.1",
       "agents": ["claude-sonnet-4-5", "gpt-4o"],
       "synthesize": true
     }'
   # Returns: {"job_id": "..."}
   ```

6. **Check status**
   ```bash
   curl http://localhost:8000/api/analysis/JOB_ID/status \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

7. **Get results**
   ```bash
   curl http://localhost:8000/api/analysis/JOB_ID/results \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## AI Analysis Flow

```
User uploads manuscript → File parsed into scenes → User triggers analysis

Analysis Job Created (status: pending)
↓
Background Task Started (status: running)
↓
TournamentOrchestrator.run_tournament()
  ├── Build context (characters, worldbuilding)
  ├── Generate 5 variations (parallel)
  │   ├── Claude Sonnet 4.5
  │   ├── Gemini 1.5 Pro
  │   ├── GPT-4o
  │   ├── Grok 2
  │   └── Claude Haiku
  ├── Score all variations (7 criteria)
  ├── Run cross-agent critique
  └── Synthesize hybrid scene
↓
Results Saved (status: completed)
  ├── All variations with scores
  ├── Critique analysis
  ├── Hybrid scene
  └── Cost + token usage
↓
User retrieves results via /api/analysis/{job_id}/results
```

## Deployment

See `../DEPLOYMENT.md` for full deployment guide.

**Quick Railway Deploy:**

1. Connect GitHub repo
2. Add PostgreSQL addon
3. Set environment variables (API keys)
4. Deploy from `/backend` directory
5. Railway auto-detects Python and runs

**Environment Variables:**
```
DATABASE_URL              # Auto-created by Railway
SECRET_KEY                # openssl rand -hex 32
ANTHROPIC_API_KEY         # Claude
OPENAI_API_KEY            # GPT
GOOGLE_API_KEY            # Gemini
XAI_API_KEY               # Grok
```

## Cost Management

AI analysis costs vary by model:
- Claude Sonnet 4.5: $0.003/1k tokens
- GPT-4o: $0.0025/1k tokens
- Gemini 1.5 Pro: $0.0025/1k tokens
- Grok 2: $0.002/1k tokens
- Claude Haiku: $0.0004/1k tokens

**Typical scene analysis (5 agents + synthesis):**
- Input: ~2000 tokens (context)
- Output: ~3000 tokens per agent (15k total)
- Cost: ~$0.05 - $0.10 per scene

Costs tracked in `analysis_results.total_cost` field.

## Future Enhancements (Post-MVP)

### Production Job Queue
Replace FastAPI BackgroundTasks with Celery + Redis for:
- Job persistence
- Retry logic
- Distributed workers
- Better monitoring

### File Storage
Add cloud storage for original files:
- Railway volumes (simple)
- AWS S3 / Google Cloud Storage (scalable)
- Preserve original formatting

### Advanced AI Features
- Custom agent prompts
- Fine-tuned models
- Context caching
- Batch processing

### Analytics
- User analysis history
- Cost dashboards
- Quality metrics over time

## License

Copyright (c) 2025 Writers Platform
All rights reserved.
