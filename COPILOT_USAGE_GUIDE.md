# AI Copilot Usage Guide

**Real-time Writing Assistance - Like Cursor AI for Creative Writing**

---

## What is Copilot Mode?

The AI Copilot provides **real-time, inline writing suggestions** as you type, similar to GitHub Copilot or Cursor AI, but specifically designed for creative writing.

### Features

✅ **Real-time suggestions** - Get AI completions while you write
✅ **FREE** - Uses local Ollama (Llama 3.3), no API costs
✅ **Knowledge graph integration** - AI knows your characters, locations, story
✅ **Context-aware** - Understands voice, tone, and story continuity
✅ **Keyboard shortcuts** - Tab to accept, Esc to dismiss
✅ **Ghost text rendering** - Non-intrusive inline suggestions

---

## Prerequisites

### 1. Install Ollama

```bash
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# Or download from: https://ollama.ai/download
```

### 2. Download Llama 3.3 Model

```bash
# Download the 70B model (recommended)
ollama pull llama3.3:70b

# Or use the smaller 8B model (faster, less accurate)
ollama pull llama3.3
```

### 3. Start Ollama Service

```bash
# Start Ollama server
ollama serve

# Should see: "Ollama is running on http://localhost:11434"
```

### 4. Verify Installation

```bash
# Test Ollama is working
curl http://localhost:11434/api/tags

# Should return list of models
```

---

## Backend Setup

The copilot backend is already implemented! Just ensure:

1. ✅ Ollama is running (`ollama serve`)
2. ✅ Llama 3.3 model is downloaded
3. ✅ Backend server is running

### Check Copilot Status

```bash
# Check if copilot is available for a project
GET /api/copilot/{project_id}/status

# Response:
{
  "project_id": "...",
  "copilot_enabled": true,
  "ollama_available": true,
  "available_models": ["llama3.3:70b"],
  "free": true,
  "cost_per_suggestion": 0.0
}
```

---

## Frontend Usage

### Basic Implementation

```typescript
import { CopilotEditor } from '../components/editor/CopilotEditor';

function MyWritingPage() {
  const [content, setContent] = useState('');

  return (
    <CopilotEditor
      projectId="your-project-id"
      sceneId="optional-scene-id"
      initialContent={content}
      onContentChange={setContent}
      copilotEnabled={true}
    />
  );
}
```

### Full Example with Save

```typescript
import React, { useState } from 'react';
import { CopilotEditor } from '../components/editor/CopilotEditor';

export const SceneEditor: React.FC<{ projectId: string; sceneId: string }> = ({
  projectId,
  sceneId,
}) => {
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`/api/scenes/${sceneId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });
      alert('Scene saved!');
    } catch (error) {
      alert('Save failed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Scene Editor</h1>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          {saving ? 'Saving...' : 'Save Scene'}
        </button>
      </div>

      <CopilotEditor
        projectId={projectId}
        sceneId={sceneId}
        initialContent={content}
        onContentChange={setContent}
        onSave={handleSave}
        copilotEnabled={true}
        placeholder="Start writing your scene..."
        className="mb-4"
      />
    </div>
  );
};
```

---

## How to Use

### 1. Start Writing

Just start typing in the editor. The copilot listens in the background.

```
You type: "Mickey walked into the"
```

### 2. Pause for Suggestions

After you stop typing for ~800ms, the copilot generates a suggestion:

```
abandoned warehouse, his footsteps echoing in the darkness.
```

The suggestion appears as **ghost text** (gray, italic) after your cursor.

### 3. Accept or Dismiss

**Accept**: Press `Tab`
- Suggestion is inserted at cursor
- You can continue writing

**Dismiss**: Press `Esc` or just keep typing
- Suggestion disappears
- No change to your text

### 4. Continue Writing

The copilot continuously provides suggestions as you write!

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Accept current suggestion |
| `Esc` | Dismiss suggestion |
| `Ctrl/Cmd + S` | Save document |

---

## Props Reference

### CopilotEditor Props

```typescript
interface CopilotEditorProps {
  // Required
  projectId: string;              // Project ID for knowledge graph context
  initialContent: string;          // Initial text content
  onContentChange: (content: string) => void;  // Called when text changes

