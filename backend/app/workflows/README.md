# Workflows

Pre-built workflows for common writing tasks.

## Available Workflows

### 1. Multi-Model Generation
Generate content with multiple models and compare results.

```python
from factory.workflows.multi_model_generation.workflow import MultiModelGenerationWorkflow

workflow = MultiModelGenerationWorkflow(
    agent_pool=pool,
    prompt="Write an opening scene...",
    agents=["claude-sonnet-4.5", "gpt-4o", "gemini-2-flash"],
    temperature=0.8,
    max_tokens=2000
)

result = await workflow.run()

# Get ranked results
ranked = workflow.get_ranked_results(scoring_function=my_scorer)
for i, result in enumerate(ranked, 1):
    print(f"{i}. {result['agent']}: Score {result['score']}")
```

### 2. Project Genesis
Initialize a new writing project from scratch.

```python
from factory.workflows.project_genesis.workflow import ProjectGenesisWorkflow

workflow = ProjectGenesisWorkflow(
    agent_pool=pool,
    project_name="My Novel",
    genre="sci-fi thriller",
    themes=["identity", "technology", "consciousness"],
    basic_idea="A scientist discovers...",
    num_characters=5,
    act_structure=3
)

result = await workflow.run()

# Project structure created at ./My Novel/
```

## Creating Custom Workflows

### 1. Inherit from BaseWorkflow

```python
from factory.workflows.base_workflow import BaseWorkflow
from factory.core.workflow_engine import WorkflowResult

class MyWorkflow(BaseWorkflow):
    def __init__(self, **kwargs):
        super().__init__(name="my-workflow", context=kwargs)

    async def setup(self):
        # Initialize resources
        self.validate_context(["required_key"])

    async def execute(self) -> WorkflowResult:
        # Main workflow logic
        result = WorkflowResult(...)
        # ... do work ...
        return result

    async def cleanup(self):
        # Release resources
        pass
```

### 2. Use Workflow Engine

```python
from factory.core.workflow_engine import WorkflowEngine

engine = WorkflowEngine()
workflow = MyWorkflow(required_key="value")

result = await engine.run_workflow(workflow)
print(f"Status: {result.status}")
print(f"Duration: {result.duration}s")
```

## Best Practices

1. **Always validate context** in setup()
2. **Handle errors gracefully** with try/except
3. **Log progress** for debugging
4. **Store intermediate results** in outputs
5. **Clean up resources** in cleanup()
6. **Make workflows reusable** with parameters
