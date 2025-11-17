"""Starter Skill Generator - Generate skills from personal (non-fiction) voice.

Generates 6 custom skills for beginners based on StarterVoiceProfile extracted
from personal writing (emails, social media, diary).

Differences from novel skills:
- Lower confidence prompts
- Broader acceptance criteria
- Reminders about starter mode
- Encouragement to upgrade at 2,500 words
"""

from typing import Dict, Any
from pathlib import Path
from anthropic import Anthropic
import json
import logging

from factory.core.dual_voice_profiles import StarterVoiceProfile
from factory.core.skill_generator import GeneratedSkill

logger = logging.getLogger(__name__)


class StarterSkillGenerator:
    """Generate skills from personal (non-fiction) voice for beginners."""

    def __init__(self, anthropic_client: Anthropic):
        """Initialize starter skill generator.

        Args:
            anthropic_client: Anthropic API client for LLM-based generation
        """
        self.client = anthropic_client
        self.templates_dir = Path("factory/knowledge/templates")

    async def generate_starter_skills(
        self,
        project_name: str,
        starter_voice: StarterVoiceProfile,
        genre: str
    ) -> Dict[str, GeneratedSkill]:
        """Generate 6 starter skills tuned to personal voice.

        Skills generated:
        1. scene-analyzer-starter (broad criteria)
        2. scene-enhancer-starter (focus on basics)
        3. character-validator-starter (consistency only)
        4. scene-writer-starter (simple generation)
        5. scene-multiplier-starter (3 variations instead of 5)
        6. scaffold-generator-starter (basic scaffolds)

        Args:
            project_name: Name of the project
            starter_voice: StarterVoiceProfile from personal writing
            genre: Target genre

        Returns:
            Dict mapping skill_type -> GeneratedSkill
        """
        logger.info(f"Generating starter skills for project: {project_name}")

        skills = {}

        # Generate each skill type with starter mode flags
        skills["scene-analyzer"] = await self._generate_starter_analyzer(
            project_name, starter_voice, genre
        )

        skills["scene-enhancer"] = await self._generate_starter_enhancer(
            project_name, starter_voice, genre
        )

        skills["character-validator"] = await self._generate_starter_character_validator(
            project_name, starter_voice, genre
        )

        skills["scene-writer"] = await self._generate_starter_writer(
            project_name, starter_voice, genre
        )

        skills["scene-multiplier"] = await self._generate_starter_multiplier(
            project_name, starter_voice, genre
        )

        skills["scaffold-generator"] = await self._generate_starter_scaffold(
            project_name, starter_voice, genre
        )

        logger.info(f"Generated {len(skills)} starter skills successfully")
        return skills

    # Private methods for generating each skill type

    async def _generate_starter_analyzer(
        self,
        project_name: str,
        starter_voice: StarterVoiceProfile,
        genre: str
    ) -> GeneratedSkill:
        """Generate scene-analyzer-starter skill.

        Uses broader criteria since starter voice is from casual writing.
        """
        skill_name = f"scene-analyzer-starter-{project_name}"

        prompt = f"""Create a scene analyzer skill for a BEGINNER writer in starter mode.

CONTEXT:
- Project: {project_name}
- Genre: {genre}
- Voice extracted from: {', '.join(starter_voice.source_types)}
- This is STARTER MODE (casual writing, not fiction yet)

VOICE PROFILE:
{json.dumps(starter_voice.to_dict(), indent=2)}

Generate a SKILL.md that:
1. Scores scenes 0-100 using BROAD criteria (more forgiving)
2. Uses voice characteristics from personal writing
3. Focuses on basics: clarity, engagement, craft fundamentals
4. Includes encouragement to reach 2,500 words for upgrade

QUALITY CRITERIA (100 points):
{json.dumps(starter_voice.quality_criteria.to_dict(), indent=2)}

IMPORTANT: Add reminders that this is starter mode:
- "This is a starter skill based on your casual writing"
- "Upgrade at 2,500 words for fiction-tuned analysis"
- Be encouraging and supportive

Return complete SKILL.md in markdown format.
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt}]
        )

        skill_prompt = response.content[0].text

        # Add starter caveats
        skill_prompt = self._add_starter_caveats(skill_prompt, starter_voice.upgrade_threshold)

        # Generate references
        references = {
            "voice-profile.md": self._format_starter_voice_profile(starter_voice),
            "quality-criteria.md": self._format_quality_criteria(starter_voice.quality_criteria),
            "starter-mode-guide.md": self._create_starter_mode_guide(starter_voice)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scene-analyzer",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=starter_voice
        )

    async def _generate_starter_enhancer(
        self,
        project_name: str,
        starter_voice: StarterVoiceProfile,
        genre: str
    ) -> GeneratedSkill:
        """Generate scene-enhancer-starter skill.

        Focuses on basic improvements, not deep voice matching.
        """
        skill_name = f"scene-enhancer-starter-{project_name}"

        prompt = f"""Create a scene enhancer skill for a BEGINNER writer in starter mode.

