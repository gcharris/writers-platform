# Desktop Claude: Parallel Bug-Squashing & Support Plan

**Date**: 2025-01-18
**Role**: Support agent running in parallel while Cloud Claude implements KG system
**Mission**: Monitor Cloud Claude's progress, fix bugs, answer questions, review code

---

## 🎯 Primary Responsibilities

While Cloud Claude implements the Knowledge Graph system, Desktop Claude will:

1. **Monitor for questions** from Cloud Claude in shared docs/commits
2. **Review pull requests** and provide feedback
3. **Fix bugs** that Cloud Claude encounters
4. **Test deployed code** and report issues
5. **Document solutions** to common problems
6. **Optimize performance** bottlenecks

---

## 📋 Bug-Squashing Workflow

### Step 1: Monitor Cloud Claude's Progress

**Check every 2-3 hours**:
- GitHub commits on `main` or feature branches
- Railway deployment logs
- Error messages in commit messages
- Questions in code comments

**Communication channels**:
- GitHub commit messages
- Code comments with `TODO: Desktop Claude - help with X`
- Shared markdown files (e.g., `BLOCKERS.md`)

---

### Step 2: Common Issues & Solutions

Based on the KG implementation, here are **likely bugs** and **preemptive fixes**:

---

#### Bug #1: spaCy Model Download Fails

**Symptom**:
```python
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Root cause**: Railway doesn't persist downloads between builds

**Solution**:
```python
# In backend/app/services/knowledge_graph/extractors/ner_extractor.py
import spacy
from spacy.cli import download

def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("📦 Downloading spaCy model...")
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

# Use in NERExtractor.__init__()
self.nlp = load_spacy_model()
```

**Alternative**: Add to `requirements.txt`:
```
https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

---

#### Bug #2: JSONB Serialization Error

**Symptom**:
```python
TypeError: Object of type datetime is not JSON serializable
```

**Root cause**: `created_at`, `updated_at` timestamps in graph metadata

**Solution**:
```python
# In graph_service.py - to_json() method
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Usage
def to_json(self) -> str:
    data = {
        "entities": {eid: e.to_dict() for eid, e in self._entity_index.items()},
        "relationships": [r.to_dict() for r in self._relationship_index.values()],
        "metadata": self.metadata.to_dict()
    }
    return json.dumps(data, cls=DateTimeEncoder)
```

---

#### Bug #3: WebSocket Connection Refused

**Symptom**:
```
WebSocket connection to 'ws://localhost:8000/api/...' failed
```

**Root cause**: CORS not configured for WebSocket, or wrong protocol (ws vs wss)

**Solution 1**: Update CORS middleware
```python
# In backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Solution 2**: Fix WebSocket URL in frontend
```typescript
// In useKnowledgeGraphWebSocket.ts
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/api/projects/${projectId}/graph/stream?token=${token}`;
```

---

#### Bug #4: React Force Graph Not Rendering

**Symptom**: Blank canvas, no graph visible

**Root cause**: Missing canvas element, or data format mismatch

**Solution**:
```typescript
// In GraphVisualization.tsx - check data format
interface GraphNode {
  id: string;           // REQUIRED
  name: string;
  type: string;
  // ... other fields
}

interface GraphLink {
  source: string;       // REQUIRED - must match node.id
  target: string;       // REQUIRED - must match node.id
  type: string;
  // ... other fields
}

// Ensure nodes have unique IDs
const nodes = data.nodes.map(n => ({
  ...n,
  id: n.id.toString()  // Force string type
}));
```

---

#### Bug #5: Background Job Stuck in "Pending"

**Symptom**: Extraction job never completes, status stays "pending"

**Root cause**: Background task runner not started, or async function not awaited

**Solution**:
```python
# Check that background task is actually running
from fastapi import BackgroundTasks

@router.post("/projects/{project_id}/extract")
async def extract_from_scene(
    background_tasks: BackgroundTasks,  # REQUIRED
    ...
):
    # Schedule task
    background_tasks.add_task(
        run_extraction_job,  # Must be async def
        job_id=str(job.id),
        ...
    )
```

**Verify**:
```bash
# Check Railway logs for:
# "Background task started: job-123"
railway logs --tail 100
```

---

#### Bug #6: LLM API Rate Limit

**Symptom**:
```
anthropic.RateLimitError: 429 Too Many Requests
```

**Root cause**: Batch extraction hitting API rate limits

