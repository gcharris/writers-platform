# Phase 2: Community Platform Migration - UPDATED PLAN

**Status**: 📋 **READY TO START**
**Created**: 2025-01-18 (Updated after Knowledge Graph + Copilot completion)
**Priority**: HIGH (Complete public platform)
**Budget**: ~$200-300 (6-8 hours)

---

## What Changed Since Original Plan

**Original Plan** (from MASTER_ROADMAP.md):
- Written BEFORE Knowledge Graph (Phases 1-8) completion
- Written BEFORE Copilot implementation
- Assumed minimal frontend existed

**Current Reality**:
- ✅ Community-frontend EXISTS with Badge components, pages, vercel.json
- ✅ Knowledge Graph system COMPLETE (can showcase entity graphs for published works)
- ✅ Copilot system COMPLETE (can offer FREE writing assistance to Community)
- ✅ Home page has Factory CTAs and badge explainer
- ❌ Backend missing Badge table, Factory linking, AI detection
- ❌ Browse doesn't filter by badge type
- ❌ No knowledge graph visualization for published works

---

## Current State Analysis

### ✅ What's Already Implemented

**Frontend** (`community-frontend/`):
- Badge component with 4 badge types (ai_analyzed, human_verified, human_self, community_upload)
- BadgeExplainer component for landing page
- Home page with "Discover AI-Validated Fiction" hero
- Factory CTAs ("Try Writers Factory →")
- Browse page with filters
- Upload page
- ViewWork page
- API client configured
- vercel.json ready for deployment

**Backend**:
- `/api/works/` - Basic CRUD for works
- `/api/browse/` - Browse with filters (genre, rating, word count)
- `/api/browse/search` - Full-text search
- Work model with ratings, comments, engagement stats

### ❌ What's Missing

**Backend**:
1. ❌ Badge table and model
2. ❌ Work.factory_project_id (link to Factory projects)
3. ❌ Work.factory_scores (store AI analysis scores)
4. ❌ Badge relationship on Work model
5. ❌ AI detection service for direct uploads
6. ❌ Badge assignment logic
7. ❌ Browse filter by badge_type
8. ❌ Knowledge graph export for published works

**Frontend**:
1. ❌ Browse page doesn't use badge_type filter
2. ❌ ViewWork doesn't show knowledge graph visualization
3. ❌ Upload doesn't offer AI detection
4. ❌ No copilot integration for Community writers
5. ❌ Factory integration CTAs could be improved

---

## New Opportunities (From Knowledge Graph + Copilot)

### 1. Knowledge Graph Showcase
**Feature**: Show entity graphs for AI-Analyzed works

**User Value**: Readers can explore characters, locations, relationships in 3D before reading

**Implementation**:
- Add "Explore Knowledge Graph" tab on ViewWork page
- Embed GraphVisualization component (already exists from Phase 8)
- Query `/api/knowledge-graph/projects/{factory_project_id}/graph`
- Show purple NotebookLM-sourced entities if applicable

### 2. FREE Copilot for Community
**Feature**: Offer copilot mode to Community writers during upload

**User Value**: Writers can get real-time AI assistance WITHOUT paying for Factory

**Implementation**:
- Add CopilotEditor option on Upload page (already exists from Copilot implementation)
- Connect to `/api/copilot/{temp_project_id}/stream`
- Create temporary project for copilot context
- After writing, offer "Publish to Community" or "Continue in Factory"

### 3. Entity-Based Discovery
**Feature**: Browse works by characters, locations, themes

**User Value**: "Find sci-fi stories with AI characters" or "Stories set in Shanghai"

**Implementation**:
- Add entity search: `/api/browse/by-entity?entity_name=Mickey&entity_type=character`
- Query knowledge graphs for works containing entity
- Show works with matching entities

### 4. Research Citations
**Feature**: Show NotebookLM research sources for AI-Analyzed works

**User Value**: Readers see the research foundation behind the story

**Implementation**:
- If work has knowledge graph with NotebookLM entities
- Show "Research Foundation" panel
- List NotebookLM sources with citations

---

## Updated Implementation Plan

### Step 1: Backend - Badge System (1.5 hours)

**1.1: Create Badge Model** (`backend/app/models/badge.py`):