CONTEXT:
- Project: {project_name}
- Genre: {genre}
- Voice from: {', '.join(starter_voice.source_types)}
- STARTER MODE: Focus on basics, not perfection

VOICE PROFILE:
{json.dumps(starter_voice.to_dict(), indent=2)}

Generate SKILL.md that:
1. Makes SIMPLE improvements (clarity, grammar, pacing)
2. Preserves the writer's natural voice (don't over-polish)
3. Fixes only obvious issues
4. Encourages progress ("Getting words on page matters most!")

Use a simplified 5-pass ritual:
1. Read for understanding
2. Fix grammar/typos
3. Improve clarity
4. Polish dialogue
5. Final check

IMPORTANT: Keep it simple. Don't try to make every sentence perfect.
Remind them this is starter mode and will upgrade at 2,500 words.

Return complete SKILL.md in markdown format.
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt}]
        )

        skill_prompt = response.content[0].text
        skill_prompt = self._add_starter_caveats(skill_prompt, starter_voice.upgrade_threshold)

        references = {
            "voice-profile.md": self._format_starter_voice_profile(starter_voice),
            "starter-mode-guide.md": self._create_starter_mode_guide(starter_voice)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scene-enhancer",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=starter_voice
        )

    async def _generate_starter_character_validator(
        self,
        project_name: str,
        starter_voice: StarterVoiceProfile,
        genre: str
    ) -> GeneratedSkill:
        """Generate character-validator-starter skill.

        Checks basic consistency only.
        """
        skill_name = f"character-validator-starter-{project_name}"

        # Character validator is less voice-dependent
        prompt = f"""Create a character validator skill for a BEGINNER writer.

CONTEXT:
- Project: {project_name}
- Genre: {genre}
- STARTER MODE: Check basics only

Generate SKILL.md that checks:
1. Name consistency (same name throughout)
2. Basic trait consistency (eye color, age, etc.)
3. Dialogue patterns (does character sound consistent?)
4. Simple relationship tracking

Don't be overly strict. Focus on catching obvious errors.

IMPORTANT: This is starter mode. Be encouraging!
"You're building your characters. Consistency will improve as you write."

Return complete SKILL.md in markdown format.
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        skill_prompt = response.content[0].text
        skill_prompt = self._add_starter_caveats(skill_prompt, starter_voice.upgrade_threshold)

        references = {
            "starter-mode-guide.md": self._create_starter_mode_guide(starter_voice)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="character-validator",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=starter_voice
        )

    async def _generate_starter_writer(
        self,
        project_name: str,
        starter_voice: StarterVoiceProfile,
        genre: str
    ) -> GeneratedSkill:
        """Generate scene-writer-starter skill.

        Writes new scenes based on personal voice, adapted for fiction.
        """
        skill_name = f"scene-writer-starter-{project_name}"

        prompt = f"""Create a scene writer skill for a BEGINNER in starter mode.

CONTEXT:
- Project: {project_name}
- Genre: {genre}
- Voice from: {', '.join(starter_voice.source_types)}

VOICE PROFILE (from personal writing):
{json.dumps(starter_voice.to_dict(), indent=2)}

