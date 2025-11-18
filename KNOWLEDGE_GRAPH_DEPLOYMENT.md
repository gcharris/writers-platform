# Knowledge Graph Deployment Guide

Complete deployment guide for the Writers Platform Knowledge Graph system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Post-Deployment Verification](#post-deployment-verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services
- **PostgreSQL database** (Railway, Supabase, or local)
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Railway CLI** (optional, for Railway deployment)
- **Vercel CLI** (optional, for Vercel deployment)

### API Keys Required
- `ANTHROPIC_API_KEY` - For Claude-based LLM extraction
- `OPENAI_API_KEY` - For GPT-based LLM extraction (optional)
- `GOOGLE_API_KEY` - For Gemini-based extraction (optional)

---

## Backend Deployment

### Step 1: Install Python Dependencies

```bash
cd backend

# Install base dependencies
pip install -r requirements.txt

# Install knowledge graph dependencies
pip install networkx==3.2.1 spacy==3.7.2

# Download spaCy language model for NER extraction
python -m spacy download en_core_web_sm

# Optional: Download larger model for better accuracy
# python -m spacy download en_core_web_lg
```

### Step 2: Run Database Migrations

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run knowledge graph migration
python migrate.py \
  --migration-file migrations/add_knowledge_graph_tables.sql \
  --verify-tables project_graphs extraction_jobs
```

Expected output:
```
✓ Migration completed successfully
✓ Verified tables: project_graphs, extraction_jobs
```

### Step 3: Set Environment Variables

Add these to your Railway environment or `.env` file:

```bash
# Database
DATABASE_URL=postgresql://...

# API Keys (at least one required for LLM extraction)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Optional: Configure extraction defaults
DEFAULT_EXTRACTOR=ner  # or "llm"
DEFAULT_LLM_MODEL=claude-sonnet-4.5
```

### Step 4: Deploy to Railway

#### Option A: Using Railway CLI

```bash
# From backend directory
railway login
railway link
railway up

# Or deploy specific service
railway deploy
```

#### Option B: Using Git Push

```bash
# Link your git repository in Railway dashboard
git push railway main
```

#### Option C: Using Railway UI

1. Go to Railway dashboard
2. Create new project from GitHub repo
3. Select backend directory as root
4. Add environment variables
5. Deploy

### Step 5: Verify Backend Deployment

```bash
# Test health endpoint
curl https://your-backend.up.railway.app/health

# Test knowledge graph endpoint
curl https://your-backend.up.railway.app/api/knowledge-graph/health \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Frontend Deployment

### Step 1: Install Dependencies

```bash
cd factory-frontend
npm install
```

### Step 2: Configure Environment

Create `.env.production`:

```env
VITE_API_URL=https://your-backend.up.railway.app
VITE_WS_URL=wss://your-backend.up.railway.app
```

### Step 3: Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Step 4: Deploy to Vercel

#### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

#### Option B: Using Git Integration

1. Go to Vercel dashboard
2. Import your GitHub repository
3. Select `factory-frontend` as root directory
4. Configure environment variables
5. Deploy

#### Option C: Manual Upload

```bash
# Build first
npm run build

# Deploy dist folder
vercel --prod ./dist
```

### Step 5: Configure Vercel Settings

In Vercel dashboard, set:

**Framework Preset**: Vite
**Build Command**: `npm run build`
**Output Directory**: `dist`
**Install Command**: `npm install`

**Environment Variables**:
- `VITE_API_URL`: Your backend URL
- `VITE_WS_URL`: Your WebSocket URL

---

## Post-Deployment Verification

### 1. Test Knowledge Graph API

```bash
# Get project graph
curl https://your-backend.up.railway.app/api/knowledge-graph/projects/{project_id}/graph \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected response:**
```json
{
  "nodes": [],
  "links": [],
  "metadata": {
    "project_id": "...",
    "entity_count": 0,
    "relationship_count": 0
  }
}
```

### 2. Test Entity Extraction

```bash
# Trigger extraction (NER - Free)
curl -X POST https://your-backend.up.railway.app/api/knowledge-graph/projects/{project_id}/extract \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scene_id": "test-scene",
    "scene_content": "Mickey walked on Mars with Sarah.",
    "extractor_type": "ner"
  }'
```

**Expected response:**
```json
{
  "job_id": "...",
  "status": "pending",
  "extractor_type": "ner"
}
```

### 3. Test LLM Extraction

```bash
# Trigger extraction (LLM - Paid)
curl -X POST https://your-backend.up.railway.app/api/knowledge-graph/projects/{project_id}/extract \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scene_id": "test-scene-2",
    "scene_content": "Captain Elena Rodriguez commanded the starship Discovery. She had a complex relationship with Dr. Marcus Chen, the ship'\''s chief scientist.",
    "extractor_type": "llm",
    "model_name": "claude-sonnet-4.5"
  }'