```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Badge(Base):
    __tablename__ = "badges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_id = Column(UUID(as_uuid=True), ForeignKey("works.id", ondelete="CASCADE"))
    badge_type = Column(String(50), nullable=False)
    # badge_type: ai_analyzed, human_verified, human_self, community_upload

    verified = Column(Boolean, default=False)
    metadata_json = Column(JSON, default=dict)
    # metadata_json for ai_analyzed:
    # {
    #   "score": 65,
    #   "best_agent": "claude-sonnet-4.5",
    #   "models_used": ["claude", "gemini", "gpt"],
    #   "factory_project_id": "uuid-123"
    # }
    # metadata_json for human_verified:
    # {
    #   "confidence": 92,
    #   "detection_model": "copyleaks",
    #   "verified_at": "2025-01-18T..."
    # }

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    work = relationship("Work", back_populates="badges")
```

**1.2: Update Work Model** (`backend/app/models/work.py`):

```python
# Add fields
factory_project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
factory_scores = Column(JSON, nullable=True)
# factory_scores: {"best_score": 65, "hybrid_score": 68, "models": [...]}

# Add relationships
badges = relationship("Badge", back_populates="work", cascade="all, delete-orphan")
factory_project = relationship("Project", backref="published_works")
```

**1.3: Database Migration** (`backend/migrations/add_community_badges.sql`):

```sql
-- Create badges table
CREATE TABLE IF NOT EXISTS badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_id UUID NOT NULL REFERENCES works(id) ON DELETE CASCADE,
    badge_type VARCHAR(50) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    metadata_json JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes
CREATE INDEX idx_badges_work_id ON badges(work_id);
CREATE INDEX idx_badges_type ON badges(badge_type);

-- Add Factory linking to works
ALTER TABLE works
ADD COLUMN IF NOT EXISTS factory_project_id UUID REFERENCES projects(id),
ADD COLUMN IF NOT EXISTS factory_scores JSONB;

CREATE INDEX idx_works_factory_project ON works(factory_project_id);
```

---

### Step 2: Backend - Badge Assignment Logic (1 hour)

**File**: `backend/app/services/badge_service.py`

```python
"""
Badge Assignment Service
Automatically assigns badges based on work source and analysis
"""
from typing import Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.work import Work
from app.models.badge import Badge
from app.models.project import Project

class BadgeService:
    """Service for assigning and managing badges"""

    @staticmethod
    def assign_badge_for_factory_work(
        work: Work,
        factory_project: Project,
        db: Session
    ) -> Badge:
        """
        Assign AI-Analyzed badge to work published from Factory.

        Args:
            work: Work model instance
            factory_project: Source Factory project
            db: Database session

        Returns:
            Created Badge instance
        """
        # Get latest analysis result
        analysis = factory_project.analysis_results[-1] if factory_project.analysis_results else None

        metadata = {}
        if analysis:
            metadata = {
                "score": analysis.best_score,
                "best_agent": analysis.best_agent,
                "hybrid_score": analysis.hybrid_score,
                "models_used": ["claude", "gemini", "gpt", "grok", "deepseek"],
                "factory_project_id": str(factory_project.id),
                "analysis_cost": analysis.total_cost
            }

        badge = Badge(
            work_id=work.id,
            badge_type="ai_analyzed",
            verified=True,
            metadata_json=metadata
        )

        db.add(badge)
        return badge

    @staticmethod
    async def detect_ai_authorship(content: str) -> Dict:
        """
        Detect if content was AI-generated using multiple detection models.

        Args:
            content: Text content to analyze

        Returns:
            Detection result with confidence score
        """
        # TODO: Integrate with Copyleaks, GPTZero, or similar
        # For now, return placeholder

        # Simple heuristic: check for common AI patterns
        ai_phrases = [
            "as an ai", "i don't have personal", "i can't provide",
            "it's important to note", "delve into", "navigate the landscape"
        ]

        content_lower = content.lower()
        matches = sum(1 for phrase in ai_phrases if phrase in content_lower)

        confidence = max(0, 100 - (matches * 20))  # Rough estimate

        return {
            "is_human": confidence > 50,
            "confidence": confidence,
            "detection_model": "simple_heuristic",
            "details": f"Found {matches} AI-like phrases"
        }

    @staticmethod
    async def assign_badge_for_upload(
        work: Work,
        claim_human_authored: bool,
        db: Session
    ) -> Badge:
        """
        Assign badge for direct community upload based on AI detection.

        Args:
            work: Work model instance
            claim_human_authored: Whether author claims human authorship
            db: Database session

        Returns:
            Created Badge instance
        """
        if not claim_human_authored:
            # User didn't claim human authorship
            badge = Badge(
                work_id=work.id,
                badge_type="community_upload",
                verified=False,
                metadata_json={}
            )
        else:
            # Run AI detection
            detection = await BadgeService.detect_ai_authorship(work.content)

            if detection["is_human"] and detection["confidence"] >= 80:
                # High confidence human authorship
                badge = Badge(
                    work_id=work.id,
                    badge_type="human_verified",
                    verified=True,
                    metadata_json={
                        "confidence": detection["confidence"],
                        "detection_model": detection["detection_model"],
                        "details": detection["details"]
                    }
                )
            elif detection["is_human"]:
                # Medium confidence - self-certified
                badge = Badge(
                    work_id=work.id,
                    badge_type="human_self",
                    verified=True,
                    metadata_json={
                        "confidence": detection["confidence"],
                        "note": "Self-certified by author"
                    }
                )
            else:
                # Likely AI-generated
                badge = Badge(
                    work_id=work.id,
                    badge_type="community_upload",
                    verified=False,
                    metadata_json={
                        "note": "AI authorship detected",
                        "confidence": detection["confidence"]
                    }
                )

        db.add(badge)
        return badge
```

