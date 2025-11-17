# Writers Factory Core Framework

Multi-agent Python framework for AI-assisted novel writing with context-aware generation.

## Overview

This framework orchestrates multiple AI models (Claude, Gemini, GPT, Qwen, DeepSeek) to collaboratively write, edit, and analyze creative fiction. Each agent can autonomously query knowledge systems for context before generating content.

## Directory Structure

```
factory/core/
├── agents/              # AI model integrations
│   ├── claude.py        # Claude (Opus, Sonnet)
│   ├── gemini.py        # Google Gemini
│   ├── openai.py        # GPT-4, GPT-3.5
│   ├── qwen.py          # Qwen (Alibaba)
│   └── deepseek.py      # DeepSeek
│
├── analysis/            # Content analysis tools
│   ├── voice_consistency_tester.py  # Multi-model voice comparison
│   └── metaphor_analyzer.py         # Metaphor pattern analysis
│
├── google_store/        # Gemini File Search integration
│   ├── query.py         # Context retrieval
│   ├── sync.py          # Upload/download files
│   ├── indexer.py       # Build searchable index
│   └── config.py        # Credentials management
│
├── cognee_knowledge_graph/  # Local knowledge graph
│   ├── indexer.py       # Build semantic graph
│   └── query.py         # Graph query interface
│
├── orchestration/       # Multi-agent workflows
│   ├── scene_writer.py  # Coordinate scene generation
│   └── context_builder.py  # Build context packages
│
├── templates/           # Claude Code skills
│   ├── character-agent/
│   ├── scene-multiplier/
│   └── voice-enforcer/
│
├── utils/               # Helper functions
│   └── validators.py    # Input validation
│
└── config/              # Configuration
    ├── credentials.json # API keys (gitignored)
    └── settings.json    # Framework settings
```

## Core Philosophy

**Context-Aware Generation**: Before writing any scene, agents automatically query the knowledge systems (Cognee, Gemini File Search, or NotebookLM) to retrieve:
- Character details and development arcs
- Worldbuilding and setting information
- Previous related scenes
- Story themes and motifs
- Narrative voice guidelines

This ensures every generated piece is informed by the full context of your creative universe.

## Quick Start

### Prerequisites

- Python 3.11+
- API keys for desired platforms (Claude, OpenAI, Google, etc.)
- Google Cloud account (for Gemini File Search)

### Installation

```bash
# From repository root
cd factory/core

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp config/credentials.example.json config/credentials.json
# Edit config/credentials.json with your API keys
```

### Basic Usage

```python
from factory.core.agents import ClaudeAgent
from factory.core.google_store.query import query_context

# Initialize agent
agent = ClaudeAgent(model="claude-sonnet-4.5")

# Query knowledge system for context
context = query_context("Mickey Bardot character details")

# Generate scene with full context
scene = agent.generate(
    prompt="Write Mickey discovering the truth about her implant",
    context=context
)
```

## Key Features

### Multi-Model Generation

Compare outputs from different AI models side-by-side:

```bash
python factory/core/analysis/voice_consistency_tester.py \
  --prompt "Opening scene for Volume 2" \
  --models claude,gemini,gpt4,qwen,deepseek \
  --output test-results.md
```

### Knowledge System Integration

Three-tier knowledge architecture:

1. **Cognee** ([factory/knowledge/cognee-system](../knowledge/cognee-system/)) - Local semantic graph, 17MB, instant queries
2. **Gemini File Search** ([factory/core/google_store](google_store/)) - Cloud semantic search, ~400MB indexed
3. **NotebookLM** ([.claude/skills/notebooklm](.claude/skills/notebooklm)) - External knowledge base via skill

The framework automatically routes queries to the most appropriate system based on query type, data freshness, and cost.

### Voice Consistency Testing

Test how well different models maintain character voice:

```bash
python factory/core/analysis/voice_consistency_tester.py \
  --character "Mickey Bardot" \
  --test-scenes project/manuscript/volume-1/ACT\ 1/
```

### Scene Generation Workflow

1. Provide scene outline
2. Framework queries knowledge for context
3. Multiple agents generate variations
4. Automated scoring and comparison
5. Human selects best version or merges elements

## Agent System

### Base Agent Class

All agents inherit from `BaseAgent`:

