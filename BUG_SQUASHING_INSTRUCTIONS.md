# Desktop Claude Bug-Squashing: Specific Instructions

**Date**: 2025-01-18
**Cloud Claude's Branch**: `claude/implement-knowledge-graph-01JRcFCWvxPePiR6k4QTnSRD`

---

## 🎯 Your Mission

Review Cloud Claude's Knowledge Graph implementation **file by file** and look for:
1. **Bugs** - Code that won't work or will crash
2. **TypeScript errors** - Type mismatches, missing imports
3. **API integration issues** - Wrong endpoints, missing auth
4. **Performance issues** - Inefficient loops, missing memoization
5. **Security issues** - Missing validation, XSS vulnerabilities

---

## 📋 Step-by-Step Review Process

### Step 1: Switch to Cloud Claude's Branch

```bash
cd /Users/gch2024/Documents/Documents\ -\ Mac\ Mini/writers-platform
git fetch origin
git checkout claude/implement-knowledge-graph-01JRcFCWvxPePiR6k4QTnSRD
```

### Step 2: See What Was Changed

```bash
# List all files Cloud Claude created/modified
git diff main --name-status

# See the 5 most recent commits
git log --oneline -5
```

**Expected commits:**
1. `4ca06dd` - Phase 6: Real-Time Integration
2. `dcc359a` - Session 2 complete (advanced components)
3. `807a7ec` - Session 1 (core visualization)
4. `d0b89fa` - Phase 1.5 (API layer)
5. `3f76f1b` - Phase 1 (backend core)

---

## 🔍 File-by-File Review Checklist

### **Backend Files (Phase 1)**

#### 1. Review: `backend/migrations/add_knowledge_graph_tables.sql`

**What to check:**
- [ ] Proper UUID types for IDs
- [ ] JSONB columns for graph_data
- [ ] GIN indexes created for JSONB queries
- [ ] Foreign key constraints on project_id
- [ ] NOT NULL constraints on required fields

**Look for:**
```sql
-- Good: Uses UUID
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- Bad: Missing index
-- CREATE INDEX should be present for project_id

-- Good: JSONB column
graph_data JSONB NOT NULL

-- Check: Is there a GIN index?
CREATE INDEX idx_project_graphs_data ON project_graphs USING GIN (graph_data);
```

**Action if issues found:**
```bash
# Create BLOCKER file
echo "## BLOCKER: Migration missing GIN index

File: backend/migrations/add_knowledge_graph_tables.sql
Issue: No GIN index on graph_data JSONB column
Impact: Slow queries on large graphs

Fix needed:
CREATE INDEX idx_project_graphs_data ON project_graphs USING GIN (graph_data);
" > BLOCKERS.md

git add BLOCKERS.md
git commit -m "🚨 BLOCKER: Migration missing GIN index"
git push origin claude/implement-knowledge-graph-01JRcFCWvxPePiR6k4QTnSRD
```

---

#### 2. Review: `backend/app/services/knowledge_graph/models.py`

**What to check:**
- [ ] Proper dataclass definitions
- [ ] All required fields present
- [ ] to_dict() methods return correct types
- [ ] from_dict() handles missing fields gracefully
- [ ] Enums for entity_type and relationship_type

**Look for:**
```python
# Good: Uses dataclass
@dataclass
class Entity:
    id: str
    name: str
    type: EntityType  # Should be Literal or Enum
    properties: Dict[str, Any]
    source_scenes: List[str]

# Bad: Missing type hints
def to_dict(self):  # Should be -> Dict[str, Any]
    return {...}

# Good: Handles None values
def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
    return cls(
        id=data.get('id', ''),
        name=data.get('name', 'Unknown'),
        ...
    )
```

**Action if issues found:**
Create BLOCKER with specific fix needed.

---

#### 3. Review: `backend/app/services/knowledge_graph/graph_service.py`

**What to check:**
- [ ] NetworkX import present
- [ ] Proper graph initialization (MultiDiGraph)
- [ ] add_entity() prevents duplicates
- [ ] add_relationship() validates entity existence
- [ ] JSON serialization handles datetime
- [ ] Performance: Uses indexes for lookups