---

### Step 3: Backend - API Updates (1 hour)

**3.1: Update Works Endpoints** (`backend/app/routes/works.py`):

```python
from app.services.badge_service import BadgeService
from app.schemas.work import WorkCreateWithBadge

@router.post("/", response_model=WorkResponse, status_code=status.HTTP_201_CREATED)
async def create_work(
    work_data: WorkCreateWithBadge,
    claim_human_authored: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new work with automatic badge assignment."""

    word_count = len(work_data.content.split())

    work = Work(
        author_id=current_user.id,
        title=work_data.title,
        genre=work_data.genre,
        content_rating=work_data.content_rating,
        content=work_data.content,
        word_count=word_count,
        summary=work_data.summary,
        status="draft"
    )

    db.add(work)
    db.flush()  # Get work.id before creating badge

    # Assign badge based on upload type
    badge = await BadgeService.assign_badge_for_upload(
        work=work,
        claim_human_authored=claim_human_authored,
        db=db
    )

    db.commit()
    db.refresh(work)

    return work

@router.post("/from-factory/{factory_project_id}")
async def publish_from_factory(
    factory_project_id: UUID,
    title: str,
    summary: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a Factory project to Community with AI-Analyzed badge."""

    # Get Factory project
    project = db.query(Project).filter(
        Project.id == factory_project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(404, "Project not found")

    # Combine all scenes into content
    scenes = db.query(Scene).filter(Scene.project_id == factory_project_id).order_by(Scene.sequence).all()
    content = "\n\n".join([f"# {scene.title}\n\n{scene.content}" for scene in scenes])

    # Create work
    work = Work(
        author_id=current_user.id,
        title=title,
        summary=summary,
        genre=project.genre,
        content=content,
        word_count=project.word_count,
        factory_project_id=factory_project_id,
        status="published",
        visibility="public"
    )

    # Get Factory scores
    if project.analysis_results:
        latest_analysis = project.analysis_results[-1]
        work.factory_scores = {
            "best_score": latest_analysis.best_score,
            "hybrid_score": latest_analysis.hybrid_score,
            "total_cost": latest_analysis.total_cost
        }

    db.add(work)
    db.flush()

    # Assign AI-Analyzed badge
    badge = BadgeService.assign_badge_for_factory_work(
        work=work,
        factory_project=project,
        db=db
    )

    db.commit()
    db.refresh(work)

    return work
```

**3.2: Update Browse Endpoints** (`backend/app/routes/browse.py`):

Add badge_type filter:

```python
@router.get("/works", response_model=BrowseResponse)
async def browse_works(
    badge_type: Optional[str] = None,  # NEW PARAMETER
    genre: Optional[str] = None,
    # ... other parameters
    db: Session = Depends(get_db)
):
    """Browse works with filters and pagination."""

    # Build query
    query = db.query(Work).filter(
        and_(
            Work.status == "published",
            Work.visibility == "public"
        )
    ).join(User, Work.author_id == User.id)

    # NEW: Filter by badge type
    if badge_type:
        query = query.join(Badge).filter(Badge.badge_type == badge_type)

    # ... rest of function
```

