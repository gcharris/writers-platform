# The-Explants Project Structure Analysis
## Template for Writers Platform Projects

**Analyzed**: 2025-01-17
**Source**: https://github.com/gcharris/The-Explants
**Purpose**: Create project template for writers-platform

---

## Complete Project Structure

```
The Explants Series/
│
├── Reference_Library/              # ← THE KNOWLEDGE BASE (markdown files)
│   ├── Characters/
│   │   ├── Core_Cast/
│   │   │   ├── Mickey_Bardot_Enhanced_Identity.md
│   │   │   ├── Noni_Complete_Character_Profile.md
│   │   │   └── ... (detailed character profiles)
│   │   ├── Supporting_Cast/
│   │   ├── Antagonists/
│   │   └── Relationships/
│   │
│   ├── Story_Structure/
│   │   ├── Scene_Arc_Map.md            # Complete story arc
│   │   ├── The Explants Character Roster.md
│   │   └── Volume_2_Complete_Plot_Summary_CORRECTED2.md
│   │
│   ├── World_Building/
│   │   ├── Locations/
│   │   └── Technology/
│   │
│   ├── Themes_and_Philosophy/
│   └── Archive/
│
├── Volume 1/                        # ← THE MANUSCRIPT (actual prose)
│   ├── A FRONT_MATTER/
│   ├── ACT 1/
│   ├── ACT 2A/
│   ├── ACT 2B/
│   ├── ACT 3/
│   └── BACK_MATTER/
│
├── Volume 2/
├── Volume 3/
│
├── Production/                      # ← EXPORT/PUBLISHING
│   ├── Audiobook/
│   ├── Illustrations/
│   └── Screenplay/
│
├── Skills-Development/              # ← CLAUDE CODE SKILLS
├── AI_Systems/                      # ← AI CONFIGURATION
├── Enhancement-Prompts/             # ← PROMPT LIBRARY
└── Shared Resources/
```

---

## Key Insights: The "Novel Codebase"

### 1. Reference_Library = The Knowledge Base

**Structure**:
```
Reference_Library/
├── Characters/
│   ├── Core_Cast/        # Main protagonists (Mickey, Noni, etc.)
│   ├── Supporting_Cast/  # Secondary characters
│   ├── Antagonists/      # Villains and opposition
│   └── Relationships/    # Character dynamics
├── Story_Structure/      # Plot, arcs, beats
├── World_Building/       # Settings, tech, rules
├── Themes_and_Philosophy/# Deeper meaning
└── Archive/              # Historical versions
```

**Example Character Profile**: `Mickey_Bardot_Enhanced_Identity.md`
- 7,482 words of detailed character framework
- Sections: Pre-Quantum Identity, Transformation, Post-Quantum Capabilities, Relationships
- Tables with psychological traits, motivations, skills
- Designed for **AI agents** to maintain character consistency
- Quote: "This document outlines the core psychological framework... to ensure consistent and authentic character application by all agents"

**This IS the knowledge base you query for scene generation!**

### 2. Manuscript Structure = Act → Chapter → Scene

**Volume 1 Structure**:
```
ACT 1/
├── Chapter 01/
│   ├── Scene 01.md
│   ├── Scene 02.md
│   └── ...
├── Chapter 02/
└── ...
```

**Matches factory-core's manuscript structure.py exactly!**
```python
Manuscript
  └─ Acts[] (ACT 1, ACT 2A, ACT 2B, ACT 3)
      └─ Chapters[] (Chapter 01, 02, 03...)
          └─ Scenes[] (Scene 01, 02, 03...)
```

### 3. The Workflow (Now Clear!)

**Writer's Process**:
```
1. SETUP (One-time)
   ├─ User creates NotebookLM notebooks (external)
   │  ├─ Character 1 notebook
   │  ├─ Character 2 notebook
   │  ├─ World building notebook
   │  └─ Plot/themes notebook
   │
   ├─ Wizard asks for notebook URLs
   ├─ Agent queries NotebookLM
   └─ Generates Reference_Library/ structure
       ├─ Characters/Core_Cast/Mickey.md
       ├─ World_Building/Technology/Quantum.md
       └─ Story_Structure/Scene_Arc_Map.md

2. WRITING (Continuous)
   ├─ Writer: "Let's write ACT 1, Chapter 3, Scene 2"
   │
   ├─ Agent queries Reference_Library/ for context:
   │  ├─ Characters/Core_Cast/Mickey.md
   │  ├─ Characters/Core_Cast/Noni.md
   │  ├─ Story_Structure/Scene_Arc_Map.md (position in arc)
   │  ├─ World_Building/Locations/Vegas_Dojo.md
   │  └─ Previous scenes (Chapter 3, Scene 1)
   │
   ├─ Agent builds detailed prompt with ALL context
   ├─ AI generates scene
   ├─ Writer reviews/edits
   │
   └─ Agent saves to:
       ├─ Volume 1/ACT 1/Chapter 03/Scene 02.md
       └─ Updates Reference_Library/ if needed

3. ONGOING
   ├─ Each scene adds to the knowledge
   ├─ Reference_Library/ grows
   └─ Later scenes have MORE context
```

