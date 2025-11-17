"""Project Creator - Create complete project directory structure.

Creates:
- .claude/skills/ - 6 custom skills
- knowledge/craft/ - Voice profile and story context
- scenes/ - Manuscript directory
- config.json - Project metadata
- README.md - Project documentation
- references/ - Uploaded reference docs
"""

from pathlib import Path
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .skill_generator import GeneratedSkill
from .voice_extractor import VoiceProfile

logger = logging.getLogger(__name__)


class ProjectCreator:
    """
    Creates complete project structure for a new novel project.

    Manages the creation of all directories, files, and metadata
    needed for a Writers Factory project.
    """

    def __init__(self, projects_root: Path):
        """Initialize project creator.

        Args:
            projects_root: Root directory for all projects (e.g., "projects/")
        """
        self.projects_root = Path(projects_root)
        self.projects_root.mkdir(parents=True, exist_ok=True)

    def create_project(
        self,
        project_name: str,
        voice_profile: VoiceProfile,
        generated_skills: Dict[str, GeneratedSkill],
        notebooklm_context: str = "",
        uploaded_docs: Optional[List[Dict]] = None
    ) -> Path:
        """
        Create complete project structure.

        Creates:
        projects/{project_name}/
        ├─ .claude/
        │   └─ skills/
        │       ├─ scene-analyzer-{project}/
        │       ├─ scene-enhancer-{project}/
        │       └─ ... (4 more)
        ├─ knowledge/
        │   └─ craft/
        │       ├─ voice-gold-standard.md (project-specific)
        │       └─ story-context.md (from NotebookLM)
        ├─ scenes/
        ├─ references/ (uploaded docs)
        ├─ config.json
        └─ README.md

        Args:
            project_name: Project identifier (e.g., "the-explants")
            voice_profile: Extracted voice profile
            generated_skills: Dictionary of skill_type -> GeneratedSkill
            notebooklm_context: Knowledge extracted from NotebookLM
            uploaded_docs: List of uploaded reference documents

        Returns:
            Path to created project directory
        """

        logger.info(f"Creating project: {project_name}")

        project_dir = self.projects_root / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create .claude/skills/
        logger.info("Saving generated skills...")
        for skill_type, skill in generated_skills.items():
            skill.save_to_disk(project_dir)

        # Create knowledge/
        logger.info("Creating knowledge base...")
        self._create_knowledge_base(project_dir, voice_profile, notebooklm_context)

        # Create scenes/
        logger.info("Creating scenes directory...")
        (project_dir / "scenes").mkdir(exist_ok=True)

        # Create config.json
        logger.info("Creating config.json...")
        self._create_config(project_dir, project_name, voice_profile, generated_skills)

        # Create README.md
        logger.info("Creating README.md...")
        self._create_readme(project_dir, project_name, voice_profile)

        # Copy uploaded docs
        if uploaded_docs:
            logger.info(f"Saving {len(uploaded_docs)} uploaded documents...")
            self._save_uploaded_docs(project_dir, uploaded_docs)

        logger.info(f"Project created successfully at: {project_dir}")
        return project_dir

    def _create_knowledge_base(
        self,
        project_dir: Path,
        voice_profile: VoiceProfile,
        notebooklm_context: str
    ):
        """Create project-specific knowledge base.

        Args:
            project_dir: Project root directory
            voice_profile: Voice profile
            notebooklm_context: NotebookLM context
        """

        kb_dir = project_dir / "knowledge" / "craft"
        kb_dir.mkdir(parents=True, exist_ok=True)

        # voice-gold-standard.md (project-specific)
        voice_gold_standard = f"""# {voice_profile.voice_name} - Voice Gold Standard

## Core Principle: Voice Authenticity

This project's voice is: **{voice_profile.voice_name}**

**Primary Characteristics:**
{chr(10).join(f"- {char}" for char in voice_profile.primary_characteristics)}

## Voice Characteristics

### Sentence Structure

- **Typical Length:** {voice_profile.sentence_structure.get('typical_length', 'N/A')} words
- **Compression Level:** {voice_profile.sentence_structure.get('compression_level', 'N/A')}/10
- **Preferred Patterns:** {', '.join(voice_profile.sentence_structure.get('preferred_patterns', []) or ['None specified'])}

### Vocabulary

- **Formality:** {voice_profile.vocabulary.get('formality_level', 'N/A')}
- **Complexity:** {voice_profile.vocabulary.get('complexity', 'N/A')}
- **Distinctive Domains:** {', '.join(voice_profile.vocabulary.get('distinctive_domains', []) or ['None specified'])}

### POV Style

- **Depth:** {voice_profile.pov_style.get('depth', 'N/A')}
- **Consciousness Mode:** {voice_profile.pov_style.get('consciousness_mode_percentage', 'N/A')}
- **Filter Word Tolerance:** {voice_profile.pov_style.get('filter_word_tolerance', 'N/A')}

## Voice Consistency Tests

Use the `scene-analyzer-{project_dir.name}` skill to check voice authenticity.

All scenes should match this voice profile. Any deviations should be intentional
and motivated by story needs (e.g., different POV character, stylistic variation).

## Metaphor Domains

{self._format_metaphor_domains_summary(voice_profile)}

## Anti-Patterns to Avoid

See `.claude/skills/*/references/anti-patterns.md` for complete list.

High-severity anti-patterns:
{self._format_high_severity_anti_patterns(voice_profile)}
"""
        (kb_dir / "voice-gold-standard.md").write_text(voice_gold_standard, encoding='utf-8')

        # story-context.md (from NotebookLM)
        if notebooklm_context:
            (kb_dir / "story-context.md").write_text(
                f"# Story Context\n\n{notebooklm_context}",
                encoding='utf-8'
            )
        else:
            (kb_dir / "story-context.md").write_text(
                "# Story Context\n\nTo be populated as project develops.\n",
                encoding='utf-8'
            )

    def _format_metaphor_domains_summary(self, voice_profile: VoiceProfile) -> str:
        """Format brief summary of metaphor domains.

        Args:
            voice_profile: Voice profile

        Returns:
            Formatted string
        """
        if not voice_profile.metaphor_domains:
            return "_No specific metaphor domains identified._"

        domains = []
        for name, domain in voice_profile.metaphor_domains.items():
            domains.append(f"- **{name.title()}**: Max {domain.max_percentage}% of metaphors")

        return "\n".join(domains)

    def _format_high_severity_anti_patterns(self, voice_profile: VoiceProfile) -> str:
        """Format high-severity anti-patterns.

        Args:
            voice_profile: Voice profile

        Returns:
            Formatted string
        """
        high_severity = [ap for ap in voice_profile.anti_patterns if ap.severity == "high"]

        if not high_severity:
            return "_None identified._"

        patterns = []
        for ap in high_severity[:5]:  # Limit to top 5
            patterns.append(f"- **{ap.name}**: {ap.description}")

        return "\n".join(patterns)

    def _create_config(
        self,
        project_dir: Path,
        project_name: str,
        voice_profile: VoiceProfile,
        generated_skills: Dict[str, GeneratedSkill]
    ):
        """Create project config.json.

        Args:
            project_dir: Project root directory
            project_name: Project name/ID
            voice_profile: Voice profile
            generated_skills: Generated skills
        """

        config = {
            "project_name": project_name,
            "project_id": project_name,
            "created_at": datetime.now().isoformat(),
            "voice_profile": {
                "name": voice_profile.voice_name,
                "genre": voice_profile.genre,
                "characteristics": voice_profile.primary_characteristics
            },
            "skills": {
                skill_type: skill.skill_name
                for skill_type, skill in generated_skills.items()
            },
            "directory_structure": {
                "skills": ".claude/skills/",
                "knowledge": "knowledge/",
                "scenes": "scenes/",
                "references": "references/"
            },
            "metadata": {
                "created_by": "Writers Factory Project Setup Wizard",
                "sprint_version": "14",
                "skill_count": len(generated_skills)
            }
        }

        (project_dir / "config.json").write_text(
            json.dumps(config, indent=2),
            encoding='utf-8'
        )

    def _create_readme(
        self,
        project_dir: Path,
        project_name: str,
        voice_profile: VoiceProfile
    ):
        """Create project README.md.

        Args:
            project_dir: Project root directory
            project_name: Project name
            voice_profile: Voice profile
        """

        readme = f"""# {project_name}

**Voice:** {voice_profile.voice_name}
**Genre:** {voice_profile.genre}
**Created:** {datetime.now().strftime('%B %d, %Y')}

## Overview

This Writers Factory project has custom AI skills generated specifically for your voice.
Each skill understands your style, your quality standards, and your anti-patterns.

## Custom Skills

This project has 6 custom AI skills:

### Analysis & Quality

- **`scene-analyzer-{project_name}`**: Score scenes 0-100 using your quality criteria
  - Checks voice authenticity, character consistency, craft quality
  - Detects your specific anti-patterns
  - Provides detailed fix suggestions

- **`scene-enhancer-{project_name}`**: Make surgical fixes to match your voice
  - 8-pass ritual for systematic improvement
  - Focuses on your anti-patterns
  - Preserves your intent while elevating craft

- **`character-validator-{project_name}`**: Check character consistency
  - Voice consistency across scenes
  - Behavioral and relationship tracking
  - Knowledge and arc validation

### Writing & Generation

- **`scene-writer-{project_name}`**: Write new scenes in your voice
  - Generates prose matching your style
  - Uses story knowledge from NotebookLM
  - Avoids your anti-patterns

- **`scene-multiplier-{project_name}`**: Generate 5 variations of a scene
  - Verbalized sampling approach
  - Explores different narrative choices
  - All variations maintain voice

- **`scaffold-generator-{project_name}`**: Expand outlines using your story knowledge
  - Transforms minimal outlines into detailed scaffolds
  - Incorporates world and character knowledge
  - Includes voice-appropriate guidance

## Usage

### Via Writers Factory Web App

Access skills through the Craft Panel:
1. Select your skill
2. Paste scene content
3. Run analysis or enhancement

### Via Claude Code CLI

```bash
# Analyze a scene
claude skill scene-analyzer-{project_name} "path/to/scene.md"

# Enhance a scene
claude skill scene-enhancer-{project_name} "path/to/scene.md"

# Generate scene variations
claude skill scene-multiplier-{project_name} "path/to/scene.md"
```

## Project Structure

```
{project_name}/
├── .claude/skills/          # Your 6 custom skills
│   ├── scene-analyzer-{project_name}/
│   │   ├── SKILL.md        # Skill prompt
│   │   └── references/     # Voice profile, criteria, etc.
│   ├── scene-enhancer-{project_name}/
│   └── ...                 # 4 more skills
├── knowledge/craft/         # Voice profile & story context
│   ├── voice-gold-standard.md
│   └── story-context.md
├── scenes/                  # Your manuscript scenes
├── references/              # Uploaded docs (style guides, etc.)
├── config.json              # Project metadata
└── README.md                # This file
```

## Voice Profile Summary

**Primary Characteristics:**
{chr(10).join(f"- {char}" for char in voice_profile.primary_characteristics)}

See `knowledge/craft/voice-gold-standard.md` for complete voice profile.

## Getting Started

1. **Add scenes**: Place manuscript files in `scenes/`
2. **Analyze**: Use `scene-analyzer-{project_name}` to score scenes
3. **Enhance**: Use `scene-enhancer-{project_name}` to improve low-scoring scenes
4. **Write**: Use `scene-writer-{project_name}` to draft new scenes
5. **Iterate**: Analyze → Enhance → Validate cycle

## Quality Standards

This project uses a 100-point scoring system:

- **95-100 (A+)**: Gold Standard - Publishable quality
- **90-94 (A)**: Excellent - Minor polish needed
- **85-89 (A-)**: Very Good - Some improvements needed
- **80-84 (B+)**: Good - Noticeable issues to address
- **Below 80**: Needs significant work

Target: All scenes at A- (85+) or better before final polish.

## Anti-Patterns

Your voice has {len(voice_profile.anti_patterns)} identified anti-patterns that skills will detect and fix.

High-severity patterns:
{self._format_high_severity_anti_patterns(voice_profile)}

See `.claude/skills/*/references/anti-patterns.md` for complete list.

---

**Generated by Writers Factory Project Setup Wizard**
Sprint 14: Project Setup Wizard
"""
        (project_dir / "README.md").write_text(readme, encoding='utf-8')

    def _save_uploaded_docs(self, project_dir: Path, uploaded_docs: List[Dict[str, Any]]):
        """Save uploaded reference documents.

        Args:
            project_dir: Project root directory
            uploaded_docs: List of document dictionaries with 'filename' and 'content'
        """

        docs_dir = project_dir / "references"
        docs_dir.mkdir(exist_ok=True)

        for doc in uploaded_docs:
            filename = doc.get("filename", "unknown.txt")
            content = doc.get("content", "")

            # Sanitize filename
            safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")

            (docs_dir / safe_filename).write_text(content, encoding='utf-8')

        logger.info(f"Saved {len(uploaded_docs)} documents to {docs_dir}")

    def load_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Load project configuration.

        Args:
            project_name: Project identifier

        Returns:
            Project config dictionary or None if not found
        """

        project_dir = self.projects_root / project_name
        config_path = project_dir / "config.json"

        if not config_path.exists():
            logger.warning(f"Project not found: {project_name}")
            return None

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        logger.info(f"Loaded project: {project_name}")
        return config

    def list_projects(self) -> List[str]:
        """List all projects.

        Returns:
            List of project names
        """

        if not self.projects_root.exists():
            return []

        projects = []
        for item in self.projects_root.iterdir():
            if item.is_dir() and (item / "config.json").exists():
                projects.append(item.name)

        return sorted(projects)

    def project_exists(self, project_name: str) -> bool:
        """Check if project exists.

        Args:
            project_name: Project identifier

        Returns:
            True if project exists
        """

        project_dir = self.projects_root / project_name
        return project_dir.exists() and (project_dir / "config.json").exists()