---

### Step 4: Frontend - Badge Filter Integration (30 minutes)

**File**: `community-frontend/src/pages/Browse.tsx`

Update to include badge filter:

```typescript
const [filters, setFilters] = useState({
  genre: '',
  badge_type: '',  // NEW
  min_rating: 0,
  search: ''
});

// Badge filter dropdown
<select
  value={filters.badge_type}
  onChange={(e) => setFilters({ ...filters, badge_type: e.target.value })}
  className="px-4 py-2 border border-gray-300 rounded-lg"
>
  <option value="">All Badges</option>
  <option value="ai_analyzed">AI-Analyzed</option>
  <option value="human_verified">Human-Verified</option>
  <option value="human_self">Self-Certified</option>
  <option value="community_upload">Community Upload</option>
</select>
```

---

### Step 5: Frontend - Knowledge Graph Showcase (1.5 hours)

**File**: `community-frontend/src/pages/ViewWork.tsx`

Add knowledge graph visualization tab for AI-Analyzed works:

```typescript
import { GraphVisualization } from '../../factory-frontend/src/components/knowledge-graph/GraphVisualization';

export default function ViewWork() {
  const [activeTab, setActiveTab] = useState<'read' | 'graph'>('read');
  const [work, setWork] = useState<Work | null>(null);

  // Check if work has Factory project (and thus knowledge graph)
  const hasKnowledgeGraph = work?.factory_project_id &&
                            work?.badges?.some(b => b.badge_type === 'ai_analyzed');

  return (
    <div>
      {/* Tabs */}
      {hasKnowledgeGraph && (
        <div className="border-b border-gray-200 mb-6">
          <nav className="flex gap-8">
            <button
              onClick={() => setActiveTab('read')}
              className={`py-4 px-1 border-b-2 ${
                activeTab === 'read'
                  ? 'border-sky-500 text-sky-600'
                  : 'border-transparent text-gray-500'
              }`}
            >
              Read Story
            </button>
            <button
              onClick={() => setActiveTab('graph')}
              className={`py-4 px-1 border-b-2 ${
                activeTab === 'graph'
                  ? 'border-sky-500 text-sky-600'
                  : 'border-transparent text-gray-500'
              }`}
            >
              Explore Knowledge Graph
            </button>
          </nav>
        </div>
      )}

      {/* Content */}
      {activeTab === 'read' && (
        <div className="prose max-w-none">
          {work?.content}
        </div>
      )}

      {activeTab === 'graph' && hasKnowledgeGraph && (
        <div>
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded">
            <p className="text-sm text-blue-800">
              This knowledge graph was automatically generated from the author's
              manuscript using AI analysis. Explore characters, locations, and
              relationships.
            </p>
          </div>

          <GraphVisualization projectId={work.factory_project_id!} />
        </div>
      )}
    </div>
  );
}
```

---

### Step 6: Frontend - Copilot for Community (1 hour)

**File**: `community-frontend/src/pages/Upload.tsx`

Add copilot option during upload:

```typescript
import { CopilotEditor } from '../../factory-frontend/src/components/editor/CopilotEditor';

export default function Upload() {
  const [useCopilot, setUseCopilot] = useState(false);
  const [content, setContent] = useState('');
  const [tempProjectId, setTempProjectId] = useState<string | null>(null);

  // Create temporary project for copilot context
  const enableCopilot = async () => {
    const response = await fetch('/api/projects/temp', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ purpose: 'community_upload' })
    });
    const data = await response.json();
    setTempProjectId(data.id);
    setUseCopilot(true);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Upload Your Work</h1>

      {/* Copilot Toggle */}
      <div className="mb-6 p-4 bg-purple-50 border border-purple-200 rounded">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-purple-900">
              ✨ FREE AI Writing Assistant
            </h3>
            <p className="text-sm text-purple-700">
              Get real-time suggestions as you write (powered by local Ollama)
            </p>
          </div>
          <button
            onClick={enableCopilot}
            disabled={useCopilot}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
          >
            {useCopilot ? 'Copilot Active' : 'Enable Copilot'}
          </button>
        </div>
      </div>

      {/* Editor */}
      {useCopilot && tempProjectId ? (
        <CopilotEditor
          projectId={tempProjectId}
          initialContent={content}
          onContentChange={setContent}
          copilotEnabled={true}
          placeholder="Start writing your story... (Press Tab to accept suggestions, Esc to dismiss)"
        />
      ) : (
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-96 p-4 border border-gray-300 rounded"
          placeholder="Paste or write your story here..."
        />
      )}

      {/* Upload button */}
      <button
        onClick={handleUpload}
        className="mt-6 px-6 py-3 bg-sky-600 text-white rounded"
      >
        Publish to Community
      </button>
    </div>
  );
}
```

