# Multi-Agent Scene Tournament System

## Architecture Overview

The tournament system automates the proven scene generation workflow for The Explants novel trilogy. It orchestrates multiple AI agents to generate, score, critique, and synthesize high-quality scenes that maintain Enhanced Mickey Bardot's voice authenticity.

---

## System Components

### Phase 1: Core Tournament System

#### 1. **Validation Module** (`framework/utils/validation.py`)

**Purpose**: Rule-based validation of bi-location mechanics and voice authenticity

**Components**:
- `BiLocationValidator`: Detects forbidden jargon, validates Mickey's terms
- `VoiceValidator`: Checks for voice authenticity markers and anti-patterns
- `validate_scene()`: Comprehensive scene validation

**Key Features**:
- Forbidden jargon detection: "quantum link", "bi-location mode", etc.
- Mickey's terms validation: "The Line", "The Tether", "The Shared Vein"
- Bi-location showing indicators: physical strain symptoms
- Technical announcement detection (violations)

#### 2. **Scoring Module** (`framework/utils/scoring.py`)

**Purpose**: Hybrid scoring approach (rule-based + LLM)

**Components**:
- `SceneScorer`: Main scoring engine
- Integrates validation results with LLM-based quality assessment
- Scores 7 criteria on 0-10 scale:
  1. Voice authenticity
  2. Character consistency
  3. Worldbuilding integration
  4. Pacing
  5. Dialogue naturalness
  6. Emotional impact
  7. Consciousness war argument progression

**Key Features**:
- Claude Sonnet 4.5 for LLM scoring (consistent, high-quality)
- Rule-based adjustments (penalties for jargon, bonuses for correct terms)
- Structured JSON output with reasoning

#### 3. **Tournament Orchestrator** (`framework/orchestration/tournament.py`)

**Purpose**: Core orchestration of multi-agent tournament workflow

**Workflow**:
1. **Context Building**: Fetches relevant context from Google Cloud Storage
2. **Parallel Generation**: Generates 5 variations using different agents (ThreadPoolExecutor)
3. **Scoring**: Scores each variation using hybrid approach
4. **Critique**: Cross-agent analysis of variations
5. **Synthesis**: Combines best elements into hybrid scene (configurable threshold)
6. **Output**: Structured JSON + markdown files

**Supported Agents**:
- `claude-sonnet-4-5`: Primary agent (best voice/emotion)
- `gemini-1-5-pro`: Philosophical arguments and structure
- `gpt-4o`: Dialogue and character consistency
- `grok-2`: Worldbuilding integration
- `claude-haiku`: Budget option for simple scenes

**Key Features**:
- Parallel API calls for efficiency
- Retry logic with exponential backoff
- Graceful degradation (skips unavailable agents)
- Cost tracking and token usage reporting
- Configurable synthesis threshold (default: 7.0/10)

### Phase 2: Batch Processing

#### **Batch Tournament Processor** (`framework/orchestration/batch-tournament.py`)

**Purpose**: Process multiple scenes with rate limiting

**Input Format**:
```json
{
  "chapter": "2.4",
  "scenes": [
    {
      "scene_id": "2.4.1",
      "title": "The Seduction Deepens",
      "outline": "Vance makes his offer explicit...",
      "context_requirements": ["Mickey", "Vance"],
      "previous_scenes": ["2.3.3", "2.3.4"]
    }
  ]
}
```

**Key Features**:
- Sequential or parallel scene processing
- Rate limiting per API platform
- Batch summary with cost breakdown
- Automatic resume on partial failure
- Progress tracking and error reporting

### Phase 3: Agent Analytics

#### **Agent Analyzer** (`framework/orchestration/agent-analytics.py`)

**Purpose**: Analyze agent performance and generate recommendations

**Analysis Dimensions**:
- Win rate (highest scoring variations)
- Hybrid contribution rate (included in final synthesis)
- Average scores by criteria
- Cost efficiency (cost per quality point)
- Strengths and weaknesses identification

**Output**:
- Agent performance profiles
- Scene-type recommendations
- Optimal tournament lineup
- Cost efficiency rankings

---

## Data Flow

```
Input Scene Outline
    ↓
Context Building (Google Cloud Storage)
    ↓
┌─────────────────────────────────────────────┐
│ Parallel Agent Generation (5 variations)   │
│  - Claude Sonnet 4.5                        │
│  - Gemini 1.5 Pro                           │
│  - GPT-4o                                   │
│  - Grok-2                                   │
│  - Claude Haiku                             │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Scoring System (Hybrid)                     │
│  - Rule-based validation                    │
│  - LLM scoring (7 criteria)                 │
│  - Score adjustment                         │
└─────────────────────────────────────────────┘
    ↓
Cross-Agent Critique (Claude Sonnet 4.5)
    ↓
┌─────────────────────────────────────────────┐
│ Hybrid Synthesis                            │
│  - Filter by threshold (default: 7.0)      │
│  - Extract best structural chassis          │
│  - Combine best philosophical moments       │
│  - Apply Enhanced Mickey voice              │
└─────────────────────────────────────────────┘
    ↓
Output (JSON + Markdown)
```

---

## Configuration

### Credentials Setup

**File**: `framework/config/credentials.json`

```json
{
  "ai_platforms": {
    "claude": {
      "api_key": "your-anthropic-api-key"
    },
    "openai": {
      "api_key": "your-openai-api-key"
    },
    "google": {
      "api_key": "your-google-api-key"
    },
    "xai": {
      "api_key": "your-xai-api-key"
    }
  },
  "google_cloud": {
    "project_id": "your-project-id",
    "credentials_path": "config/google-cloud-credentials.json"
  },
  "projects": {
    "The-Explants": {
      "bucket_name": "explants-story-store",
      "description": "The Explants trilogy"
    }
  }
}
```