**Solution**: Add exponential backoff
```python
# In llm_extractor.py
import time
from anthropic import RateLimitError

async def extract_entities(self, content: str, scene_id: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            # Make API call
            response = await self.client.messages.create(...)
            return parse_entities(response)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⏳ Rate limit hit, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

---

#### Bug #7: Graph Visualization Laggy with Many Nodes

**Symptom**: Browser freezes, slow rendering with 1000+ nodes

**Root cause**: Too many nodes rendering at once

**Solution**: Implement pagination and filtering
```typescript
// In GraphVisualization.tsx
const MAX_NODES = 500;

useEffect(() => {
  let nodes = data.nodes;

  // Filter by type if selected
  if (filterByType.length > 0) {
    nodes = nodes.filter(n => filterByType.includes(n.type));
  }

  // Limit to most important nodes
  if (nodes.length > MAX_NODES) {
    nodes = nodes
      .sort((a, b) => (b.entity.properties.importance || 0) - (a.entity.properties.importance || 0))
      .slice(0, MAX_NODES);
  }

  setGraphData({ nodes, links: filteredLinks });
}, [data, filterByType]);
```

---

#### Bug #8: Migration Fails on Railway

**Symptom**:
```
psycopg2.errors.DuplicateTable: relation "project_graphs" already exists
```

**Root cause**: Migration ran twice

**Solution**: Use `CREATE TABLE IF NOT EXISTS`
```sql
-- In migrations/add_knowledge_graph_tables.sql
CREATE TABLE IF NOT EXISTS project_graphs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ...
);
```

---

### Step 3: Performance Optimization Checklist

Once Cloud Claude has basic implementation working, optimize:

#### Backend Optimizations

1. **Database Indexes**:
```sql
-- Add index on project_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_project_graphs_project_id ON project_graphs(project_id);
CREATE INDEX IF NOT EXISTS idx_extraction_jobs_project_id ON extraction_jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_extraction_jobs_status ON extraction_jobs(status);
```

2. **Query Optimization**:
```python
# Use .filter() instead of loading all entities
entities = db.query(Entity).filter(Entity.project_id == project_id).limit(100).all()

# Instead of:
# entities = db.query(Entity).all()  # Loads everything!
```

3. **Caching**:
```python
# Cache graph data for 5 minutes
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_cached_graph(project_id: str, cache_key: int):
    # cache_key = int(time.time() / 300)  # 5 min cache
    return db.query(ProjectGraph).filter_by(project_id=project_id).first()
```

#### Frontend Optimizations

1. **Lazy Loading**:
```typescript
// Load graph data in chunks
const [loadedNodes, setLoadedNodes] = useState<GraphNode[]>([]);
const [page, setPage] = useState(0);

useEffect(() => {
  const loadNextPage = async () => {
    const response = await fetch(
      `/api/projects/${projectId}/entities?limit=100&offset=${page * 100}`
    );
    const data = await response.json();
    setLoadedNodes(prev => [...prev, ...data.entities]);
  };

  loadNextPage();
}, [page]);
```

2. **Debounced Search**:
```typescript
// In EntityBrowser.tsx - already implemented!
const debouncedSetSearchQuery = useCallback(
  debounce((value: string) => setSearchQuery(value), 300),
  []
);
```

3. **Memoization**:
```typescript
// Prevent unnecessary re-renders
const MemoizedGraphVisualization = React.memo(GraphVisualization);
```

---

## 🔬 Testing Strategy

### Phase 1: Smoke Tests (After Cloud Claude deploys)

Run these immediately:

```bash
# 1. Backend health check
curl https://writers-platform-production.up.railway.app/health

# 2. Graph API
curl https://writers-platform-production.up.railway.app/api/projects/test-id/graph \
  -H "Authorization: Bearer $TOKEN"

# 3. Extraction API
curl -X POST https://writers-platform-production.up.railway.app/api/projects/test-id/extract \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scene_id": "test", "scene_content": "Mickey walked on Mars.", "extractor_type": "ner"}'

# 4. Frontend loads
curl https://your-frontend.vercel.app/
```

---

### Phase 2: Integration Tests

```bash
cd factory-frontend
npm test
```

Expected output:
- GraphVisualization: 4 tests passing
- useAutoExtraction: 2 tests passing
- KnowledgeGraphWorkflow: 1 test passing

---

### Phase 3: E2E Tests

```bash
npm run test:e2e
```

Expected output:
- ✅ can view knowledge graph visualization
- ✅ can search and select entities
- ✅ can trigger extraction from scene editor
- ✅ can export graph to GraphML

---

### Phase 4: Performance Tests

```python
# Run performance benchmarks
cd factory-frontend
npm run test:performance

