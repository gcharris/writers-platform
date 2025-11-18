# Cloud Claude: Knowledge Graph Implementation Handoff

**Date**: 2025-01-18
**Task**: Implement complete Knowledge Graph system (Option A: Gold Standard)
**Priority**: CRITICAL
**Budget**: $800 Claude Cloud credits
**Philosophy**: "We have all the time in the world to build a gold standard product"

---

## 🎯 Mission

Implement the **complete, production-grade Knowledge Graph system** documented in:
- `KNOWLEDGE_GRAPH_IMPLEMENTATION.md` (Part 1: Backend Core)
- `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART2.md` (Part 2: API & Jobs)
- `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` (Part 3: Frontend & Testing)
- `KNOWLEDGE_GRAPH_COMPLETE_SUMMARY.md` (Overview & Reference)

**NO SHORTCUTS**. Build it RIGHT the first time.

---

## 📋 What Desktop Claude Built

Desktop Claude created **complete documentation** with production-ready code for:

✅ NetworkX-based graph engine (15+ methods)
✅ Dual extraction strategy (LLM + NER)
✅ PostgreSQL JSONB persistence
✅ 15+ REST API endpoints
✅ Background job processing
✅ WebSocket real-time updates
✅ 3D graph visualization (React Force Graph)
✅ Entity browser, relationship explorer, analytics dashboard
✅ Scene editor integration with auto-extraction
✅ Reference file auto-linking
✅ Knowledge context panel
✅ Graph-powered semantic search
✅ Export to GraphML, NotebookLM, JSON
✅ Complete test suite (unit, integration, E2E)
✅ Deployment guide

**Your job**: Copy the code from documentation → actual files, test, deploy.

---

## 🚀 Implementation Steps

### Phase 1: Backend Core (6-8 hours)

#### Step 1.1: Database Migration (30 min)

**File**: `backend/migrations/add_knowledge_graph_tables.sql`

Read from: `KNOWLEDGE_GRAPH_IMPLEMENTATION.md` → Phase 3 → Database Integration

Creates 2 tables:
- `project_graphs` - Stores graph data as JSONB
- `extraction_jobs` - Tracks background extraction jobs

**Action**:
```bash
# Copy SQL from documentation
# Run migration on Railway
python backend/migrate.py --migration-file backend/migrations/add_knowledge_graph_tables.sql
```

**Verification**:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('project_graphs', 'extraction_jobs');
```

---

#### Step 1.2: Core Graph Engine (2 hours)

**Files to create**:
1. `backend/app/services/knowledge_graph/__init__.py`
2. `backend/app/services/knowledge_graph/models.py`
3. `backend/app/services/knowledge_graph/graph_service.py`

**Source**: `KNOWLEDGE_GRAPH_IMPLEMENTATION.md` → Phase 1

**Key classes**:
- `Entity` - Character, location, object, concept, event, organization, theme
- `Relationship` - knows, conflicts_with, located_in, owns, etc.
- `GraphMetadata` - Project ID, entity/relationship counts, timestamps
- `KnowledgeGraphService` - NetworkX-based graph operations

**Critical methods**:
- `add_entity()`, `add_relationship()`
- `query_entities()`, `get_entity()`
- `get_connected_entities()`, `find_path()`
- `get_central_entities()`, `get_communities()`
- `to_json()`, `from_json()`
- `export_for_visualization()`, `export_graphml()`

**Testing**:
```python
# Create test
kg = KnowledgeGraphService("test-project")
kg.add_entity(Entity(id="1", name="Mickey", type="character", properties={}, source_scenes=[]))
kg.add_entity(Entity(id="2", name="Mars", type="location", properties={}, source_scenes=[]))
kg.add_relationship(Relationship(source="1", target="2", type="located_in", properties={}, source_scenes=[]))

