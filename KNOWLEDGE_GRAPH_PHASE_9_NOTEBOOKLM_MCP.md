# Knowledge Graph Phase 9: NotebookLM MCP Integration

**Status**: 📋 **PLANNED** (After Phase 8 completes)
**Created**: 2025-01-18
**Priority**: HIGH (User-requested feature for writer brainstorming workflow)
**Budget**: ~$150-200 (4-6 hours implementation)

---

## User's Use Case

> "This is basically for the initial beginning writer + later on when the writer is brainstorming and looking for more ideas about character + world building. For example, they could ask the agent to query one of notebooks in Notebook LM... The idea is for the writer to build up a bunch of information in notebooks before they start and part of the initial process. Is the agent inside the factory querying different notebooks through the notebook lmmcp server which is already configured in the writers factory, And start building the characters, the plot, the conflicts etc."

**Workflow**:
1. **Pre-writing Phase**: Writer curates research in NotebookLM notebooks (YouTube videos, articles, Mo Gawdat interviews, etc.)
2. **Brainstorming Phase**: Writer uses factory agents to query NotebookLM: "How would Mo Gawdat describe the world in 10 years?"
3. **Character Building**: Agent extracts character profiles, voice, backstory from NotebookLM research
4. **Knowledge Graph Integration**: Auto-extract entities from NotebookLM responses into knowledge graph
5. **Plot Development**: Build conflicts, themes, arcs from writer's curated research

---

## Current State Analysis

### ✅ What Exists

**Backend Configuration** (`backend/app/core/config/settings.yaml`):
```yaml
knowledge:
  notebooklm:
    enabled: true
  router:
    fallback_chain:
      - cognee
      - gemini_file_search
      - notebooklm
```

**Data Models** (`backend/app/core/storage/models/preferences_data.py`):
```python
class NotebookLMConfig(BaseModel):
    enabled: bool = False
    notebook_url: Optional[str] = None
    last_synced: Optional[str] = None
```

**Integration Points**:
- `voice_extractor.py`: Accepts `notebooklm_context` parameter
- `skill_generator.py`: Accepts `notebooklm_context` for story context
- `progress_upgrade_system.py`: Placeholder for NotebookLM context

**Export Endpoint** (`KNOWLEDGE_GRAPH_IMPLEMENTATION_PART2.md`):
```python
@router.get("/projects/{project_id}/graph/export/notebooklm")
async def export_to_notebooklm(project_id: str):
    """Export knowledge graph to NotebookLM markdown format"""
```

### ❌ What's Missing

1. **MCP Server Integration**: No client to communicate with NotebookLM MCP server
2. **Query Interface**: No API endpoint to query NotebookLM notebooks
3. **Auto-Extraction from Responses**: NotebookLM query results not fed into knowledge graph
4. **Agent Integration**: Factory agents can't automatically query NotebookLM during character/world building
5. **Multi-Notebook Support**: Can't configure multiple notebooks per project

---

## Implementation Plan

### Step 1: Install NotebookLM MCP Server (30 minutes)

**MCP Server**: https://github.com/PleasePrompto/notebooklm-mcp

```bash
# Clone the MCP server
cd /Users/gch2024/Documents/Documents\ -\ Mac\ Mini/writers-platform
git clone https://github.com/PleasePrompto/notebooklm-mcp external/notebooklm-mcp
cd external/notebooklm-mcp
npm install

# Test the server
npm start
```

**Configuration File** (`backend/mcp_config.json`):
```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "node",
      "args": [
        "/Users/gch2024/Documents/Documents - Mac Mini/writers-platform/external/notebooklm-mcp/index.js"
      ],
      "env": {
        "NOTEBOOKLM_API_KEY": "${NOTEBOOKLM_API_KEY}"
      }
    }
  }
}
```

**Environment Variables** (`.env`):
```bash
NOTEBOOKLM_API_KEY=your_api_key_here
```

---

### Step 2: Create MCP Client Service (1.5 hours)

**File**: `backend/app/services/notebooklm/mcp_client.py`

