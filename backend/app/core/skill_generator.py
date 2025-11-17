"""Skill Generator - Generate custom Claude Code skills for projects.

Generates 6 project-specific skills:
1. scene-analyzer - Score scenes using project-specific criteria
2. scene-enhancer - Make surgical fixes matching voice
3. character-validator - Validate character consistency
4. scene-writer - Write new scenes in project voice
5. scene-multiplier - Create 5 variations using verbalized sampling
6. scaffold-generator - Transform outlines into detailed scaffolds
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from anthropic import Anthropic
import json
import logging

from .voice_extractor import VoiceProfile, MetaphorDomain, AntiPattern, QualityCriteria

logger = logging.getLogger(__name__)


class GeneratedSkill:
    """A generated skill with all its files."""

    def __init__(
        self,
        skill_name: str,
        skill_type: str,
        skill_prompt: str,
        references: Dict[str, str],
        voice_profile: VoiceProfile
    ):
        """Initialize generated skill.

        Args:
            skill_name: Name of the skill (e.g., "scene-analyzer-the-explants")
            skill_type: Type of skill (e.g., "scene-analyzer")
            skill_prompt: Complete SKILL.md content
            references: Dictionary mapping filename -> content for reference files
            voice_profile: Voice profile used to generate this skill
        """
        self.skill_name = skill_name
        self.skill_type = skill_type
        self.skill_prompt = skill_prompt
        self.references = references
        self.voice_profile = voice_profile

    def save_to_disk(self, project_dir: Path):
        """
        Save skill to project directory.

        Creates:
        projects/{project_name}/.claude/skills/{skill_name}/
        ├─ SKILL.md
        └─ references/
            ├─ voice-profile.md
            ├─ anti-patterns.md
            └─ ...

        Args:
            project_dir: Path to project root directory
        """

        skill_dir = project_dir / ".claude" / "skills" / self.skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Write SKILL.md
        (skill_dir / "SKILL.md").write_text(self.skill_prompt, encoding='utf-8')
        logger.info(f"Saved SKILL.md to {skill_dir}")

        # Write references
        ref_dir = skill_dir / "references"
        ref_dir.mkdir(exist_ok=True)

        for filename, content in self.references.items():
            (ref_dir / filename).write_text(content, encoding='utf-8')

        logger.info(f"Saved {len(self.references)} reference files to {ref_dir}")


class SkillGenerator:
    """
    Generates custom Claude Code skills for a project.

    For each skill type, generates:
    - SKILL.md with project-specific prompts
    - references/ directory with voice profile, anti-patterns, etc.
    """

    def __init__(self, anthropic_client: Anthropic):
        """Initialize skill generator.

        Args:
            anthropic_client: Anthropic API client for LLM customization
        """
        self.client = anthropic_client
        self.templates_dir = Path("factory/knowledge/templates")

    async def generate_project_skills(
        self,
        project_name: str,
        voice_profile: VoiceProfile,
        notebooklm_context: Optional[str] = None
    ) -> Dict[str, GeneratedSkill]:
        """
        Generate all 6 skills for a project.

        Skills generated:
        1. scene-analyzer-[project]
        2. scene-enhancer-[project]
        3. character-validator-[project]
        4. scene-writer-[project]
        5. scene-multiplier-[project]
        6. scaffold-generator-[project]

        Args:
            project_name: Project identifier (e.g., "the-explants")
            voice_profile: Extracted voice profile
            notebooklm_context: Optional context from NotebookLM

        Returns:
            Dictionary mapping skill_type -> GeneratedSkill
        """

        logger.info(f"Generating 6 skills for project: {project_name}")

        skills = {}

        # Generate each skill type
        logger.info("Generating scene-analyzer skill...")
        skills["scene-analyzer"] = await self._generate_scene_analyzer(
            project_name, voice_profile
        )

        logger.info("Generating scene-enhancer skill...")
        skills["scene-enhancer"] = await self._generate_scene_enhancer(
            project_name, voice_profile
        )

        logger.info("Generating character-validator skill...")
        skills["character-validator"] = await self._generate_character_validator(
            project_name, voice_profile
        )

        logger.info("Generating scene-writer skill...")
        skills["scene-writer"] = await self._generate_scene_writer(
            project_name, voice_profile, notebooklm_context
        )

        logger.info("Generating scene-multiplier skill...")
        skills["scene-multiplier"] = await self._generate_scene_multiplier(
            project_name, voice_profile
        )

        logger.info("Generating scaffold-generator skill...")
        skills["scaffold-generator"] = await self._generate_scaffold_generator(
            project_name, voice_profile, notebooklm_context
        )

        logger.info(f"Successfully generated all 6 skills for {project_name}")
        return skills

    async def _generate_scene_analyzer(
        self,
        project_name: str,
        voice_profile: VoiceProfile
    ) -> GeneratedSkill:
        """
        Generate scene-analyzer-[project] skill.

        This skill scores scenes 0-100 using project-specific criteria.

        Args:
            project_name: Project identifier
            voice_profile: Voice profile for customization

        Returns:
            GeneratedSkill object
        """

        skill_name = f"scene-analyzer-{project_name}"

        # Generate SKILL.md
        skill_prompt = await self._generate_analyzer_prompt(voice_profile, project_name)

        # Generate reference files
        references = {
            "voice-profile.md": self._format_voice_profile_md(voice_profile),
            "anti-patterns.md": self._format_anti_patterns_md(voice_profile.anti_patterns),
            "quality-criteria.md": self._format_quality_criteria_md(voice_profile.quality_criteria),
            "metaphor-domains.md": self._format_metaphor_domains_md(voice_profile.metaphor_domains)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scene-analyzer",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=voice_profile
        )

    async def _generate_analyzer_prompt(
        self,
        voice_profile: VoiceProfile,
        project_name: str
    ) -> str:
        """
        Generate custom SKILL.md prompt for scene analyzer.

        Args:
            voice_profile: Voice profile for customization
            project_name: Project name for placeholders

        Returns:
            Complete SKILL.md content
        """

        # Load base template
        template_path = self.templates_dir / "scene-analyzer-template.md"
        template = template_path.read_text(encoding='utf-8')

        # Replace project name placeholder
        template = template.replace("{{PROJECT_NAME}}", project_name)

        # Use LLM to customize template for this voice
        customization_prompt = f"""Customize this scene analyzer skill template for a specific voice.