assert kg.get_entity("1").name == "Mickey"
assert len(kg.query_entities({"type": "character"})) == 1
```

---

#### Step 1.3: Entity Extraction (2-3 hours)

**Files to create**:
1. `backend/app/services/knowledge_graph/extractors/__init__.py`
2. `backend/app/services/knowledge_graph/extractors/llm_extractor.py`
3. `backend/app/services/knowledge_graph/extractors/ner_extractor.py`

**Source**: `KNOWLEDGE_GRAPH_IMPLEMENTATION.md` → Phase 2

**LLM Extractor** (High quality, paid):
- Uses Claude Sonnet 4.5 or GPT-4o
- Structured prompts for entity/relationship extraction
- Returns Entity and Relationship objects
- Cost: ~$0.01 per scene

**NER Extractor** (Fast, free):
- Uses spaCy `en_core_web_sm` model
- Extracts PERSON, LOC, ORG, etc.
- Maps to Entity types
- Free, local processing

**Testing**:
```python
# Test LLM extractor
llm = LLMExtractor(model_name="claude-sonnet-4.5")
entities = await llm.extract_entities("Mickey walked on Mars.", "scene-1")
assert len(entities) >= 2  # Mickey, Mars

# Test NER extractor
ner = NERExtractor()
entities = ner.extract_entities("Mickey walked on Mars.", "scene-1")
assert len(entities) >= 2
```

---

#### Step 1.4: Database Models (1 hour)

**File**: `backend/app/models/knowledge_graph.py`

**Source**: `KNOWLEDGE_GRAPH_IMPLEMENTATION.md` → Phase 3

**SQLAlchemy models**:
- `ProjectGraph` - Stores graph_data as JSONB
- `ExtractionJob` - Tracks extraction status, cost, results

**Key fields**:
- `ProjectGraph.graph_data` - JSONB containing full NetworkX graph
- `ExtractionJob.status` - pending, running, completed, failed
- `ExtractionJob.entities_found`, `relationships_found`, `cost`

---

#### Step 1.5: API Layer (2-3 hours)

**File**: `backend/app/routes/knowledge_graph.py`

**Source**: `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART2.md` → Phase 4

**15+ endpoints to implement**:

**Graph Management**:
- `GET /api/projects/{id}/graph` - Get visualization data
- `GET /api/projects/{id}/graph/stats` - Get statistics
- `WS /api/projects/{id}/graph/stream` - WebSocket updates

**Entity Operations**:
- `GET /api/projects/{id}/entities` - List/search
- `GET /api/projects/{id}/entities/{entity_id}` - Get details
- `PUT /api/projects/{id}/entities/{entity_id}` - Update
- `DELETE /api/projects/{id}/entities/{entity_id}` - Delete
- `GET /api/projects/{id}/entities/{entity_id}/connections` - Get connected

**Relationship Operations**:
- `GET /api/projects/{id}/relationships` - List
- `POST /api/projects/{id}/find-path` - Find path between entities

**Extraction Operations**:
- `POST /api/projects/{id}/extract` - Extract from scene
- `POST /api/projects/{id}/extract-all` - Batch extraction
- `GET /api/projects/{id}/extract/jobs` - List jobs
- `GET /api/projects/{id}/extract/jobs/{job_id}` - Get status

**Export Operations**:
- `GET /api/projects/{id}/graph/export/graphml` - GraphML format
- `GET /api/projects/{id}/graph/export/notebooklm` - NotebookLM markdown

**Testing each endpoint**:
```bash
# Test graph endpoint
curl https://your-backend.up.railway.app/api/projects/{id}/graph \
  -H "Authorization: Bearer $TOKEN"

# Test extraction
curl -X POST https://your-backend.up.railway.app/api/projects/{id}/extract \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"scene_id": "scene-1", "scene_content": "Mickey walked on Mars.", "extractor_type": "ner"}'
```

---

### Phase 2: Frontend Implementation (6-8 hours)

#### Step 2.1: Install Dependencies (15 min)

```bash
cd factory-frontend
npm install react-force-graph-3d three @types/three
```

---

#### Step 2.2: Visualization Components (3-4 hours)

**Files to create** (from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` → Phase 5):

1. **`src/components/knowledge-graph/GraphVisualization.tsx`** (1.5 hours)
   - 3D interactive graph using React Force Graph
   - Custom node rendering (size based on importance, color by type)
   - Click to focus, zoom controls
   - Entity highlighting
   - Real-time updates