```

### 4. Test WebSocket Connection

Open browser console on your frontend and run:

```javascript
const token = localStorage.getItem('auth_token');
const ws = new WebSocket(`wss://your-backend.up.railway.app/api/knowledge-graph/projects/test-project/stream?token=${token}`);

ws.onopen = () => console.log('✓ WebSocket connected');
ws.onmessage = (event) => console.log('Update:', JSON.parse(event.data));
ws.onerror = (error) => console.error('✗ WebSocket error:', error);
```

### 5. Test Graph Export

```bash
# Export to GraphML
curl https://your-backend.up.railway.app/api/knowledge-graph/projects/{project_id}/export/graphml \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output knowledge-graph.graphml

# Export to NotebookLM
curl https://your-backend.up.railway.app/api/knowledge-graph/projects/{project_id}/export/notebooklm \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output knowledge-graph-notebooklm.md
```

### 6. Frontend Verification

Visit your deployed frontend and verify:

- [ ] Knowledge Graph page loads without errors
- [ ] 3D graph visualization renders
- [ ] Entity browser shows entities
- [ ] Search functionality works
- [ ] Export buttons trigger downloads
- [ ] Scene editor with KG sidebar works
- [ ] Auto-extraction can be toggled
- [ ] WebSocket connection status shows "connected"

---

## Running Tests

### Frontend Unit Tests

```bash
cd factory-frontend
npm test
```

### Integration Tests

```bash
npm run test:integration
```

### E2E Tests

```bash
# Install Playwright
npx playwright install

# Run E2E tests
npm run test:e2e
```

### Performance Benchmarks

```bash
npm run test:performance
```

---

## Troubleshooting

### Backend Issues

**Migration fails:**
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# Verify migrations directory
ls backend/migrations/

# Run migration with verbose output
python migrate.py --migration-file migrations/add_knowledge_graph_tables.sql --verbose
```

**spaCy model not found:**
```bash
# Reinstall language model
python -m spacy download en_core_web_sm --force
```

**NetworkX import error:**
```bash
# Reinstall networkx
pip uninstall networkx
pip install networkx==3.2.1
```

### Frontend Issues

**Build fails:**
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

**WebSocket connection fails:**
- Verify `VITE_WS_URL` environment variable
- Check CORS settings in backend
- Ensure WebSocket route is registered

**Graph visualization doesn't render:**
- Check browser console for THREE.js errors
- Verify `react-force-graph-3d` is installed
- Ensure graph data format is correct

### Performance Issues

**Slow extraction:**
- Use NER extractor for large batches
- Switch to LLM only for important scenes
- Consider increasing timeout values

**Large graph slow to render:**
- Enable graph filtering by entity type
- Implement pagination for entity browser
- Use graph clustering for visualization

**High memory usage:**
- Limit graph size in visualization (max 500 nodes recommended)
- Implement lazy loading for entity lists
- Clear graph cache periodically

---

## Monitoring & Maintenance

### Monitor Extraction Jobs

```bash
# Check job status
curl https://your-backend.up.railway.app/api/knowledge-graph/projects/{project_id}/extract/jobs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Monitor Graph Size

```bash
# Get graph statistics
curl https://your-backend.up.railway.app/api/knowledge-graph/projects/{project_id}/graph/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Database Backup

```bash
# Backup project graphs
pg_dump $DATABASE_URL --table=project_graphs --table=extraction_jobs > knowledge-graph-backup.sql
```

### Cost Monitoring

Monitor LLM extraction costs:
- Track `cost` field in `extraction_jobs` table
- Set up alerts for high usage
- Consider implementing usage quotas

---

## Security Checklist

- [ ] Environment variables are not committed to git
- [ ] API keys are rotated regularly
- [ ] Database credentials are secure
- [ ] WebSocket connections use authentication
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] Input validation is in place
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (React auto-escaping)

---

## Production Optimization

### Backend Optimizations

1. **Enable caching**: Cache graph serialization results
2. **Connection pooling**: Configure PostgreSQL connection pool
3. **Background job processing**: Use Celery or similar for async extraction
4. **Load balancing**: Deploy multiple backend instances

### Frontend Optimizations

1. **Code splitting**: Lazy load graph components
2. **CDN**: Serve static assets via CDN
3. **Image optimization**: Optimize entity type icons
4. **Bundle analysis**: Monitor and reduce bundle size

```bash
# Analyze bundle
npm run build -- --analyze
```

---

## Support & Documentation

- **Main Documentation**: `KNOWLEDGE_GRAPH_IMPLEMENTATION.md`
- **API Documentation**: `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART2.md`
- **Frontend Documentation**: `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md`
- **GitHub Issues**: Report bugs and request features

---

**Last Updated**: November 2024
**Version**: 1.0.0