---

## Project Template for Writers Platform

### Template Structure to Create

```
backend/app/templates/project_template/
│
├── reference/                      # Knowledge base (markdown)
│   ├── characters/
│   │   ├── protagonists/
│   │   ├── supporting/
│   │   ├── antagonists/
│   │   └── relationships/
│   ├── story_structure/
│   │   ├── outline.md
│   │   ├── beats.md
│   │   └── arcs.md
│   ├── world_building/
│   │   ├── locations/
│   │   ├── technology/
│   │   ├── culture/
│   │   └── rules.md
│   ├── themes/
│   │   └── philosophy.md
│   └── voice_and_style/
│       └── guidelines.md
│
├── manuscript/                     # Actual prose
│   ├── volume-1/
│   │   ├── act-1/
│   │   │   ├── chapter-01/
│   │   │   │   ├── scene-01.md
│   │   │   │   └── scene-02.md
│   │   │   └── chapter-02/
│   │   ├── act-2/
│   │   └── act-3/
│   └── volume-2/
│
├── planning/                       # Outlines and planning
│   ├── outline.md
│   ├── beat_sheet.md
│   └── scene_list.md
│
├── output/                         # Generated content
│   └── exports/
│
└── metadata.json                   # Project info
```

### Database Schema (PostgreSQL)

**Replaces JSON storage with proper database**:

```sql
-- Projects table (already exists in writers-platform)
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    author VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Reference files (knowledge base)
CREATE TABLE reference_files (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    category VARCHAR(50),       -- 'characters', 'world_building', etc.
    subcategory VARCHAR(50),    -- 'protagonists', 'locations', etc.
    filename VARCHAR(255),
    content TEXT,               -- Markdown content
    metadata JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Manuscript structure (Acts/Chapters/Scenes)
CREATE TABLE manuscript_acts (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    volume INT DEFAULT 1,
    act_number INT,
    title VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP
);

CREATE TABLE manuscript_chapters (
    id UUID PRIMARY KEY,
    act_id UUID REFERENCES manuscript_acts(id) ON DELETE CASCADE,
    chapter_number INT,
    title VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP
);

CREATE TABLE manuscript_scenes (
    id UUID PRIMARY KEY,
    chapter_id UUID REFERENCES manuscript_chapters(id) ON DELETE CASCADE,
    scene_number INT,
    title VARCHAR(255),
    content TEXT,              -- The actual prose
    word_count INT,
    notes TEXT,
    metadata JSONB,           -- Generation context, prompts, etc.
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Integration with Factory-Core

### Knowledge Router Integration

**Current (factory-core router.py)**:
```python
# Queries go to Cognee (local graph) or NotebookLM
await knowledge_router.query("What is Mickey's relationship with Noni?")
```

**Writers-Platform Adaptation**:
```python
# Queries search reference_files table + NotebookLM
class KnowledgeRouter:
    async def query(self, query: str, project_id: UUID):
        # 1. Search reference_files (PostgreSQL full-text search)
        files = await db.query(
            "SELECT * FROM reference_files WHERE project_id = $1
             AND content @@ to_tsquery($2)",
            project_id, query
        )

        # 2. If analytical query and NotebookLM configured, query it
        if is_analytical(query) and has_notebooklm(project_id):
            notebook_result = await notebooklm.query(query)

        # 3. Combine results
        return QueryResult(
            answer=combine_results(files, notebook_result),
            references=[f.filename for f in files]
        )
```

### Scene Generation Workflow Integration

**Scene Generation with Knowledge Context**:
```python
# workflows/scene_operations/generation.py (from factory-core)
async def generate_scene(
    chapter_id: UUID,
    scene_number: int,
    outline: str
):
    # Step 1: Get chapter context
    chapter = await db.get_chapter(chapter_id)
    act = await db.get_act(chapter.act_id)
    project = await db.get_project(act.project_id)

    # Step 2: Query knowledge base
    context_queries = [
        "Characters in this scene",
        "Location and setting",
        "Previous scene summary",
        "Relevant plot threads",
        "Character emotional states"
    ]

    context = {}
    for query in context_queries:
        result = await knowledge_router.query(query, project.id)
        context[query] = result.answer

    # Step 3: Build detailed prompt
    prompt = f"""
    Scene: {act.title}, {chapter.title}, Scene {scene_number}
    Outline: {outline}

    Context:
    {format_context(context)}

    Write the scene with authentic voice and character consistency.
    """

    # Step 4: Generate via AI
    scene_text = await agent_pool.generate(prompt, model="claude-sonnet-4.5")

    # Step 5: Save to database
    scene = await db.create_scene(
        chapter_id=chapter_id,
        scene_number=scene_number,
        content=scene_text,
        metadata={
            "outline": outline,
            "context_used": context,
            "prompt": prompt,
            "model": "claude-sonnet-4.5"
        }
    )

    return scene