**Environment Variable Fallback**:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `XAI_API_KEY`

---

## Error Handling

### Retry Logic
- **Exponential backoff**: 1s, 2s, 4s delays
- **Max retries**: 3 attempts per API call
- **Graceful degradation**: Continues with available agents

### Rate Limiting
- Anthropic: 50 requests/minute
- OpenAI: 500 requests/minute
- Google: 60 requests/minute
- xAI: 60 requests/minute

### Partial Results
- Saves completed variations if interrupted
- Tournament can be resumed manually
- Batch processing tracks failed scenes

---

## Cost Tracking

### Pricing (as of 2025)
- **Claude Sonnet 4.5**: $3/M input, $15/M output
- **Gemini 1.5 Pro**: $3.50/M input, $10.50/M output
- **GPT-4o**: $5/M input, $15/M output
- **Grok-2**: ~$5/M input, ~$15/M output
- **Claude Haiku**: $0.25/M input, $1.25/M output

### Cost Estimation
- **Single tournament** (5 agents + scoring + critique + synthesis): ~$0.50-1.50
- **Batch (10 scenes)**: ~$5-15
- **Full chapter (30 scenes)**: ~$15-45

### Cost Reporting
- Per-agent cost tracking
- Per-scene cost breakdown
- Cumulative batch cost
- Cost efficiency analysis ($/quality point)

---

## Performance Optimization

### Parallel Execution
- **Agent generation**: 5 agents in parallel (ThreadPoolExecutor)
- **Batch processing**: Configurable parallelism (default: sequential)
- **Network I/O**: Non-blocking for API calls

### Caching
- Agent instances cached per session
- Context packages reused within batch

### Token Optimization
- Scene truncation for scoring (max 3000 words)
- Context compression for large projects
- Prompt engineering for conciseness

---

## Quality Assurance

### Validation Gates
- ✅ No forbidden jargon
- ✅ Mickey's terms used correctly
- ✅ Bi-location shown through strain (not announced)
- ✅ Noni's morphic resonance active
- ✅ Voice authenticity score ≥7.0

### Score Thresholds
- **Minimum acceptable**: 5.0/10 per criterion
- **Synthesis threshold**: 7.0/10 (configurable)
- **High quality**: 8.0+/10
- **Exceptional**: 9.0+/10

### Human Review Checkpoints
- Review hybrid scene before committing
- Validate critique recommendations
- Adjust synthesis threshold based on results

---

## Integration Points

### Google Cloud Storage
- `GoogleStoreQuerier`: Fetches character/worldbuilding context
- `ContextPackage`: Structured context for prompts
- Graceful fallback if storage unavailable

### Existing Agent Classes
- `BaseAgent`: Abstract interface
- `ClaudeAgent`, `GeminiAgent`, `ChatGPTAgent`, `GrokAgent`
- Factory functions for configuration-based instantiation

### Future Extensions
- NotebookLM integration (browser automation)
- Git auto-commit for winning scenes
- Web dashboard for visual comparison
- A/B testing of synthesis strategies

---

## Extensibility

### Adding New Agents
1. Implement `BaseAgent` subclass
2. Add to `AGENT_CONFIGS` in `tournament.py`
3. Update agent factory in `batch-tournament.py`

### Custom Scoring Criteria
1. Extend `CRITERIA` list in `scoring.py`
2. Update scoring prompt template
3. Adjust score adjustment logic

### Alternative Synthesis Strategies
1. Implement new `_synthesize_*` method
2. Add CLI flag for strategy selection
3. Compare results with agent analytics

---

## Monitoring and Logging

### Structured Logging
- Timestamps for all operations
- API call tracking
- Error stacktraces
- Cost accumulation

### Progress Reporting
- Per-agent generation status
- Score summary tables
- Batch progress tracking
- Final summary statistics

### Output Files
- `*-tournament.json`: Complete tournament results
- `*-hybrid.md`: Synthesized hybrid scene
- `*-summary.md`: Human-readable summary
- `batch-summary.json`: Batch processing report
- `agent-analytics.json`: Performance analysis

---

## Best Practices

### Development
1. Test with single scene before batch
2. Use `claude-haiku` for cheap testing
3. Start with sequential batch processing
4. Monitor costs during development

### Production
1. Always set synthesis threshold appropriately
2. Review analytics before full batch runs
3. Use optimal agent lineup from analytics
4. Save all tournament results for future analysis

### Cost Management
1. Use `--agents` flag to limit agents
2. Set reasonable `--max-tokens` limits
3. Run analytics to identify most cost-efficient agents
4. Consider scene complexity when selecting agents

---

## Troubleshooting

### Common Issues

**Issue**: No API key found
- **Solution**: Create `framework/config/credentials.json` or set environment variables

**Issue**: Agent generation fails
- **Solution**: Check API key validity, rate limits, network connectivity

**Issue**: Scoring returns default values
- **Solution**: Verify Claude Sonnet 4.5 API access, check prompt format

**Issue**: Hybrid synthesis quality low
- **Solution**: Lower synthesis threshold, review critique guidance

**Issue**: Batch processing slow
- **Solution**: Increase `--parallel` setting (with caution for rate limits)

### Debug Mode
```bash
# Add verbose logging
export DEBUG=1
python3 framework/orchestration/tournament.py --scene "..." --output ...
```

---

## Version History

- **v1.0** (November 2025): Initial implementation
  - Phase 1: Core tournament system
  - Phase 2: Batch processing
  - Phase 3: Agent analytics
  - Hybrid scoring system
  - Comprehensive documentation

---

**Maintained by**: Claude Code Cloud Agent
**Repository**: https://github.com/gcharris/The-Explants
**License**: Project-specific (see repository)
