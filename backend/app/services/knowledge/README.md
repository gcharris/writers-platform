# Knowledge Base System

Smart routing between multiple knowledge systems for context-aware generation.

## Knowledge Sources

### 1. Cognee (Local Semantic Graph)
- **Type**: Local graph database
- **Strengths**: Fast, free, relationships
- **Best for**: Entity queries, conceptual relationships
- **Storage**: Local SQLite + LanceDB + Kuzu

### 2. Gemini File Search (Cloud Semantic Search)
- **Type**: Cloud vector search
- **Strengths**: Semantic search, large scale
- **Best for**: Document search, factual queries
- **Storage**: Google Cloud

### 3. NotebookLM (External Queries)
- **Type**: External AI assistant
- **Strengths**: Complex analysis, citations
- **Best for**: Analytical queries, research
- **Storage**: Google NotebookLM

## Smart Routing

The router automatically selects the best knowledge source based on query type:

```python
from factory.knowledge.router import KnowledgeRouter

router = KnowledgeRouter(prefer_local=True)

# Automatically routes to appropriate source
result = await router.query("What is Mickey's relationship with Noni?")
print(result.answer)
print(f"Source: {result.source.value}")
```

## Query Types

- **Factual**: "What is X?" → Cognee or Gemini File Search
- **Conceptual**: "How are X and Y related?" → Cognee (graph)
- **Analytical**: "Why does X happen?" → NotebookLM
- **General**: Any other query → Preferred source

## Caching

Enable caching to avoid redundant queries:

```python
from factory.knowledge.cache import QueryCache

cache = QueryCache(max_size=1000, ttl=3600)

# Check cache first
result = cache.get(query)
if result is None:
    result = await router.query(query)
    cache.set(query, result)
```

## Configuration

Set in `factory/core/config/settings.yaml`:

```yaml
knowledge:
  cognee:
    enabled: true
    database_path: ".factory/knowledge/cognee"

  gemini_file_search:
    enabled: true
    project_id: "YOUR_PROJECT_ID"

  notebooklm:
    enabled: true

  router:
    prefer_local: true
    enable_caching: true
    cache_ttl: 3600
    fallback_chain:
      - cognee
      - gemini_file_search
      - notebooklm
```

## Integration Example

```python
from factory.knowledge.router import KnowledgeRouter
from factory.knowledge.cache import QueryCache

# Initialize
router = KnowledgeRouter(prefer_local=True)
cache = QueryCache()

async def get_context(query: str) -> str:
    # Check cache
    result = cache.get(query)

    if result is None:
        # Query knowledge base
        result = await router.query(query, max_results=5)
        cache.set(query, result)

    return result.answer

# Use in workflow
context = await get_context("Tell me about quantum cognition in the story")
```