Generate SKILL.md that:
1. Writes scenes using the writer's natural voice
2. Adapts casual patterns for fiction (show don't tell, deeper POV)
3. Keeps it simple and achievable
4. Encourages "Done is better than perfect"

IMPORTANT: This is their FIRST fiction writing.
- Use their personal voice as foundation
- Don't expect literary perfection
- Focus on storytelling over style
- Celebrate every scene written ("You're 50 words closer to 2,500!")

Return complete SKILL.md in markdown format.
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt}]
        )

        skill_prompt = response.content[0].text
        skill_prompt = self._add_starter_caveats(skill_prompt, starter_voice.upgrade_threshold)

        references = {
            "voice-profile.md": self._format_starter_voice_profile(starter_voice),
            "starter-mode-guide.md": self._create_starter_mode_guide(starter_voice)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scene-writer",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=starter_voice
        )

    async def _generate_starter_multiplier(
        self,
        project_name: str,
        starter_voice: StarterVoiceProfile,
        genre: str
    ) -> GeneratedSkill:
        """Generate scene-multiplier-starter skill.

        Creates 3 variations instead of 5 (simpler for beginners).
        """
        skill_name = f"scene-multiplier-starter-{project_name}"

        prompt = f"""Create a scene multiplier skill for a BEGINNER in starter mode.

CONTEXT:
- Project: {project_name}
- Genre: {genre}
- STARTER MODE: Generate 3 variations (not 5)

VOICE PROFILE:
{json.dumps(starter_voice.to_dict(), indent=2)}

Generate SKILL.md that:
1. Creates 3 variations of a scene (simpler than 5)
2. Each uses the writer's personal voice
3. Each explores different narrative choices
4. Helps writer see options without overwhelming

IMPORTANT: Starter mode = 3 variations.
Upgrade to 5 at 2,500 words for more variety.

Return complete SKILL.md in markdown format.
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=5000,
            messages=[{"role": "user", "content": prompt}]
        )

        skill_prompt = response.content[0].text
        skill_prompt = self._add_starter_caveats(skill_prompt, starter_voice.upgrade_threshold)

        references = {
            "voice-profile.md": self._format_starter_voice_profile(starter_voice)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scene-multiplier",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=starter_voice
        )

    async def _generate_starter_scaffold(
        self,
        project_name: str,
        starter_voice: StarterVoiceProfile,
        genre: str
    ) -> GeneratedSkill:
        """Generate scaffold-generator-starter skill.

        Creates basic scaffolds to help beginners get started.
        """
        skill_name = f"scaffold-generator-starter-{project_name}"

        prompt = f"""Create a scaffold generator skill for a BEGINNER in starter mode.

CONTEXT:
- Project: {project_name}
- Genre: {genre}
- STARTER MODE: Simple, clear scaffolds

Generate SKILL.md that:
1. Transforms minimal outlines into basic scaffolds
2. Uses clear, simple structure
3. Helps writer see what to write next
4. Provides gentle guidance without overwhelming

IMPORTANT: Beginners need SIMPLE scaffolds.
- Clear beat-by-beat breakdown
- Obvious scene goals
- Hints at emotional trajectory
- Not too prescriptive (let them discover their voice)

