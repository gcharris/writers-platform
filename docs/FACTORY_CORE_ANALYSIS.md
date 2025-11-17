# Writers-Factory-Core Deep Dive Analysis
## Complete Architecture & Migration Strategy

**Analyzed**: 2025-01-17
**Source**: https://github.com/gcharris/writers-factory-core
**Target**: writers-platform consolidation

---

## Executive Summary

After deep-diving into writers-factory-core, I now understand this is **far more sophisticated** than initial assumptions. This is NOT just "wizard + tournament" - this is a **complete AI-powered novel writing orchestration platform** with:

### Core Innovation
1. **Conversational Orchestration Agent** - Like Cursor IDE's AI assistant, but for novel writing
2. **Knowledge-Driven Scene Generation** - Every scene prompt is built from KB queries
3. **Workflow Engine** - Flexible, dependency-based task orchestration
4. **Smart Knowledge Router** - Cognee (local) + NotebookLM (external) integration
5. **Manuscript as Code** - Acts → Chapters → Scenes in JSON + Markdown

---

## What I Learned About the System

### 1. The Orchestration Model (NOT One-Time Analysis!)

**Current Understanding** ✅:
```
User: "Let's write Scene 4"
Agent: "That's Chapter 3, Scene 3: Mary kills Joe"
Agent: *Queries KB for*:
  ├─ Mary's character profile
  ├─ Joe's character profile
  ├─ Their relationship history
  ├─ Previous scenes (Chapter 3, Scenes 1-2)
  ├─ Plot threads (murder foreshadowed in Scene 1)
  ├─ World-building (location, time period)
  └─ Voice/tone guidelines
Agent: *Builds detailed prompt* with ALL context
Agent: *Sends to AI model(s)* for generation
Writer: *Reviews, edits, approves*
Agent: *Saves scene to KB*
Agent: *Updates character/plot files*
Repeat for next scene...
```

This is **continuous collaboration**, not batch processing!

### 2. Manuscript Structure (The "Codebase")

**File Structure**: `/home/user/writers-factory-core/factory/core/manuscript/`

```python
# structure.py defines:
Manuscript
  └─ Acts[] (Act 1, Act 2, Act 3)
      └─ Chapters[] (Chapter 1, 2, 3...)
          └─ Scenes[] (Scene 1, 2, 3...)
              ├─ title
              ├─ content (actual prose)
              ├─ word_count
              ├─ notes
              └─ metadata {}
```

**Storage**: `/home/user/writers-factory-core/factory/core/manuscript/storage.py`
- Main file: `manuscript.json` (all structure)
- Optional: `scenes/{scene_id}.md` (individual markdown)
- Backup: `manuscript.json.backup` (atomic writes)

**Key Insight**: The "novel codebase" you mentioned is this JSON structure + optional markdown exports!

### 3. Knowledge Base Architecture

**File**: `/home/user/writers-factory-core/factory/knowledge/router.py`

**Two Knowledge Sources**:

1. **Cognee (Local Semantic Graph)**
   - Handles: Factual, Conceptual, General queries
   - Uses: Gemini File Search internally (hidden from user)
   - Always available
   - Lightweight: ~17MB

2. **NotebookLM (External Analysis)**
   - Handles: Analytical queries
   - Optional: User configures in preferences
   - Used for: Deep research, thematic analysis
   - Returns: Text + optional audio summaries

**Query Routing**:
```python
query = "What is Mary's relationship with Joe?"
router.classify_query(query)  # → FACTUAL
router.route_query(query)     # → COGNEE

query = "Why would Mary kill Joe given her moral code?"
router.classify_query(query)  # → ANALYTICAL
router.route_query(query)     # → NOTEBOOKLM (if enabled)
                              # → COGNEE (fallback)
```

**Critical for Scene Prompts**:
```python
# scene_operations/generation.py lines 121-150
async def _get_context(context):
    """Query knowledge base for relevant context"""
    queries = auto_generate_from_outline(outline)
    for query in queries:
        result = await knowledge_router.query(query)
        context_data[query] = result.answer
    return context_data
```

### 4. Workflow Engine (The Orchestration Core)

**File**: `/home/user/writers-factory-core/factory/core/workflow_engine.py`

