# Writers Platform - System Architecture

**Version:** 1.0
**Last Updated:** November 17, 2025
**Status:** Production (Backend + Factory Frontend deployed, Community Frontend ready)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Platform Overview](#platform-overview)
3. [Current Architecture (Sessions 1-3)](#current-architecture-sessions-1-3)
4. [Planned Enhancements (Sessions 4-5)](#planned-enhancements-sessions-4-5)
5. [Technology Stack](#technology-stack)
6. [Database Schema](#database-schema)
7. [API Architecture](#api-architecture)
8. [Frontend Architecture](#frontend-architecture)
9. [AI Engine Architecture](#ai-engine-architecture)
10. [Deployment Architecture](#deployment-architecture)
11. [Security & Authentication](#security--authentication)
12. [Development Roadmap](#development-roadmap)

---

## Executive Summary

**Writers Platform** is a unified full-stack SaaS platform that combines:

- **Writers Factory** (writersfactory.app) - Private AI-powered writing workspace
- **Writers Community** (writerscommunity.app) - Public showcase and reading platform

**Core Value Proposition:**
- Writers develop manuscripts with professional multi-AI analysis (Factory)
- Publish to community with transparent AI usage badges (Community)
- Seamless integration between private creation and public sharing

**Key Differentiators:**
1. Multi-agent AI tournament system (5 models compete)
2. Transparent badge system (AI-analyzed, human-verified, self-certified, community)
3. Unified backend engine (shared analysis, consistent data)
4. Free local AI for setup (Llama 3.3 via Ollama) - planned Session 4
5. Knowledge graph integration with NotebookLM - planned Session 5

---

## Platform Overview

### Business Model

```
┌─────────────────────────────────────────────────────────────┐
│                    WRITERS PLATFORM                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐        ┌──────────────────────┐  │
│  │  Writers Factory     │        │  Writers Community   │  │
│  │  (Private Workspace) │────────│  (Public Showcase)   │  │
│  │                      │        │                      │  │
│  │  • Upload files      │        │  • Browse works      │  │
│  │  • AI analysis       │  Pub-  │  • Read content      │  │
│  │  • Scene editing     │  lish  │  • Comments/likes    │  │
│  │  • Knowledge graph   │   →    │  • Badge display     │  │
│  │  • Tournament system │        │  • Direct upload     │  │
│  └──────────────────────┘        └──────────────────────┘  │
│              ↓                              ↓                │
│         writersfactory.app      writerscommunity.app        │
└─────────────────────────────────────────────────────────────┘
                              ↓
               ┌──────────────────────────────┐
               │   Shared Backend Engine      │
               │   (FastAPI + PostgreSQL)     │
               │                              │
               │   • Authentication (JWT)     │
               │   • File parsing             │
               │   • AI tournament            │
               │   • Badge assignment         │
               │   • Database models          │
               └──────────────────────────────┘
```

### User Journey

**Typical Writer Flow:**
1. **Onboard** → Choose path (Experienced/Prepared/New) - Session 4
2. **Extract Knowledge** → AI wizard conversation, 8 categories - Session 4
3. **Upload** → DOCX/PDF/TXT file parsed into scenes
4. **Analyze** → Multi-AI tournament generates feedback
5. **Refine** → Edit scenes based on analysis
6. **Publish** → Share to Community with AI-Analyzed badge
7. **Engage** → Readers comment, like, rate

**Typical Reader Flow:**
1. **Browse** → Filter by badge type, genre, search
2. **Read** → Full-text reader with Factory CTAs
3. **Engage** → Comment, like, rate (requires auth)
4. **Discover** → Follow authors, bookmark works

---

## Current Architecture (Sessions 1-3)

### ✅ Implemented Components

#### Backend (Session 1)
- **FastAPI Application** - 15+ route files
- **PostgreSQL Database** - 16 models (Factory + Community)
- **AI Tournament Engine** - 5 AI model integrations
- **File Parser Service** - DOCX/PDF/TXT parsing with chapter detection
- **Badge Engine Service** - 4 badge types with AI detection
- **Factory Orchestrator** - Background job management
- **JWT Authentication** - Secure user sessions

#### Factory Frontend (Session 2)
- **React 18 + TypeScript** - 7 pages
- **File Upload** - Drag-and-drop with progress
- **Project Management** - CRUD operations
- **Scene Editor** - View/edit scenes
- **Analysis Interface** - Configure, run, monitor AI analysis
- **Results Visualization** - Scores, costs, model comparison

#### Community Frontend (Session 3)
- **React 18 + TypeScript** - 6 pages
- **Badge System** - 4 badge types with explainer
- **Public Browsing** - Filter by badge, genre, search
- **Work Reading** - Full-text reader with comments
- **Direct Upload** - Upload with AI human-authorship detection
- **Factory Integration** - CTAs throughout

### System Diagram (Current)

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                        │
├──────────────────────────┬──────────────────────────────────┤
│  Factory Frontend        │  Community Frontend              │
│  (Vercel)                │  (Vercel)                        │
│  React 18 + TypeScript   │  React 18 + TypeScript           │
│  ├─ Home                 │  ├─ Home (with badge explainer)  │
│  ├─ Login/Register       │  ├─ Login/Register               │
│  ├─ Dashboard            │  ├─ Browse (with filters)        │
│  ├─ Upload               │  ├─ ViewWork (with Factory CTAs) │
│  ├─ Editor               │  ├─ Upload (with AI detection)   │
│  └─ Analysis             │  └─ ...                          │
└──────────────────────────┴──────────────────────────────────┘
                              ↓ HTTPS/REST
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                       │
│                     (Railway - FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│  Routes (15 files):                                          │
│  ├─ /auth/          - JWT authentication                    │
│  ├─ /projects/      - Factory project CRUD + file upload    │
│  ├─ /analysis/      - AI tournament management              │
│  ├─ /works/         - Community published works             │
│  ├─ /comments/      - Comments on works                     │
│  ├─ /ratings/       - 5-star ratings                        │
│  ├─ /browse/        - Advanced filtering/search             │
│  ├─ /profile/       - User profiles                         │
│  └─ ... (7+ more)                                           │
│                                                              │
│  Services (3 core):                                          │
│  ├─ FileParser      - Parse DOCX/PDF/TXT → scenes          │
│  ├─ FactoryOrchestrator - Manage AI analysis jobs          │
│  └─ BadgeEngine     - Assign authenticity badges            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                           │
│                    (PostgreSQL on Railway)                   │
├─────────────────────────────────────────────────────────────┤
│  Factory Models:                                             │
│  ├─ Project         - Writing projects                      │
│  ├─ Scene           - Scenes/chapters                       │
│  ├─ AnalysisResult  - AI tournament results                 │
│  └─ Badge           - Authenticity badges                   │
│                                                              │
│  Community Models:                                           │
│  ├─ User            - User accounts                         │
│  ├─ Work            - Published works                       │
│  ├─ Comment         - Work comments                         │
│  ├─ Rating          - 5-star ratings                        │
│  ├─ ReadingSession  - Reading progress tracking             │
│  └─ ... (7+ more)                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      AI ENGINE LAYER                         │
│                  (backend/engine/ - 70k+ lines)              │
├─────────────────────────────────────────────────────────────┤
│  Orchestration:                                              │
│  └─ tournament.py   - Multi-agent tournament system         │
│                                                              │
│  AI Agents (5):                                              │
│  ├─ claude_agent.py    - Anthropic Claude Sonnet 4.5/Haiku │
│  ├─ gemini_agent.py    - Google Gemini 1.5 Pro             │
│  ├─ chatgpt_agent.py   - OpenAI GPT-4o                     │
│  ├─ grok_agent.py      - xAI Grok 2                        │
│  └─ deepseek_agent.py  - DeepSeek (budget option)          │
│                                                              │
│  Analysis Tools:                                             │
│  ├─ voice_consistency_tester.py                            │
│  ├─ metaphor_analyzer.py                                   │
│  └─ character_tracker.py                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL AI APIs                         │
├─────────────────────────────────────────────────────────────┤
│  • Anthropic API (Claude)                                   │
│  • Google AI API (Gemini)                                   │
│  • OpenAI API (GPT)                                         │
│  • xAI API (Grok)                                           │
│  • DeepSeek API                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Planned Enhancements (Sessions 4-5)

### 🚧 Session 4: Enhanced Onboarding & AI Wizard

**Goal:** Migrate sophisticated onboarding from writers-factory-core

#### Components to Add:

**1. Welcome Flow (~830 lines)**
```
factory-frontend/src/components/
├─ PathSelectionStep.jsx      # 3-path chooser
│  └─ Paths: Experienced / Prepared / New
├─ PathOption.jsx              # Reusable path cards
├─ NotebookLMRecommendation.jsx # Modal for NotebookLM
└─ NotebookLMGuide.jsx         # 5-step setup guide
```

**Features:**
- Visual path selection with RECOMMENDED badges
- NotebookLM integration guide (downloadable)
- Smooth onboarding animation
- Conditional routing based on writer type

**2. AI Wizard Backend (~1,965 lines)**
```
backend/app/services/wizard/
├─ setup_wizard_agent.py       # Intelligent conversation agent
│  └─ Validates findings, disambiguates, creates files
├─ category_templates.py       # 8 comprehensive templates
│  ├─ Characters (15+ fields)
│  ├─ Story_Structure
│  ├─ World_Building
│  ├─ Themes_and_Philosophy
│  ├─ Voice_and_Craft
│  ├─ Antagonism_and_Conflict
│  ├─ Key_Beats_and_Pacing
│  └─ Research_and_Setting_Specifics
└─ model_router.py             # Task-specific model assignments

backend/app/services/ai/
└─ ollama_setup.py             # Llama 3.3 local AI integration
   ├─ Auto-download models
   ├─ Health checks
   └─ FREE local inference

backend/app/routes/
└─ wizard.py                   # WebSocket endpoint
   └─ Real-time streaming chat
```

**Features:**
- **FREE local AI** (Llama 3.3 via Ollama)
- Intelligent conversation (not just forms!)
- WebSocket streaming for real-time updates
- 8 comprehensive category templates (50+ total fields)
- Progress tracking across categories
- Cost optimization (free setup, paid analysis)

**3. AI Wizard Frontend (~388 lines)**
```
factory-frontend/src/components/wizard/
├─ ChatMessage.jsx             # AI/User message display
├─ ProgressSteps.jsx           # 8-category progress tracker
└─ AIWizard.jsx                # Complete chat interface

factory-frontend/src/pages/
└─ Wizard.tsx                  # Wizard page route
```

**Features:**
- Professional chat UI with markdown support
- Real-time WebSocket connection
- Visual progress tracking (8 categories)
- Multiple input types (text, select, textarea)
- Accessible, responsive design

#### Updated Architecture (Post-Session 4)

```
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND LAYER (Enhanced)                  │
├──────────────────────────┬──────────────────────────────────┤
│  Factory Frontend        │  Community Frontend              │
│  ├─ Home (NEW: Welcome)  │  [Unchanged]                     │
│  ├─ Wizard (NEW) ────────┼─ WebSocket ──→ Backend          │
│  ├─ Dashboard            │                                  │
│  ├─ Upload               │                                  │
│  ├─ Editor               │                                  │
│  └─ Analysis             │                                  │
└──────────────────────────┴──────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               BACKEND API LAYER (Enhanced)                   │
│  Routes:                                                     │
│  ├─ /wizard/ (NEW)      - WebSocket chat endpoint          │
│  ├─ /auth/                                                  │
│  ├─ /projects/                                              │
│  └─ ... (existing)                                          │
│                                                              │
│  Services:                                                   │
│  ├─ wizard/ (NEW)       - Wizard agent, templates, router  │
│  ├─ ai/ (NEW)           - Ollama/Llama 3.3 integration     │
│  ├─ FileParser                                              │
│  ├─ FactoryOrchestrator                                     │
│  └─ BadgeEngine                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI LAYER (Enhanced)                       │
│  Cloud AI:                                                   │
│  ├─ Claude, Gemini, GPT, Grok (scene analysis)             │
│                                                              │
│  Local AI (NEW):                                             │
│  └─ Ollama + Llama 3.3 (wizard, knowledge extraction)      │
│     └─ FREE - No API costs!                                 │
└─────────────────────────────────────────────────────────────┘
```

---

### 🚧 Session 5: Knowledge Graph & NotebookLM Integration

**Goal:** Add live knowledge graph with NotebookLM export

#### Components to Add:

**1. Knowledge Graph Backend**
```
backend/app/services/knowledge_graph/
├─ manager.py                  # Graph lifecycle management
├─ entity_extractor.py         # Extract entities from scenes
├─ exporter.py                 # Generate summaries for NotebookLM
└─ query_engine.py             # Query graph for context

backend/app/models/
└─ knowledge_entity.py         # KG entity model

backend/app/routes/
└─ knowledge_graph.py          # KG endpoints
```

**2. Knowledge Graph Frontend**
```
factory-frontend/src/components/
├─ SceneCompleteNotification.jsx # Notify graph updates
└─ ExportPanel.jsx               # Export UI for NotebookLM

factory-frontend/src/pages/
└─ KnowledgeGraph.tsx            # Visualization page
```

**Features:**
- Auto-update graph when scenes completed
- Entity extraction (characters, locations, themes)
- Export summaries to NotebookLM
- Bidirectional sync (scenes ↔ graph ↔ NotebookLM)
- Visual graph explorer
- Context queries for AI agents

#### Updated Architecture (Post-Session 5)

```
┌─────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE LAYER (NEW)                   │
├─────────────────────────────────────────────────────────────┤
│  Knowledge Graph:                                            │
│  ├─ Entities (characters, locations, themes)                │
│  ├─ Relationships (appears_in, conflicts_with, etc.)        │
│  └─ Metadata (descriptions, attributes, arcs)               │
│                                                              │
│  Integration:                                                │
│  ├─ Scenes → Entity Extraction → Graph Update              │
│  ├─ Graph → Context Queries → AI Agents                    │
│  └─ Graph → Export Summaries → NotebookLM                  │
└─────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS                      │
│  • NotebookLM (Google) - Upload summaries for RAG          │
│  • Ollama - Local AI inference (Llama 3.3)                 │
│  • Anthropic, OpenAI, Google, xAI - Cloud AI               │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
```yaml
Language: Python 3.11+
Framework: FastAPI 0.115.0
Database: PostgreSQL 15+ (via SQLAlchemy 2.0.36)
ORM: SQLAlchemy
Validation: Pydantic 2.10.3
Authentication: JWT (python-jose, passlib/bcrypt)
API Documentation: OpenAPI (Swagger UI)
Server: Uvicorn (ASGI)
File Processing:
  - python-docx (DOCX parsing)
  - PyPDF2 (PDF parsing)
  - charset-normalizer (encoding detection)
AI SDKs:
  - anthropic >= 0.18.0 (Claude)
  - openai >= 1.12.0 (GPT)
  - google-generativeai >= 0.3.0 (Gemini)
  - xai-sdk (Grok)
  - deepseek-sdk (DeepSeek)
Planned (Session 4):
  - ollama-python (Llama 3.3 local)
  - websockets (real-time chat)
```

### Frontend (Both Factory & Community)
```yaml
Language: TypeScript 5.9.3
Framework: React 19.2.0
Build Tool: Vite 7.2.2
Styling: Tailwind CSS 3.4.18
Routing: React Router 7.9.6
State Management:
  - Global: Zustand 5.0.8
  - Server: TanStack Query 5.90.10
HTTP Client: Axios 1.13.2
UI Components: Headless UI 2.2.9
Icons: Heroicons 2.2.0
Planned (Session 4):
  - WebSocket API (native)
  - react-markdown (chat messages)
```

### Infrastructure
```yaml
Backend Hosting: Railway
  - Auto-deploy from git
  - PostgreSQL addon
  - Environment variables
  - Custom domains

Frontend Hosting: Vercel
  - Auto-deploy from git
  - Edge network CDN
  - Preview deployments
  - Custom domains

Domains:
  - writersfactory.app (Factory)
  - writerscommunity.app (Community)
  - api.writersfactory.app (Backend - optional)

CI/CD: Git-based auto-deployment
Monitoring: Railway metrics + Vercel analytics
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │───┐
│ username    │   │
│ email       │   │
│ password    │   │
│ role        │   │
│ bio         │   │
└─────────────┘   │
                  │
       ┌──────────┴──────────┬─────────────────┬────────────────┐
       │                     │                 │                │
       ↓                     ↓                 ↓                ↓
┌─────────────┐      ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Project   │      │    Work     │  │   Comment   │  │   Rating    │
├─────────────┤      ├─────────────┤  ├─────────────┤  ├─────────────┤
│ id (PK)     │      │ id (PK)     │  │ id (PK)     │  │ id (PK)     │
│ user_id(FK) │      │ user_id(FK) │  │ user_id(FK) │  │ user_id(FK) │
│ title       │──┐   │ title       │  │ work_id(FK) │  │ work_id(FK) │
│ genre       │  │   │ content     │  │ content     │  │ score (1-5) │
│ status      │  │   │ genre       │  │ created_at  │  │ review      │
│ word_count  │  │   │ word_count  │  └─────────────┘  └─────────────┘
│ scene_count │  │   │ status      │
│ created_at  │  │   │ visibility  │
└─────────────┘  │   │ rating_avg  │
                 │   │ views_count │
       ┌─────────┘   └─────────────┘
       │                     │
       ↓                     ↓
┌─────────────┐      ┌─────────────┐
│    Scene    │      │    Badge    │
├─────────────┤      ├─────────────┤
│ id (PK)     │      │ id (PK)     │
│ project(FK) │      │ work_id(FK) │
│ content     │      │ badge_type  │
│ title       │      │ verified    │
│ chapter_num │      │ metadata    │
│ scene_num   │      │ created_at  │
│ sequence    │      └─────────────┘
│ word_count  │
│ scene_type  │
└─────────────┘
       │
       ↓
┌──────────────────┐
│  AnalysisResult  │
├──────────────────┤
│ id (PK)          │
│ project_id (FK)  │
│ scene_id (FK)    │
│ status           │
│ scene_outline    │
│ results_json     │
│ best_agent       │
│ best_score       │
│ hybrid_score     │
│ total_cost       │
│ total_tokens     │
│ started_at       │
│ completed_at     │
└──────────────────┘
```

### Key Models

#### Factory Models

**Project**
```python
- id: UUID (PK)
- user_id: UUID (FK → User)
- title: String(255)
- description: Text
- genre: String(100)
- status: Enum(draft, analyzing, analyzed, published)
- word_count: Integer
- scene_count: Integer
- original_filename: String(500)
- file_path: String(1000)
- created_at: DateTime
- updated_at: DateTime
```

**Scene**
```python
- id: UUID (PK)
- project_id: UUID (FK → Project)
- content: Text
- title: String(500)
- chapter_number: Integer
- scene_number: Integer
- sequence: Integer
- word_count: Integer
- scene_type: Enum(original, variation, hybrid)
- parent_scene_id: UUID (FK → Scene, nullable)
- created_at: DateTime
```

**AnalysisResult**
```python
- id: UUID (PK)
- project_id: UUID (FK → Project)
- scene_id: UUID (FK → Scene, nullable)
- status: Enum(pending, running, completed, failed)
- scene_outline: Text
- chapter: String(50)
- results_json: JSON
- best_agent: String(100)
- best_score: Float
- hybrid_score: Float (nullable)
- total_cost: Float
- total_tokens: Integer
- started_at: DateTime
- completed_at: DateTime
- error_message: Text
```

**Badge**
```python
- id: UUID (PK)
- work_id: UUID (FK → Work)
- badge_type: Enum(ai_analyzed, human_verified, human_self, community_upload)
- verified: Boolean
- metadata_json: JSON
- created_at: DateTime
```

#### Community Models

**Work**
```python
- id: UUID (PK)
- user_id: UUID (FK → User)
- title: String(500)
- content: Text
- summary: Text
- genre: String(100)
- word_count: Integer
- status: Enum(draft, published, archived)
- visibility: Enum(public, unlisted, private)
- factory_project_id: UUID (FK → Project, nullable)
- factory_scores: JSON (nullable)
- rating_average: Float
- rating_count: Integer
- comment_count: Integer
- views_count: Integer
- reads_count: Integer
- bookmarks_count: Integer
- created_at: DateTime
- updated_at: DateTime
```

**Comment, Rating, ReadingSession, etc.** - See full schema in database migrations

#### Planned Models (Session 5)

**KnowledgeEntity**
```python
- id: UUID (PK)
- project_id: UUID (FK → Project)
- entity_type: Enum(character, location, theme, object, event)
- name: String(255)
- description: Text
- attributes: JSON
- first_appearance: UUID (FK → Scene)
- metadata: JSON
- created_at: DateTime
- updated_at: DateTime
```

---

## API Architecture

### RESTful Endpoints

#### Authentication (`/api/auth/`)
```
POST   /register          - Create new user account
POST   /login             - Login (returns JWT)
GET    /me                - Get current user info
POST   /logout            - Logout (optional, client-side token removal)
```

#### Factory Projects (`/api/projects/`)
```
POST   /                  - Create new project from scratch
POST   /upload            - Upload file (DOCX/PDF/TXT) → auto-parse
GET    /                  - List user's projects (with filters)
GET    /{id}              - Get project details
PUT    /{id}              - Update project metadata
DELETE /{id}              - Delete project
GET    /{id}/scenes       - Get all scenes in project
POST   /{id}/scenes       - Add new scene manually
PUT    /scenes/{id}       - Update scene content
DELETE /scenes/{id}       - Delete scene
```

#### AI Analysis (`/api/analysis/`)
```
POST   /run               - Trigger AI tournament analysis
                            Body: {
                              project_id: UUID,
                              scene_outline: String,
                              chapter?: String,
                              agents?: String[],
                              synthesize?: Boolean
                            }
                            Returns: { job_id: UUID }

GET    /{job_id}/status   - Poll analysis progress
                            Returns: {
                              status: "pending"|"running"|"completed"|"failed",
                              ...
                            }

GET    /{job_id}/results  - Get full analysis results
                            Returns: {
                              summary: { best_agent, best_score, hybrid_score, ... },
                              full_results: { ... }
                            }

GET    /project/{id}/analyses - List all analyses for project
GET    /models            - List available AI models
```

#### Community Works (`/api/works/`)
```
GET    /                  - Browse published works (with filters)
                            Query: badge_type, genre, search, sort_by
POST   /                  - Create/publish work to Community
GET    /{id}              - Read specific work
PATCH  /{id}              - Update work
DELETE /{id}              - Delete work
POST   /{id}/like         - Like work
DELETE /{id}/like         - Unlike work
```

#### Comments (`/api/comments/`)
```
GET    /works/{id}        - Get all comments for work
POST   /works/{id}        - Add comment (requires reading validation)
PUT    /{id}              - Update own comment
DELETE /{id}              - Delete own comment
```

#### Ratings (`/api/ratings/`)
```
POST   /works/{id}        - Rate work 1-5 stars (requires full read)
PUT    /works/{id}        - Update rating
GET    /works/{id}        - Get all ratings for work
GET    /works/{id}/stats  - Get rating statistics
```

#### Community Upload (`/api/community/`)
```
POST   /upload            - Direct upload to Community with AI detection
                            Form data: file, title, description, genre, claim_human_authored
                            Returns: Work with auto-assigned badge
```

### Planned Endpoints (Session 4)

#### AI Wizard (`/api/wizard/`) - WebSocket
```
WS     /chat              - WebSocket endpoint for wizard conversation
                            Messages: {
                              type: "user_message"|"agent_response"|"progress_update",
                              content: String,
                              category?: String (1 of 8),
                              progress?: { current: Number, total: Number }
                            }

GET    /categories        - Get list of 8 category templates
GET    /categories/{name} - Get specific category template structure
POST   /categories/{name}/save - Save category data for project
```

### Planned Endpoints (Session 5)

#### Knowledge Graph (`/api/knowledge-graph/`)
```
POST   /projects/{id}/extract    - Extract entities from project scenes
GET    /projects/{id}/entities   - Get all entities for project
GET    /projects/{id}/graph      - Get graph visualization data
POST   /projects/{id}/query      - Query graph for context
                                    Body: { query: String, entity_type?: String }
GET    /projects/{id}/export     - Export summary for NotebookLM
POST   /projects/{id}/sync       - Sync with NotebookLM
```

---

## Frontend Architecture

### Factory Frontend Structure

```
factory-frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios instance with auth
│   │   └── factory.ts             # API endpoint functions
│   ├── components/
│   │   ├── Layout.tsx             # Navigation header
│   │   ├── ProtectedRoute.tsx    # Auth guard
│   │   └── wizard/                # Session 4
│   │       ├── ChatMessage.jsx
│   │       ├── ProgressSteps.jsx
│   │       └── AIWizard.jsx
│   ├── pages/
│   │   ├── Home.tsx               # Landing + welcome flow (Session 4)
│   │   ├── Login.tsx              # Authentication
│   │   ├── Register.tsx           # User registration
│   │   ├── Dashboard.tsx          # Project list + management
│   │   ├── Upload.tsx             # File upload interface
│   │   ├── Editor.tsx             # Scene viewer/editor
│   │   ├── Analysis.tsx           # AI analysis workflow
│   │   └── Wizard.tsx             # Session 4: AI wizard
│   ├── store/
│   │   └── authStore.ts           # Zustand auth state
│   ├── types/
│   │   └── index.ts               # TypeScript definitions
│   ├── App.tsx                    # Main app with routing
│   ├── main.tsx                   # Entry point
│   └── index.css                  # Tailwind styles
├── .env
├── .env.example
├── package.json
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── vercel.json
```

### Community Frontend Structure

```
community-frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios instance with auth
│   │   └── community.ts           # API endpoint functions
│   ├── components/
│   │   ├── Badge.tsx              # Badge display component
│   │   └── Layout.tsx             # Navigation + footer
│   ├── pages/
│   │   ├── Home.tsx               # Landing + badge explainer
│   │   ├── Browse.tsx             # Browse works with filters
│   │   ├── ViewWork.tsx           # Read work + comments
│   │   ├── Upload.tsx             # Direct upload with AI detection
│   │   ├── Login.tsx              # Authentication
│   │   └── Register.tsx           # User registration
│   ├── store/
│   │   └── authStore.ts           # Zustand auth state
│   ├── types/
│   │   └── index.ts               # TypeScript definitions
│   ├── App.tsx                    # Main app with routing
│   ├── main.tsx                   # Entry point
│   └── index.css                  # Tailwind styles
├── .env
├── .env.example
├── package.json
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── vercel.json
```

### State Management Philosophy

**Zustand (Global Client State):**
- Authentication state (user, token, isAuthenticated)
- Simple, predictable, minimal boilerplate
- Persists to localStorage

**TanStack Query (Server State):**
- API data fetching and caching
- Automatic refetching and invalidation
- Loading/error states
- Optimistic updates
- Query key-based cache management

**Local State:**
- Form inputs (useState)
- UI state (modals, dropdowns)
- Component-specific logic

---

## AI Engine Architecture

### Tournament System Flow

```
1. User Triggers Analysis
   ↓
2. Create AnalysisResult (status: pending)
   ↓
3. Background Job Starts
   ↓
4. Update Status → running
   ↓
5. Tournament Execution:
   ├─ Generate (Parallel)
   │  ├─ Claude Sonnet 4.5 → Scene variation
   │  ├─ Gemini 1.5 Pro → Scene variation
   │  ├─ GPT-4o → Scene variation
   │  ├─ Grok 2 → Scene variation
   │  └─ Claude Haiku → Scene variation (budget)
   │
   ├─ Score (Sequential)
   │  └─ Each variation scored on 7 dimensions (0-70 total):
   │     ├─ Voice Authenticity (0-10)
   │     ├─ Pacing/Tension (0-10)
   │     ├─ Dialogue Naturalness (0-10)
   │     ├─ Show Don't Tell (0-10)
   │     ├─ Character Development (0-10)
   │     ├─ Emotional Impact (0-10)
   │     └─ Prose Quality (0-10)
   │
   ├─ Critique (Cross-Agent)
   │  └─ Each agent critiques all other variations
   │
   └─ Synthesize (Optional)
      └─ If synthesize=true AND scores > threshold:
         └─ Merge best elements from top variations
   ↓
6. Store Results
   ├─ results_json: Full tournament data
   ├─ best_agent: Model with highest score
   ├─ best_score: Top score achieved
   ├─ hybrid_score: Synthesized version score
   ├─ total_cost: Sum of API costs
   └─ total_tokens: Sum of tokens used
   ↓
7. Update Status → completed
   ↓
8. Frontend Polls → Gets Results
```

### Cost Tracking

**Per-Model Costs (Approximate):**
- Claude Sonnet 4.5: $3/1M input, $15/1M output
- Gemini 1.5 Pro: $1.25/1M input, $5/1M output
- GPT-4o: $2.50/1M input, $10/1M output
- Grok 2: $2/1M input, $10/1M output
- Claude Haiku: $0.25/1M input, $1.25/1M output

**Typical Scene Analysis:**
- Input: ~2k tokens (scene outline + context)
- Output per model: ~1k tokens (variation)
- Total tokens: ~5 models × 3k = 15k tokens
- Estimated cost: $0.30-$0.50 per scene

**Planned (Session 4):**
- Llama 3.3 via Ollama: **$0** (local inference)
- Use for wizard, knowledge extraction
- Save cloud API credits for actual writing

---

## Deployment Architecture

### Current Deployment

```
┌────────────────────────────────────────────────────────────┐
│                     PRODUCTION STACK                        │
└────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│  Vercel (CDN)    │         │  Vercel (CDN)    │
│  Factory Frontend│         │Community Frontend│
│                  │         │                  │
│  writersfactory  │         │writerscommunity  │
│  .app            │         │.app              │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         └────────────┬───────────────┘
                      │ HTTPS
                      ↓
         ┌────────────────────────┐
         │   Railway              │
         │   Backend API          │
         │                        │
         │   writers-platform     │
         │   -production          │
         │   .up.railway.app      │
         └────────┬───────────────┘
                  │
                  ↓
         ┌────────────────────────┐
         │   Railway              │
         │   PostgreSQL           │
         │                        │
         │   (Addon Database)     │
         └────────────────────────┘
```

### Environment Variables

**Backend (Railway):**
```bash
# Database
DATABASE_URL=postgresql://...  # Auto-provided by Railway

# Security
SECRET_KEY=<32-byte-hex>
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
XAI_API_KEY=...
DEEPSEEK_API_KEY=...

# Google Cloud (optional, for Gemini File Search)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# CORS Origins
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://writersfactory.app,https://writerscommunity.app,https://*.vercel.app
```

**Factory Frontend (Vercel):**
```bash
VITE_API_URL=https://writers-platform-production.up.railway.app/api
```

**Community Frontend (Vercel):**
```bash
VITE_API_URL=https://writers-platform-production.up.railway.app/api
```

### Deployment Process

**Backend (Railway):**
1. Push to `main` or session branch
2. Railway auto-detects Python
3. Runs `pip install -r requirements.txt`
4. Starts with `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Database migrations run on startup (if configured)

**Frontend (Vercel):**
1. Connect GitHub repo
2. Set root directory (`factory-frontend` or `community-frontend`)
3. Auto-detects Vite
4. Runs `npm run build`
5. Deploys `dist/` to CDN
6. Preview deployments for PRs

---

## Security & Authentication

### JWT Authentication Flow

```
1. User Registration/Login
   ↓
2. Server Validates Credentials
   ↓
3. Server Generates JWT Token
   {
     sub: user_id,
     exp: expiration_timestamp,
     iat: issued_at_timestamp
   }
   ↓
4. Client Stores Token (localStorage)
   ↓
5. Client Includes Token in Headers
   Authorization: Bearer <token>
   ↓
6. Server Validates Token on Each Request
   ├─ Valid → Process request
   └─ Invalid → 401 Unauthorized
```

### Security Measures

**Backend:**
- ✅ Password hashing (bcrypt)
- ✅ JWT token signing (HS256)
- ✅ CORS configuration
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (Pydantic validation)
- ✅ Rate limiting (planned)
- ✅ Environment variable secrets

**Frontend:**
- ✅ HttpOnly cookies for tokens (planned upgrade from localStorage)
- ✅ CSRF protection (planned)
- ✅ Input validation
- ✅ Protected routes (auth required)
- ✅ Secure API calls (HTTPS only)

**Database:**
- ✅ Parameterized queries (ORM)
- ✅ Row-level security (user_id checks)
- ✅ Encrypted connections (SSL)
- ✅ Regular backups (Railway automatic)

---

## Development Roadmap

### ✅ Phase 1: Core Platform (COMPLETE)
**Sessions 1-3 (Completed November 2025)**

- ✅ Backend API with 15+ routes
- ✅ PostgreSQL database with 16 models
- ✅ File parsing (DOCX/PDF/TXT)
- ✅ AI tournament system (5 models)
- ✅ Badge engine (4 badge types)
- ✅ Factory frontend (7 pages)
- ✅ Community frontend (6 pages)
- ✅ Deployment to Railway + Vercel
- ✅ Documentation (README, DEPLOYMENT.md)

**Status:** Production-ready, Factory deployed, Community ready

---

### 🚧 Phase 2: Enhanced Onboarding (PLANNED)
**Session 4 (Estimated: 1 full session, ~15-20 hours)**

**Goals:**
- Migrate sophisticated onboarding from writers-factory-core
- Add FREE local AI for setup (Llama 3.3)
- Implement intelligent AI wizard conversation
- Create 8 comprehensive category templates

**Components:**
1. ✅ Welcome Flow (~830 lines)
   - PathSelectionStep (3 writer types)
   - NotebookLM recommendation + guide

2. ✅ AI Wizard Backend (~1,965 lines)
   - setup_wizard_agent.py (conversation intelligence)
   - category_templates.py (8 templates, 50+ fields)
   - model_router.py (task-specific AI selection)
   - ollama_setup.py (Llama 3.3 integration)
   - wizard.py (WebSocket endpoint)

3. ✅ AI Wizard Frontend (~388 lines)
   - ChatMessage.jsx (message display)
   - ProgressSteps.jsx (8-category tracker)
   - AIWizard.jsx (complete chat UI)

**Value:**
- Cost savings (free setup vs. paid API)
- Better onboarding UX
- Structured story knowledge
- NotebookLM integration

**Success Criteria:**
- Users can select writer path
- AI wizard extracts knowledge via conversation
- 8 category files generated automatically
- $0 cost for entire setup process

---

### 🚧 Phase 3: Knowledge Graph (PLANNED)
**Session 5 (Estimated: 1 full session, ~15-20 hours)**

**Goals:**
- Live knowledge graph auto-updates
- NotebookLM export for RAG
- Bidirectional sync (scenes ↔ graph ↔ NotebookLM)
- Visual graph explorer

**Components:**
1. ✅ Knowledge Graph Backend
   - manager.py (lifecycle)
   - entity_extractor.py (auto-extraction)
   - exporter.py (NotebookLM summaries)
   - query_engine.py (context queries)

2. ✅ Knowledge Graph Frontend
   - SceneCompleteNotification.jsx
   - ExportPanel.jsx
   - KnowledgeGraph.tsx (visualization)

**Value:**
- Automatic knowledge extraction
- Context-aware AI agents
- NotebookLM integration for RAG
- Consistent story knowledge

**Success Criteria:**
- Scenes auto-update graph on completion
- Entities extracted (characters, locations, themes)
- Export summaries to NotebookLM
- AI agents query graph for context

---

### 🔮 Phase 4: Advanced Features (FUTURE)

**Potential Features:**
1. **Collaborative Editing**
   - Real-time co-editing (WebSocket)
   - Comments and suggestions
   - Change tracking

2. **Version Control**
   - Git-like versioning for manuscripts
   - Branch/merge scenes
   - Compare versions

3. **Advanced Analytics**
   - Writing velocity tracking
   - Style consistency over time
   - Agent performance trends

4. **Multi-Format Export**
   - EPUB generation
   - MOBI for Kindle
   - Print-ready PDF
   - Audio narration support

5. **Advanced Cost Optimization**
   - Model selection based on budget
   - Batch processing discounts
   - Smart caching of similar scenes

6. **Professional Features**
   - Submission tracking
   - Contract management
   - Rights tracking
   - Royalty calculations

7. **Community Enhancements**
   - Private messaging
   - Recommendation engine
   - Activity feeds
   - Content curation tools

---

## Monitoring & Observability

### Current Monitoring

**Railway (Backend):**
- CPU/Memory usage
- Request logs
- Error logs
- Database queries
- Deployment history

**Vercel (Frontend):**
- Web vitals (LCP, FID, CLS)
- Edge network performance
- Build logs
- Preview deployment status

### Planned Monitoring

**Application-Level:**
- Request tracing (OpenTelemetry)
- Error tracking (Sentry)
- Performance monitoring (DataDog/New Relic)
- User analytics (PostHog/Mixpanel)

**AI-Specific:**
- Model latency tracking
- Cost per request
- Token usage trends
- Success/failure rates
- Agent performance comparison

---

## Testing Strategy

### Current Testing (Minimal)

**Manual Testing:**
- API endpoint testing via Swagger UI
- Frontend flow testing in browser
- Cross-browser compatibility
- Mobile responsive testing

### Planned Testing

**Backend:**
- Unit tests (pytest)
- Integration tests (FastAPI TestClient)
- Database tests (in-memory SQLite)
- API contract tests

**Frontend:**
- Unit tests (Vitest)
- Component tests (React Testing Library)
- E2E tests (Playwright)
- Visual regression tests

**AI Engine:**
- Agent response validation
- Cost calculation accuracy
- Tournament consistency
- Knowledge graph integrity

---

## Performance Optimization

### Current Optimizations

**Backend:**
- SQLAlchemy query optimization
- Connection pooling
- Background jobs for long-running tasks
- JSON response caching

**Frontend:**
- Code splitting (Vite automatic)
- Tree shaking (Vite automatic)
- Image optimization
- CDN delivery (Vercel)

### Planned Optimizations

**Backend:**
- Redis caching layer
- Database indexing strategy
- Query result pagination
- Celery for distributed jobs

**Frontend:**
- Route-based code splitting
- Lazy loading images
- Service worker caching
- Virtual scrolling for long lists

**AI:**
- Prompt caching (Anthropic)
- Response streaming
- Parallel API calls
- Smart model routing (cheap for simple, expensive for complex)

---

## Appendix: Quick Reference

### Key Repositories
- Main: `gcharris/writers-platform`
- Legacy: `gcharris/writers-factory-core` (being consolidated)
- Legacy: `gcharris/writers-community` (being consolidated)

### Key Branches
- `main` - Production code
- `claude/build-backend-api-*` - Active development
- Session branches for each feature set

### Key URLs
- **Production:**
  - Factory: https://writers-platform.vercel.app (temp)
  - Community: (pending deployment)
  - Backend API: https://writers-platform-production.up.railway.app/api

- **Documentation:**
  - OpenAPI: https://writers-platform-production.up.railway.app/docs
  - ReDoc: https://writers-platform-production.up.railway.app/redoc

### Key Contacts
- Repository Owner: gcharris
- Development: Claude (AI assistant)
- Deployment: Railway + Vercel

---

## Document Versioning

**Version 1.0** - November 17, 2025
- Initial architecture document
- Sessions 1-3 complete
- Sessions 4-5 planned

**Next Update:** After Session 4 completion
- Add wizard implementation details
- Update with Ollama integration
- Document WebSocket architecture

---

*This document serves as the single source of truth for the Writers Platform architecture. Update it as the system evolves.*