Return complete SKILL.md in markdown format.
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=5000,
            messages=[{"role": "user", "content": prompt}]
        )

        skill_prompt = response.content[0].text
        skill_prompt = self._add_starter_caveats(skill_prompt, starter_voice.upgrade_threshold)

        references = {
            "starter-mode-guide.md": self._create_starter_mode_guide(starter_voice)
        }

        return GeneratedSkill(
            skill_name=skill_name,
            skill_type="scaffold-generator",
            skill_prompt=skill_prompt,
            references=references,
            voice_profile=starter_voice
        )

    # Helper methods

    def _add_starter_caveats(self, skill_prompt: str, upgrade_threshold: int) -> str:
        """Add reminders that this is starter mode.

        Args:
            skill_prompt: Original skill prompt
            upgrade_threshold: Words needed to upgrade

        Returns:
            Skill prompt with starter caveats added
        """
        caveat = f"""
---

## ⚠️ STARTER MODE ACTIVE

This is a **STARTER SKILL** based on your casual writing (emails, social media, diary).

**What this means:**
- Analysis is based on personal voice, not fiction voice yet
- Criteria are broader and more forgiving
- Focus is on getting words on the page

**Your Progress:**
- Write {upgrade_threshold:,} words of fiction to unlock **NOVEL SKILLS**
- Novel skills will be tuned to YOUR fiction voice
- This upgrade will feel like leveling up! 🎉

**For now:**
- Don't worry about perfection
- Focus on storytelling
- Build momentum
- Every word counts toward your upgrade!

---

"""
        # Insert caveat after the first heading or at the beginning
        if skill_prompt.startswith("#"):
            # Find first double newline after heading
            first_break = skill_prompt.find("\n\n")
            if first_break != -1:
                return skill_prompt[:first_break] + "\n\n" + caveat + skill_prompt[first_break+2:]

        # Default: add at beginning after title
        return caveat + skill_prompt

    def _format_starter_voice_profile(self, voice: StarterVoiceProfile) -> str:
        """Format starter voice profile as markdown reference.

        Args:
            voice: StarterVoiceProfile to format

        Returns:
            Markdown formatted voice profile
        """
        md = f"""# Starter Voice Profile: {voice.voice_name}

**⚠️ STARTER MODE**
Based on: {', '.join(voice.source_types)}
Total words analyzed: {voice.total_words:,}
Confidence level: {voice.confidence_level}

**Upgrade Threshold:** {voice.upgrade_threshold:,} words of fiction

---

## Primary Characteristics

{chr(10).join(f"- {char}" for char in voice.primary_characteristics)}

## Sentence Structure

- **Typical Length:** {voice.sentence_structure.get('typical_length', 'N/A')}
- **Compression Level:** {voice.sentence_structure.get('compression_level', 'N/A')}/10
- **Preferred Patterns:** {', '.join(voice.sentence_structure.get('preferred_patterns', []))}

## Vocabulary

- **Formality:** {voice.vocabulary.get('formality_level', 'N/A')}
- **Complexity:** {voice.vocabulary.get('complexity', 'N/A')}
- **Distinctive Domains:** {', '.join(voice.vocabulary.get('distinctive_domains', []))}

## POV Style

- **Depth:** {voice.pov_style.get('depth', 'N/A')}
- **Consciousness Mode:** {voice.pov_style.get('consciousness_mode_percentage', 'N/A')}
- **Filter Word Tolerance:** {voice.pov_style.get('filter_word_tolerance', 'N/A')}

---

## ⚡ Warnings

{chr(10).join(f"- {warning}" for warning in voice.warnings)}

---

## Usage

This is your **starter voice** from personal writing. As you write fiction, your voice may evolve:
- Sentence structure may shift (more varied, more compressed, etc.)
- Vocabulary may expand (more literary, more specific to genre)
- POV depth may deepen (more immersive)

**At {voice.upgrade_threshold:,} words:** Upgrade to novel skills tuned to YOUR fiction voice!
"""
        return md

    def _format_quality_criteria(self, criteria) -> str:
        """Format quality criteria as markdown.

        Args:
            criteria: QualityCriteria object

        Returns:
            Markdown formatted criteria
        """
        md = f"# Quality Criteria ({criteria.total_points} points)\n\n"
        md += "**⚠️ STARTER MODE:** Criteria are broader and more forgiving.\n\n"
        md += "---\n\n"

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

    def _create_starter_mode_guide(self, voice: StarterVoiceProfile) -> str:
        """Create starter mode guide reference.

        Args:
            voice: StarterVoiceProfile

        Returns:
            Markdown guide
        """
        return f"""# Starter Mode Guide

## What is Starter Mode?

You're in **Starter Mode** because you're beginning with **0 words of fiction** written. Your skills are based on your personal writing ({', '.join(voice.source_types)}) instead of fiction samples.

## How It Works

### Phase 1: Write with Starter Skills (0 - {voice.upgrade_threshold:,} words)

- ✅ Use AI tools tuned to your personal voice
- ✅ Focus on getting words on the page
- ✅ Don't worry about perfection
- ✅ Build momentum and learn your story

### Phase 2: Upgrade to Novel Skills ({voice.upgrade_threshold:,}+ words)

- 🎉 Automatic prompt when you hit {voice.upgrade_threshold:,} words
- 🔄 System analyzes your fiction writing
- ⚡ Generates new skills tuned to YOUR fiction voice
- 🚀 Unlock advanced features and higher accuracy

## Differences: Starter vs Novel Skills

| Feature | Starter Skills | Novel Skills |
|---------|---------------|--------------|
| Based on | Personal writing | Your fiction |
| Confidence | Medium | High |
| Criteria | Broader, forgiving | Precise, genre-specific |
| Focus | Getting started | Fine-tuning craft |
| Variations | 3 | 5 |

## Tips for Starter Mode

1. **Don't overthink it** - Your first draft is meant to be rough
2. **Trust the process** - Your fiction voice will emerge as you write
3. **Celebrate progress** - Every 100 words is a win
4. **Watch your word count** - You're building toward something better!

## Your Progress

Track your progress in the sidebar:
- **Current words:** 0
- **Target:** {voice.upgrade_threshold:,}
- **Progress:** ░░░░░░░░░░ 0%

Every scene you write brings you closer to **Novel Skills**! 🎯

---

*This guide will be replaced with advanced features when you upgrade.*
"""
