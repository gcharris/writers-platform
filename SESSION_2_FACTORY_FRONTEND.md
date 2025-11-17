# Session 2: Writers Factory Frontend

**Prerequisites:** Session 1 backend deployed to Railway

## Context

Build the web interface for writersfactory.app using React + TypeScript + Tailwind CSS.

**GitHub Repository:**
```
https://github.com/gcharris/writers-platform
```

**Backend API (from Session 1):**
```
https://writers-platform-production.up.railway.app/api
(or whatever Railway URL was deployed)
```

## Your Task

Create a React frontend for Writers Factory with file upload, AI analysis, and publishing features.

---

## PRIORITY 1: Frontend Structure

**Create:** `factory-frontend/` directory

**Tech Stack:**
- React 19 + TypeScript
- Vite (build tool)
- Tailwind CSS 4
- React Router 7
- Axios (API client)
- Zustand (state management)

**Copy baseline from:** `community-frontend/` as reference for structure

**Key difference:** Factory is a private workspace (editing, analyzing), Community is public (browsing, reading)

---

## PRIORITY 2: Core Pages

### 1. Home Page (`src/pages/Home.tsx`)

**Two-column layout:**

**Left Column: "I Have a Draft"**
- File upload button (DOCX, PDF, TXT)
- Drag-and-drop zone
- "Upload and Analyze" CTA

**Right Column: "I'm Just Starting"**
- "Start New Project" button
- Genre selection
- Brief onboarding wizard

**Footer:**
- "Browse published works → writerscommunity.app"

---

### 2. Projects Dashboard (`src/pages/Dashboard.tsx`)

**List all user's projects:**
- Project card shows:
  - Title
  - Word count
  - Status (Draft, Analyzing, Analyzed, Published)
  - Last modified
  - AI score (if analyzed)
- Actions: Edit, Analyze, View Results, Publish, Delete
- "New Project" button

---

### 3. Project Editor (`src/pages/Editor.tsx`)

**For writing/editing:**
- Rich text editor (TipTap or similar)
- Auto-save every 30 seconds
- Word count
- Chapter/scene organization
- "Save" and "Analyze" buttons

---

### 4. Upload Flow (`src/pages/Upload.tsx`)

**File upload:**
- File picker (DOCX, PDF, TXT)
- Upload progress bar
- Preview parsed structure (chapters/scenes)
- Edit metadata (title, genre)
- "Save Project" or "Save & Analyze"

---

### 5. Analysis Dashboard (`src/pages/Analysis.tsx`)

**Shows analysis results:**

**While running:**
- Progress indicator
- Status: "Analyzing with Claude Sonnet..." (real-time updates)
- Estimated time remaining

**When complete:**
- Overall score (0-100)
- Breakdown by dimension:
  - Voice consistency
  - Pacing
  - Character development
  - Dialogue
  - Scene effectiveness
  - Structure
  - Originality
- Model-by-model comparison (if multi-model tournament)
- Detailed feedback text
- "Publish to Community" button
- "Download Report" button

---

### 6. Publish Flow (`src/pages/Publish.tsx`)

**Before publishing to Community:**
- Preview how work will appear in Community
- Select visibility (Public, Unlisted)
- Add description/summary
- Confirm publication
- Show "Published! View on Community →" with link

---

## PRIORITY 3: API Integration

**Create:** `src/api/factory.ts`

```typescript
// Projects
export const projectsApi = {
  create: (data: ProjectCreate) => 
    apiClient.post('/projects/', data),
  
  list: () => 
    apiClient.get('/projects/'),
  
  get: (id: string) => 
    apiClient.get(`/projects/${id}`),
  
  update: (id: string, data: ProjectUpdate) => 
    apiClient.patch(`/projects/${id}`, data),
  
  delete: (id: string) => 
    apiClient.delete(`/projects/${id}`),
};

// Analysis
export const analysisApi = {
  run: (projectId: string, models: string[]) =>
    apiClient.post('/analysis/run', { project_id: projectId, models }),
  
  getStatus: (jobId: string) =>
    apiClient.get(`/analysis/${jobId}/status`),
  
  getResults: (jobId: string) =>
    apiClient.get(`/analysis/${jobId}/results`),
};

// Publishing
export const publishApi = {
  toCommmunity: (projectId: string) =>
    apiClient.post(`/projects/${projectId}/publish`),
};
```

---

## PRIORITY 4: Deployment to Vercel

**Why Vercel (not Railway):**
- Optimized for React/Vite
- Global CDN
- Automatic preview deployments
- Better build performance
- Free tier generous

**Steps:**

1. **Add `vercel.json`:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

2. **Environment Variables (in Vercel dashboard):**
```
VITE_API_URL=https://writers-platform-production.up.railway.app/api
```

3. **Deploy:**
- Connect GitHub repo to Vercel
- Set root directory to `factory-frontend/`
- Deploy
- Configure custom domain: writersfactory.app

4. **Update Backend CORS:**
Add Vercel domain to CORS allowed origins in Railway

---

## Success Criteria

✅ Factory frontend deployed to Vercel
✅ Accessible at writersfactory.app
✅ Can create project via upload or new
✅ Can edit project content
✅ Can trigger AI analysis
✅ Can view analysis results
✅ Can publish to Community (creates work in Community with Factory badges)
✅ All flows working end-to-end

---

## Important Notes

**Reuse from Community frontend:**
- Auth components (Login, Register)
- API client setup (axios)
- Tailwind config
- TypeScript config

**Different from Community:**
- Factory = private workspace (CRUD projects)
- Community = public browse (read-only + comments)
- Factory has analysis features
- Community has reading/rating features

**Design Consistency:**
- Both frontends should share brand colors
- Similar header/navigation
- But distinct user experience (workspace vs. showcase)

---

## Budget

Session 2 Budget: $300-400

---

**After Session 2 completes, notify user for Session 3: Community Updates & Integration**