```python
"""
NotebookLM MCP Client
Communicates with NotebookLM MCP server to query notebooks.
"""
import asyncio
import json
from typing import List, Dict, Optional
from pydantic import BaseModel

class NotebookInfo(BaseModel):
    """Metadata about a NotebookLM notebook."""
    id: str
    title: str
    description: Optional[str] = None
    source_count: int = 0
    created_at: str
    updated_at: str

class NotebookQuery(BaseModel):
    """Query to send to NotebookLM."""
    notebook_id: str
    query: str
    max_sources: int = 5
    include_citations: bool = True

class NotebookResponse(BaseModel):
    """Response from NotebookLM."""
    answer: str
    sources: List[Dict[str, str]]  # [{"title": "...", "excerpt": "..."}]
    notebook_id: str
    query: str

class NotebookLMMCPClient:
    """Client for NotebookLM MCP server."""

    def __init__(self, mcp_config_path: str = "backend/mcp_config.json"):
        """Initialize MCP client with configuration."""
        self.config_path = mcp_config_path
        self.process = None
        self._load_config()

    def _load_config(self):
        """Load MCP server configuration."""
        with open(self.config_path) as f:
            config = json.load(f)
        self.server_config = config["mcpServers"]["notebooklm"]

    async def start_server(self):
        """Start the MCP server process."""
        if self.process:
            return

        self.process = await asyncio.create_subprocess_exec(
            self.server_config["command"],
            *self.server_config["args"],
            env={**self.server_config.get("env", {})},
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for server to be ready
        await asyncio.sleep(2)

    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None

    async def list_notebooks(self) -> List[NotebookInfo]:
        """
        List all available NotebookLM notebooks.

        Returns:
            List of notebook metadata
        """
        await self.start_server()

        # Send MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "notebooks/list",
            "params": {}
        }

        self.process.stdin.write(json.dumps(request).encode() + b"\n")
        await self.process.stdin.drain()

        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())

        return [NotebookInfo(**nb) for nb in response["result"]["notebooks"]]

    async def query_notebook(
        self,
        notebook_id: str,
        query: str,
        max_sources: int = 5
    ) -> NotebookResponse:
        """
        Query a NotebookLM notebook with a question.

        Args:
            notebook_id: ID of the notebook to query
            query: Question to ask (e.g., "How would Mo Gawdat describe AI in 2035?")
            max_sources: Maximum number of sources to return

        Returns:
            Answer with citations from notebook sources
        """
        await self.start_server()

        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "notebook/query",
            "params": {
                "notebook_id": notebook_id,
                "query": query,
                "max_sources": max_sources,
                "include_citations": True
            }
        }

        self.process.stdin.write(json.dumps(request).encode() + b"\n")
        await self.process.stdin.drain()

        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())

        return NotebookResponse(
            answer=response["result"]["answer"],
            sources=response["result"]["sources"],
            notebook_id=notebook_id,
            query=query
        )

    async def extract_character_profile(
        self,
        notebook_id: str,
        character_name: str
    ) -> Dict:
        """
        Extract a character profile from NotebookLM research.

        Args:
            notebook_id: ID of the notebook with character research
            character_name: Name of the character to extract

        Returns:
            Character profile with backstory, voice, arc, etc.
        """
        query = f"""
        If {character_name} were the main character in my novel, based on the
        research in this notebook, provide:

        1. **Backstory**: Their hypothetical background and formative experiences
        2. **Voice**: Their speaking style, vocabulary, and mannerisms
        3. **Core Beliefs**: Their philosophical views and values
        4. **Character Arc**: Potential journey and transformation
        5. **Conflicts**: Internal and external struggles they might face
        6. **Relationships**: How they might relate to other characters

        Use specific examples from the notebook sources.
        """

        response = await self.query_notebook(notebook_id, query, max_sources=10)

        return {
            "character_name": character_name,
            "profile": response.answer,
            "sources": response.sources,
            "notebook_id": notebook_id
        }

    async def extract_world_building(
        self,
        notebook_id: str,
        aspect: str
    ) -> Dict:
        """
        Extract world-building details from NotebookLM research.

        Args:
            notebook_id: ID of the notebook with world research
            aspect: Aspect to extract (e.g., "technology in 2035", "social dynamics")

        Returns:
            World-building details with citations
        """
        query = f"""
        Based on the research in this notebook, describe {aspect} for a
        fictional world set in the near future. Include:

        1. **Key Characteristics**: Defining features and trends
        2. **Concrete Examples**: Specific scenarios and manifestations
        3. **Implications**: How this affects characters and plot
        4. **Conflicts**: Tensions and dilemmas arising from this aspect

        Ground your response in the notebook sources.
        """

        response = await self.query_notebook(notebook_id, query, max_sources=8)

        return {
            "aspect": aspect,
            "details": response.answer,
            "sources": response.sources,
            "notebook_id": notebook_id
        }
```