  // Optional
  sceneId?: string;               // Scene ID for specific context
  onSave?: () => void;            // Save handler (triggered by Ctrl/Cmd+S)
  placeholder?: string;            // Placeholder text
  className?: string;              // Additional CSS classes
  copilotEnabled?: boolean;        // Enable/disable copilot (default: true)
}
```

---

## How It Works

### 1. WebSocket Connection

```
Frontend Editor
     ↓ (WebSocket connection)
Backend Copilot Endpoint (/api/copilot/{project_id}/stream)
     ↓
Context Manager (gathers writing context)
     ├─ Knowledge Graph (characters, locations, relationships)
     ├─ Project Info (title, genre, description)
     └─ Current Text (previous paragraphs, tone analysis)
     ↓
Suggestion Engine (Ollama + Llama 3.3)
     ↓
Generated Suggestion
     ↓ (WebSocket)
Frontend (displays as ghost text)
```

### 2. Context Integration

The copilot is **context-aware**:

**Knowledge Graph**:
- Knows all your characters, their traits, relationships
- Knows locations, objects, themes
- Maintains story continuity

**Scene Context**:
- Previous paragraphs for continuity
- POV character identification
- Tone analysis (intense, quiet, dark, etc.)

**Project Context**:
- Genre (sci-fi, fantasy, thriller, etc.)
- Overall story arc
- Writing style

### 3. Suggestion Generation

```python
# Backend generates suggestions using:

prompt = f"""
You are a creative writing assistant for {genre} stories.

Project: {project_title}
Current tone: {detected_tone}

Characters mentioned: {entity_list}

Continue the text naturally from:
"{previous_text}"
"""

# Ollama generates suggestion (FREE!)
suggestion = await ollama.generate(prompt)
```

---

## Customization

### Disable Copilot

```typescript
<CopilotEditor
  copilotEnabled={false}  // Turns off AI suggestions
  {...otherProps}
/>
```

### Check Copilot Status

```typescript
const [copilotAvailable, setCopilotAvailable] = useState(false);

useEffect(() => {
  fetch(`/api/copilot/${projectId}/status`)
    .then(res => res.json())
    .then(data => setCopilotAvailable(data.copilot_enabled));
}, [projectId]);