**Features**:
- Dependency-based execution (topological sort)
- Parallel execution of independent steps
- Pause/resume capabilities
- Retry logic with exponential backoff
- State persistence

**Example Scene Generation Workflow**:
```python
# workflows/scene_operations/generation.py
class SceneGenerationWorkflow(Workflow):
    def run(outline, model_name, use_knowledge_context):
        # Step 1: Parse outline
        add_step("parse_outline", self._parse_outline)

        # Step 2: Get KB context (depends on step 1)
        add_step("get_context", self._get_context,
                 dependencies=["parse_outline"])

        # Step 3: Generate scene (depends on step 2)
        add_step("generate_scene", self._generate_scene,
                 dependencies=["get_context"])

        # Execute workflow
        result = await engine.run_workflow(self)
        return result.outputs["scene"]
```

**This is the "ongoing agent" you described** - the workflow engine executing steps based on user conversation!

### 5. Creation Wizard (Initial Setup)

**File**: `/home/user/writers-factory-core/factory/wizard/wizard.py`

**5 Phases**:
1. **Foundation** - Genre, theme, concept, audience
2. **Character** - Protagonist, wants, needs, flaws, supporting cast
3. **Plot** - 15-beat structure (Save the Cat)
4. **World** - Setting, rules, cultural context, visual details
5. **Symbolism** - Symbolic objects, philosophical questions, allegory

**Output**: 4,000-6,000 word "Story Bible" in markdown

**Key Insight**: This is simpler than I expected! It's NOT the complex wizard Desktop Claude described. This is just Q&A that generates a story bible markdown file.

**What's MISSING**: The 8-category wizard with NotebookLM queries that Desktop Claude referenced! That might be in a different branch or planned feature.

---

## Directory Structure to Copy

Based on my analysis, here are the **complete directories** to copy:

### Priority 1: Core System (REQUIRED)

```bash
# Copy entire directories:
/factory/core/                    # → backend/app/core/
├── workflow_engine.py            #    Orchestration engine
├── agent_pool.py                 #    Multi-agent management
├── manuscript/                   #    Manuscript data models
│   ├── structure.py             #    Act/Chapter/Scene classes
│   └── storage.py               #    JSON persistence
└── config/                       #    Configuration

/factory/workflows/               # → backend/app/workflows/
├── base_workflow.py             #    Base workflow class
├── scene_operations/            #    Scene generation/enhancement
│   ├── generation.py            #    Context-aware scene generation
│   ├── enhancement.py           #    Scene improvement
│   └── voice_testing.py         #    Voice consistency
├── project_genesis/             #    Initial project setup
│   └── workflow.py              #    Project initialization
└── multi_model_generation/      #    Tournament system

/factory/knowledge/               # → backend/app/services/knowledge/
├── router.py                     #    Smart query routing
└── cache.py                      #    Query result caching

/factory/agents/                  # → backend/app/services/agents/
├── base_agent.py                 #    Base agent class
├── ollama_agent.py               #    Local AI (Llama 3.3)
└── chinese/                      #    Fallback models (DeepSeek, etc.)

/factory/wizard/                  # → backend/app/services/wizard/
└── wizard.py                     #    Creation wizard (story bible)
```

### Priority 2: Web Integration (REQUIRED for UI)

```bash
/webapp/backend/                  # → backend/app/routes/ (analyze & adapt)
├── app.py                        #    Main Flask/FastAPI app
├── agent_integration.py          #    How agent connects to web
└── simple_app.py                 #    Simplified version

/webapp/frontend-v2/              # → factory-frontend/src/ (if exists)
# (Check if this directory has the chat UI - if so, copy components)
```

### Priority 3: Tools & Utilities

```bash
/factory/tools/                   # → backend/app/utils/ or backend/app/tools/
# (Check what's in here - might have useful utilities)

/factory/storage/                 # → backend/app/storage/
├── database.py                   #    Database integration
└── README.md                     #    Storage documentation

/factory/ui/ or /factory/tui/     # → Analyze (might be CLI interface)
# (Might not need if we have web UI)
```

---

## What's NOT in writers-factory-core

Based on Desktop Claude's SESSION_4_BRIEF.md, they mentioned:

❌ **8-Category Wizard with NotebookLM Queries**
- `category_templates.py` with 50+ fields
- `setup_wizard_agent.py` with AI conversation
- WebSocket wizard endpoint