**Look for:**
```python
# Good: Uses index for fast lookups
self._entity_index: Dict[str, Entity] = {}

# Bad: Searches through all nodes (slow!)
for node in self.graph.nodes():
    if node.name == name:  # O(n) search
        return node

# Good: O(1) lookup
return self._entity_index.get(entity_id)

# Check: DateTime serialization
def to_json(self) -> str:
    # Should use custom encoder for datetime
    return json.dumps(data, cls=DateTimeEncoder)
```

**Common bug to fix:**
If datetime serialization is missing, add:
```python
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
```

---

#### 4. Review: `backend/app/services/knowledge_graph/extractors/llm_extractor.py`

**What to check:**
- [ ] API key from environment variable
- [ ] Proper error handling for API failures
- [ ] Rate limit handling (exponential backoff)
- [ ] Token counting for cost calculation
- [ ] Timeout on API calls
- [ ] Structured output parsing

**Look for:**
```python
# Good: API key from env
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

# Bad: No timeout
response = self.client.messages.create(...)

# Good: Has timeout
response = self.client.messages.create(..., timeout=30.0)

# Good: Rate limit handling
except RateLimitError:
    time.sleep(2 ** attempt)  # Exponential backoff
```

---

#### 5. Review: `backend/app/services/knowledge_graph/extractors/ner_extractor.py`

**What to check:**
- [ ] spaCy model loads correctly
- [ ] Auto-download if model missing
- [ ] Proper entity type mapping
- [ ] Handles empty text gracefully

**Look for:**
```python
# Good: Auto-download missing model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Bad: Crashes if model missing
nlp = spacy.load("en_core_web_sm")  # Will crash!
```

---

#### 6. Review: `backend/app/routes/knowledge_graph.py`

**What to check:**
- [ ] All endpoints have authentication (@require_auth)
- [ ] Proper error handling (try/except)
- [ ] Input validation on request bodies
- [ ] Correct HTTP status codes
- [ ] CORS headers for WebSocket
- [ ] Background tasks properly scheduled

**Look for:**
```python
# Good: Has auth
@router.get("/projects/{project_id}/graph")
async def get_graph(
    project_id: str,
    current_user: User = Depends(get_current_user)  # Auth!
):
    ...

# Bad: No auth
@router.get("/projects/{project_id}/graph")
async def get_graph(project_id: str):  # Anyone can access!
    ...

# Good: Input validation
if not scene_content or len(scene_content) < 10:
    raise HTTPException(400, "Scene content too short")

# Good: Proper status codes
return JSONResponse(content=data, status_code=201)  # Created

# Good: Error handling
try:
    result = kg.extract(...)
except Exception as e:
    logger.error(f"Extraction failed: {e}")
    raise HTTPException(500, "Extraction failed")
```

---

### **Frontend Files (Sessions 1-2-6)**

#### 7. Review: `factory-frontend/src/types/knowledge-graph.ts`

**What to check:**
- [ ] All types exported
- [ ] Enums match backend
- [ ] Optional fields marked with ?
- [ ] Proper TypeScript syntax

**Look for:**
```typescript
// Good: Literal types
export type EntityType =
  | 'character'
  | 'location'
  | 'object'
  // ... etc

// Bad: Stringly typed
export type EntityType = string  // Too loose!

// Good: Optional fields
export interface Entity {
  id: string;
  name: string;
  type: EntityType;
  properties: Record<string, any>;
  source_scenes: string[];
  created_at?: string;  // Optional!
}
```

---

#### 8. Review: `factory-frontend/src/components/knowledge-graph/GraphVisualization.tsx`

**What to check:**
- [ ] react-force-graph-3d import works
- [ ] Proper TypeScript types for props
- [ ] Loading/error states present
- [ ] Memory leaks (cleanup in useEffect)
- [ ] Large graph performance (node limit)