2. **`src/components/knowledge-graph/EntityBrowser.tsx`** (1 hour)
   - Search and filter entities
   - Type filters (character, location, etc.)
   - Sort by name, importance, mentions
   - Click to view details

3. **`src/components/knowledge-graph/EntityDetails.tsx`** (30 min)
   - Display entity properties
   - Show connected entities
   - Navigate to relationships

4. **`src/components/knowledge-graph/RelationshipExplorer.tsx`** (45 min)
   - List relationships
   - Path finding between entities
   - Filter by relationship type

5. **`src/components/knowledge-graph/AnalyticsDashboard.tsx`** (45 min)
   - Graph statistics
   - Entity/relationship type distribution
   - Most connected entities
   - Community detection results

6. **`src/components/knowledge-graph/ExportImport.tsx`** (30 min)
   - Export to GraphML button
   - Export to NotebookLM button
   - Export to JSON button

**Testing**:
- Verify graph loads and displays
- Test entity search/filter
- Test path finding
- Test export downloads

---

#### Step 2.3: Real-Time Integration (2 hours)

**Files to create** (from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` → Phase 6):

1. **`src/hooks/useKnowledgeGraphWebSocket.ts`** (45 min)
   - Connect to WebSocket endpoint
   - Auto-reconnect on disconnect
   - Parse graph update messages
   - Callback for update events

2. **`src/hooks/useAutoExtraction.ts`** (30 min)
   - Trigger extraction on scene save
   - Poll for job status
   - Callback for completion

3. **`src/components/knowledge-graph/LiveGraphUpdates.tsx`** (30 min)
   - Display real-time update notifications
   - Connection status indicator
   - Update feed

4. **`src/components/knowledge-graph/ExtractionJobMonitor.tsx`** (45 min)
   - List running/completed jobs
   - Progress bars
   - Cancel job button

**Testing**:
- WebSocket connects successfully
- Updates appear in real-time
- Job status updates correctly

---

#### Step 2.4: Workflow Integration (2-3 hours)

**Files to create** (from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` → Phase 7):

1. **`src/components/editor/SceneEditorWithKnowledgeGraph.tsx`** (1.5 hours)
   - Scene editor with graph sidebar
   - Auto-extraction toggle
   - Extractor type selector (LLM vs NER)
   - Highlight entities mentioned in scene
   - Show entity connections

2. **`src/components/reference/ReferenceFileWithAutoLink.tsx`** (45 min)
   - Auto-link entities to reference files
   - Suggest related entities
   - Add entity mention button

3. **`src/components/knowledge-graph/KnowledgeContextPanel.tsx`** (30 min)
   - Display context for current scene
   - Custom query input
   - Show relevant entities

4. **`src/components/knowledge-graph/GraphPoweredSearch.tsx`** (45 min)
   - Semantic search
   - Search type selector (direct, semantic, path)
   - Ranked results with relevance scores

**Testing**:
- Scene editor integration works
- Auto-extraction triggers on save
- Context panel shows relevant entities
- Search returns accurate results

---

### Phase 3: Testing & Deployment (3-4 hours)

#### Step 3.1: Unit Tests (1.5 hours)

