# Workflow API Documentation

Session 5 progress: FastAPI endpoints for Factory workflow orchestration.

## Overview

The Workflow API provides endpoints for AI-assisted scene generation, enhancement, and voice testing. All endpoints use the workflow engine from Session 4's factory-core integration.

**Base URL**: `/api/workflows`

**Authentication**: All endpoints require Bearer token authentication via `Authorization` header.

---

## Endpoints

### 1. Generate Scene with Knowledge Context

Generate a new scene using AI with automatic knowledge base queries for character consistency, plot continuity, and world-building accuracy.

**Endpoint**: `POST /api/workflows/scene/generate`

**Request Body**:
```json
{
  "project_id": "uuid",
  "act_number": 1,
  "chapter_number": 3,
  "scene_number": 2,
  "outline": "POV: Mickey. Location: The Explants compound. Mickey confronts Noni about the memory glitches.",
  "title": "Memory Confrontation",
  "model_name": "claude-sonnet-4.5",
  "use_knowledge_context": true,
  "context_queries": [
    "What is Mickey's personality?",
    "What is Noni's relationship with Mickey?"
  ]
}
```

**Parameters**:
- `project_id` (UUID, required): Project ID
- `act_number` (integer, required): Act number (≥1)
- `chapter_number` (integer, required): Chapter number within act (≥1)
- `scene_number` (integer, required): Scene number within chapter (≥1)
- `outline` (string, required): Scene outline/scaffold (min 10 chars)
- `title` (string, optional): Scene title
- `model_name` (string, default: "claude-sonnet-4.5"): AI model to use
- `use_knowledge_context` (boolean, default: true): Query knowledge base for context
- `context_queries` (array, optional): Specific KB queries to run

**Response** (200 OK):
```json
{
  "workflow_id": "workflow-uuid",
  "status": "completed",
  "scene_id": "scene-uuid",
  "scene_content": "The generated prose...",
  "word_count": 842,
  "metadata": {
    "model": "claude-sonnet-4.5",
    "outline_words": 23
  }
}
```

**Workflow Process**:
1. Validates project access
2. Creates Act/Chapter structure if needed
3. Parses scene outline
4. Queries knowledge base for context (if enabled)
5. Generates scene with AI model
6. Saves scene to database with metadata
7. Returns generated content

**Errors**:
- `404`: Project not found or access denied
- `400`: Scene already exists at that position
- `500`: Generation workflow failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/workflows/scene/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "123e4567-e89b-12d3-a456-426614174000",
    "act_number": 1,
    "chapter_number": 1,
    "scene_number": 1,
    "outline": "POV: Protagonist. Scene: Opening scene of the novel.",
    "model_name": "claude-sonnet-4.5"
  }'