```

---

## NotebookLM Integration Strategy

### Setup Phase

**User Workflow**:
1. User creates NotebookLM notebooks externally (before Writers Platform)
2. During project setup wizard, system asks:
   - "Do you have NotebookLM notebooks prepared?"
   - If yes: "Provide notebook URLs:"
     - Character 1 notebook URL
     - Character 2 notebook URL
     - World building notebook URL
     - Plot/themes notebook URL
3. System stores URLs in project metadata

**Database Storage**:
```sql
-- Add to projects table metadata:
{
  "notebooklm": {
    "enabled": true,
    "notebooks": [
      {
        "name": "Main Character - Mickey",
        "url": "https://notebooklm.google.com/notebook/...",
        "category": "characters"
      },
      {
        "name": "World Building - Quantum Tech",
        "url": "https://notebooklm.google.com/notebook/...",
        "category": "world_building"
      }
    ]
  }
}
```

### Query Phase

**During wizard or scene generation**:
```python
# Query specific notebook for context
async def query_notebooklm_notebook(
    notebook_url: str,
    query: str
) -> str:
    # Use MCP server or API
    result = await notebooklm_client.query(
        notebook_id=extract_id(notebook_url),
        query=query
    )
    return result.answer
```

---

## Migration Steps

### Step 1: Copy Project Template from The-Explants

```bash
# Copy the reference library structure (user does this):
cp -r "/home/user/The-Explants/The Explants Series/Reference_Library" \
      /home/user/writers-platform/backend/app/templates/project_template/reference

# We'll use this as the TEMPLATE for new projects
```

### Step 2: Create Database Models (I do this)

```python
# backend/app/models/manuscript.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

class Act(Base):
    __tablename__ = "manuscript_acts"
    id = Column(UUID(as_uuid=True), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    volume = Column(Integer, default=1)
    act_number = Column(Integer)
    title = Column(String(255))
    # ... rest of fields

class Chapter(Base):
    __tablename__ = "manuscript_chapters"
    # ... similar structure

class Scene(Base):
    __tablename__ = "manuscript_scenes"
    # ... with content TEXT field
```

### Step 3: Adapt Factory-Core (I do this)

- Replace `factory/core/manuscript/storage.py` (JSON) with SQLAlchemy
- Keep `factory/core/manuscript/structure.py` (data models work as-is!)
- Update `factory/workflows/scene_operations/generation.py` to use PostgreSQL
- Adapt `factory/knowledge/router.py` to query `reference_files` table

### Step 4: Create Web UI (Session 5)

- Project file browser (shows reference/, manuscript/ structure)
- Markdown editor for reference files
- Scene editor with context panel
- Conversational agent chat (WebSocket)

---

## Summary: What We Learned

### The "8-Category Wizard" Mystery SOLVED

**It's NOT a wizard in factory-core** - it's the **Reference_Library structure**!

The "8 categories" are:
1. Characters/ (with sub-categories)
2. Story_Structure/
3. World_Building/
4. Themes_and_Philosophy/
5. Voice_and_Style/ (implied)
6. Planning/ (beats, outlines)
7. Relationships/ (character dynamics)
8. Archive/ (versions)

**The "wizard"** is:
- NotebookLM setup instructions (external)
- Queries to populate reference files
- Not a complex AI conversation (that's the ongoing agent!)

### The Ongoing Agent IS the Workflow Engine

**Factory-core's workflow_engine.py** = The orchestration system
- Executes scene generation workflows
- Queries knowledge (reference files)
- Builds context-rich prompts
- Coordinates AI models

**What's missing**: Web UI for conversation
- Need WebSocket chat interface
- Need to show workflow progress
- Need to display KB query results

### The Knowledge Base = PostgreSQL + NotebookLM

**Not Cognee** (too heavy for deployment)
- Store reference markdown files in PostgreSQL
- Use full-text search for queries
- Query NotebookLM for analytical questions
- Simple, fast, deployable!

---

## Next Actions

### You Do (2 seconds each):

1. **Copy factory-core directories**:
   ```bash
   cp -r ~/writers-factory-core/factory/core ~/writers-platform/backend/app/
   cp -r ~/writers-factory-core/factory/workflows ~/writers-platform/backend/app/
   cp -r ~/writers-factory-core/factory/knowledge ~/writers-platform/backend/app/services/
   cp -r ~/writers-factory-core/factory/agents ~/writers-platform/backend/app/services/
   cp -r ~/writers-factory-core/factory/wizard ~/writers-platform/backend/app/services/
   cp -r ~/writers-factory-core/factory/storage ~/writers-platform/backend/app/
   cp -r ~/writers-factory-core/factory/tools ~/writers-platform/backend/app/
   ```

2. **Copy project template**:
   ```bash
   cp -r "/home/user/The-Explants/The Explants Series/Reference_Library" \
         /home/user/writers-platform/backend/app/templates/project_template/reference
   ```

### I Do (4-6 hours):

1. Fix all imports
2. Create database models (Acts, Chapters, Scenes, ReferenceFiles)
3. Replace JSON storage with PostgreSQL
4. Create FastAPI endpoints
5. Test workflow execution

### Then We Build (Session 5):

- WebSocket conversational agent
- React chat UI
- Project file browser
- Markdown editor
- Context display

---

**Ready to copy those directories!** 🚀

*Analysis complete. Template structure documented. Migration strategy clear.*
