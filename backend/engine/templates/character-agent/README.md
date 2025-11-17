# Character Agent Template

## Purpose

Maintains character consistency, tracks development, and ensures authentic character behavior across scenes and chapters.

## Features

- **Character Profile Management**: Centralized character data in Google File Store
- **Consistency Checking**: Validates character actions against established traits
- **Development Tracking**: Monitors character arcs and growth
- **Voice Authentication**: Ensures dialogue matches character personality

## Setup for Your Project

1. Create character profiles in `characters/` folder (JSON or Markdown)
2. Define character traits, backstory, relationships, goals
3. Upload to Google File Store
4. Use in scene generation to auto-query character data

## Character Profile Template

```json
{
  "name": "Character Name",
  "role": "protagonist/antagonist/supporting",
  "age": 30,
  "background": "Brief backstory",
  "personality_traits": [
    "trait1",
    "trait2"
  ],
  "goals": {
    "immediate": "Short-term goal",
    "long_term": "Overall arc"
  },
  "relationships": {
    "character2": "nature of relationship"
  },
  "voice_notes": "How they speak, quirks, patterns",
  "arc_notes": "Character development trajectory"
}
```

## Integration

The framework automatically queries character data when generating scenes:

```python
results = writer.write_scene(
    scene_outline="Character confronts their past",
    character_names=["CharacterName"],  # Auto-queries character profile
    agents=['claude', 'gemini']
)
```