```

---

### 2. Enhance Scene with Voice Consistency

Improve an existing scene with AI-assisted enhancement and voice consistency validation.

**Endpoint**: `POST /api/workflows/scene/enhance`

**Request Body**:
```json
{
  "scene_id": "uuid",
  "model_name": "claude-sonnet-4.5",
  "character": "protagonist"
}
```

**Parameters**:
- `scene_id` (UUID, required): ID of scene to enhance
- `model_name` (string, default: "claude-sonnet-4.5"): AI model to use
- `character` (string, default: "protagonist"): Character for voice testing

**Response** (200 OK):
```json
{
  "workflow_id": "workflow-uuid",
  "status": "completed",
  "scene_id": "scene-uuid",
  "enhanced_content": "The enhanced prose...",
  "word_count": 923,
  "validation": {
    "passed": true,
    "score": 88.5,
    "issues": [],
    "character": "protagonist"
  }
}
```

**Workflow Process**:
1. Retrieves existing scene
2. Validates user access
3. Queries knowledge base for voice requirements
4. Enhances scene using AI
5. Validates voice consistency
6. Updates scene in database
7. Returns enhanced content with validation score

**Errors**:
- `404`: Scene not found
- `403`: Access denied (not your project)
- `500`: Enhancement workflow failed

---

### 3. Test Voice Consistency Across Models

Compare multiple AI models to find which best captures a character's voice.

**Endpoint**: `POST /api/workflows/voice/test`

**Request Body**:
```json
{
  "prompt": "Write a paragraph where the protagonist reflects on their mission.",
  "models": ["claude-sonnet-4.5", "gpt-4o", "gemini-2-flash"],
  "character": "Mickey"
}
```

**Parameters**:
- `prompt` (string, required): Test prompt (min 10 chars)
- `models` (array, required): 2-5 model names to compare
- `character` (string, default: "protagonist"): Character name

**Response** (200 OK):
```json
{
  "workflow_id": "workflow-uuid",
  "status": "completed",
  "comparison": [
    {
      "model": "claude-sonnet-4.5",
      "output": "Generated text...",
      "score": 92.0,
      "word_count": 156
    },
    {
      "model": "gpt-4o",
      "output": "Generated text...",
      "score": 85.0,
      "word_count": 143
    }
  ],
  "recommendation": {
    "winner": "claude-sonnet-4.5",
    "score": 92.0,
    "reasoning": "claude-sonnet-4.5 achieved the highest voice consistency score of 92.0",
    "top_3": [
      {"model": "claude-sonnet-4.5", "score": 92.0},
      {"model": "gpt-4o", "score": 85.0}
    ]
  },
  "metadata": {
    "models_tested": 3,
    "character": "Mickey"
  }
}
```

**Workflow Process**:
1. Generates outputs from all specified models in parallel
2. Scores voice consistency for each output
3. Compares results
4. Recommends best model for the character's voice

**Errors**:
- `422`: Invalid request (need 2-5 models)
- `500`: Voice testing workflow failed

---

### 4. Get Workflow Status

Query the status of a running or completed workflow.

**Endpoint**: `GET /api/workflows/{workflow_id}`

**Response** (200 OK):
```json
{
  "workflow_id": "workflow-uuid",
  "status": "completed",
  "started_at": "2025-01-17T10:30:00Z",
  "completed_at": "2025-01-17T10:30:15Z",
  "steps_completed": 4,
  "steps_total": 4,
  "outputs": {
    "scene": "Generated scene content...",
    "parse_outline": {...},
    "get_context": {...}
  },
  "errors": [],
  "metadata": {
    "model": "claude-sonnet-4.5",
    "outline_words": 23
  },
  "duration": 15.3,
  "success": true
}
```

**Workflow Statuses**:
- `pending`: Workflow created but not started
- `running`: Currently executing
- `paused`: Paused (can be resumed)
- `completed`: Successfully finished
- `failed`: Execution failed (see `errors` array)
- `cancelled`: Manually cancelled

**Errors**:
- `404`: Workflow not found

---

### 5. WebSocket: Stream Workflow Progress

Real-time updates for workflow execution progress.

**Endpoint**: `WS /api/workflows/{workflow_id}/stream`

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/workflows/{workflow_id}/stream');

ws.onopen = () => {
  console.log('Connected to workflow stream');
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Workflow update:', update);

  if (update.type === 'status') {
    console.log(`Status: ${update.status}, Steps: ${update.steps_completed}/${update.steps_total}`);
  }

  if (update.type === 'workflow_completed') {
    console.log('Workflow finished!', update.outputs);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Connection closed');
};
```

**Message Types**:

1. **Initial Status**:
```json
{
  "type": "status",
  "workflow_id": "workflow-uuid",
  "status": "running",
  "steps_completed": 2,
  "steps_total": 4
}
```

2. **Workflow Completed**:
```json
{
  "type": "workflow_completed",
  "status": "completed",
  "outputs": {
    "scene": "Generated content..."
  }
}
```

3. **Error**:
```json
{
  "type": "error",
  "message": "Workflow not found"
}
```

---

## Available AI Models

### Cloud Models (Require API Keys)

- **`claude-sonnet-4.5`** (default): Anthropic Claude Sonnet 4.5 (best for prose)
- **`claude-opus-4`**: Anthropic Claude Opus 4 (highest quality, slower)
- **`gpt-4o`**: OpenAI GPT-4 Optimized
- **`gemini-2-flash`**: Google Gemini 2.0 Flash (fast, good quality)
- **`grok-2`**: xAI Grok 2
- **`deepseek-chat`**: DeepSeek Chat (Chinese model, cost-effective)

### Local Model (FREE)

- **`llama-3.3`**: Meta Llama 3.3 via Ollama (requires local Ollama installation)

---

## Knowledge Context Integration

When `use_knowledge_context: true`, the workflow automatically queries the project's Reference Library for relevant context:

### Auto-Generated Queries

If no `context_queries` specified, the system generates queries based on the outline:
- Character names → Character profiles
- Locations → World-building details
- Plot points → Story structure documents

### Manual Queries

Provide specific queries for fine-grained control:
```json
{
  "context_queries": [
    "What is the protagonist's main flaw?",
    "What technology exists in this world?",
    "What happened in the previous scene?"
  ]
}
```

### Knowledge Sources

The system queries:
1. **Reference Library**: Markdown files in `reference/` directory
   - `Characters/` - Character profiles
   - `Story_Structure/` - Plot, arcs, beats
   - `World_Building/` - Locations, technology, culture
   - `Themes_and_Philosophy/` - Thematic elements

2. **Previous Scenes**: Continuity from earlier scenes in the manuscript

3. **NotebookLM** (if configured): External research notebooks

