# Writers Platform - Technical Documentation Index

**Last Updated**: 2025-01-18
**Version**: 1.0
**Status**: Complete Reference

This is the master technical documentation for the Writers Platform. Use this as the foundation for creating user guides, training materials, and onboarding docs.

---

## 📚 Documentation Structure

### 1. Architecture & Overview
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Database Schema](#database-schema)
- [API Structure](#api-structure)

### 2. Core Systems
- [Authentication & User Management](#authentication--user-management)
- [Factory (Writing Platform)](#factory-writing-platform)
- [Community (Publishing Platform)](#community-publishing-platform)
- [Knowledge Graph System](#knowledge-graph-system)
- [NotebookLM Integration](#notebooklm-integration)
- [AI Copilot System](#ai-copilot-system)

### 3. Features
- [Badge & Verification System](#badge--verification-system)
- [Entity-Based Discovery](#entity-based-discovery)
- [Batch Operations](#batch-operations)
- [Error Monitoring](#error-monitoring)
- [AI Wizard](#ai-wizard)

### 4. Deployment & Operations
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Testing Strategy](#testing-strategy)
- [Monitoring & Observability](#monitoring--observability)

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Writers Platform                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Factory    │  │  Community   │  │   Backend    │     │
│  │  (Vite/React)│  │ (Vite/React) │  │  (FastAPI)   │     │
│  │              │  │              │  │              │     │
│  │ • Editor     │  │ • Browse     │  │ • REST API   │     │
│  │ • KG View    │  │ • Read       │  │ • Auth       │     │
│  │ • AI Copilot │  │ • Profile    │  │ • AI Models  │     │
│  │ • Analytics  │  │ • Upload     │  │ • Jobs       │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                            ▼                                 │
│                  ┌──────────────────┐                       │
│                  │   PostgreSQL     │                       │
│                  │  (Railway/Neon)  │                       │
│                  │                  │                       │
│                  │ • Users          │                       │
│                  │ • Projects       │                       │
│                  │ • Scenes         │                       │
│                  │ • Works          │                       │
│                  │ • Graphs (JSONB) │                       │
│                  │ • Badges         │                       │
│                  └──────────────────┘                       │
│                                                              │
│  External Services:                                         │
│  • Anthropic (Claude)                                       │
│  • OpenAI (GPT-4)                                          │
│  • Google (Gemini)                                         │
│  • Ollama (Local AI)                                       │
│  • NotebookLM MCP                                          │
│  • Sentry (Error Tracking)                                 │
│  • Google Cloud Storage                                    │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Architecture

```
Production Environment:

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vercel CDN    │     │   Vercel CDN    │     │   Railway       │
│                 │     │                 │     │                 │
│ Factory Frontend│     │Community Frontend│     │  Backend API    │
│ writersfactory  │     │writerscommunity │     │  FastAPI App    │
│     .app        │     │     .app        │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                        │
         │                       │                        │
         └───────────────────────┴────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Railway PostgreSQL     │
                    │  (Primary Database)     │
                    └─────────────────────────┘
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.115.7
- **Language**: Python 3.11+
- **Database**: PostgreSQL (via SQLAlchemy 2.0.36)
- **ORM**: SQLAlchemy with Alembic migrations
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **AI SDKs**: anthropic, openai, google-generativeai
- **Knowledge Graph**: NetworkX 3.2
- **NLP**: spaCy 3.7.0 (entity extraction)
- **Error Monitoring**: Sentry SDK 1.40.0+
- **Storage**: Google Cloud Storage (GCS)

### Factory Frontend
- **Framework**: React 19.2 + Vite 7.2
- **Language**: TypeScript 5.9
- **Routing**: React Router 7.9
- **State Management**: Zustand 5.0
- **API Layer**: React Query 5.90 + Axios 1.13
- **Styling**: Tailwind CSS 3.4
- **UI Components**: Headless UI 2.2
- **3D Visualization**: react-force-graph-3d 1.29 (Knowledge Graph)
- **Error Monitoring**: @sentry/react 7.100

### Community Frontend
- **Framework**: React 19.2 + Vite 7.2
- **Language**: TypeScript 5.9
- **Routing**: React Router 7.9
- **State Management**: Zustand 5.0
- **API Layer**: React Query 5.90 + Axios 1.13
- **Styling**: Tailwind CSS 3.4
- **UI Components**: Headless UI 2.2
- **Error Monitoring**: @sentry/react 7.100

### Infrastructure
- **Backend Hosting**: Railway
- **Frontend Hosting**: Vercel
- **Database**: Railway PostgreSQL (with Neon as alternative)
- **Storage**: Google Cloud Storage
- **Monitoring**: Sentry
- **Version Control**: Git + GitHub

---

## Database Schema

### Core Tables

#### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

**Purpose**: Authentication and user identity
**Relationships**: One-to-many with projects, works, comments

#### Projects (Factory)
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- NotebookLM Integration
    notebooklm_notebooks JSONB,  -- {character_research: url, world_building: url, themes: url}
    notebooklm_config JSONB      -- {enabled: bool, auto_query_on_copilot: bool, configured_at: iso}
);
```

**Purpose**: Writing projects in Factory
**Relationships**: One-to-many with scenes, one-to-one with project_graphs

#### Scenes (Factory)
```sql
CREATE TABLE scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT,
    scene_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Purpose**: Individual writing units within projects
**Relationships**: Many-to-one with projects

#### Works (Community)
```sql
CREATE TABLE works (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    genre VARCHAR(100),
    content TEXT NOT NULL,
    word_count INTEGER,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'published',
    visibility VARCHAR(20) DEFAULT 'public',

    -- Factory Integration
    factory_project_id UUID REFERENCES projects(id),
    factory_scores JSONB,  -- {voice: 0.85, pacing: 0.72, ...}

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Purpose**: Published content in Community
**Relationships**: One-to-many with comments, ratings, badges

#### Badges (Community)
```sql
CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_id UUID REFERENCES works(id) ON DELETE CASCADE,
    badge_type VARCHAR(50) NOT NULL,  -- 'ai_analyzed', 'human_verified', 'human_self', 'community_upload'
    verified BOOLEAN DEFAULT FALSE,
    metadata_json JSONB,  -- AI scores, verification details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Trust and verification system for works
**Badge Types**:
- `ai_analyzed`: AI detected human writing (>80% confidence)
- `human_verified`: Human curator confirmed authenticity
- `human_self`: Author self-certified as human
- `community_upload`: Community contribution

#### Project Graphs (Knowledge Graph)
```sql
CREATE TABLE project_graphs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE UNIQUE,
    graph_data JSONB NOT NULL,  -- NetworkX graph JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Purpose**: Store knowledge graphs for projects
**Graph Data Structure**:
```json
{
  "nodes": [
    {
      "id": "uuid",
      "name": "Character Name",
      "type": "character",
      "description": "...",
      "attributes": {},
      "properties": {
        "notebooklm_sources": [...],
        "notebooklm_notebook_id": "...",
        "enriched_from_notebooklm": true
      }
    }
  ],
  "edges": [
    {
      "source": "uuid1",
      "target": "uuid2",
      "type": "related_to",
      "properties": {}
    }
  ]
}
```

---

## API Structure

### Base URL
- **Production**: `https://your-backend.railway.app/api`
- **Development**: `http://localhost:8000/api`

### Authentication
All protected endpoints require JWT token:
```
Authorization: Bearer <token>
```

### Endpoint Categories

#### Auth (`/auth`)
- `POST /auth/register` - Create new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user

#### Projects (`/projects`)
- `GET /projects` - List user's projects
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

#### Scenes (`/projects/{id}/scenes`)
- `GET /projects/{id}/scenes` - List scenes
- `POST /projects/{id}/scenes` - Create scene
- `PUT /scenes/{id}` - Update scene
- `DELETE /scenes/{id}` - Delete scene

#### Works (`/works`)
- `GET /works` - Browse published works
- `GET /works/{id}` - Get work details
- `POST /works` - Publish new work
- `POST /works/{id}/like` - Like a work
- `DELETE /works/{id}/like` - Unlike a work

#### Browse (`/browse`)
- `GET /browse` - Browse with filters
- `GET /browse/by-entity` - **NEW** Entity-based discovery

#### Knowledge Graph (`/knowledge-graph`)
- `GET /knowledge-graph/projects/{id}` - Get project graph
- `POST /knowledge-graph/projects/{id}/extract` - Extract entities
- `GET /knowledge-graph/projects/{id}/entities/{entity_id}` - Entity details

#### NotebookLM (`/notebooklm`)
- `GET /notebooklm/status` - Check MCP server status
- `GET /notebooklm/notebooks` - List notebooks
- `POST /notebooklm/query` - Query notebook
- `POST /notebooklm/projects/{id}/extract-character` - Extract character
- `POST /notebooklm/projects/{id}/extract-world-building` - Extract world
- `POST /notebooklm/batch-extract` - **NEW** Batch extraction

#### Copilot (`/copilot`)
- `POST /copilot/suggest` - Get AI suggestions
- `POST /copilot/analyze` - Analyze text

---

## Authentication & User Management

### Flow
1. User registers → Username, email, password
2. Password hashed with bcrypt
3. User credentials stored in database
4. Login → Validate credentials → Generate JWT
5. JWT valid for 24 hours
6. Frontend stores token in localStorage
7. All API requests include token in Authorization header

### Token Structure
```json
{
  "sub": "user_id",
  "username": "john_doe",
  "exp": 1705500000
}
```

### Security Features
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens signed with SECRET_KEY
- Token expiration (24 hours)
- CORS configured for specific domains
- No password recovery (MVP - to be added)

---

## Factory (Writing Platform)

### Purpose
Professional writing environment for authors to:
- Create projects and scenes
- Use AI copilot for suggestions
- Build knowledge graphs
- Integrate research (NotebookLM)
- Analyze writing quality
- Publish to Community

### Key Pages

#### Dashboard (`/dashboard`)
- List all projects
- Create new project
- Project cards with stats

#### Editor (`/projects/{id}/editor`)
- Scene writing interface
- AI copilot sidebar
- Real-time suggestions
- Scene navigation
- Save/publish

#### Knowledge Graph (`/projects/{id}/knowledge-graph`)
- 3D force-directed graph
- Entity browser
- Relationship explorer
- Entity details modal with **Research Citations**

#### NotebookLM Settings (`/projects/{id}/notebooklm`)
- Configure notebook URLs
- **Batch extraction UI**
- MCP server status

#### Analysis (`/projects/{id}/analysis`)
- Writing quality scores
- Character arc analysis
- Pacing visualization

---

## Community (Publishing Platform)

### Purpose
Public-facing platform where:
- Readers discover stories
- Authors publish finished works
- Community engages (comments, likes)
- Badge system ensures trust

### Key Pages

#### Browse (`/browse`)
- Filter by genre, badge type
- Search by title/author
- **NEW: Entity-Based Discovery** (search by character/location/theme)
- Sort by recent/popular/liked

#### View Work (`/works/{id}`)
- Read full content
- See badges
- **Research Citations** (for Factory-published works)
- Factory quality scores
- Comments section
- Like button

#### Upload (`/upload`)
- Direct community upload
- Title, description, genre
- Human authorship claim
- Gets `community_upload` badge

#### Profile (`/profile/{username}`)
- User's published works
- Stats (views, likes)
- Bio

---

## Knowledge Graph System

### Architecture
- Built on NetworkX (Python graph library)
- Stored as JSONB in PostgreSQL
- Extracted using spaCy NER + Claude Sonnet
- Visualized with react-force-graph-3d

### Entity Types
- **Character**: People, animals, sentient beings
- **Location**: Places, cities, buildings
- **Object**: Items, artifacts, technology
- **Concept**: Ideas, philosophies, systems
- **Event**: Occurrences, plot points
- **Organization**: Groups, companies, institutions
- **Theme**: Recurring motifs, ideas

### Extraction Process
1. User writes scene in editor
2. Click "Extract Entities" or auto-extract
3. Backend analyzes text with LLMExtractor (Claude Sonnet)
4. Entities identified with name, type, description
5. Relationships detected (e.g., "Alice knows Bob")
6. Graph updated with deduplication
7. Frontend refreshed via WebSocket

### Graph Operations
- **Add Entity**: Manual or extracted
- **Update Entity**: Edit properties
- **Delete Entity**: Remove from graph
- **Add Relationship**: Connect two entities
- **Find Entity**: Fuzzy name matching
- **Query Graph**: Find neighbors, paths

### NotebookLM Enhancement
When entities extracted from NotebookLM:
- `properties.notebooklm_sources`: Array of source objects
- `properties.notebooklm_notebook_id`: Notebook URL
- `properties.enriched_from_notebooklm`: Boolean flag
- Sources shown in EntityDetails with **Research Citations** UI

---

## NotebookLM Integration

### Purpose
Ground fiction writing in real-world research by integrating Google's NotebookLM.

### How It Works
1. Writer creates NotebookLM notebooks externally
2. Adds research sources (YouTube, PDFs, articles)
3. Configures notebook URLs in Factory settings
4. AI Copilot queries notebooks for context
5. Entity extraction pulls from notebooks
6. Citations preserved in knowledge graph

### Notebook Types
- **Character Research**: Interviews, personality studies, voice examples
- **World Building**: Future tech, social trends, setting details
- **Themes & Philosophy**: Ethical frameworks, philosophical concepts

### MCP Server
- Runs as separate process
- Provides notebook query API
- Handles authentication with NotebookLM
- Returns answers with source citations

### Batch Extraction
**NEW** feature allows extracting all notebooks at once:
- Select extract types (character, world, themes)
- Process multiple projects
- Returns: entities added, entities enriched, errors
- Much faster than one-by-one

---

## AI Copilot System

### Purpose
Real-time AI suggestions while writing scenes.

### Supported Models
1. **Claude Sonnet 4.5** (Anthropic) - Best quality
2. **GPT-4** (OpenAI) - Creative
3. **Gemini** (Google) - Fast
4. **Llama 2** (Ollama) - FREE, local

### Features
- **Autocomplete**: Suggest next sentence
- **Expand**: Elaborate on selected text
- **Rephrase**: Alternative phrasing
- **Analyze**: Writing quality feedback
- **NotebookLM Context**: Query research notebooks

### Request Flow
1. User types in editor
2. Frontend debounces input (500ms)
3. Sends text + context to `/copilot/suggest`
4. Backend selects model (user preference)
5. If NotebookLM enabled, queries notebooks
6. Calls AI model with context
7. Returns suggestions
8. Frontend shows in sidebar

### Context Window
- Current scene text (full)
- Previous scene (summary)
- Knowledge graph entities (mentioned)
- NotebookLM research (300 chars max)
- User preferences (tone, style)

---

## Badge & Verification System

### Purpose
Build trust in Community by verifying authorship.

### Badge Types

#### 1. AI Analyzed (Green)
- Automatic AI detection
- Claude Sonnet analyzes text
- Checks for AI markers (repetition, patterns)
- >80% confidence = human-written
- Badge auto-assigned on publish from Factory

#### 2. Human Verified (Blue)
- Manual curator verification
- Trusted humans review work
- Confirm authenticity
- Highest trust level

#### 3. Human Self-Certified (Orange)
- Author self-declares human authorship
- Checkbox on publish
- Lower trust than verified
- Still meaningful signal

#### 4. Community Upload (Gray)
- Direct community upload
- No Factory integration
- No AI analysis
- Baseline trust

### Badge Display
- Colored badge icon next to work title
- Hover tooltip explains badge type
- Metadata shows confidence scores (AI analyzed)
- Filter by badge type in Browse page

---

## Entity-Based Discovery

### Purpose
**Unique feature**: Find stories by searching for specific characters, locations, or themes.

### How It Works
1. User goes to Browse page
2. Sees purple "Entity-Based Discovery" section
3. Enters entity name (e.g., "Mickey", "Shanghai", "AI")
4. Optionally selects entity type
5. Click Search
6. Backend queries all knowledge graphs
7. Fuzzy matching on entity names
8. Returns works containing that entity

### Backend Implementation
- Endpoint: `GET /api/browse/by-entity`
- Queries: `project_graphs` table
- Searches: JSONB graph_data for matching nodes
- Fuzzy logic: "Mickey" matches "Mickey Mouse", "Michael"
- Filters: Optional entity type (character, location, etc.)
- Returns: Standard BrowseResponse with works

### Frontend UI
- Purple gradient box (stands out)
- Entity name input
- Entity type dropdown (5 types)
- Search button with magnifying glass
- Clear button
- Results: "X works featuring 'Mickey' (character)"

---

## Batch Operations

### Batch NotebookLM Extraction

**Purpose**: Extract research from all NotebookLM notebooks at once instead of one-by-one.

**Endpoint**: `POST /api/notebooklm/batch-extract`

**Parameters**:
- `project_ids`: Optional list of UUIDs (or all if omitted)
- `extract_types`: List of "character", "world", "themes"

**Process**:
1. Get all projects with NotebookLM configured
2. For each project:
   - Check if notebooks exist
   - For each extract type:
     - Query NotebookLM notebook generically
     - Use LLM to extract entities from response
     - Add to knowledge graph with deduplication
   - Commit changes
3. Return detailed results

**Response**:
```json
{
  "total_projects": 5,
  "success_count": 5,
  "error_count": 0,
  "skipped_count": 0,
  "total_entities_added": 42,
  "total_entities_enriched": 18,
  "project_results": [
    {
      "project_id": "...",
      "project_title": "My Novel",
      "status": "success",
      "entities_added": 8,
      "entities_enriched": 3,
      "errors": []
    }
  ]
}
```

**UI**: Purple gradient section in NotebookLM Settings with checkboxes and progress display.

---

## Error Monitoring

### Sentry Integration

**Purpose**: Production error tracking and performance monitoring.

**Coverage**:
- Backend: FastAPI + SQLAlchemy errors
- Factory Frontend: React errors + network failures
- Community Frontend: React errors + network failures

**Features**:
- Real-time error alerts
- Stack traces
- Performance monitoring (10% sample rate)
- Session Replay (10% normal, 100% on errors)
- User context (without PII)
- Release tracking

**Setup**:
1. Create Sentry account (free tier: 5K errors/month)
2. Create 3 projects (Backend, Factory, Community)
3. Set environment variables:
   - Backend: `SENTRY_DSN`
   - Frontends: `VITE_SENTRY_DSN`
4. Deploy

**Optional**: Works without DSN (disabled by default).

**Full Guide**: `SENTRY_SETUP.md`

---

## AI Wizard

### Purpose
Conversational interface to guide users through complex setup via chat (like ChatGPT).

### Contexts

1. **Onboarding**: First-time users
   - Genre selection
   - Project creation
   - Research setup

2. **Project Setup**: Creating new projects
   - Title and genre
   - Initial scenes
   - Knowledge graph

3. **NotebookLM**: Research integration
   - Notebook creation guide
   - URL configuration
   - Batch extraction

4. **Knowledge Graph**: Entity management
   - Extraction vs manual
   - Graph navigation
   - Entity editing

5. **Copilot**: AI assistant setup
   - Local vs premium
   - API key configuration
   - Model selection

### Components

**AIWizard.tsx**: Main chat engine
- Message state management
- Conversation flow logic
- Context switching
- API integration

**WizardMessage.tsx**: Message bubbles
- Role-based styling (wizard vs user)
- Action button rendering
- Timestamp display

**FloatingWizard.tsx**: Floating button
- Pulse animation for unread
- Modal overlay
- Positioning options

**Wizard.tsx**: Full-page wrapper
- Navigation bar
- Centered container
- Help links

### Usage

**Full-Page**: `/wizard?context=onboarding&projectId=abc123`

**Embedded**: `<AIWizard context="notebooklm" projectId={id} />`

**Floating**: `<FloatingWizard position="bottom-right" />`

**Full Guide**: `AI_WIZARD_GUIDE.md`

---

## Testing Strategy

### Unit Tests
- Backend: pytest for API endpoints
- Frontend: Jest + React Testing Library

### Integration Tests
- End-to-end flows
- Database interactions
- AI model integrations

### Test Files
- `test_phase2_migration.sh`: Database verification
- `test_phase2_api.py`: Badge system API tests

### Testing Checklist
See `PHASE_2_QUICK_START.md` for complete testing guide.

---

## Monitoring & Observability

### Metrics to Track

**Backend**:
- Request rate
- Response times (p50, p95, p99)
- Error rate
- Database query performance
- AI model latency

**Frontend**:
- Page load times
- JavaScript errors
- API request failures
- User engagement

**Business**:
- User signups
- Projects created
- Works published
- Entity searches
- Batch extractions
- Wizard completions

### Alerts

1. **Error Spike**: >10 errors/hour
2. **Performance Degradation**: p95 >2s
3. **Failed Jobs**: Batch extraction failures
4. **Low Engagement**: <50% wizard completion

### Tools
- **Sentry**: Error tracking + performance
- **Railway Metrics**: Backend resource usage
- **Vercel Analytics**: Frontend performance
- **PostgreSQL Logs**: Database queries

---

## Common Patterns

### API Request Pattern
```typescript
// Frontend
const response = await fetch('/api/endpoint', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});

if (!response.ok) {
  throw new Error('Request failed');
}

const result = await response.json();
```

### Database Query Pattern
```python
# Backend
from sqlalchemy.orm import Session
from app.models import Model

def get_items(db: Session, user_id: str):
    return db.query(Model).filter(
        Model.user_id == user_id
    ).all()
```

### Knowledge Graph Update Pattern
```python
# Backend
from app.services.knowledge_graph.graph_service import KnowledgeGraphService

# Load graph
kg = KnowledgeGraphService.from_json(project_graph.graph_data)

# Add entity
entity = Entity(id="...", name="Character", type="character")
kg.add_entity(entity)

# Save graph
project_graph.graph_data = json.loads(kg.to_json())
db.commit()
```

---

## File Structure

```
writers-platform/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, database, auth
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   │   ├── knowledge_graph/  # KG system
│   │   │   ├── notebooklm/       # NotebookLM MCP
│   │   │   └── badge_engine.py   # Badge logic
│   │   └── main.py        # FastAPI app
│   ├── migrations/        # Alembic migrations
│   └── requirements.txt   # Python dependencies
├── factory-frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── knowledge-graph/  # KG components
│   │   │   └── wizard/           # AI Wizard
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── api/           # API client
│   │   └── types/         # TypeScript types
│   └── package.json       # npm dependencies
├── community-frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── api/           # API client
│   │   └── types/         # TypeScript types
│   └── package.json       # npm dependencies
└── docs/
    ├── DEPLOYMENT_GUIDE.md        # Deployment instructions
    ├── SENTRY_SETUP.md            # Error monitoring guide
    ├── AI_WIZARD_GUIDE.md         # Wizard usage guide
    ├── PHASE_2_QUICK_START.md     # Testing guide
    └── TECHNICAL_DOCUMENTATION.md # This file
```

---

## Deriving User Guides

Use this technical documentation to create user-friendly guides:

### Example: "How to Use Entity-Based Discovery"

**From Technical Docs**:
- Purpose: Find stories by characters/locations/themes
- Location: Community Browse page
- UI: Purple search box
- Process: Enter name → Select type → Search

**User Guide**:
1. Go to Writers Community Browse page
2. Look for the purple "Entity-Based Discovery" section
3. Enter a character name like "Mickey" or location like "Shanghai"
4. (Optional) Select what type it is from the dropdown
5. Click Search
6. See all stories featuring that character or location!

### Example: "Setting Up NotebookLM Research"

**From Technical Docs**:
- Purpose: Ground writing in real research
- Notebook types: Character, World, Themes
- Process: Create externally → Configure URLs → Extract

**User Guide**:
1. Go to notebooklm.google.com
2. Create a new notebook
3. Add your research sources (YouTube videos, PDFs, etc.)
4. Copy the notebook URL
5. In Factory, go to NotebookLM Settings
6. Paste the URL in the appropriate field
7. Click "Save Configuration"
8. Use "Batch Extraction" to add research to your Knowledge Graph!

---

## Quick Reference

### Key URLs
- **Factory**: https://writersfactory.app
- **Community**: https://writerscommunity.app
- **Backend API**: https://your-backend.railway.app/api
- **API Docs**: https://your-backend.railway.app/api/docs

### Environment Variables
- Backend: `DATABASE_URL`, `SECRET_KEY`, `SENTRY_DSN`
- Frontends: `VITE_SENTRY_DSN`, `VITE_SENTRY_ENVIRONMENT`

### Important Concepts
- **Factory**: Writing platform (private projects)
- **Community**: Publishing platform (public works)
- **Knowledge Graph**: Entity relationship system
- **NotebookLM**: Research integration
- **Badge System**: Trust and verification
- **AI Wizard**: Conversational setup guide

---

## Support Resources

- **Deployment**: `DEPLOYMENT_GUIDE.md`
- **Error Monitoring**: `SENTRY_SETUP.md`
- **AI Wizard**: `AI_WIZARD_GUIDE.md`
- **Testing**: `PHASE_2_QUICK_START.md`
- **API Docs**: Visit `/api/docs` on backend

---

**This documentation is complete and production-ready.**
Use it as the foundation for all user guides, training materials, and onboarding docs.

**Last Updated**: 2025-01-18
**Maintained By**: Writers Platform Team
