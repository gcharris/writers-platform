# Writers Platform - Backend Deployment Guide

## Overview

This guide covers deploying the Writers Platform backend to Railway.

**Backend Stack:**
- FastAPI (Python web framework)
- PostgreSQL (database)
- SQLAlchemy (ORM)
- Factory Engine (AI analysis via tournament.py)

## Prerequisites

1. Railway account (https://railway.app)
2. GitHub repository with backend code
3. API keys for AI providers:
   - Anthropic (Claude)
   - OpenAI (GPT)
   - Google (Gemini)
   - xAI (Grok)

## Railway Deployment Steps

### Step 1: Create Railway Project

```bash
# Install Railway CLI (optional)
npm install -g @railway/cli

# Or use Railway web dashboard
# https://railway.app/new
```

### Step 2: Add PostgreSQL Database

1. Go to Railway dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Railway automatically creates DATABASE_URL environment variable

### Step 3: Configure Environment Variables

In Railway dashboard, add these environment variables:

```bash
# Database (auto-created by Railway)
DATABASE_URL=postgresql://...

# Security
SECRET_KEY=<generate-random-string>  # Use: openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# AI Provider API Keys
ANTHROPIC_API_KEY=<your-claude-key>
OPENAI_API_KEY=<your-gpt-key>
GOOGLE_API_KEY=<your-gemini-key>
XAI_API_KEY=<your-grok-key>

# Python environment
PYTHON_VERSION=3.11

# App config
PROJECT_NAME="Writers Platform API"
VERSION="1.0.0"
API_PREFIX="/api"
```

### Step 4: Deploy Backend

**Option A: Connect GitHub Repository**

1. In Railway, click "New" → "GitHub Repo"
2. Select `writers-platform` repository
3. Set root directory to `/backend`
4. Railway auto-detects Python and deploys

**Option B: Deploy via CLI**

```bash
cd backend
railway login
railway init
railway up
```

### Step 5: Run Database Migrations

Railway automatically runs SQLAlchemy migrations on startup via:
```python
Base.metadata.create_all(bind=engine)
```

If you need to run manual migrations:
```bash
railway run alembic upgrade head
```

### Step 6: Verify Deployment

1. Check deployment logs in Railway dashboard
2. Test endpoints:
   ```bash
   curl https://your-app.up.railway.app/health
   curl https://your-app.up.railway.app/api/docs
   ```

3. Verify database connection:
   ```bash
   railway run python -c "from app.core.database import engine; engine.connect(); print('✓ Database connected')"
   ```

## API Endpoints

### Health Check
```
GET /health
```

### OpenAPI Docs
```
GET /api/docs       # Swagger UI
GET /api/redoc      # ReDoc
```

### Authentication
```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

### Factory Projects
```
POST   /api/projects/              # Create project
POST   /api/projects/upload        # Upload file (DOCX/PDF/TXT)
GET    /api/projects/              # List user's projects
GET    /api/projects/{id}          # Get project details
PUT    /api/projects/{id}          # Update project
DELETE /api/projects/{id}          # Delete project
GET    /api/projects/{id}/scenes   # Get project scenes
POST   /api/projects/{id}/scenes   # Add scene
```

### AI Analysis
```
POST /api/analysis/run?project_id={id}  # Trigger analysis (returns job_id)
GET  /api/analysis/{job_id}/status      # Check status
GET  /api/analysis/{job_id}/results     # Get results
GET  /api/analysis/project/{id}/analyses # List all analyses
GET  /api/analysis/models               # List available AI models
```

### Community (existing)
```
POST /api/works/          # Publish to Community
GET  /api/works/          # Browse works
GET  /api/works/{id}      # Read work
... (see existing docs)
```

## Environment Setup

### Development (Local)

```bash
# Create .env file
cat > backend/.env << EOF
DATABASE_URL=postgresql://localhost/writers_platform
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=1440

ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key
GOOGLE_API_KEY=your-key
XAI_API_KEY=your-key
EOF

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start server
uvicorn app.main:app --reload --port 8000
```

### Production (Railway)

Railway automatically:
- Detects Python via `requirements.txt`
- Installs dependencies
- Runs database migrations
- Starts server with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## File Storage (Cloud)

**Current MVP:** Files uploaded via `/api/projects/upload` are parsed and stored in database (text content only).

**Production TODO:** Integrate cloud storage for original files:

```python
# Option 1: Railway Volumes
# Mount volume at /app/storage
# Set FILE_STORAGE_PATH=/app/storage

# Option 2: AWS S3 / Google Cloud Storage
# Add to requirements.txt: boto3 or google-cloud-storage
# Update file_parser.py to store files in cloud
```

## Background Jobs

**Current MVP:** Uses FastAPI BackgroundTasks for AI analysis jobs.

**Production TODO:** For better reliability, use Celery + Redis:

```bash
# Add to requirements.txt
celery[redis]>=5.3.0
redis>=4.5.0

# Add Redis to Railway
# Click "New" → "Database" → "Redis"

# Update orchestrator.py to use Celery
```

## Scaling

### Horizontal Scaling
Railway supports horizontal scaling:
1. Go to project settings
2. Enable "Horizontal Scaling"
3. Set min/max replicas

### Database Connection Pooling
For multiple workers, use connection pooling:
```python
# In database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

## Monitoring

### Logs
```bash
railway logs
```

### Metrics
Railway dashboard shows:
- CPU usage
- Memory usage
- Request count
- Error rate

### Cost Tracking
AI analysis costs are tracked in `analysis_results` table:
```sql
SELECT SUM(total_cost) FROM analysis_results WHERE status = 'completed';
```

## Troubleshooting

### Database connection errors
```bash
# Check DATABASE_URL
railway variables

# Test connection
railway run python -c "from app.core.database import engine; engine.connect()"
```

### Import errors
```bash
# Ensure all dependencies installed
railway run pip list

# Check Python path
railway run python -c "import sys; print('\n'.join(sys.path))"
```

### AI provider errors
```bash
# Check API keys
railway variables | grep API_KEY

# Test individual providers
railway run python -c "from backend.engine.agents import ClaudeAgent; print('Claude OK')"
```

## Next Steps (Session 2)

After backend is deployed and tested:

1. **Deploy Factory Frontend** (Vercel)
   - Connect to this backend API
   - Set `VITE_API_URL=https://your-backend.up.railway.app`

2. **Deploy Community Frontend** (Vercel)
   - Already deployed, just verify connection

3. **Custom Domains**
   - Backend: api.writersfactory.app (Railway)
   - Factory: writersfactory.app (Vercel)
   - Community: writerscommunity.app (Vercel)

## Support

- Railway docs: https://docs.railway.app
- FastAPI docs: https://fastapi.tiangolo.com
- Repository issues: https://github.com/gcharris/writers-platform/issues