```python
class BaseAgent(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: dict) -> str:
        """Generate content with context awareness."""
        pass

    def count_tokens(self, text: str) -> int:
        """Count tokens for cost tracking."""
        pass
```

### Adding New Agents

Create a new agent in `factory/core/agents/`:

```python
from factory.core.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__("MyAgent")
        self.api_key = api_key

    async def generate(self, prompt, context):
        # Implement your API integration
        pass
```

## Google File Search Setup

See [../knowledge/GEMINI_FILE_SEARCH_SETUP.md](../knowledge/GEMINI_FILE_SEARCH_SETUP.md) for complete setup instructions.

Quick setup:

```bash
# Upload project files
python factory/core/google_store/sync.py \
  --upload \
  --source project/reference/ \
  --categories characters,worldbuilding,themes

# Query the index
python factory/core/google_store/query.py \
  --query "Tell me about Mickey's transformation"
```

## Cognee Knowledge Graph

Local semantic knowledge graph using Cognee:

```bash
# Index your project
python factory/knowledge/cognee-system/indexer.py \
  --source project/manuscript/volume-1/ \
  --rebuild

# Query the graph
python factory/knowledge/cognee-system/query.py \
  "What are Mickey's key relationships?"
```

## Configuration

### API Keys

Store in `factory/core/config/credentials.json`:

```json
{
  "anthropic_api_key": "sk-ant-...",
  "openai_api_key": "sk-...",
  "google_api_key": "...",
  "qwen_api_key": "...",
  "deepseek_api_key": "..."
}
```

### Framework Settings

Configure in `factory/core/config/settings.json`:

```json
{
  "default_model": "claude-sonnet-4.5",
  "context_window": 200000,
  "temperature": 0.7,
  "knowledge_system": "auto"
}
```

## Testing

```bash
# Run framework tests
pytest factory/core/tests/

# Test specific agent
python factory/core/tests/test_claude_agent.py

# Test knowledge integration
python factory/core/tests/test_context_retrieval.py
```

## Integration with Claude Code Skills

Skills in [.claude/skills](.claude/skills) can directly use this framework:

```python
# From a Claude Code skill
from factory.core.agents import ClaudeAgent
from factory.core.google_store.query import query_context

# Use in your skill logic
agent = ClaudeAgent()
context = query_context("scene context needed")
result = agent.generate(prompt, context)
```

## Cost Tracking

All agents track token usage and costs:

```python
from factory.core.analytics import get_usage_stats

stats = get_usage_stats(start_date="2024-11-01")
print(f"Total cost: ${stats.total_cost}")
print(f"Tokens used: {stats.total_tokens}")
print(f"By model: {stats.by_model}")
```

## Documentation

- **Architecture**: [../docs/WRITERS_FACTORY_ARCHITECTURE.md](../docs/WRITERS_FACTORY_ARCHITECTURE.md)
- **Workflows**: [../docs/BATCH_PROCESSOR_README.md](../docs/BATCH_PROCESSOR_README.md)
- **Voice Testing**: [../docs/VOICE_TESTING_README.md](../docs/VOICE_TESTING_README.md)
- **Knowledge Systems**: [../knowledge/COGNEE_KNOWLEDGE_GRAPH_README.md](../knowledge/COGNEE_KNOWLEDGE_GRAPH_README.md)

## Troubleshooting

**Import errors after reorganization:**
- Ensure you're using `from factory.core.` prefix for all imports
- Check that Python path includes repository root
- Verify all `__init__.py` files exist

**Knowledge system not found:**
- Cognee: Check `factory/knowledge/cognee-system/.venv-cognee/` exists
- Gemini: Verify credentials in `factory/core/config/credentials.json`
- NotebookLM: Ensure skill is in `.claude/skills/notebooklm/`

**Agent API failures:**
- Verify API keys are current and have sufficient credits
- Check network connectivity
- Review error logs in `factory/core/logs/`

## Contributing

This framework is part of the Writers Factory project. Eventually it will be extracted into a standalone open-source repository.

For now, improvements should maintain:
- Context-aware generation philosophy
- Multi-platform agent support
- Knowledge system integration
- Reusability for other writing projects

---

**Part of**: Writers Factory
**Status**: Active development | Reorganized Nov 2024
**Primary Use**: The Explants trilogy writing system