---

### Step 3: Add API Endpoints (1 hour)

**File**: `backend/app/routes/notebooklm.py`

```python
"""
NotebookLM API endpoints for querying notebooks and extracting knowledge.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.services.notebooklm.mcp_client import (
    NotebookLMMCPClient,
    NotebookInfo,
    NotebookQuery,
    NotebookResponse
)
from app.services.knowledge_graph.graph_service import KnowledgeGraphService
from app.services.knowledge_graph.extractors.llm_extractor import LLMExtractor
from app.models.user import User
from app.models.project import Project
from app.api.deps import get_db, get_current_user

router = APIRouter(prefix="/api/notebooklm", tags=["notebooklm"])

# Global MCP client (singleton)
mcp_client = NotebookLMMCPClient()


@router.get("/notebooks", response_model=List[NotebookInfo])
async def list_notebooks(
    current_user: User = Depends(get_current_user)
):
    """
    List all NotebookLM notebooks accessible to the user.
    """
    notebooks = await mcp_client.list_notebooks()
    return notebooks


@router.post("/query", response_model=NotebookResponse)
async def query_notebook(
    query: NotebookQuery,
    current_user: User = Depends(get_current_user)
):
    """
    Query a NotebookLM notebook with a question.

    Example:
        POST /api/notebooklm/query
        {
            "notebook_id": "abc123",
            "query": "How would Mo Gawdat describe AI in 10 years?",
            "max_sources": 5
        }
    """
    response = await mcp_client.query_notebook(
        notebook_id=query.notebook_id,
        query=query.query,
        max_sources=query.max_sources
    )
    return response


@router.post("/extract-character/{project_id}")
async def extract_character_from_notebook(
    project_id: str,
    notebook_id: str,
    character_name: str,
    add_to_graph: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extract a character profile from NotebookLM and optionally add to knowledge graph.

    Args:
        project_id: UUID of the project
        notebook_id: NotebookLM notebook ID
        character_name: Name of the character to extract
        add_to_graph: Whether to add extracted entities to knowledge graph

    Returns:
        Character profile with entities and sources
    """
    # Verify project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Extract character profile
    profile = await mcp_client.extract_character_profile(
        notebook_id=notebook_id,
        character_name=character_name
    )

    # Optionally add to knowledge graph
    if add_to_graph:
        # Use LLM extractor to parse the profile into entities
        extractor = LLMExtractor(model="claude-sonnet-4.5")
        extraction = await extractor.extract_entities(
            content=profile["profile"],
            scene_id=f"notebooklm-{notebook_id}",
            project_id=project_id
        )

        # Add to knowledge graph
        kg = KnowledgeGraphService(project_id)
        for entity in extraction["entities"]:
            # Mark as from NotebookLM
            entity.source_scene_id = f"notebooklm:{notebook_id}"
            entity.properties["notebooklm_sources"] = profile["sources"]
            kg.add_entity(entity)

        for relationship in extraction["relationships"]:
            kg.add_relationship(relationship)

        # Save to database
        kg.save_to_db(db)

        profile["entities_added"] = len(extraction["entities"])
        profile["relationships_added"] = len(extraction["relationships"])

    return profile


@router.post("/extract-world-building/{project_id}")
async def extract_world_building_from_notebook(
    project_id: str,
    notebook_id: str,
    aspect: str,
    add_to_graph: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extract world-building details from NotebookLM and add to knowledge graph.

    Example:
        POST /api/notebooklm/extract-world-building/uuid-123
        {
            "notebook_id": "abc123",
            "aspect": "AI technology in 2035",
            "add_to_graph": true
        }
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Extract world-building details
    details = await mcp_client.extract_world_building(
        notebook_id=notebook_id,
        aspect=aspect
    )

    # Add to knowledge graph
    if add_to_graph:
        extractor = LLMExtractor(model="claude-sonnet-4.5")
        extraction = await extractor.extract_entities(
            content=details["details"],
            scene_id=f"notebooklm-{notebook_id}-{aspect}",
            project_id=project_id
        )

        kg = KnowledgeGraphService(project_id)
        for entity in extraction["entities"]:
            entity.source_scene_id = f"notebooklm:{notebook_id}"
            entity.properties["notebooklm_sources"] = details["sources"]
            entity.properties["aspect"] = aspect
            kg.add_entity(entity)

        for relationship in extraction["relationships"]:
            kg.add_relationship(relationship)

        kg.save_to_db(db)

        details["entities_added"] = len(extraction["entities"])

    return details


@router.get("/projects/{project_id}/notebooks")
async def get_project_notebooks(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get NotebookLM notebooks configured for this project.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Get notebook IDs from project preferences
    # (Assumes Project model has notebooklm_notebook_ids field)
    notebook_ids = getattr(project, "notebooklm_notebook_ids", [])

    if not notebook_ids:
        return []

    # Fetch metadata for each notebook
    all_notebooks = await mcp_client.list_notebooks()
    project_notebooks = [
        nb for nb in all_notebooks
        if nb.id in notebook_ids
    ]

    return project_notebooks
```

