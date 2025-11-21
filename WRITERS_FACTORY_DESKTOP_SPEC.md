# Writers Factory Desktop App - Technical Specification

**Version:** 1.0
**Date:** November 21, 2025
**Status:** Ready for Implementation

---

## Executive Summary

Writers Factory Desktop is a **local-first, graph-centric desktop application** for novelists that combines AI-assisted writing with dynamic knowledge graph management. Think "VS Code for writers" - a powerful, extensible tool where the **knowledge graph is the source of truth** for your entire story.

### Why Desktop Instead of Web?

The existing web platform (writerscommunity.app / writersfactory.app) became too complex with:
- Two separate frontends (Community + Factory)
- Multi-user authentication
- Database migrations, CORS issues, deployment complexity
- Social features diluting the core writing experience

The desktop app returns to the **core vision**: Help writers write better novels with AI assistance and sophisticated story tracking.

### Core Philosophy

1. **Graph-Centric**: The knowledge graph IS the story state. Files are just serialization.
2. **Local-First**: All data on your machine. No accounts, no cloud dependency.
3. **Agent-Powered**: Multiple AI models compete to write your scenes.
4. **Research-Integrated**: NotebookLM/MCP feeds directly into your story graph.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        TAURI SHELL                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SVELTE FRONTEND                       │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │    │
│  │  │  Graph   │ │  Editor  │ │  Agent   │ │   MCP    │   │    │
│  │  │  Panel   │ │  (Monaco)│ │  Panel   │ │  Panel   │   │    │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │    │
│  └───────┼────────────┼────────────┼────────────┼──────────┘    │
│          │            │            │            │                │
│          └────────────┴─────┬──────┴────────────┘                │
│                             │ IPC                                 │
│  ┌──────────────────────────┴──────────────────────────────┐    │
│  │                   PYTHON BACKEND                         │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │            KNOWLEDGE GRAPH ENGINE                │    │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │    │    │
│  │  │  │NetworkX │ │ SQLite  │ │Extractor│           │    │    │
│  │  │  │(runtime)│ │(persist)│ │ (LLM/   │           │    │    │
│  │  │  │         │ │         │ │  NER)   │           │    │    │
│  │  │  └─────────┘ └─────────┘ └─────────┘           │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  │                                                          │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐          │    │
│  │  │   Agent    │ │    MCP     │ │   File     │          │    │
│  │  │Orchestrator│ │   Client   │ │  Parser    │          │    │
│  │  └────────────┘ └────────────┘ └────────────┘          │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LOCAL FILESYSTEM                            │
│  workspace/my-novel/                                             │
│  ├── graph.db              # SQLite - THE SOURCE OF TRUTH        │
│  ├── scenes/               # Markdown exports (generated)        │
│  ├── context/              # Character sheets, world building    │
│  ├── research/             # MCP-imported research               │
│  ├── checkpoints/          # Graph version snapshots             │
│  ├── agents.yaml           # Agent registry config               │
│  └── project.yaml          # Project metadata                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Desktop Shell | **Tauri** | Smaller than Electron, Rust-based security, native OS integration |
| Frontend UI | **Svelte** | Lighter than React, simpler state management, faster |
| Text Editor | **Monaco Editor** | VS Code's editor, excellent Markdown support |
| Graph Visualization | **D3.js** | Industry standard, highly customizable |
| Backend | **Python 3.11+** | Existing code compatibility, AI library ecosystem |
| Graph Engine | **NetworkX** | Already implemented, proven in current project |
| Local Database | **SQLite** | Zero configuration, portable, fast |
| AI Integration | **Anthropic/OpenAI/Ollama** | Multiple provider support |
| File Parsing | **python-docx, PyPDF2** | Already implemented in current project |

---

## Core Modules

### 1. Knowledge Graph Engine (THE HEART)

**Source:** Copy from existing project

**Location in existing project:**
```
backend/app/services/knowledge_graph/
├── graph_service.py      # 558 lines - NetworkX operations
├── models.py             # 194 lines - Entity/Relationship models
├── extractors/
│   ├── llm_extractor.py  # Claude-based entity extraction
│   └── ner_extractor.py  # spaCy-based fast extraction
```

**Capabilities Already Implemented:**

| Feature | Method | Description |
|---------|--------|-------------|
| Entity CRUD | `add_entity()`, `get_entity()`, `update_entity()`, `delete_entity()` | Full entity management |
| Fuzzy Search | `find_entity_by_name(fuzzy=True)` | Find entities by name/alias |
| Filtered Queries | `query_entities(type, min_mentions, verified_only)` | Complex entity filtering |
| Relationship CRUD | `add_relationship()`, `get_relationships()`, `delete_relationship()` | Full relationship management |
| Path Finding | `find_path(source, target)` | Shortest path between entities |
| Centrality | `get_central_entities(top_n)` | PageRank-based importance |
| Communities | `get_communities()` | Louvain community detection |
| Entity Stats | `get_entity_stats(id)` | Degree, betweenness, closeness |
| Serialization | `to_json()`, `from_json()` | Full graph persistence |
| Visualization Export | `export_for_visualization()` | D3.js compatible format |
| GraphML Export | `export_graphml()` | Gephi/Cytoscape compatible |