❌ **Complex NotebookLM Integration**
- Direct MCP server queries during wizard
- Real NotebookLM client (only mock in router.py)

❌ **Cognee Knowledge Graph (Complete)**
- `cognee_knowledge_graph/` exists in `backend/engine/` (writers-platform!)
- But router.py only has mock implementation
- Might be in writers-platform already?

**Question**: Are these in a different branch of writers-factory-core? Or already in writers-platform?

---

## Cognee Situation

**In writers-platform** (`backend/engine/cognee_knowledge_graph/`):
```
├── __init__.py
├── bulk_uploader.py
├── cognee_graph.py
├── entity_queries.py
```

**In writers-factory-core** (`factory/knowledge/router.py`):
- Only mock Cognee integration (lines 182-219)
- Real integration might be in writers-platform already!

**Recommendation**:
- Use NetworkX-based lightweight KB for MVP
- Avoid Cognee's 500MB dependencies for deployment
- Keep it simple: JSON storage + in-memory graph

---

## The Missing Piece: Continuous Agent UI

**What I DIDN'T find**: The conversational agent UI (like Cursor's side panel)

**What exists**:
- Workflow engine ✅ (backend orchestration)
- Knowledge router ✅ (KB queries)
- Scene generation ✅ (prompt building)
- Manuscript structure ✅ (data models)

**What's missing**:
- Web UI for ongoing conversation ❌
- Agent state management ❌
- Context-aware chat interface ❌
- "What scene should I write next?" UI ❌

**Where this might be**:
1. In `/webapp/frontend-v2/` (need to check)
2. In a separate repo?
3. Planned but not built?
4. **Already in writers-platform?** (we should check!)

---

## Migration Strategy: Copy Complete Directories

### Step 1: Copy Core Directories (User Action)

**You said you can copy directories in "two seconds" - here's what to copy**:

```bash
# From writers-factory-core to writers-platform:

cp -r /path/to/writers-factory-core/factory/core \
      /path/to/writers-platform/backend/app/core

cp -r /path/to/writers-factory-core/factory/workflows \
      /path/to/writers-platform/backend/app/workflows

cp -r /path/to/writers-factory-core/factory/knowledge \
      /path/to/writers-platform/backend/app/services/knowledge

cp -r /path/to/writers-factory-core/factory/agents \
      /path/to/writers-platform/backend/app/services/agents

cp -r /path/to/writers-factory-core/factory/wizard \
      /path/to/writers-platform/backend/app/services/wizard

cp -r /path/to/writers-factory-core/factory/storage \
      /path/to/writers-platform/backend/app/storage

cp -r /path/to/writers-factory-core/factory/tools \
      /path/to/writers-platform/backend/app/tools
```

### Step 2: I'll Adapt Imports (30-60 min)

After you copy, I'll:
- Fix all import paths
- Update to match writers-platform structure
- Integrate with existing FastAPI routes
- Add database models for new structures

### Step 3: Web Integration (2-4 hours)

- Analyze `/webapp/backend/app.py` integration
- Create FastAPI endpoints for workflows
- Add WebSocket for real-time agent conversation
- Build or adapt frontend chat UI

---

## Key Architectural Decisions

### 1. Manuscript Storage

**Factory-Core Approach**: JSON file (`manuscript.json`)
**Writers-Platform Approach**: PostgreSQL database

**Recommendation**: **Use PostgreSQL** (already have it)
- Store Acts/Chapters/Scenes in DB tables
- Keep factory-core's data models (structure.py)
- Replace storage.py with SQLAlchemy models

### 2. Knowledge Base

**Factory-Core Approach**: Cognee (mock) + NotebookLM (mock)
**Deployment Reality**: Cognee has 500MB dependencies → breaks Railway

**Recommendation**: **Lightweight NetworkX KB**
```python
# backend/app/services/knowledge/simple_kb.py
class SimpleDevelopmentKB:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.scenes = {}
        self.characters = {}
        self.plot_threads = {}

    async def query(self, query: str) -> QueryResult:
        # Simple keyword matching + context assembly
        # Good enough for MVP!
        pass
```

### 3. Workflow Engine

