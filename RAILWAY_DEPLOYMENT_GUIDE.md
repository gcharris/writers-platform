# Railway Deployment Guide - Writers Platform Backend

## Quick Start (5 minutes)

### Step 1: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `gcharris/writers-platform`
4. Railway will detect the backend automatically

### Step 2: Configure Root Directory

Railway needs to know the backend is in a subdirectory:

1. In Railway dashboard, go to Settings
2. Under "Build & Deploy", set:
   - **Root Directory**: `backend`
   - **Start Command**: (leave empty - uses railway.json)

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway automatically creates `DATABASE_URL` variable

### Step 4: Set Environment Variables

Click "Variables" tab and add these:

```bash
# Security (REQUIRED)
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Provider Keys (REQUIRED for analysis)
ANTHROPIC_API_KEY=<your-claude-api-key>
OPENAI_API_KEY=<your-openai-api-key>
GOOGLE_API_KEY=<your-google-gemini-api-key>
XAI_API_KEY=<your-xai-grok-api-key>

# Optional - Railway auto-detects these
PROJECT_NAME=Writers Platform API
VERSION=1.0.0
API_PREFIX=/api
```

**To generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

### Step 5: Deploy

1. Click "Deploy" (Railway auto-deploys on git push)
2. Wait for deployment (usually 2-3 minutes)
3. Check logs for errors

### Step 6: Verify Deployment

Once deployed, Railway gives you a URL like: `https://writers-platform-production.up.railway.app`

Test these endpoints:

```bash
# Health check
curl https://your-app.up.railway.app/health

# API docs (Swagger UI)
open https://your-app.up.railway.app/api/docs

# Test registration
curl -X POST https://your-app.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

## Critical Environment Variables

### Required for Basic Operation

- `DATABASE_URL` - Auto-created by Railway PostgreSQL addon
- `SECRET_KEY` - Generate with `openssl rand -hex 32`

### Required for AI Analysis (Factory Features)

Without these, the Factory analysis features won't work:

- `ANTHROPIC_API_KEY` - For Claude Sonnet 4.5 agent
- `OPENAI_API_KEY` - For GPT-4o agent
- `GOOGLE_API_KEY` - For Gemini 1.5 Pro agent
- `XAI_API_KEY` - For Grok 2 agent

**Where to get API keys:**
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys
- Google: https://makersuite.google.com/app/apikey
- xAI: https://console.x.ai/

## Troubleshooting

### "Application failed to respond" error

Check Railway logs:
1. Go to Railway dashboard
2. Click "Deployments" tab
3. Look for error messages

Common issues:
- Missing `DATABASE_URL` → Add PostgreSQL addon
- Missing `SECRET_KEY` → Add to variables
- Port binding issue → Railway.json sets this automatically

### Database connection errors

```bash
# In Railway console, test database
python -c "from app.core.database import engine; engine.connect(); print('✓ Connected')"
```

### Import errors

The backend imports the Factory engine from `backend/engine/`. If you see import errors:

1. Check that `backend/engine/` directory exists in repo
2. Verify `sys.path.insert()` in `orchestrator.py:18`
3. Check Railway logs for Python path issues

### AI Analysis failing

If analysis jobs fail:

1. Verify all 4 API keys are set
2. Check API key validity:
   ```bash
   # Test Claude
   curl https://api.anthropic.com/v1/messages \
     -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01"
   ```
3. Check cost limits on AI provider accounts

## Next Steps

After backend is deployed and tested:

### 1. Get Backend URL
Copy your Railway backend URL (e.g., `https://writers-platform-production.up.railway.app`)

### 2. Deploy Factory Frontend (Session 2)
- Create React app for Writers Factory
- Set `VITE_API_URL` to your Railway backend URL
- Deploy to Vercel

### 3. Update Community Frontend (Session 3)
- Add badge system integration
- Update API URL if needed
- Redeploy to Vercel

### 4. Custom Domains (Optional)
Set up custom domains:
- Backend: `api.writersfactory.app` (Railway)
- Factory: `writersfactory.app` (Vercel)
- Community: `writerscommunity.app` (Vercel)

## Cost Monitoring

### Railway Costs
- Starter plan: $5/month
- Database: Included in Starter
- Bandwidth: $0.10/GB after 100GB

### AI Provider Costs
The backend tracks AI costs in the database:

```sql
-- Total AI spending
SELECT SUM(total_cost) FROM analysis_results WHERE status = 'completed';

-- Cost by model
SELECT best_agent, SUM(total_cost), COUNT(*)
FROM analysis_results
WHERE status = 'completed'
GROUP BY best_agent;
```

**Estimated costs per analysis:**
- Full tournament (5 agents): $0.50 - $2.00
- Single agent: $0.10 - $0.40
- Depends on scene length and max_tokens

## Production Recommendations

For production deployment, consider:

1. **Background Jobs**: Replace FastAPI BackgroundTasks with Celery + Redis
2. **File Storage**: Use AWS S3 or Google Cloud Storage instead of database
3. **Monitoring**: Set up Sentry for error tracking
4. **Rate Limiting**: Add rate limiting to API endpoints
5. **Caching**: Add Redis for caching AI results
6. **Scaling**: Enable Railway horizontal scaling

## Support

- Railway docs: https://docs.railway.app
- Repository: https://github.com/gcharris/writers-platform
- Issues: https://github.com/gcharris/writers-platform/issues
