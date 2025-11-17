# Session 3: Community Updates & Final Integration

**Prerequisites:** 
- Session 1: Backend deployed to Railway ✅
- Session 2: Factory frontend deployed to Vercel ✅

## Context

Update Writers Community frontend to work with the new unified backend and display Factory badges.

**GitHub Repository:**
```
https://github.com/gcharris/writers-platform
```

**Deployed Services:**
- Backend API: Railway
- Factory Frontend: Vercel (writersfactory.app)
- Community Frontend: Currently at feisty-passion-production-a7f1.up.railway.app

---

## Your Task

Migrate Community frontend to Vercel, add badge system, update with Factory integration.

---

## PRIORITY 1: Migrate Community to Vercel

**Current:** Deployed on Railway  
**Target:** Vercel (writerscommunity.app)

**Steps:**

1. **Copy current Community frontend to repo:**
   - From: writers-community/frontend/
   - To: writers-platform/community-frontend/

2. **Update API client:**
   ```typescript
   // src/api/client.ts
   const API_URL = import.meta.env.VITE_API_URL || 
                   'https://writers-platform-production.up.railway.app/api';
   ```

3. **Add vercel.json:**
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "devCommand": "npm run dev",
     "framework": "vite",
     "rewrites": [
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```

4. **Deploy to Vercel:**
   - Root directory: `community-frontend/`
   - Custom domain: writerscommunity.app
   - Environment: `VITE_API_URL` pointing to Railway backend

---

## PRIORITY 2: Add Badge System

**Update Work Cards** (`src/components/WorkCard.tsx`):

```typescript
interface Badge {
  type: 'ai_analyzed' | 'human_verified' | 'human_self' | 'community';
  verified: boolean;
  metadata?: {
    score?: number;
    models?: string[];
  };
}

function WorkCard({ work }: { work: Work & { badges?: Badge[] } }) {
  return (
    <div className="work-card">
      <div className="badges">
        {work.badges?.map(badge => (
          <Badge key={badge.type} badge={badge} />
        ))}
      </div>
      {/* rest of card */}
    </div>
  );
}

function Badge({ badge }: { badge: Badge }) {
  switch (badge.type) {
    case 'ai_analyzed':
      return (
        <span className="badge badge-ai">
          ✓ AI-Analyzed {badge.metadata?.score && `(${badge.metadata.score}/100)`}
        </span>
      );
    case 'human_verified':
      return (
        <span className="badge badge-verified">
          🖋️ Human-Authored (Verified {badge.metadata?.confidence}%)
        </span>
      );
    case 'human_self':
      return (
        <span className="badge badge-self">
          🖋️ Human-Authored (Self-Certified)
        </span>
      );
    case 'community':
      return (
        <span className="badge badge-community">
          Community Upload
        </span>
      );
  }
}
```

---

## PRIORITY 3: Update Direct Upload Flow

**Add "Upload Your Work" Page** (`src/pages/UploadWork.tsx`):

**Flow:**
1. User uploads file (DOCX/PDF/TXT)
2. Backend auto-parses and runs basic analysis
3. Backend assigns badges:
   - Run AI detection → "Human-Authored (Verified)" if passes
   - If user opts out of analysis → "Community Upload"
4. Work appears in browse with appropriate badge

**UI:**
```typescript
function UploadWork() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [genre, setGenre] = useState('');
  const [humanAuthored, setHumanAuthored] = useState(false);
  
  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('genre', genre);
    formData.append('claim_human_authored', humanAuthored.toString());
    
    // POST /api/community/upload
    // Backend handles: file parsing, AI detection, badge assignment
    const response = await apiClient.post('/community/upload', formData);
    
    // Redirect to work page
    navigate(`/works/${response.data.id}`);
  };
  
  return (
    <div>
      <h1>Share Your Work</h1>
      
      <FileUpload onChange={setFile} />
      
      <Input label="Title" value={title} onChange={setTitle} />
      <Select label="Genre" value={genre} onChange={setGenre} />
      
      <Checkbox 
        label="This work was written entirely by me, without AI assistance"
        checked={humanAuthored}
        onChange={setHumanAuthored}
      />
      
      <p className="text-sm">
        Want professional AI feedback before publishing? 
        <a href="https://writersfactory.app">Try Writers Factory →</a>
      </p>
      
      <Button onClick={handleSubmit}>Upload & Publish</Button>
    </div>
  );
}
```

---

## PRIORITY 4: Add Factory Integration CTAs

**On Work Pages** (`src/pages/ViewWork.tsx`):

If work has Factory badges:
```typescript
{work.factory_project_id && (
  <div className="factory-info">
    <h3>AI Analysis Results</h3>
    <div className="scores">
      <Score label="Voice" value={work.factory_scores?.voice} />
      <Score label="Pacing" value={work.factory_scores?.pacing} />
      {/* ... */}
    </div>
    <a href={`https://writersfactory.app/projects/${work.factory_project_id}`}>
      View Full Analysis in Factory →
    </a>
  </div>
)}
```

If work does NOT have Factory badges:
```typescript
{!work.factory_project_id && (
  <div className="cta-factory">
    <p>Want professional AI feedback on this work?</p>
    <a href="https://writersfactory.app">Analyze with Writers Factory →</a>
  </div>
)}
```

---

## PRIORITY 5: Update Landing Page

**New Home Page** (`src/pages/Home.tsx`):

```typescript
function Home() {
  return (
    <div>
      <Hero>
        <h1>Discover AI-Validated Fiction</h1>
        <p>Browse manuscripts developed with professional AI analysis</p>
        <Link to="/browse">Start Reading</Link>
      </Hero>
      
      <BadgeExplainer>
        <h2>What Do the Badges Mean?</h2>
        <BadgeCard type="ai_analyzed" />
        <BadgeCard type="human_verified" />
        <BadgeCard type="community" />
      </BadgeExplainer>
      
      <CTASection>
        <h2>Ready to Share Your Work?</h2>
        <Link to="/upload">Upload to Community</Link>
        <p>or</p>
        <a href="https://writersfactory.app">
          Get AI Feedback in Writers Factory →
        </a>
      </CTASection>
      
      <FeaturedWorks />
    </div>
  );
}
```

---

## PRIORITY 6: Add Filters by Badge

**Browse Page** (`src/pages/Browse.tsx`):

Add filter dropdown:
```typescript
const [badgeFilter, setBadgeFilter] = useState<string | null>(null);