**Factory-Core**: Complete, production-ready workflow engine
**Recommendation**: **Copy as-is!** It's excellent.

### 4. Agent Pool

**Factory-Core**: Has agent pool system
**Writers-Platform**: Has tournament system

**Recommendation**: **Merge both**
- Use factory-core's agent pool architecture
- Integrate writers-platform's 5-model tournament
- Best of both worlds!

---

## What to Build Next

### Phase 1: Copy & Integrate Core (Session 4)
1. **User copies directories** (you said 2 seconds!)
2. **I adapt imports** (30-60 min)
3. **Add database models** (1-2 hours)
4. **Create FastAPI endpoints** (2-3 hours)
5. **Test workflow execution** (1 hour)

**Result**: Backend orchestration engine working!

### Phase 2: Agent UI (Session 5)
1. **WebSocket endpoint** for real-time chat
2. **Frontend chat component** (like Cursor panel)
3. **Context display** (show what KB queries returned)
4. **Workflow progress** tracker
5. **Test end-to-end** conversation flow

**Result**: "What's next?" conversational UI!

### Phase 3: Scene Generation (Session 6)
1. **Integrate KB queries** with scene prompts
2. **Test context-aware generation**
3. **Add to tournament system**
4. **Verify coherence** across scenes

**Result**: AI writes scenes with full context!

---

## Critical Questions for You

### Q1: The 8-Category Wizard - Where is it?
Desktop Claude mentioned:
- `category_templates.py` with 50+ fields (Characters, Plot, World, etc.)
- `setup_wizard_agent.py` with AI conversation
- WebSocket endpoint for wizard chat

**I only found**: Simple 5-phase wizard (wizard.py) that generates story bible

**Is the complex wizard**:
- A) In a different branch of writers-factory-core?
- B) Planned but not built yet?
- C) Somewhere else entirely?

### Q2: NotebookLM MCP Integration - Where is it?
You mentioned NotebookLM MCP server is "already configured in writers-factory"

**I only found**: Mock implementation in router.py

**Where is**:
- A) The actual MCP configuration?
- B) The NotebookLM client code?
- C) Example queries?

### Q3: Conversational Agent UI - Where is it?
The "like Cursor side panel" agent for ongoing conversation

**I only found**: Backend workflow engine (no UI)

**Is the UI**:
- A) In `/webapp/frontend-v2/`? (need to check)
- B) Already in writers-platform factory-frontend?
- C) Needs to be built?

### Q4: Character/Plot Markdown Files - Where?
You mentioned "characters.md, plot.md, worldbuilding.md"

**I only found**: JSON structure in manuscript.json

**Are these**:
- A) Exported from wizard (story_bible.md)?
- B) Created manually by user?
- C) Generated by a process I haven't found?

---

## Next Steps - What Should We Do?

### Option A: You Copy Core Directories Now ⚡ FASTEST
**You said**: "I can copy directories in two seconds"

**Do this**:
```bash
# Copy these 7 directories to writers-platform:
1. factory/core → backend/app/core
2. factory/workflows → backend/app/workflows
3. factory/knowledge → backend/app/services/knowledge
4. factory/agents → backend/app/services/agents
5. factory/wizard → backend/app/services/wizard
6. factory/storage → backend/app/storage
7. factory/tools → backend/app/tools
```

**Then I'll**:
- Fix imports (30 min)
- Integrate with FastAPI (2 hours)
- Test workflows (1 hour)

**Total**: ~4 hours to working backend!

### Option B: Answer Questions First 🤔 SAFER
- Tell me where the 8-category wizard is
- Show me the NotebookLM MCP config
- Clarify the UI situation
- **Then** copy directories with full understanding

### Option C: Let Me Explore More 🔍 THOROUGH
- I check `/webapp/frontend-v2/`
- I search for MCP configs
- I find the missing pieces
- **Then** create complete migration plan

---

## My Recommendation

**Do Option A + B Hybrid**:

1. **You copy the 7 core directories NOW** (2 seconds!)
2. **I'll adapt imports immediately** (30 min)
3. **While I work, you answer the 4 questions** (helps me integrate correctly)
4. **We iterate together** as issues come up

This gets us moving fast while clarifying architecture!

**Sound good?** 🚀

---

*Analysis Complete*
*Ready to execute migration when you are!*