# Should complete in:
# - Add 1000 entities: <1s
# - Query entities: <100ms
# - Serialize graph: <500ms
```

---

## 📊 Monitoring & Metrics

### Backend Metrics (Railway Dashboard)

Monitor:
- **Request latency**: Should be <500ms for most endpoints
- **Error rate**: Should be <1%
- **Memory usage**: Should be <512MB
- **Database connections**: Should be <20 concurrent

### Frontend Metrics (Vercel Analytics)

Monitor:
- **Page load time**: <3s
- **Time to interactive**: <5s
- **Largest contentful paint**: <2.5s

### Database Metrics (Railway PostgreSQL)

Check:
```sql
-- Active connections
SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';

-- Slow queries
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Table sizes
SELECT
  schemaname, tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🐛 Bug Reporting Template

When Cloud Claude encounters a bug, they should create:

**File**: `BUGS.md` (or GitHub issue)

```markdown
## Bug: [Short description]

**Priority**: High/Medium/Low
**Blocker?**: Yes/No

### Symptoms
- What happened?
- Error message (if any)
- Which file/function?

### Expected Behavior
- What should happen?

### Steps to Reproduce
1. ...
2. ...
3. ...

### Environment
- Railway backend: [URL]
- Vercel frontend: [URL]
- Browser: [Chrome/Firefox/Safari]

### Request for Desktop Claude
- [ ] Help debug this issue
- [ ] Review my attempted fix
- [ ] Provide alternative solution
```

---

## 🎯 Success Metrics

Desktop Claude's bug-squashing is successful when:

- ✅ All 15+ API endpoints return 200/201 responses
- ✅ Entity extraction completes without errors
- ✅ Graph visualization renders in <2s
- ✅ WebSocket connection stays stable for 5+ minutes
- ✅ All unit tests pass (100%)
- ✅ All integration tests pass (100%)
- ✅ All E2E tests pass (100%)
- ✅ Performance benchmarks meet targets
- ✅ Zero critical bugs remaining
- ✅ Writers can use system for real work

---

## 📞 Communication Protocol

### Cloud Claude → Desktop Claude

**For blockers**:
1. Create file: `BLOCKERS.md` with issue details
2. Commit with message: `🚨 BLOCKER: [description]`
3. Desktop Claude will check within 2 hours

**For questions**:
1. Add comment in code: `// TODO: Desktop Claude - [question]`
2. Commit and push
3. Desktop Claude reviews next sync

**For review requests**:
1. Create PR with description
2. Tag Desktop Claude in PR description
3. Desktop Claude reviews within 4 hours

### Desktop Claude → Cloud Claude

**For fixes**:
1. Commit fix with message: `🔧 Fix: [description]`
2. Reference original issue in commit message
3. Add test to prevent regression

**For suggestions**:
1. Add comment in code: `// SUGGESTION: [idea]`
2. Create GitHub issue with `enhancement` label
3. Don't block on suggestions

---

## 🚀 Handoff Complete Checklist

Before declaring KG implementation "done":

### Backend
- [ ] All 15+ API endpoints implemented
- [ ] Database migration successful
- [ ] Both extractors working (LLM + NER)
- [ ] Background jobs completing successfully
- [ ] WebSocket streaming functional
- [ ] Export endpoints returning valid files
- [ ] Railway deployment stable

### Frontend
- [ ] Graph visualization renders correctly
- [ ] Entity browser search/filter works
- [ ] Relationship explorer shows connections
- [ ] Analytics dashboard displays stats
- [ ] Scene editor integration functional
- [ ] Auto-extraction triggers on save
- [ ] Export buttons download files
- [ ] Vercel deployment stable

### Testing
- [ ] Unit tests: 100% passing
- [ ] Integration tests: 100% passing
- [ ] E2E tests: 100% passing
- [ ] Performance benchmarks met
- [ ] Manual testing completed

### Documentation
- [ ] API endpoints documented
- [ ] Deployment process documented
- [ ] Known issues documented
- [ ] User guide created

### Performance
- [ ] API latency <500ms
- [ ] Graph render <2s
- [ ] Database queries optimized
- [ ] No memory leaks

---

## 🎉 Final Notes

Desktop Claude's role is to **support, not replace** Cloud Claude's implementation.

**Philosophy**:
- Let Cloud Claude own the implementation
- Jump in only when blocked or for code review
- Focus on quality, not speed
- No shortcuts, gold standard only

**Budget awareness**:
- Cloud Claude has $800 budget
- Track spend via API costs
- Optimize for efficiency, not penny-pinching
- Quality > cost savings

**Parallel execution**:
- Desktop Claude works on bugs/optimization
- Cloud Claude works on new features
- Both push to same repo
- Coordinate via commit messages

---

**Ready to squash bugs!** 🐛🔨

---

*Created by: Desktop Claude Code*
*Date: 2025-01-18*
*Role: Parallel Bug-Squashing Support Agent*