BASE TEMPLATE:
{template}

VOICE PROFILE:
{voice_profile.to_json()}

QUALITY CRITERIA:
{json.dumps(voice_profile.quality_criteria.to_dict() if voice_profile.quality_criteria else {}, indent=2)}

ANTI-PATTERNS:
{json.dumps([{'pattern_id': ap.pattern_id, 'name': ap.name, 'description': ap.description, 'severity': ap.severity} for ap in voice_profile.anti_patterns], indent=2)}

Generate a complete SKILL.md that:
1. Uses the base template structure
2. Customizes scoring criteria for THIS voice (total 100 points)
3. Includes voice-specific anti-patterns in detection
4. Provides voice-specific examples
5. References the project's voice-profile.md, anti-patterns.md, etc.

Return ONLY the complete SKILL.md content (markdown format)."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8000,
                messages=[{"role": "user", "content": customization_prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Failed to customize analyzer prompt: {e}")
            # Return template with basic customization
            return template

    async def _generate_scene_enhancer(
        self,
        project_name: str,
        voice_profile: VoiceProfile
    ) -> GeneratedSkill:
        """
        Generate scene-enhancer-[project] skill.

        This skill makes surgical fixes to match the voice profile.

        Args:
            project_name: Project identifier
            voice_profile: Voice profile for customization

        Returns:
            GeneratedSkill object
        """

        skill_name = f"scene-enhancer-{project_name}"

        # Load template
        template_path = self.templates_dir / "scene-enhancer-template.md"
        template = template_path.read_text(encoding='utf-8')
        template = template.replace("{{PROJECT_NAME}}", project_name)

        # Customize for voice
        customization_prompt = f"""Customize this scene enhancer skill for a specific voice.

BASE TEMPLATE:
{template}

VOICE PROFILE:
{voice_profile.to_json()}

ANTI-PATTERNS TO FIX:
{json.dumps([{'pattern_id': ap.pattern_id, 'name': ap.name, 'description': ap.description, 'regex': ap.regex, 'keywords': ap.keywords} for ap in voice_profile.anti_patterns], indent=2)}

Generate SKILL.md that:
1. Uses 8-pass ritual structure (Read, Voice Auth, Fix 1-5, Final Check)
2. Focuses on THIS voice's anti-patterns
3. Maintains THIS voice's characteristics
4. Includes voice-specific fix examples

Return complete SKILL.md (markdown)."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8000,
                messages=[{"role": "user", "content": customization_prompt}]
            )

            skill_prompt = response.content[0].text

        except Exception as e:
            logger.error(f"Failed to customize enhancer prompt: {e}")
            skill_prompt = template

        references = {
            "voice-profile.md": self._format_voice_profile_md(voice_profile),
            "anti-patterns.md": self._format_anti_patterns_md(voice_profile.anti_patterns),
            "fix-patterns.md": self._format_fix_patterns_md(voice_profile)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scene-enhancer",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=voice_profile
        )

    async def _generate_character_validator(
        self,
        project_name: str,
        voice_profile: VoiceProfile
    ) -> GeneratedSkill:
        """
        Generate character-validator-[project] skill.

        Args:
            project_name: Project identifier
            voice_profile: Voice profile for customization

        Returns:
            GeneratedSkill object
        """

        skill_name = f"character-validator-{project_name}"

        template_path = self.templates_dir / "character-validator-template.md"
        template = template_path.read_text(encoding='utf-8')

        # This skill is less voice-dependent, more about consistency
        skill_prompt = template.replace("{{PROJECT_NAME}}", project_name)

        references = {
            "voice-profile.md": self._format_voice_profile_md(voice_profile)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="character-validator",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=voice_profile
        )

    async def _generate_scene_writer(
        self,
        project_name: str,
        voice_profile: VoiceProfile,
        notebooklm_context: Optional[str]
    ) -> GeneratedSkill:
        """
        Generate scene-writer-[project] skill.

        This writes NEW scenes in the project's voice.

        Args:
            project_name: Project identifier
            voice_profile: Voice profile for customization
            notebooklm_context: Context from NotebookLM

        Returns:
            GeneratedSkill object
        """

        skill_name = f"scene-writer-{project_name}"

        template_path = self.templates_dir / "scene-writer-template.md"
        template = template_path.read_text(encoding='utf-8')
        template = template.replace("{{PROJECT_NAME}}", project_name)

        customization_prompt = f"""Customize this scene writer skill for a specific voice.

BASE TEMPLATE:
{template}

VOICE PROFILE:
{voice_profile.to_json()}

NOTEBOOKLM CONTEXT (story world, characters):
{notebooklm_context or "Not provided"}

Generate SKILL.md that:
1. Writes scenes in THIS specific voice
2. Uses voice characteristics (compression, metaphors, POV depth)
3. Avoids anti-patterns
4. Incorporates story world knowledge from NotebookLM

Return complete SKILL.md."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8000,
                messages=[{"role": "user", "content": customization_prompt}]
            )

            skill_prompt = response.content[0].text

        except Exception as e:
            logger.error(f"Failed to customize writer prompt: {e}")
            skill_prompt = template

        references = {
            "voice-profile.md": self._format_voice_profile_md(voice_profile),
            "anti-patterns.md": self._format_anti_patterns_md(voice_profile.anti_patterns),
            "story-context.md": notebooklm_context or "# Story Context\n\nTo be populated during project work."
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scene-writer",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=voice_profile
        )

    async def _generate_scene_multiplier(
        self,
        project_name: str,
        voice_profile: VoiceProfile
    ) -> GeneratedSkill:
        """
        Generate scene-multiplier-[project] skill.

        Creates 5 variations of a scene using verbalized sampling.

        Args:
            project_name: Project identifier
            voice_profile: Voice profile for customization

        Returns:
            GeneratedSkill object
        """

        skill_name = f"scene-multiplier-{project_name}"

        template_path = self.templates_dir / "scene-multiplier-template.md"
        template = template_path.read_text(encoding='utf-8')
        template = template.replace("{{PROJECT_NAME}}", project_name)

        customization_prompt = f"""Customize this scene multiplier for a specific voice.

BASE TEMPLATE:
{template}

VOICE PROFILE:
{voice_profile.to_json()}

Generate SKILL.md that:
1. Creates 5 variations using verbalized sampling
2. Each variation maintains THIS voice
3. Each explores different narrative choices
4. All avoid anti-patterns

Return complete SKILL.md."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8000,
                messages=[{"role": "user", "content": customization_prompt}]
            )

            skill_prompt = response.content[0].text

        except Exception as e:
            logger.error(f"Failed to customize multiplier prompt: {e}")
            skill_prompt = template

        references = {
            "voice-profile.md": self._format_voice_profile_md(voice_profile)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scene-multiplier",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=voice_profile
        )

    async def _generate_scaffold_generator(
        self,
        project_name: str,
        voice_profile: VoiceProfile,
        notebooklm_context: Optional[str]
    ) -> GeneratedSkill:
        """
        Generate scaffold-generator-[project] skill.

        Transforms minimal outlines into detailed scaffolds.

        Args:
            project_name: Project identifier
            voice_profile: Voice profile for customization
            notebooklm_context: Context from NotebookLM

        Returns:
            GeneratedSkill object
        """

        skill_name = f"scaffold-generator-{project_name}"

        template_path = self.templates_dir / "scaffold-generator-template.md"
        template = template_path.read_text(encoding='utf-8')
        template = template.replace("{{PROJECT_NAME}}", project_name)

        customization_prompt = f"""Customize this scaffold generator for a project.

BASE TEMPLATE:
{template}

VOICE PROFILE:
{voice_profile.to_json()}

NOTEBOOKLM CONTEXT:
{notebooklm_context or "Not provided"}

Generate SKILL.md that:
1. Expands outlines using NotebookLM knowledge
2. Generates scaffolds appropriate for THIS voice
3. Includes voice requirements in success criteria

Return complete SKILL.md."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=8000,
                messages=[{"role": "user", "content": customization_prompt}]
            )

            skill_prompt = response.content[0].text

        except Exception as e:
            logger.error(f"Failed to customize scaffold prompt: {e}")
            skill_prompt = template

        references = {
            "voice-profile.md": self._format_voice_profile_md(voice_profile),
            "story-context.md": notebooklm_context or "# Story Context\n\nTo be populated."
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scaffold-generator",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=voice_profile
        )

    # Helper methods for formatting reference files

    def _format_voice_profile_md(self, voice_profile: VoiceProfile) -> str:
        """Format voice profile as markdown reference file.

        Args:
            voice_profile: Voice profile to format

        Returns:
            Markdown content
        """

        md = f"""# Voice Profile: {voice_profile.voice_name}

**Genre:** {voice_profile.genre}

## Primary Characteristics

{chr(10).join(f"- {char}" for char in voice_profile.primary_characteristics)}

## Sentence Structure

- **Typical Length:** {voice_profile.sentence_structure.get('typical_length', 'N/A')}
- **Compression Level:** {voice_profile.sentence_structure.get('compression_level', 'N/A')}/10
- **Preferred Patterns:** {', '.join(voice_profile.sentence_structure.get('preferred_patterns', []))}

## Vocabulary

- **Formality:** {voice_profile.vocabulary.get('formality_level', 'N/A')}
- **Complexity:** {voice_profile.vocabulary.get('complexity', 'N/A')}
- **Distinctive Domains:** {', '.join(voice_profile.vocabulary.get('distinctive_domains', []))}

## POV Style

- **Depth:** {voice_profile.pov_style.get('depth', 'N/A')}
- **Consciousness Mode:** {voice_profile.pov_style.get('consciousness_mode_percentage', 'N/A')}
- **Filter Word Tolerance:** {voice_profile.pov_style.get('filter_word_tolerance', 'N/A')}

## Consistency Notes

{chr(10).join(f"- {note}" for note in voice_profile.voice_consistency_notes)}

## Usage

This voice profile defines the target voice for all writing in this project.
Use it to evaluate authenticity and guide revisions.
"""
        return md

    def _format_anti_patterns_md(self, anti_patterns: List[AntiPattern]) -> str:
        """Format anti-patterns as markdown.

        Args:
            anti_patterns: List of anti-patterns to format

        Returns:
            Markdown content
        """

        md = "# Anti-Patterns to Avoid\n\n"

        for ap in anti_patterns:
            md += f"## {ap.name}\n\n"
            md += f"**Severity:** {ap.severity.upper()}\n\n"
            md += f"**Description:** {ap.description}\n\n"
            md += f"**Why Avoid:** {ap.why_avoid}\n\n"

            if ap.regex:
                md += f"**Detection (Regex):** `{ap.regex}`\n\n"
            if ap.keywords:
                md += f"**Detection (Keywords):** {', '.join(ap.keywords)}\n\n"

            if ap.examples:
                md += "**Examples from your writing:**\n"
                for ex in ap.examples:
                    md += f"- _{ex}_\n"
                md += "\n"

            md += "---\n\n"

        return md

    def _format_quality_criteria_md(self, criteria: Optional[QualityCriteria]) -> str:
        """Format quality criteria as markdown.

        Args:
            criteria: Quality criteria to format

        Returns:
            Markdown content
        """

        if not criteria:
            return "# Quality Criteria\n\nTo be defined.\n"

        md = f"# Quality Criteria ({criteria.total_points} points)\n\n"

        for cat in criteria.categories:
            md += f"## {cat['name']} ({cat['points']} points)\n\n"
            md += f"{cat['description']}\n\n"

            if 'sub_criteria' in cat:
                md += "**Sub-criteria:**\n\n"
                for sub in cat['sub_criteria']:
                    md += f"- **{sub['name']}** ({sub['points']} pts): {sub['check']}\n"
                md += "\n"

            md += "---\n\n"

        return md

    def _format_metaphor_domains_md(self, domains: Dict[str, MetaphorDomain]) -> str:
        """Format metaphor domains as markdown.

        Args:
            domains: Dictionary of metaphor domains

        Returns:
            Markdown content
        """

        md = "# Metaphor Domains\n\n"

        if not domains:
            md += "No specific metaphor domains identified.\n"
            return md

        for name, domain in domains.items():
            md += f"## {name.title()}\n\n"
            md += f"**Max Recommended:** {domain.max_percentage}% of metaphors\n\n"
            md += f"**Keywords:** {', '.join(domain.keywords)}\n\n"
            md += "**Examples from your writing:**\n"
            for ex in domain.examples:
                md += f"- _{ex}_\n"
            md += "\n---\n\n"

        return md

    def _format_fix_patterns_md(self, voice_profile: VoiceProfile) -> str:
        """Format fix patterns for enhancer.

        Args:
            voice_profile: Voice profile with anti-patterns

        Returns:
            Markdown content
        """

        md = "# Fix Patterns\n\n"
        md += "Common fixes to apply during enhancement:\n\n"

        for ap in voice_profile.anti_patterns:
            md += f"## Fix: {ap.name}\n\n"
            md += f"**Detection:** {ap.detection_method}\n\n"
            md += f"**Fix Strategy:** Remove or rewrite to avoid {ap.description.lower()}\n\n"
            md += "---\n\n"

        return md