**Files to create** (from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` → Phase 8):

1. **`src/components/knowledge-graph/__tests__/GraphVisualization.test.tsx`**
2. **`src/hooks/__tests__/useAutoExtraction.test.ts`**

Run:
```bash
npm test
```

---

#### Step 3.2: Integration Tests (1 hour)

**File**: `src/__tests__/integration/KnowledgeGraphWorkflow.test.tsx`

Test full workflow: edit → save → extract → display

---

#### Step 3.3: E2E Tests (1 hour)

**File**: `e2e/knowledge-graph.spec.ts`

Playwright tests:
- View graph visualization
- Search and select entities
- Trigger extraction from scene editor
- Export graph to GraphML

Run:
```bash
npm run test:e2e
```

---

#### Step 3.4: Deployment (30 min)

**Backend** (Railway):
```bash
cd backend
pip install networkx spacy
python -m spacy download en_core_web_sm
railway deploy
```

**Frontend** (Vercel):
```bash
cd factory-frontend
npm run build
vercel --prod
```

---

## 📊 Success Criteria

Writers must be able to:
- ✅ Write scenes and auto-extract entities
- ✅ Visualize entire story knowledge graph in 3D
- ✅ Search for characters, locations, relationships
- ✅ See context about entities while writing
- ✅ Track character connections and conflicts
- ✅ Export graph to Gephi/NotebookLM
- ✅ Choose extraction quality (LLM vs. NER)
- ✅ Monitor extraction jobs in real-time

---

## 🐛 Known Issues to Watch For

### Issue 1: spaCy Model Download
**Problem**: `en_core_web_sm` might not install correctly
**Solution**: Run `python -m spacy download en_core_web_sm` separately

### Issue 2: WebSocket CORS
**Problem**: WebSocket connection blocked by CORS
**Solution**: Add WebSocket support to CORS middleware in `backend/app/main.py`

### Issue 3: Graph Serialization Size
**Problem**: Large graphs (>10MB) slow to serialize
**Solution**: Use pagination for entity lists, lazy-load graph data

### Issue 4: React Force Graph Performance
**Problem**: Slow rendering with 1000+ nodes
**Solution**: Implement entity filtering, limit initial render to 500 nodes

---

## 🔍 Code Quality Checklist

- [ ] All API endpoints return proper error codes (400, 404, 500)
- [ ] Database queries use indexes (check `EXPLAIN ANALYZE`)
- [ ] WebSocket connections close gracefully
- [ ] Background jobs have timeout limits
- [ ] LLM API calls have retry logic
- [ ] Frontend components have loading states
- [ ] Tests achieve >80% code coverage
- [ ] No hardcoded credentials in code
- [ ] All imports are properly typed (TypeScript)
- [ ] Error messages are user-friendly

---

## 📈 Performance Targets

- **Entity query**: <100ms
- **Graph serialization**: <500ms (500 entities + 1000 relationships)
- **NER extraction**: <5 seconds per scene
- **LLM extraction**: <30 seconds per scene
- **WebSocket latency**: <200ms
- **3D graph render**: <2 seconds (500 nodes)

---

## 💰 Cost Tracking

Track LLM extraction costs:
```python
# In llm_extractor.py
cost = (input_tokens / 1_000_000 * INPUT_PRICE) + (output_tokens / 1_000_000 * OUTPUT_PRICE)
# Store in ExtractionJob.cost
```

Monitor total spend:
```sql
SELECT SUM(cost) FROM extraction_jobs WHERE created_at > NOW() - INTERVAL '24 hours';
```

---

## 🚨 Critical Paths

**Must work for launch**:
1. Scene editor → auto-extract (NER) → graph visualization
2. Entity browser → search → view details
3. Export to GraphML

**Nice to have**:
1. LLM extraction (can add later if NER works)
2. Path finding between entities
3. Community detection

---

## 📞 Questions?

If you encounter blockers:
1. Check documentation in `KNOWLEDGE_GRAPH_IMPLEMENTATION*.md` files
2. Refer to `KNOWLEDGE_GRAPH_COMPLETE_SUMMARY.md` for API reference
3. Check `CLOUD_CLAUDE_HANDOFF.md` (this file) for deployment steps
4. Review `backend/engine/cognee_knowledge_graph/` for reference implementation (not used, but shows pattern)

Desktop Claude will be running a **parallel bug-squashing agent** to help fix issues.

---

## 🎯 Final Notes

This is **Option A: The Gold Standard**. Take your time, build it right, test thoroughly.

**No shortcuts. No compromises. Production-grade code.**

Budget: $800 (plenty for 15-20 hours of careful work)

Philosophy: "We have all the time in the world to build a gold standard product."

---

**Ready to build!** 🚀

---

*Handoff created by: Desktop Claude Code*
*Date: 2025-01-18*
*For: Cloud Claude Implementation*