return (
  <div>
    {!copilotAvailable && (
      <div className="alert">
        ⚠️ Ollama not running. Start Ollama for AI suggestions.
      </div>
    )}
    <CopilotEditor {...props} />
  </div>
);
```

---

## Troubleshooting

### "Copilot offline" Status

**Problem**: Red dot, "Copilot offline"

**Solutions**:
1. Check Ollama is running:
   ```bash
   # Should return 200 OK
   curl http://localhost:11434/api/tags
   ```

2. Start Ollama:
   ```bash
   ollama serve
   ```

3. Check model is downloaded:
   ```bash
   ollama list
   # Should show llama3.3:70b or llama3.3
   ```

### No Suggestions Appearing

**Problem**: Copilot connected but no suggestions

**Solutions**:
1. **Write more text** - Need at least 10-20 words for context
2. **Pause typing** - Wait ~1 second after you stop
3. **Check backend logs** - Look for errors in terminal
4. **Verify knowledge graph** - Ensure project has entities extracted

### Suggestions Are Poor Quality

**Problem**: Suggestions don't match your style

**Solutions**:
1. **Use larger model**: `ollama pull llama3.3:70b` (better than 8b)
2. **Build knowledge graph**: Extract entities for better context
3. **Write more content**: More context = better suggestions
4. **Adjust tone**: Copilot adapts to your writing style over time

### High CPU Usage

**Problem**: Ollama using lots of CPU/RAM

**Solutions**:
1. Use smaller model: `llama3.3` (8B) instead of `llama3.3:70b`
2. Limit concurrent connections
3. Increase debounce time (edit `requestSuggestion` timeout)

---

## Performance

### Latency

- **Cold start**: 2-5 seconds (first suggestion)
- **Warm suggestions**: 0.5-2 seconds
- **Network**: <100ms (local WebSocket)

### Resource Usage

**Llama 3.3 70B**:
- RAM: ~40GB
- CPU: High during generation
- GPU: Optional (speeds up 5-10x)

**Llama 3.3 8B**:
- RAM: ~8GB
- CPU: Moderate
- GPU: Optional

---

## Best Practices

### 1. Pause for Suggestions

Don't expect instant suggestions. Pause typing for ~1 second.

### 2. Build Your Knowledge Graph

The more entities you have, the better the suggestions:

```typescript
// Before writing, extract entities
POST /api/knowledge-graph/projects/{id}/extract
```

### 3. Accept Selectively

Not every suggestion is perfect. Use Tab for good ones, Esc for bad ones.

### 4. Customize Prompts (Advanced)

Edit `backend/app/routes/copilot.py` → `_build_suggestion_prompt()` to customize AI behavior.

### 5. Monitor Cost

Copilot is **FREE** (uses local Ollama), but be aware of:
- CPU usage
- Memory usage
- Power consumption (laptop battery)

---

## Comparison: Copilot vs Tournament vs Workflow

| Feature | Copilot | Tournament | Workflow |
|---------|---------|------------|----------|
| **Timing** | While typing | After scene done | On-demand |
| **Suggestions** | Inline | 5 full rewrites | 1 complete scene |
| **Cost** | **FREE** | $0.30-$0.50 | ~$0.20 |
| **Speed** | <2 seconds | 2-3 minutes | 30-60 seconds |
| **Use Case** | Real-time assistance | Polish finished work | Generate new scenes |
| **Context** | Knowledge graph | Scene only | Knowledge graph |
| **AI Model** | Llama 3.3 (local) | 5 cloud models | User choice |

---

## Example Workflow

### Writing a New Scene with Copilot

1. **Extract entities first** (if haven't already):
   ```typescript
   POST /api/knowledge-graph/projects/{id}/extract
   ```

2. **Open copilot editor**:
   ```typescript
   <CopilotEditor
     projectId={projectId}
     sceneId={newSceneId}
     initialContent=""
     onContentChange={handleChange}
     copilotEnabled={true}
   />
   ```

3. **Start writing**:
   ```
   You: "Mickey entered the compound, looking for"
   Copilot: "Noni, the memory specialist who held the answers to his fragmented past."
   You: [Press Tab to accept]
   ```

4. **Continue with assistance**:
   ```
   You: "She turned when she heard his footsteps,"
   Copilot: "her expression shifting from surprise to calculated caution."
   You: [Press Tab]
   ```

5. **Polish with Tournament** (after scene complete):
   ```typescript
   POST /api/analysis/run
   {
     "scene_id": sceneId,
     "agents": ["claude", "gemini", "gpt"]
   }
   ```

---

## Future Enhancements

**Planned Features**:
- [ ] Multi-model suggestions (compare Llama vs Claude vs GPT)
- [ ] Voice consistency warnings (real-time)
- [ ] Character tracking (detect OOC behavior)
- [ ] Plot continuity checks
- [ ] Grammar and style suggestions
- [ ] Configurable suggestion types (continuation, completion, enhancement)

---

## Support

**Documentation**:
- Backend: `/backend/app/routes/copilot.py`
- Frontend: `/factory-frontend/src/components/editor/CopilotEditor.tsx`
- Analysis: `/AI_COPILOT_ANALYSIS.md`

**Troubleshooting**:
1. Check Ollama status: `ollama list`
2. View backend logs: Check FastAPI console
3. Check browser console: WebSocket connection logs
4. Test endpoint: `/api/copilot/{project_id}/status`

---

**Enjoy your FREE AI writing assistant!** 🚀✨

Last Updated: November 18, 2024