---

### Step 7: Deployment (1 hour)

**7.1: Backend Deployment**:
- Run migration: `add_community_badges.sql`
- Deploy to Railway with updated code
- Verify `/api/works/`, `/api/browse/works?badge_type=ai_analyzed` endpoints

**7.2: Frontend Deployment**:
- Set environment variable: `VITE_API_URL=https://writers-platform-production.up.railway.app/api`
- Deploy to Vercel: `vercel --prod`
- Configure domain: `writerscommunity.app`

**7.3: Verification**:
- Test badge assignment for direct upload
- Test Factory → Community publishing
- Test badge filtering in Browse
- Test knowledge graph visualization on ViewWork
- Test copilot on Upload page

---

## Success Criteria

Writers can:
1. ✅ Upload work to Community with automatic badge assignment
2. ✅ Publish Factory projects with AI-Analyzed badge
3. ✅ Browse works filtered by badge type
4. ✅ View knowledge graph for AI-Analyzed works
5. ✅ Use FREE copilot while writing for Community
6. ✅ See Factory CTAs throughout Community platform

Readers can:
1. ✅ Browse validated fiction with transparent badges
2. ✅ Filter by authenticity level (AI-Analyzed, Human-Verified, etc.)
3. ✅ Explore knowledge graphs before reading
4. ✅ See research foundation (NotebookLM sources) for AI-Analyzed works

---

## Cost Estimate

**Development Time**: 6-8 hours
- Backend Badge System: 1.5 hours
- Badge Assignment Logic: 1 hour
- API Updates: 1 hour
- Frontend Badge Filter: 30 minutes
- Knowledge Graph Showcase: 1.5 hours
- Copilot Integration: 1 hour
- Deployment & Testing: 1 hour

**Claude Cloud Cost**: ~$200-300
- Backend: ~$120
- Frontend: ~$80
- Testing/debugging: ~$50

**Total Phase 2 Budget**: ~$200-300

---

## Timeline

**Day 1** (4 hours):
- Backend Badge System (1.5h)
- Badge Assignment Logic (1h)
- API Updates (1h)
- Badge Filter Frontend (30min)

**Day 2** (4 hours):
- Knowledge Graph Showcase (1.5h)
- Copilot Integration (1h)
- Deployment (1h)
- Testing & Verification (30min)

---

## Comparison to Original Plan

**Original Plan** (MASTER_ROADMAP.md):
- 6-8 hours, $200-300
- Badge system, direct upload, Factory CTAs, browse filters

**Updated Plan** (This document):
- 6-8 hours, $200-300 (same budget)
- ✅ All original features
- ✅ PLUS Knowledge Graph showcase
- ✅ PLUS FREE Copilot for Community
- ✅ PLUS Entity-based discovery (future)
- ✅ PLUS Research citations (future)

**Why same budget?**
- Community frontend mostly exists
- Badge components already built
- Knowledge Graph and Copilot infrastructure already complete
- Just integrating existing systems

---

## Next Steps

1. **Review this plan** with user
2. **Start implementation** with Step 1 (Backend Badge System)
3. **Test incrementally** after each step
4. **Deploy to production** after Step 7
5. **Monitor analytics** for Community adoption

---

**Status**: 📋 **READY FOR REVIEW**

This updated plan accounts for completed Knowledge Graph and Copilot systems,
leveraging existing infrastructure to deliver enhanced Community platform features
within the original budget.

---

*Created by: Claude Code*
*Date: 2025-01-18*
*Based on: MASTER_ROADMAP.md Phase 2 + Knowledge Graph Phases 1-8 + Copilot*
