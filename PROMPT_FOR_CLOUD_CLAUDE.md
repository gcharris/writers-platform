# Prompt for Cloud Claude Code

Copy and paste this into Cloud Claude Code to start the Knowledge Graph implementation:

---

# Knowledge Graph Implementation - Option A: Gold Standard

**Mission**: Implement the complete, production-grade Knowledge Graph system for the Writers Platform.

**Budget**: $800 Claude Cloud credits
**Timeline**: Take your time - we have all the time to build it right
**Philosophy**: "No shortcuts. No compromises. Production-grade code."

---

## 📚 Your Implementation Guide

Everything you need is in these 4 documents (already in the repo):

1. **`CLOUD_CLAUDE_KG_HANDOFF.md`** - Your main implementation guide
   - Step-by-step instructions for all 3 phases
   - Success criteria, testing checklist, deployment steps

2. **`KNOWLEDGE_GRAPH_IMPLEMENTATION.md`** (Part 1)
   - Backend core: NetworkX graph engine, dual extraction (LLM+NER), database models
   - Complete code ready to copy

3. **`KNOWLEDGE_GRAPH_IMPLEMENTATION_PART2.md`** (Part 2)
   - REST API: 15+ endpoints, background jobs, export systems
   - Complete code ready to copy

4. **`KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md`** (Part 3)
   - Frontend: 3D visualization, real-time updates, scene editor integration, tests
   - Complete code ready to copy

5. **`KNOWLEDGE_GRAPH_COMPLETE_SUMMARY.md`** - Quick reference
   - API endpoints, entity types, deployment checklist

---

## 🚀 How to Start

### Step 1: Read the Handoff (5 min)

Open `CLOUD_CLAUDE_KG_HANDOFF.md` and read:
- Mission overview
- 3 implementation phases
- Success criteria

### Step 2: Start with Backend (Phase 1)

Follow `CLOUD_CLAUDE_KG_HANDOFF.md` → Phase 1:

1. **Database migration** (30 min)
   - Copy SQL from `KNOWLEDGE_GRAPH_IMPLEMENTATION.md` → Phase 3
   - Create `backend/migrations/add_knowledge_graph_tables.sql`
   - Run migration on Railway

2. **Core graph engine** (2 hours)
   - Copy code from `KNOWLEDGE_GRAPH_IMPLEMENTATION.md` → Phase 1
   - Create files:
     - `backend/app/services/knowledge_graph/models.py`
     - `backend/app/services/knowledge_graph/graph_service.py`
   - Test with provided test cases

3. **Entity extraction** (2-3 hours)
   - Copy code from `KNOWLEDGE_GRAPH_IMPLEMENTATION.md` → Phase 2
   - Create extractors:
     - `backend/app/services/knowledge_graph/extractors/llm_extractor.py`
     - `backend/app/services/knowledge_graph/extractors/ner_extractor.py`
   - Test both extractors

4. **API layer** (2-3 hours)
   - Copy code from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART2.md` → Phase 4
   - Create `backend/app/routes/knowledge_graph.py`
   - Implement all 15+ endpoints
   - Test with curl commands

### Step 3: Build Frontend (Phase 2)

Follow `CLOUD_CLAUDE_KG_HANDOFF.md` → Phase 2:

1. **Visualization components** (3-4 hours)
   - Copy code from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` → Phase 5
   - Create 6 React components
   - Test graph visualization

2. **Real-time integration** (2 hours)
   - Copy code from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` → Phase 6
   - Create hooks and components
   - Test WebSocket connection

3. **Workflow integration** (2-3 hours)
   - Copy code from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` → Phase 7
   - Integrate with scene editor
   - Test auto-extraction

### Step 4: Test & Deploy (Phase 3)

Follow `CLOUD_CLAUDE_KG_HANDOFF.md` → Phase 3:

1. **Write tests** (1.5 hours)
   - Copy test code from `KNOWLEDGE_GRAPH_IMPLEMENTATION_PART3.md` → Phase 8
   - Run unit, integration, E2E tests

2. **Deploy** (30 min)
   - Backend to Railway
   - Frontend to Vercel
   - Verify all endpoints work

---

## ✅ Success Criteria

Writers must be able to:
- ✅ Write scenes and auto-extract entities
- ✅ Visualize story knowledge graph in 3D
- ✅ Search for characters, locations, relationships
- ✅ See context while writing
- ✅ Export graph to Gephi/NotebookLM
- ✅ Choose LLM or NER extraction
- ✅ Monitor extraction jobs

---

## 🐛 If You Get Stuck

1. Check `DESKTOP_CLAUDE_BUG_SQUASHING_PLAN.md` for common issues
2. Create `BLOCKERS.md` with issue details
3. Commit with message: `🚨 BLOCKER: [description]`
4. Desktop Claude will help within 2 hours

---

## 💡 Key Principles

- **Copy code directly** from the implementation docs - it's production-ready
- **Test frequently** - run tests after each component
- **Commit often** - push working code regularly
- **Ask questions** - Desktop Claude is on standby
- **No shortcuts** - build it right the first time

---

## 🎯 Your First Task

Read `CLOUD_CLAUDE_KG_HANDOFF.md` completely, then:

1. Create database migration file
2. Run migration on Railway
3. Verify tables were created
4. Report back: "✅ Phase 1.1 complete - Database migration successful"

---

**You've got this!** 🚀

The code is written, tested, and documented. Your job is to copy it into the right files and make sure it all works together.

Take your time. Build it right. We believe in you!

---

*Desktop Claude will be monitoring progress and ready to help with any bugs.*