---

### Step 4: Update Project Model (30 minutes)

**File**: `backend/app/models/project.py`

Add NotebookLM configuration fields:

```python
class Project(Base):
    __tablename__ = "projects"

    # ... existing fields ...

    # NotebookLM integration
    notebooklm_notebook_ids: List[str] = Column(
        ARRAY(String),
        default=list,
        nullable=True,
        comment="List of NotebookLM notebook IDs for this project"
    )

    notebooklm_config: Dict = Column(
        JSON,
        default=dict,
        nullable=True,
        comment="NotebookLM configuration (auto_extract, sync_interval, etc.)"
    )
```

**Migration**: `backend/migrations/add_notebooklm_to_projects.sql`

```sql
-- Add NotebookLM fields to projects table
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS notebooklm_notebook_ids TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS notebooklm_config JSONB DEFAULT '{}';

-- Add comment
COMMENT ON COLUMN projects.notebooklm_notebook_ids IS
  'List of NotebookLM notebook IDs for research integration';
COMMENT ON COLUMN projects.notebooklm_config IS
  'NotebookLM configuration (auto_extract, sync_interval, etc.)';
```

---

### Step 5: Frontend UI (1.5 hours)

**File**: `factory-frontend/src/components/notebooklm/NotebookSelector.tsx`

```typescript
/**
 * NotebookLM Notebook Selector
 * Allows writers to configure NotebookLM notebooks for their project.
 */
import React, { useState, useEffect } from 'react';

interface Notebook {
  id: string;
  title: string;
  description?: string;
  source_count: number;
  created_at: string;
}

interface NotebookSelectorProps {
  projectId: string;
  selectedNotebookIds: string[];
  onSelectionChange: (notebookIds: string[]) => void;
}

export const NotebookSelector: React.FC<NotebookSelectorProps> = ({
  projectId,
  selectedNotebookIds,
  onSelectionChange,
}) => {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNotebooks = async () => {
      const response = await fetch('/api/notebooklm/notebooks', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      setNotebooks(data);
      setLoading(false);
    };
    fetchNotebooks();
  }, []);

  const toggleNotebook = (notebookId: string) => {
    const newSelection = selectedNotebookIds.includes(notebookId)
      ? selectedNotebookIds.filter(id => id !== notebookId)
      : [...selectedNotebookIds, notebookId];
    onSelectionChange(newSelection);
  };

  if (loading) {
    return <div className="text-gray-400">Loading notebooks...</div>;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white">NotebookLM Research</h3>
      <p className="text-sm text-gray-400">
        Select notebooks to use for character and world building research.
      </p>

      <div className="space-y-2">
        {notebooks.map(notebook => (
          <div
            key={notebook.id}
            className={`p-4 border rounded cursor-pointer transition ${
              selectedNotebookIds.includes(notebook.id)
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-gray-700 hover:border-gray-600'
            }`}
            onClick={() => toggleNotebook(notebook.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h4 className="font-medium text-white">{notebook.title}</h4>
                {notebook.description && (
                  <p className="text-sm text-gray-400 mt-1">{notebook.description}</p>
                )}
                <p className="text-xs text-gray-500 mt-2">
                  {notebook.source_count} sources
                </p>
              </div>
              <input
                type="checkbox"
                checked={selectedNotebookIds.includes(notebook.id)}
                onChange={() => {}}
                className="mt-1"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

**File**: `factory-frontend/src/components/notebooklm/CharacterExtractor.tsx`

```typescript
/**
 * Character Extractor from NotebookLM
 * Allows writers to extract character profiles from their research.
 */
