"""Project genesis workflow for starting new writing projects."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from factory.core.agent_pool import AgentPool
from factory.core.workflow_engine import WorkflowResult, WorkflowStatus
from factory.workflows.base_workflow import BaseWorkflow

logger = logging.getLogger(__name__)


class ProjectGenesisWorkflow(BaseWorkflow):
    """Initialize a new writing project from scratch.

    This workflow:
    1. Gathers initial prompts (genre, themes, ideas)
    2. Generates 3-5 main characters
    3. Generates world/setting details
    4. Generates story structure (3 or 4 acts)
    5. Creates project directory structure
    6. Populates initial reference files
    """

    def __init__(
        self,
        agent_pool: AgentPool,
        project_name: str,
        genre: str,
        themes: List[str],
        basic_idea: str,
        output_dir: Optional[Path] = None,
        num_characters: int = 5,
        act_structure: int = 3,
    ):
        """Initialize project genesis workflow.

        Args:
            agent_pool: Pool of available agents
            project_name: Name of the project
            genre: Genre (sci-fi, fantasy, thriller, etc.)
            themes: List of major themes
            basic_idea: Basic story concept
            output_dir: Output directory for project files
            num_characters: Number of main characters to generate
            act_structure: Number of acts (3 or 4)
        """
        super().__init__(
            name="project-genesis",
            context={
                "project_name": project_name,
                "genre": genre,
                "themes": themes,
                "basic_idea": basic_idea,
                "num_characters": num_characters,
                "act_structure": act_structure,
            }
        )

        self.agent_pool = agent_pool
        self.output_dir = output_dir or Path(f"./{project_name}")

        # Generation settings
        self.default_agents = ["claude-sonnet-4.5", "gpt-4o", "gemini-2-flash"]

    async def setup(self) -> None:
        """Setup workflow."""
        # Validate context
        self.validate_context([
            "project_name",
            "genre",
            "themes",
            "basic_idea"
        ])

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created project directory: {self.output_dir}")

    async def execute(self) -> WorkflowResult:
        """Execute project genesis workflow.

        Returns:
            WorkflowResult with generated project materials
        """
        result = WorkflowResult(
            workflow_id=self.workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now(),
            steps_total=5
        )

        try:
            # Step 1: Generate characters
            characters = await self._generate_characters()
            result.outputs["characters"] = characters
            result.steps_completed += 1

            # Step 2: Generate world/setting
            world = await self._generate_world()
            result.outputs["world"] = world
            result.steps_completed += 1

            # Step 3: Generate story structure
            structure = await self._generate_structure()
            result.outputs["structure"] = structure
            result.steps_completed += 1

            # Step 4: Create project files
            await self._create_project_files(characters, world, structure)
            result.steps_completed += 1

            # Step 5: Generate initial outline
            outline = await self._generate_outline(characters, world, structure)
            result.outputs["outline"] = outline
            result.steps_completed += 1

            result.status = WorkflowStatus.COMPLETED
            result.completed_at = datetime.now()

            logger.info(f"Project genesis complete: {self.context['project_name']}")

        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.now()
            logger.error(f"Project genesis failed: {e}")

        return result

    async def cleanup(self) -> None:
        """Cleanup workflow resources."""
        pass

    async def _generate_characters(self) -> List[Dict[str, str]]:
        """Generate main characters."""
        prompt = f"""Generate {self.context['num_characters']} main characters for a {self.context['genre']} story.

Story Concept: {self.context['basic_idea']}
Themes: {', '.join(self.context['themes'])}

For each character, provide:
- Name
- Age and background
- Role in the story
- Key personality traits
- Motivation/goals
- Unique abilities or skills

Make characters diverse and complementary to each other."""

        # Use multi-model generation (mock for now)
        return [
            {
                "name": f"Character {i+1}",
                "description": "Generated character description"
            }
            for i in range(self.context['num_characters'])
        ]

    async def _generate_world(self) -> Dict[str, str]:
        """Generate world/setting details."""
        prompt = f"""Generate world/setting details for a {self.context['genre']} story.

Story Concept: {self.context['basic_idea']}
Themes: {', '.join(self.context['themes'])}

Provide:
- Time period and location
- Social/political structure
- Technology level
- Magic/special systems (if applicable)
- Key locations
- Unique world rules"""

        return {
            "description": "Generated world description",
            "key_locations": ["Location 1", "Location 2"],
            "unique_elements": ["Element 1", "Element 2"]
        }

    async def _generate_structure(self) -> Dict[str, Any]:
        """Generate story structure."""
        prompt = f"""Generate a {self.context['act_structure']}-act story structure.

Story Concept: {self.context['basic_idea']}
Genre: {self.context['genre']}
Themes: {', '.join(self.context['themes'])}

Provide:
- Act breakdown with major events
- Key turning points
- Character arc milestones
- Thematic development"""

        return {
            "acts": [
                {"act": i+1, "description": f"Act {i+1} description"}
                for i in range(self.context['act_structure'])
            ]
        }

    async def _create_project_files(
        self,
        characters: List[Dict],
        world: Dict,
        structure: Dict
    ) -> None:
        """Create project directory structure and files."""
        # Create directories
        (self.output_dir / "reference" / "characters").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "reference" / "worldbuilding").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "manuscript").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "notes").mkdir(parents=True, exist_ok=True)

        # Write project info
        with open(self.output_dir / "PROJECT.md", "w") as f:
            f.write(f"# {self.context['project_name']}\n\n")
            f.write(f"**Genre**: {self.context['genre']}\n\n")
            f.write(f"**Themes**: {', '.join(self.context['themes'])}\n\n")
            f.write(f"## Story Concept\n\n{self.context['basic_idea']}\n")

        logger.info(f"Created project structure in {self.output_dir}")

    async def _generate_outline(
        self,
        characters: List[Dict],
        world: Dict,
        structure: Dict
    ) -> Dict[str, Any]:
        """Generate initial chapter outline."""
        return {
            "chapters": [
                {"chapter": i+1, "title": f"Chapter {i+1}"}
                for i in range(10)
            ]
        }
