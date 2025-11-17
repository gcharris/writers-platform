# Scene Multiplier Template

## Purpose

Generates multiple creative variations of the same scene outline using different approaches, styles, or perspectives. This template can be adapted for any writing project to explore different ways of writing the same narrative moment.

## How to Use

### For The-Explants:
Copy the skill from `/The-Explants/.claude/skills/explants-scene-multiplier/` and customize for your project.

### For New Projects:

1. **Create a project-specific skill** in your project's `.claude/skills/` directory
2. **Customize the voice requirements** based on your narrative style
3. **Define your scene variation parameters** (POV, tone, pacing, etc.)
4. **Specify your genre conventions** and constraints

## Key Components

- **Input**: Scene outline or brief description
- **Output**: 5+ variations of the same scene
- **Customization Points**:
  - Narrative voice requirements
  - Character voice specifications
  - POV constraints
  - Genre conventions
  - Success criteria

## Integration with Framework

This template works with the multi-agent orchestration system:

```python
from orchestration.scene_writer import SceneWriter

writer = SceneWriter("your-project")
results = writer.write_scene(
    scene_outline="Your scene description",
    agents=['claude', 'gemini', 'chatgpt'],
    custom_instructions="Generate 5 variations with different emotional tones"
)
```

## Example Adaptations

### Science Fiction
- Focus on worldbuilding integration
- Technical accuracy
- Speculative concepts

### Literary Fiction
- Character interiority
- Prose style variations
- Metaphor and symbolism

### Mystery/Thriller
- Pacing variations
- Suspense building
- Information reveal strategies