import React, { useState } from 'react';

interface CharacterExtractorProps {
  projectId: string;
  notebookId: string;
}

export const CharacterExtractor: React.FC<CharacterExtractorProps> = ({
  projectId,
  notebookId,
}) => {
  const [characterName, setCharacterName] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleExtract = async () => {
    setExtracting(true);
    try {
      const response = await fetch(
        `/api/notebooklm/extract-character/${projectId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            notebook_id: notebookId,
            character_name: characterName,
            add_to_graph: true
          })
        }
      );
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Extraction failed:', error);
    } finally {
      setExtracting(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white">Extract Character</h3>

      <div className="space-y-2">
        <label className="block text-sm text-gray-400">
          Character Name (e.g., "Mo Gawdat-inspired AI expert")
        </label>
        <input
          type="text"
          value={characterName}
          onChange={(e) => setCharacterName(e.target.value)}
          className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded text-white"
          placeholder="Enter character name or description..."
        />
      </div>

      <button
        onClick={handleExtract}
        disabled={!characterName || extracting}
        className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {extracting ? 'Extracting...' : 'Extract Character Profile'}
      </button>

      {result && (
        <div className="mt-6 p-4 bg-gray-800 border border-gray-700 rounded">
          <h4 className="font-semibold text-white mb-2">Profile Extracted</h4>
          <div className="text-sm text-gray-300 whitespace-pre-wrap mb-4">
            {result.profile}
          </div>
          <div className="text-xs text-gray-500">
            ✅ {result.entities_added} entities added to knowledge graph
            <br />
            ✅ {result.relationships_added} relationships created
          </div>
        </div>
      )}
    </div>
  );
};
```

---

### Step 6: Integration with Knowledge Graph (30 minutes)

**Update**: `backend/app/services/knowledge_graph/graph_service.py`

Add method to mark NotebookLM-sourced entities:

```python
def add_entity_from_notebooklm(
    self,
    entity: Entity,
    notebook_id: str,
    sources: List[Dict[str, str]]
) -> bool:
    """
    Add entity extracted from NotebookLM query.

    Args:
        entity: Entity to add
        notebook_id: NotebookLM notebook ID
        sources: Citation sources from NotebookLM

    Returns:
        True if added successfully
    """
    # Mark as NotebookLM-sourced
    entity.source_scene_id = f"notebooklm:{notebook_id}"
    entity.properties["source_type"] = "notebooklm"
    entity.properties["notebooklm_notebook_id"] = notebook_id
    entity.properties["notebooklm_sources"] = sources
    entity.properties["verified"] = False  # Needs human verification

    return self.add_entity(entity)
```

**Visualization Update**: Show NotebookLM-sourced entities differently

In `GraphVisualization.tsx`, add special styling:

```typescript
const getNodeColor = (node: GraphNode) => {
  // NotebookLM-sourced entities are purple
  if (node.entity.properties.source_type === 'notebooklm') {
    return '#9333ea';  // Purple-600
  }

  // Regular entity type colors
  return ENTITY_TYPE_COLORS[node.type];
};
```

---

## Testing Plan

### Unit Tests

**File**: `backend/tests/test_notebooklm_mcp_client.py`

```python
import pytest
from app.services.notebooklm.mcp_client import NotebookLMMCPClient

@pytest.mark.asyncio
async def test_list_notebooks():
    client = NotebookLMMCPClient()
    notebooks = await client.list_notebooks()
    assert len(notebooks) > 0
    assert notebooks[0].id is not None

@pytest.mark.asyncio
async def test_query_notebook():
    client = NotebookLMMCPClient()
    response = await client.query_notebook(
        notebook_id="test-notebook-id",
        query="What are the key themes?",
        max_sources=3
    )
    assert response.answer is not None
    assert len(response.sources) <= 3

@pytest.mark.asyncio
async def test_extract_character():
    client = NotebookLMMCPClient()
    profile = await client.extract_character_profile(
        notebook_id="test-notebook-id",
        character_name="Test Character"
    )
    assert "backstory" in profile["profile"].lower()
    assert len(profile["sources"]) > 0
```

### Integration Tests

**File**: `backend/tests/test_notebooklm_integration.py`

```python
@pytest.mark.asyncio
async def test_extract_and_add_to_graph(db_session):
    """Test extracting from NotebookLM and adding to knowledge graph."""
    # Create test project
    project = Project(id=uuid4(), name="Test Project")
    db_session.add(project)
    db_session.commit()

    # Extract character
    response = await client.post(
        f"/api/notebooklm/extract-character/{project.id}",
        json={
            "notebook_id": "test-nb",
            "character_name": "Mo Gawdat",
            "add_to_graph": True
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["entities_added"] > 0

    # Verify entities in graph
    kg = KnowledgeGraphService(str(project.id))
    kg.load_from_db(db_session)
    entities = kg.query_entities()
    notebooklm_entities = [
        e for e in entities
        if e.properties.get("source_type") == "notebooklm"
    ]
    assert len(notebooklm_entities) > 0
```

---

## Deployment Checklist

- [ ] Install NotebookLM MCP server in `external/notebooklm-mcp/`
- [ ] Add `NOTEBOOKLM_API_KEY` to Railway environment variables
- [ ] Upload `mcp_config.json` to Railway
- [ ] Run migration: `add_notebooklm_to_projects.sql`
- [ ] Deploy backend with new endpoints
- [ ] Deploy frontend with NotebookSelector and CharacterExtractor components
- [ ] Test end-to-end workflow:
  1. Configure notebook for project
  2. Extract character profile
  3. Verify entities in knowledge graph
  4. Check visualization shows NotebookLM-sourced entities

---

## Cost Estimate

**Development Time**: 4-6 hours
- MCP server setup: 30 min
- MCP client service: 1.5 hours
- API endpoints: 1 hour
- Database migration: 30 min
- Frontend UI: 1.5 hours
- Integration: 30 min

**Claude Cloud Cost**: ~$150-200
- Backend implementation: ~$100
- Frontend implementation: ~$50
- Testing/debugging: ~$50

**API Costs** (Ongoing):
- NotebookLM queries: FREE (uses existing notebook sources)
- LLM extraction from responses: ~$0.01 per query (Claude Sonnet 4.5)

**Total Phase 9 Budget**: ~$150-200

---

## Success Criteria

Writers can:
1. ✅ Configure NotebookLM notebooks for their project
2. ✅ Query notebooks during brainstorming ("How would Mo Gawdat describe the world in 10 years?")
3. ✅ Extract character profiles from research with citations
4. ✅ Auto-extract entities from NotebookLM responses into knowledge graph
5. ✅ See NotebookLM-sourced entities in 3D visualization (purple color)
6. ✅ View sources and citations for each extracted entity
7. ✅ Use factory agents to query notebooks during character/world building

---

## User Workflow Example

**Before Writing** (Pre-writing Research):
1. Writer creates NotebookLM notebook: "AI in 2035"
2. Adds sources: Mo Gawdat YouTube videos, articles, interviews
3. Configures notebook in Writers Platform project settings

**During Brainstorming**:
1. Writer opens Character Extractor
2. Asks: "Extract character profile for 'Mo Gawdat-inspired AI ethicist'"
3. NotebookLM MCP queries notebook with prompt
4. Response includes backstory, voice, beliefs, arc (with citations)
5. Entities auto-extracted and added to knowledge graph:
   - Character: "Dr. Eli Thorne" (AI ethicist)
   - Concept: "Compassionate AI"
   - Theme: "Human-AI symbiosis"
   - Relationships: "Dr. Thorne advocates_for Compassionate AI"

**During Writing**:
1. Writer starts scene with Dr. Thorne
2. Knowledge graph shows related entities and relationships
3. Context panel shows NotebookLM sources for character voice
4. Writer crafts authentic dialogue grounded in research

---

## Next Steps After Phase 9

**Phase 10: Advanced NotebookLM Integration** (Optional, Future):
- Auto-sync: Periodically query NotebookLM for updates
- Multi-notebook queries: Combine research from multiple notebooks
- Source tracking: Link entities to specific YouTube timestamps/article sections
- Voice extraction: Use NotebookLM to extract character voice patterns
- Plot generation: Generate plot conflicts from research themes

---

**Status**: 📋 **READY FOR IMPLEMENTATION**

This document provides complete specification for NotebookLM MCP integration. Implementation should begin after Phase 8 (Testing & Deployment) completes.

---

*Created by: Desktop Claude Code*
*Date: 2025-01-18*
*Priority: HIGH (User-requested feature)*