<Select 
  label="Filter by Badge"
  value={badgeFilter}
  onChange={setBadgeFilter}
>
  <option value="">All Works</option>
  <option value="ai_analyzed">AI-Analyzed Only</option>
  <option value="human_verified">Human-Authored (Verified)</option>
  <option value="human_self">Human-Authored (Self)</option>
  <option value="community">Community Uploads</option>
</Select>
```

Update API call:
```typescript
const { data } = await apiClient.get('/works/', {
  params: { badge_type: badgeFilter }
});
```

---

## Success Criteria

✅ Community frontend migrated to Vercel
✅ Deployed to writerscommunity.app
✅ Badge system working (displays on all work cards)
✅ Direct upload flow working with auto-analysis
✅ Factory CTAs appearing on work pages
✅ Landing page updated with badge explainer
✅ Filter by badge type working
✅ Both frontends (Factory + Community) fully integrated with backend

---

## Final Deployment Architecture

```
Backend (Railway):
├── FastAPI API
├── PostgreSQL
├── Background jobs
└── Domain: writers-platform-production.up.railway.app

Factory Frontend (Vercel):
├── React app
├── Private workspace features
└── Domain: writersfactory.app

Community Frontend (Vercel):
├── React app
├── Public showcase features
└── Domain: writerscommunity.app
```

---

## Budget

Session 3 Budget: $200-300

---

**After Session 3 completes: Platform is fully deployed and integrated! 🚀**