---

## Workflow Engine Features

All endpoints use the factory-core workflow engine:

- ✅ **Dependency Resolution**: Steps execute in correct order
- ✅ **Parallel Execution**: Independent steps run concurrently
- ✅ **Retry Logic**: Automatic retries with exponential backoff
- ✅ **Pause/Resume**: Can pause long-running workflows
- ✅ **Error Handling**: Graceful failure with detailed error messages
- ✅ **Progress Tracking**: Real-time status updates
- ✅ **State Persistence**: Workflow state saved for recovery

---

## Error Handling

All endpoints follow standard HTTP error conventions:

### Common Errors

**401 Unauthorized**:
```json
{
  "detail": "Not authenticated"
}
```
Solution: Include valid Bearer token in `Authorization` header.

**403 Forbidden**:
```json
{
  "detail": "Access denied"
}
```
Solution: Ensure you own the project/scene you're trying to access.

**404 Not Found**:
```json
{
  "detail": "Project 123e4567-... not found or access denied"
}
```
Solution: Verify the UUID is correct and you have access.

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "outline"],
      "msg": "ensure this value has at least 10 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```
Solution: Fix the validation errors in your request body.

**500 Internal Server Error**:
```json
{
  "detail": "Scene generation failed: Connection timeout"
}
```
Solution: Check logs for details, retry the request.

---

## Rate Limiting

(TODO: Implement rate limiting)

Planned limits:
- Scene generation: 10 per minute per user
- Voice testing: 5 per minute per user
- Workflow status: 100 per minute per user

---

## Examples

### Complete Scene Generation Flow

```javascript
// 1. Generate a scene
const generateResponse = await fetch('/api/workflows/scene/generate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    project_id: projectId,
    act_number: 1,
    chapter_number: 1,
    scene_number: 1,
    outline: 'POV: Mickey. She wakes up in a new body.',
    model_name: 'claude-sonnet-4.5',
    use_knowledge_context: true
  })
});

const { workflow_id, scene_id, scene_content } = await generateResponse.json();

// 2. Connect to WebSocket for real-time updates (optional)
const ws = new WebSocket(`ws://localhost:8000/api/workflows/${workflow_id}/stream`);
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Progress:', update);
};

// 3. Poll for workflow status (alternative to WebSocket)
const checkStatus = async () => {
  const statusResponse = await fetch(`/api/workflows/${workflow_id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const status = await statusResponse.json();

  if (status.status === 'completed') {
    console.log('Scene generated!', status.outputs.scene);
  } else if (status.status === 'failed') {
    console.error('Generation failed:', status.errors);
  } else {
    // Still running, check again
    setTimeout(checkStatus, 1000);
  }
};

// 4. Enhance the generated scene
const enhanceResponse = await fetch('/api/workflows/scene/enhance', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    scene_id: scene_id,
    model_name: 'claude-sonnet-4.5',
    character: 'Mickey'
  })
});

const { enhanced_content, validation } = await enhanceResponse.json();
console.log('Voice score:', validation.score);
```

---

## Implementation Status

**Session 5 Progress** (In Progress):

✅ **Completed**:
- FastAPI workflow endpoints created
- Scene generation endpoint with KB integration hooks
- Scene enhancement endpoint with voice validation
- Voice testing endpoint for model comparison
- Workflow status endpoint
- WebSocket streaming endpoint
- Comprehensive test suite
- API documentation

⏳ **In Progress**:
- Knowledge router integration (placeholder)
- Agent pool initialization (placeholder)

⏳ **Pending** (Next Steps):
- NotebookLM MCP integration
- Database migration execution
- Production deployment
- Rate limiting
- Caching layer for KB queries
- React UI components for conversational agent

---

## Testing

Run the test suite:

```bash
cd backend
pytest tests/test_workflows.py -v
```

Test specific scenarios:
```bash
# Test scene generation
pytest tests/test_workflows.py::test_generate_scene_success -v

# Test WebSocket streaming
pytest tests/test_workflows.py::test_websocket_workflow_stream -v

# Integration tests (requires full setup)
pytest tests/test_workflows.py -m integration -v
```

---

## Next Steps

See `docs/SESSION_5_PLAN.md` for the complete Session 5 roadmap:

1. **Knowledge Router Integration**: Connect endpoints to actual KB queries
2. **Agent Pool Setup**: Initialize multi-model agent system
3. **NotebookLM Integration**: MCP server connection
4. **React Components**: Conversational agent UI (Cursor-like side panel)
5. **Database Migration**: Run Alembic migration for manuscript tables
6. **End-to-End Testing**: Full workflow validation

---

**Documentation Version**: Session 5, Iteration 1
**Last Updated**: 2025-01-17
**Status**: Endpoints created, integration pending