**Entity Types (from models.py):**
- CHARACTER
- LOCATION
- OBJECT
- CONCEPT
- EVENT
- ORGANIZATION
- THEME

**Relationship Types (30+ defined):**
- Character: KNOWS, LOVES, FEARS, CONFLICTS_WITH, LEADS, FOLLOWS, WORKS_WITH
- Spatial: LOCATED_IN, TRAVELS_TO, OWNS, RESIDES_IN
- Temporal: OCCURS_BEFORE, OCCURS_DURING, OCCURS_AFTER, CAUSES, RESULTS_IN
- Conceptual: REPRESENTS, SYMBOLIZES, OPPOSES, SUPPORTS, RELATES_TO
- Events: PARTICIPATES_IN, WITNESSES, TRIGGERS
- Organizational: MEMBER_OF, FOUNDED_BY, CONTROLS

**Entity Data Model:**
```python
@dataclass
class Entity:
    id: str
    name: str
    entity_type: EntityType
    description: str = ""
    aliases: List[str] = []           # Alternative names
    attributes: Dict[str, Any] = {}   # Custom attributes
    first_appearance: str = None      # Scene ID
    appearances: List[str] = []       # All scene IDs
    mentions: int = 0                 # Count
    confidence: float = 1.0           # Extraction confidence
    verified: bool = False            # Human-verified flag
```

**Relationship Data Model:**
```python
@dataclass
class Relationship:
    source_id: str
    target_id: str
    relation_type: RelationType
    description: str = ""
    context: List[str] = []           # Textual evidence
    scenes: List[str] = []            # Where relationship appears
    strength: float = 1.0             # 0-1 scale
    valence: float = 0.0              # -1 (negative) to +1 (positive)
    start_scene: str = None           # When relationship began
    end_scene: str = None             # When relationship ended
    confidence: float = 1.0
    verified: bool = False
```

### 2. File Parser

**Source:** Copy from existing project

**Location:** `backend/app/services/file_parser.py` (346 lines)

**Capabilities:**
- Parse DOCX files (python-docx)
- Parse PDF files (PyPDF2)
- Parse TXT/MD files (charset detection)
- Auto-detect chapters via regex patterns:
  - "Chapter 1", "CHAPTER 1", "Ch. 1"
  - "Part 1", "PART 1"
  - Numbered headings ("1.")