**Look for:**
```typescript
// Good: Cleanup WebSocket on unmount
useEffect(() => {
  const ws = new WebSocket(url);

  return () => {
    ws.close();  // Cleanup!
  };
}, []);

// Bad: Memory leak
useEffect(() => {
  const ws = new WebSocket(url);
  // No cleanup - ws stays open forever!
}, []);

// Good: Node limit for performance
const MAX_NODES = 500;
if (nodes.length > MAX_NODES) {
  nodes = nodes.slice(0, MAX_NODES);
}
```

---

#### 9. Review: `factory-frontend/src/hooks/useKnowledgeGraphWebSocket.ts`

**What to check:**
- [ ] Proper WebSocket URL construction
- [ ] Auto-reconnect logic
- [ ] Cleanup on unmount
- [ ] Error handling
- [ ] Token in WebSocket URL

**Look for:**
```typescript
// Good: Proper WebSocket URL
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.host}/api/projects/${projectId}/graph/stream?token=${token}`;

// Bad: Hardcoded protocol
const wsUrl = `ws://localhost:8000/...`;  // Won't work in prod!

// Good: Auto-reconnect
ws.onclose = () => {
  if (autoReconnect) {
    setTimeout(() => connect(), reconnectInterval);
  }
};

// Good: Cleanup
useEffect(() => {
  connect();
  return () => disconnect();  // Cleanup!
}, []);
```

---

## 🐛 Common Bugs to Look For

### Bug Pattern #1: Missing Error Handling
```typescript
// Bad
const data = await fetch(url).then(r => r.json());

// Good
try {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
} catch (err) {
  console.error('Fetch failed:', err);
  // Handle error
}
```

### Bug Pattern #2: Missing Auth Headers
```typescript
// Bad
fetch('/api/projects/123/graph')

// Good
fetch('/api/projects/123/graph', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  }
})
```

### Bug Pattern #3: Type Mismatches
```typescript
// Bad
const nodes: GraphNode[] = data.nodes;  // Might crash if wrong type!

// Good
const nodes: GraphNode[] = Array.isArray(data.nodes) ? data.nodes : [];
```

### Bug Pattern #4: Performance Issues
```typescript
// Bad: Re-renders on every keystroke
<input onChange={(e) => setQuery(e.target.value)} />

// Good: Debounced
const debouncedSetQuery = debounce((value) => setQuery(value), 300);
<input onChange={(e) => debouncedSetQuery(e.target.value)} />
```

---

## 📊 Review Summary Template

After reviewing, create a summary:

```markdown
# Bug Review Summary - Session [X]

**Files Reviewed**: [count]
**Bugs Found**: [count]
**Critical Issues**: [count]
**Warnings**: [count]

## Critical Issues (Fix Immediately)
1. [File]: [Issue description]
   - Fix: [Specific code change needed]

## Warnings (Should Fix)
1. [File]: [Issue description]
   - Suggestion: [How to improve]

## Code Quality Notes
- [Positive feedback on well-written code]
- [Areas that could be improved]

**Overall Assessment**: [Good/Needs Work/Critical Issues]
```

---

## 🚀 How to Report Issues

### For Critical Bugs:
1. Create `BLOCKERS.md` with issue details
2. Commit with `🚨 BLOCKER:` prefix
3. Push immediately

### For Warnings:
1. Add comments to the code: `// FIXME: [description]`
2. Create GitHub issue with `bug` label
3. Don't block Cloud Claude

### For Suggestions:
1. Add comments: `// TODO: Consider [improvement]`
2. Document in review summary
3. Don't block progress

---

## ✅ Review Checklist

- [ ] Reviewed all backend Python files
- [ ] Reviewed all frontend TypeScript files
- [ ] Checked for missing error handling
- [ ] Checked for auth on all endpoints
- [ ] Checked for TypeScript type safety
- [ ] Checked for performance issues
- [ ] Checked for memory leaks
- [ ] Created BLOCKERS.md if critical issues found
- [ ] Created review summary

---

**Start with Step 1** - switch to Cloud Claude's branch and begin reviewing files one by one!