- Split chapters into scenes by:
  - Scene markers (###, ---, ***)
  - Large paragraph breaks (3+ newlines)
  - Word count limits (~1000 words)

**Output Structure:**
```python
{
    'title': str,
    'content': str,           # Full text
    'word_count': int,
    'chapters': [
        {
            'number': int,
            'title': str,
            'content': str,
            'start_para': int
        }
    ],
    'metadata': {
        'source': 'docx|pdf|txt',
        'page_count': int,    # PDF only
        'paragraph_count': int
    }
}
```

### 3. Agent Orchestrator (NEW - TO BUILD)

**Purpose:** Manage multiple AI agents for scene generation, comparison, and tournament-style selection.

**Configuration (agents.yaml):**
```yaml
agents:
  # Free/Local Tier
  local:
    - name: "Ollama Llama 3.2"
      provider: ollama
      model: llama3.2
      endpoint: http://localhost:11434
      cost_per_1k_tokens: 0.0
      capabilities: [drafting, brainstorming]

  # Paid Tier
  premium:
    - name: "Claude Sonnet"
      provider: anthropic
      model: claude-sonnet-4-20250514
      api_key_env: ANTHROPIC_API_KEY
      cost_per_1k_tokens: 0.003
      capabilities: [drafting, analysis, tournament]

    - name: "GPT-4o"
      provider: openai
      model: gpt-4o
      api_key_env: OPENAI_API_KEY
      cost_per_1k_tokens: 0.005
      capabilities: [drafting, analysis, tournament]

  # Experimental
  experimental:
    - name: "DeepSeek"
      provider: custom
      endpoint: https://api.deepseek.com/v1
      api_key_env: DEEPSEEK_API_KEY
      cost_per_1k_tokens: 0.0001
      capabilities: [drafting]

settings:
  default_drafting_agent: "Ollama Llama 3.2"
  tournament_agents: ["Claude Sonnet", "GPT-4o", "Ollama Llama 3.2"]
  cost_warning_threshold: 0.50  # Warn if single operation exceeds this
  fallback_chain: ["Ollama Llama 3.2"]  # If paid APIs fail
```

**Core Functions:**

```python
class AgentOrchestrator:
    def __init__(self, config_path: str, graph: KnowledgeGraphService):
        self.agents = load_agents(config_path)
        self.graph = graph
        self.cost_tracker = CostTracker()

    def build_context_from_graph(self, scene_id: str) -> str:
        """Build rich context from knowledge graph state."""
        scene = self.graph.get_scene(scene_id)

        # Get all relevant context
        characters = self.graph.query_entities(type=EntityType.CHARACTER)
        active_characters = [c for c in characters if scene_id in c.appearances]

        character_states = []
        for char in active_characters:
            relationships = self.graph.get_relationships(source_id=char.id)
            emotional_valence = self._calculate_emotional_state(char, scene_id)
            character_states.append({
                'name': char.name,
                'description': char.description,
                'current_emotion': emotional_valence,
                'relationships': relationships
            })

        unresolved_threads = self._get_unresolved_threads(scene_id)
        prior_events = self._get_prior_events(scene_id)
        location = self._get_scene_location(scene_id)

        return self._format_context(
            characters=character_states,
            threads=unresolved_threads,
            events=prior_events,
            location=location,
            scene_scaffold=scene.scaffold
        )

    def generate_draft(self, scene_id: str, agent_name: str) -> Draft:
        """Generate a single draft using specified agent."""
        context = self.build_context_from_graph(scene_id)
        agent = self.agents[agent_name]

        draft = agent.generate(context)
        self.cost_tracker.record(agent_name, draft.tokens_used)

        return draft

    def run_tournament(self, scene_id: str, agents: List[str] = None) -> TournamentResult:
        """Run multiple agents and compare results."""
        agents = agents or self.config.tournament_agents
        context = self.build_context_from_graph(scene_id)

        # Generate drafts in parallel
        drafts = {}
        for agent_name in agents:
            drafts[agent_name] = self.agents[agent_name].generate(context)

        # Score each draft against graph consistency
        scores = {}
        for agent_name, draft in drafts.items():
            scores[agent_name] = self._score_draft(draft, scene_id)

        return TournamentResult(
            drafts=drafts,
            scores=scores,
            recommended=max(scores, key=scores.get),
            cost=self.cost_tracker.session_total()
        )

    def _score_draft(self, draft: Draft, scene_id: str) -> float:
        """Score draft against knowledge graph for consistency."""
        score = 1.0

        # Check character consistency
        mentioned_characters = self._extract_character_mentions(draft.content)
        for char_name in mentioned_characters:
            char = self.graph.find_entity_by_name(char_name)
            if char:
                # Character exists - check if behavior matches
                expected_state = self._get_character_state(char, scene_id)
                if not self._behavior_matches(draft, char, expected_state):
                    score -= 0.1
            else:
                # Unknown character mentioned
                score -= 0.05

        # Check timeline consistency
        events_mentioned = self._extract_events(draft.content)
        for event in events_mentioned:
            if self._contradicts_timeline(event, scene_id):
                score -= 0.2

        # Check location consistency
        if self._location_mismatch(draft, scene_id):
            score -= 0.1

        return max(0, score)
```

### 4. Graph Version Control (NEW - TO BUILD)

**Purpose:** Checkpoint graph state, enable "what if" scenarios, rollback changes.

```python
class GraphVersionControl:
    def __init__(self, graph: KnowledgeGraphService, storage_path: str):
        self.graph = graph
        self.checkpoints_dir = Path(storage_path) / "checkpoints"
        self.checkpoints_dir.mkdir(exist_ok=True)

    def create_checkpoint(self, label: str, description: str = "") -> str:
        """Save current graph state as a checkpoint."""
        checkpoint_id = f"{datetime.now().isoformat()}_{slugify(label)}"

        checkpoint = {
            'id': checkpoint_id,
            'label': label,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'graph_data': self.graph.to_json(),
            'stats': self.graph.get_stats()
        }

        checkpoint_path = self.checkpoints_dir / f"{checkpoint_id}.json"
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2))

        return checkpoint_id

    def list_checkpoints(self) -> List[Dict]:
        """List all available checkpoints."""
        checkpoints = []
        for path in self.checkpoints_dir.glob("*.json"):
            data = json.loads(path.read_text())
            checkpoints.append({
                'id': data['id'],
                'label': data['label'],
                'description': data['description'],
                'created_at': data['created_at'],
                'stats': data['stats']
            })
        return sorted(checkpoints, key=lambda x: x['created_at'], reverse=True)

    def diff_checkpoints(self, checkpoint_a: str, checkpoint_b: str) -> Dict:
        """Show differences between two checkpoints."""
        graph_a = self._load_checkpoint_graph(checkpoint_a)
        graph_b = self._load_checkpoint_graph(checkpoint_b)

        entities_a = set(graph_a._entity_index.keys())
        entities_b = set(graph_b._entity_index.keys())

        return {
            'entities_added': list(entities_b - entities_a),
            'entities_removed': list(entities_a - entities_b),
            'entities_modified': self._find_modified_entities(graph_a, graph_b),
            'relationships_added': self._find_added_relationships(graph_a, graph_b),
            'relationships_removed': self._find_removed_relationships(graph_a, graph_b)
        }

    def rollback_to(self, checkpoint_id: str) -> bool:
        """Restore graph to checkpoint state."""
        checkpoint_path = self.checkpoints_dir / f"{checkpoint_id}.json"
        if not checkpoint_path.exists():
            return False

        data = json.loads(checkpoint_path.read_text())
        restored_graph = KnowledgeGraphService.from_json(data['graph_data'])

        # Replace current graph
        self.graph.graph = restored_graph.graph
        self.graph._entity_index = restored_graph._entity_index
        self.graph._relationship_index = restored_graph._relationship_index
        self.graph.metadata = restored_graph.metadata

        return True
```

### 5. Story Consistency Checker (NEW - TO BUILD)

**Purpose:** Automated detection of story problems using the knowledge graph.

```python
class StoryConsistencyChecker:
    def __init__(self, graph: KnowledgeGraphService):
        self.graph = graph

    def run_full_check(self) -> List[Issue]:
        """Run all consistency checks and return issues."""
        issues = []
        issues.extend(self.check_dropped_threads())
        issues.extend(self.check_character_absences())
        issues.extend(self.check_timeline_errors())
        issues.extend(self.check_flat_arcs())
        issues.extend(self.check_orphaned_entities())
        return sorted(issues, key=lambda x: x.severity, reverse=True)

    def check_dropped_threads(self, threshold_scenes: int = 10) -> List[Issue]:
        """Find plot threads that were introduced but not resolved."""
        issues = []
        threads = self.graph.query_entities(entity_type=EntityType.EVENT)

        for thread in threads:
            if thread.attributes.get('thread_type') == 'plot_thread':
                if not thread.attributes.get('resolved', False):
                    scenes_since = self._scenes_since_introduction(thread)
                    if scenes_since > threshold_scenes:
                        issues.append(Issue(
                            type='dropped_thread',
                            severity='warning',
                            entity_id=thread.id,
                            message=f"Plot thread '{thread.name}' unresolved for {scenes_since} scenes",
                            suggestion=f"Consider resolving or referencing in upcoming scene"
                        ))
        return issues

    def check_character_absences(self, threshold_scenes: int = 8) -> List[Issue]:
        """Find characters who haven't appeared in many scenes."""
        issues = []
        characters = self.graph.query_entities(entity_type=EntityType.CHARACTER)
        current_scene_seq = self._get_current_scene_sequence()

        for char in characters:
            if char.mentions > 3:  # Only check recurring characters
                last_appearance = self._get_last_appearance_sequence(char)
                gap = current_scene_seq - last_appearance

                if gap > threshold_scenes:
                    issues.append(Issue(
                        type='character_absence',
                        severity='info',
                        entity_id=char.id,
                        message=f"'{char.name}' hasn't appeared in {gap} scenes",
                        suggestion="Consider a reference, mention, or brief appearance"
                    ))
        return issues

    def check_timeline_errors(self) -> List[Issue]:
        """Find events that contradict the timeline."""
        issues = []
        events = self.graph.query_entities(entity_type=EntityType.EVENT)

        for event in events:
            dependencies = self.graph.get_relationships(
                target_id=event.id,
                relation_type=RelationType.CAUSES
            )

            for dep in dependencies:
                cause_event = self.graph.get_entity(dep.source_id)
                if cause_event:
                    cause_seq = self._get_event_sequence(cause_event)
                    effect_seq = self._get_event_sequence(event)

                    if cause_seq > effect_seq:
                        issues.append(Issue(
                            type='timeline_error',
                            severity='error',
                            entity_id=event.id,
                            message=f"'{event.name}' occurs before its cause '{cause_event.name}'",
                            suggestion="Reorder scenes or revise causality"
                        ))
        return issues

    def check_flat_arcs(self, min_scenes: int = 5) -> List[Issue]:
        """Find characters with stagnant emotional arcs."""
        issues = []
        characters = self.graph.query_entities(entity_type=EntityType.CHARACTER)

        for char in characters:
            if len(char.appearances) >= min_scenes:
                emotional_trajectory = self._calculate_emotional_trajectory(char)

                if self._is_flat(emotional_trajectory):
                    issues.append(Issue(
                        type='flat_arc',
                        severity='warning',
                        entity_id=char.id,
                        message=f"'{char.name}'s emotional state hasn't changed significantly",
                        suggestion="Consider giving character a challenge, revelation, or growth moment"
                    ))
        return issues

    def check_orphaned_entities(self) -> List[Issue]:
        """Find entities with no relationships."""
        issues = []

        for entity in self.graph._entity_index.values():
            incoming = self.graph.get_relationships(target_id=entity.id)
            outgoing = self.graph.get_relationships(source_id=entity.id)

            if len(incoming) == 0 and len(outgoing) == 0:
                if entity.mentions > 1:  # Mentioned multiple times but no connections
                    issues.append(Issue(
                        type='orphaned_entity',
                        severity='info',
                        entity_id=entity.id,
                        message=f"'{entity.name}' has no relationships to other entities",
                        suggestion="Consider connecting to characters, locations, or events"
                    ))
        return issues

@dataclass
class Issue:
    type: str           # dropped_thread, character_absence, timeline_error, etc.
    severity: str       # error, warning, info
    entity_id: str
    message: str
    suggestion: str
```

### 6. MCP/NotebookLM Client (NEW - TO BUILD)

**Purpose:** Import research from NotebookLM into the knowledge graph.

```python
class MCPClient:
    def __init__(self, config: Dict):
        self.notebooks = config.get('notebooks', [])
        self.sync_mode = config.get('sync_mode', 'manual')  # manual, periodic, realtime
        self.last_sync = {}

    def fetch_notebook_content(self, notebook_url: str) -> List[ResearchEntry]:
        """Fetch content from a NotebookLM notebook via MCP server."""
        # MCP server endpoint
        mcp_endpoint = self._get_mcp_endpoint(notebook_url)

        response = requests.get(
            mcp_endpoint,
            headers=self._auth_headers()
        )

        entries = []
        for item in response.json()['entries']:
            entries.append(ResearchEntry(
                id=item['id'],
                title=item['title'],
                content=item['content'],
                source=notebook_url,
                created_at=item['created_at'],
                tags=item.get('tags', [])
            ))

        return entries

    def ingest_to_graph(self, entries: List[ResearchEntry], graph: KnowledgeGraphService):
        """Parse research entries and add to knowledge graph."""
        for entry in entries:
            # Extract entities from research content
            extracted = self._extract_entities_from_research(entry)

            for entity_data in extracted['entities']:
                entity = Entity(
                    id=f"research_{entry.id}_{entity_data['name']}",
                    name=entity_data['name'],
                    entity_type=EntityType(entity_data['type']),
                    description=entity_data['description'],
                    attributes={
                        'source': 'notebooklm',
                        'research_entry_id': entry.id,
                        'notebook_url': entry.source,
                        'imported_at': datetime.now().isoformat(),
                        'confidence': 'human_researched'
                    }
                )

                # Check for existing entity to merge
                existing = graph.find_entity_by_name(entity.name, fuzzy=True)
                if existing:
                    # Merge research into existing entity
                    graph.update_entity(existing.id,
                        description=f"{existing.description}\n\n[Research]: {entity.description}",
                        attributes={**existing.attributes, **entity.attributes}
                    )
                else:
                    graph.add_entity(entity)

            # Add relationships
            for rel_data in extracted['relationships']:
                # ... similar relationship creation
                pass

    def setup_periodic_sync(self, interval_minutes: int = 30):
        """Start background sync task."""
        async def sync_loop():
            while True:
                for notebook in self.notebooks:
                    try:
                        entries = self.fetch_notebook_content(notebook['url'])
                        new_entries = self._filter_new_entries(entries, notebook['url'])
                        if new_entries:
                            self.ingest_to_graph(new_entries, self.graph)
                            self._notify_ui(f"{len(new_entries)} new research items imported")
                    except Exception as e:
                        self._notify_ui(f"Sync error: {e}", level='error')

                await asyncio.sleep(interval_minutes * 60)

        asyncio.create_task(sync_loop())

@dataclass
class ResearchEntry:
    id: str
    title: str
    content: str
    source: str
    created_at: str
    tags: List[str]
```

---

## Directory Structure

```
writers-factory-desktop/
├── README.md
├── package.json                    # Tauri/Node dependencies
├── tauri.conf.json                 # Tauri configuration
├── src-tauri/                      # Rust Tauri backend
│   ├── Cargo.toml
│   └── src/
│       └── main.rs                 # Tauri entry point, Python spawning
│
├── frontend/                       # Svelte frontend
│   ├── package.json
│   ├── svelte.config.js
│   ├── src/
│   │   ├── App.svelte
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── GraphPanel.svelte
│   │   │   │   ├── EditorPanel.svelte
│   │   │   │   ├── AgentPanel.svelte
│   │   │   │   ├── MCPPanel.svelte
│   │   │   │   ├── FileTree.svelte
│   │   │   │   └── StoryHealth.svelte
│   │   │   ├── stores/
│   │   │   │   ├── graph.ts
│   │   │   │   ├── project.ts
│   │   │   │   └── agents.ts
│   │   │   └── utils/
│   │   │       ├── ipc.ts          # Tauri IPC helpers
│   │   │       └── graphViz.ts     # D3.js graph rendering
│   │   └── routes/
│   │       └── +page.svelte
│   └── static/
│
├── backend/                        # Python backend
│   ├── requirements.txt
│   ├── main.py                     # Entry point for Tauri to spawn
│   ├── api/
│   │   ├── __init__.py
│   │   ├── graph_api.py            # Graph operations exposed to frontend
│   │   ├── agent_api.py            # Agent operations
│   │   ├── file_api.py             # File operations
│   │   └── mcp_api.py              # MCP operations
│   │
│   ├── graph/                      # [COPY FROM EXISTING PROJECT]
│   │   ├── __init__.py
│   │   ├── graph_service.py        # Core NetworkX operations
│   │   ├── models.py               # Entity, Relationship, GraphMetadata
│   │   ├── version_control.py      # [NEW] Graph checkpointing
│   │   ├── consistency_checker.py  # [NEW] Story health checks
│   │   └── extractors/
│   │       ├── __init__.py
│   │       ├── llm_extractor.py    # [COPY] Claude-based extraction
│   │       └── ner_extractor.py    # [COPY] spaCy-based extraction
│   │
│   ├── agents/                     # [NEW - TO BUILD]
│   │   ├── __init__.py
│   │   ├── registry.py             # Agent configuration management
│   │   ├── orchestrator.py         # Tournament and generation logic
│   │   ├── prompt_builder.py       # Graph -> context -> prompt
│   │   └── providers/
│   │       ├── anthropic.py
│   │       ├── openai.py
│   │       ├── ollama.py
│   │       └── custom.py
│   │
│   ├── parsers/                    # [COPY FROM EXISTING PROJECT]
│   │   ├── __init__.py
│   │   └── file_parser.py          # DOCX/PDF/TXT parsing
│   │
│   ├── mcp/                        # [NEW - TO BUILD]
│   │   ├── __init__.py
│   │   ├── client.py               # NotebookLM MCP client
│   │   └── research_parser.py      # Research -> graph entities
│   │
│   └── storage/
│       ├── __init__.py
│       ├── graph_store.py          # SQLite persistence
│       └── project_store.py        # Project metadata management
│
├── templates/                      # Project templates
│   ├── novel/
│   │   ├── project.yaml
│   │   ├── agents.yaml
│   │   └── context/
│   │       ├── characters.md
│   │       └── world.md
│   └── screenplay/
│       └── ...
│
└── docs/
    ├── ARCHITECTURE.md
    ├── AGENT_DEVELOPMENT.md
    └── MCP_INTEGRATION.md
```

---

## Files to Copy from Existing Project

### MUST COPY (Directly Portable)

| Source File | Destination | Lines | Notes |
|-------------|-------------|-------|-------|
| `backend/app/services/knowledge_graph/graph_service.py` | `backend/graph/graph_service.py` | 558 | Core graph engine - copy exactly |
| `backend/app/services/knowledge_graph/models.py` | `backend/graph/models.py` | 194 | Entity/Relationship models - copy exactly |
| `backend/app/services/knowledge_graph/extractors/llm_extractor.py` | `backend/graph/extractors/llm_extractor.py` | ~200 | LLM extraction - copy exactly |
| `backend/app/services/knowledge_graph/extractors/ner_extractor.py` | `backend/graph/extractors/ner_extractor.py` | ~150 | NER extraction - copy exactly |
| `backend/app/services/file_parser.py` | `backend/parsers/file_parser.py` | 346 | File parsing - copy exactly |

### REFERENCE (Study patterns, adapt for desktop)

| Source File | Purpose | Useful Sections |
|-------------|---------|-----------------|
| `backend/app/routes/knowledge_graph.py` | API patterns | Lines 115-156 (get_graph), 223-278 (list_entities), 543-591 (find_path) |
| `backend/app/routes/copilot.py` | AI integration patterns | Prompt building, context assembly |
| `backend/app/models/scene.py` | Scene data model | Structure for scene metadata |
| `backend/app/models/manuscript.py` | Act/Chapter/Scene hierarchy | Document organization patterns |

### DO NOT COPY

- All authentication code (auth.py, security.py)
- All web framework code (FastAPI routes, middleware)
- All database migrations
- All React/TypeScript frontend code
- Community features (social, ratings, comments)
- Deployment configurations

---

## Implementation Phases

### Phase 1: Port Graph Engine (Week 1)

**Goal:** Working knowledge graph with file import and visualization

**Tasks:**
1. Set up Tauri + Svelte project structure
2. Set up Python backend with IPC to Tauri
3. Copy graph engine files (graph_service.py, models.py, extractors/)
4. Copy file_parser.py
5. Adapt storage from PostgreSQL to SQLite
6. Create basic D3.js graph visualization
7. Implement file import → parse → extract → display flow

**Deliverables:**
- Import a novel (DOCX/PDF/TXT)
- See characters, locations, relationships in graph
- Click nodes to see entity details
- Export graph as GraphML

**Acceptance Criteria:**
```
[ ] Can import 50,000+ word novel
[ ] Correctly identifies 10+ characters
[ ] Extracts 20+ relationships
[ ] Graph renders in < 2 seconds
[ ] Can query: "Show all characters"
[ ] Can query: "Find path between Alice and Bob"
```

### Phase 2: Agent Orchestration (Week 2-3)

**Goal:** Multiple AI agents generating scene drafts with graph context

**Tasks:**
1. Build agent registry (YAML config parser)
2. Implement provider adapters (Anthropic, OpenAI, Ollama)
3. Build prompt_builder.py (graph → context → prompt)
4. Build orchestrator.py (single draft, tournament mode)
5. Create Agent Panel UI
6. Implement cost tracking
7. Add draft scoring against graph consistency

**Deliverables:**
- Configure multiple AI agents
- Generate scene with one agent
- Run tournament with 3 agents
- See cost per operation
- Score drafts for consistency

**Acceptance Criteria:**
```
[ ] Can configure 3+ agents
[ ] Single draft generates in < 30 seconds
[ ] Tournament completes in < 2 minutes
[ ] Cost tracking accurate to $0.01
[ ] Consistency scoring identifies contradictions
```

### Phase 3: Graph Versioning & Story Health (Week 4)

**Goal:** Checkpoint graph state, detect story problems automatically

**Tasks:**
1. Build version_control.py (checkpoints, diff, rollback)
2. Build consistency_checker.py (all check functions)
3. Create Story Health panel UI
4. Implement timeline slider (view graph at any point)
5. Add "what if" scenario support

**Deliverables:**
- Create/restore checkpoints
- See diff between versions
- Story health dashboard with issues
- Click issue → highlight in graph
- Timeline slider showing graph evolution

**Acceptance Criteria:**
```
[ ] Can create checkpoint in < 1 second
[ ] Can rollback in < 2 seconds
[ ] Detects dropped threads (>10 scenes)
[ ] Detects character absences (>8 scenes)
[ ] Detects timeline contradictions
[ ] Detects flat character arcs
```

### Phase 4: MCP Integration & Polish (Week 5-6)

**Goal:** Import research from NotebookLM, full writing workflow

**Tasks:**
1. Build MCP client (NotebookLM REST integration)
2. Build research_parser.py (research → graph entities)
3. Create MCP Panel UI
4. Implement Monaco editor integration
5. Build scene → graph sync (edits update graph)
6. Implement export engine (graph → DOCX/PDF)
7. Polish UI, fix bugs, optimize performance

**Deliverables:**
- Connect to NotebookLM
- Import research → see in graph
- Edit scenes in Monaco
- Edits auto-update graph entities
- Export compiled manuscript

**Acceptance Criteria:**
```
[ ] Can connect to NotebookLM notebook
[ ] Research entities appear in graph
[ ] Scene edits update graph in < 500ms
[ ] Export 80,000 word manuscript in < 10 seconds
[ ] No memory leaks after 2 hours of use
```

---

## Performance Requirements

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Graph load (100 entities) | < 500ms | Time from file read to render |
| Graph load (1000 entities) | < 2s | Time from file read to render |
| Entity search | < 100ms | Time for query_entities() |
| Path finding | < 200ms | Time for find_path() |
| Single agent draft | < 30s | Time from request to response |
| Tournament (3 agents) | < 2min | Time for all drafts + scoring |
| File import (50k words) | < 10s | Time from upload to graph populated |
| Checkpoint creation | < 1s | Time to serialize and save |
| Checkpoint restore | < 2s | Time to load and rebuild graph |
| UI responsiveness | 60fps | Graph panel dragging/zooming |

---

## Data Models

### Project Configuration (project.yaml)

```yaml
name: "My Novel"
author: "Writer Name"
created_at: "2025-11-21T10:00:00Z"
last_modified: "2025-11-21T15:30:00Z"

structure:
  type: novel  # novel, screenplay, short_story
  target_word_count: 80000
  current_word_count: 45230

settings:
  auto_extract: true
  extract_on_save: true
  extraction_model: "claude-sonnet-4"

notebooks:
  - name: "Character Research"
    url: "https://notebooklm.google.com/notebook/abc123"
    last_sync: "2025-11-21T14:00:00Z"
  - name: "World Building"
    url: "https://notebooklm.google.com/notebook/def456"
    last_sync: "2025-11-21T12:00:00Z"
```

### Scene Metadata (scenes/chapter-01-scene-01.md frontmatter)

```yaml
---
id: "scene_001"
title: "The Beginning"
chapter: 1
scene_number: 1
sequence: 1
word_count: 1234
status: draft  # draft, revised, final
characters:
  - "alice"
  - "bob"
location: "coffee_shop"
timeline_position: "day_1_morning"
created_at: "2025-11-21T10:00:00Z"
last_modified: "2025-11-21T15:30:00Z"
generated_by: "Claude Sonnet"  # or "human"
---

Scene content here...
```

---

## Security Considerations

1. **API Keys**: Stored in OS keychain, never in plain text files
2. **Local Data**: All manuscript data stays on local machine
3. **Network**: Only outbound connections to AI APIs and NotebookLM
4. **Permissions**: Tauri sandboxing limits filesystem access to workspace

---

## Future Extensibility

### Plugin System (Phase 2+)

```python
# plugins/my_custom_agent.py
class MyCustomAgent(AgentPlugin):
    name = "My Custom Agent"
    version = "1.0.0"

    def generate(self, context: str) -> Draft:
        # Custom generation logic
        pass

    def score(self, draft: Draft, graph: KnowledgeGraphService) -> float:
        # Custom scoring logic
        pass

# plugins/my_custom_query.py
class CharacterEmotionQuery(QueryPlugin):
    name = "Character Emotion Trajectory"

    def execute(self, graph: KnowledgeGraphService, params: Dict) -> QueryResult:
        character_id = params['character_id']
        # Calculate emotional trajectory across scenes
        pass
```

### Collaboration (Phase 3+)

- Git-based sync for project files
- Graph merge conflict resolution
- Shared NotebookLM notebooks

---

## Appendix A: Key Algorithms in Existing Code

### PageRank Centrality (graph_service.py:335-347)
```python
def get_central_entities(self, top_n: int = 10) -> List[Tuple[str, float]]:
    """Get most central entities using PageRank."""
    if len(self.graph.nodes) == 0:
        return []
    pagerank = nx.pagerank(self.graph)
    sorted_entities = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    return sorted_entities[:top_n]
```

### Community Detection (graph_service.py:349-361)
```python
def get_communities(self) -> List[Set[str]]:
    """Detect entity communities using Louvain method."""
    if len(self.graph.nodes) == 0:
        return []
    undirected = self.graph.to_undirected()
    from networkx.algorithms import community
    communities = community.greedy_modularity_communities(undirected)
    return [set(c) for c in communities]
```

### BFS Entity Traversal (graph_service.py:272-323)
```python
def get_connected_entities(self, entity_id: str, max_depth: int = 2,
                           relation_types: Optional[List[RelationType]] = None) -> List[Entity]:
    """Get all entities connected within max_depth using BFS."""
    # ... BFS implementation with relation type filtering
```

---

## Appendix B: Relationship Types Reference

| Category | Types | Use Case |
|----------|-------|----------|
| **Interpersonal** | KNOWS, LOVES, FEARS, CONFLICTS_WITH | Character relationships |
| **Hierarchical** | LEADS, FOLLOWS, WORKS_WITH | Power dynamics |
| **Spatial** | LOCATED_IN, TRAVELS_TO, RESIDES_IN, OWNS | Physical relationships |
| **Temporal** | OCCURS_BEFORE, OCCURS_DURING, OCCURS_AFTER | Event ordering |
| **Causal** | CAUSES, RESULTS_IN, TRIGGERS | Plot causation |
| **Conceptual** | REPRESENTS, SYMBOLIZES, OPPOSES, SUPPORTS | Thematic relationships |
| **Participatory** | PARTICIPATES_IN, WITNESSES | Event involvement |
| **Organizational** | MEMBER_OF, FOUNDED_BY, CONTROLS | Group membership |

---

## Appendix C: Entity Attributes by Type

### CHARACTER
```python
{
    'role': 'protagonist|antagonist|supporting|minor',
    'age': int,
    'gender': str,
    'occupation': str,
    'motivation': str,
    'arc_type': 'positive|negative|flat',
    'first_appearance_chapter': int,
    'emotional_state': float  # -1 to +1
}
```

### LOCATION
```python
{
    'type': 'interior|exterior|abstract',
    'region': str,
    'atmosphere': str,
    'significance': str
}
```

### EVENT
```python
{
    'event_type': 'plot_point|backstory|foreshadowing',
    'thread_type': 'main_plot|subplot|background',
    'resolved': bool,
    'chapter': int,
    'impact': 'high|medium|low'
}
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-21 | Claude + User | Initial specification |

---

*This document serves as the authoritative technical specification for the Writers Factory Desktop App. Any implementing agent or developer should reference this document for architecture decisions, implementation details, and code to port from the existing project.*
