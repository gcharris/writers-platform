"""Scene generation workflow with knowledge context."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from factory.core.workflow_engine import Workflow, WorkflowResult, WorkflowStatus
from datetime import datetime

logger = logging.getLogger(__name__)


class SceneGenerationWorkflow(Workflow):
    """Generate scene from outline with knowledge context.

    Steps:
    1. Parse outline/scaffold
    2. Query knowledge base for context
    3. Generate scene
    4. Return result with metadata
    """

    def __init__(
        self,
        knowledge_router: Optional[Any] = None,
        agent_pool: Optional[Any] = None,
        cost_tracker: Optional[Any] = None,
        **kwargs
    ):
        """Initialize scene generation workflow.

        Args:
            knowledge_router: Knowledge router for context queries
            agent_pool: Agent pool for scene generation
            cost_tracker: Cost tracker for logging operations
        """
        super().__init__(name="Scene Generation", **kwargs)
        self.knowledge_router = knowledge_router
        self.agent_pool = agent_pool
        self.cost_tracker = cost_tracker

    async def run(
        self,
        outline: str,
        model_name: str = "claude-sonnet-4.5",
        use_knowledge_context: bool = True,
        context_queries: Optional[List[str]] = None
    ) -> WorkflowResult:
        """Execute scene generation workflow.

        Args:
            outline: Scene outline/scaffold text
            model_name: Model to use for generation
            use_knowledge_context: Whether to query knowledge base
            context_queries: Optional specific queries for context

        Returns:
            WorkflowResult with generated scene
        """
        # Add workflow steps
        self.add_step(
            "parse_outline",
            self._parse_outline,
            dependencies=[]
        )

        if use_knowledge_context and self.knowledge_router:
            self.add_step(
                "get_context",
                self._get_context,
                dependencies=["parse_outline"]
            )
            context_dep = ["get_context"]
        else:
            context_dep = ["parse_outline"]

        self.add_step(
            "generate_scene",
            self._generate_scene,
            dependencies=context_dep
        )

        # Set initial context
        self.context.update({
            "outline": outline,
            "model_name": model_name,
            "context_queries": context_queries or []
        })

        # Execute workflow
        try:
            self.status = WorkflowStatus.RUNNING
            result = await self.execute()
            return result
        except Exception as e:
            logger.error(f"Scene generation workflow failed: {e}")
            raise

    async def _parse_outline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse scene outline and extract metadata.

        Args:
            context: Workflow context

        Returns:
            Parsed outline data
        """
        outline = context["outline"]

        # Simple parsing - extract key information
        parsed = {
            "raw_outline": outline,
            "word_count": len(outline.split()),
            "has_pov": "POV:" in outline or "pov:" in outline.lower(),
            "has_location": "Location:" in outline or "location:" in outline.lower(),
        }

        logger.info(f"Parsed outline: {parsed['word_count']} words")
        return parsed

    async def _get_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Query knowledge base for relevant context.

        Args:
            context: Workflow context

        Returns:
            Context data from knowledge base
        """
        outline_data = context["parse_outline"]
        queries = context.get("context_queries", [])

        if not queries:
            # Auto-generate query from outline
            queries = [f"Provide context for: {outline_data['raw_outline'][:100]}"]

        context_data = {}

        for query in queries:
            try:
                result = await self.knowledge_router.query(query)
                context_data[query] = result.answer
            except Exception as e:
                logger.warning(f"Context query failed: {e}")
                context_data[query] = ""

        return {
            "queries": queries,
            "context": context_data
        }

    async def _generate_scene(self, context: Dict[str, Any]) -> str:
        """Generate scene using selected model.

        Args:
            context: Workflow context

        Returns:
            Generated scene text
        """
        outline_data = context["parse_outline"]
        model_name = context["model_name"]

        # Build prompt
        prompt = f"Generate a scene based on this outline:\n\n{outline_data['raw_outline']}"

        # Add knowledge context if available
        if "get_context" in context:
            kb_context = context["get_context"]
            context_text = "\n".join(
                f"Context: {answer}" for answer in kb_context["context"].values() if answer
            )
            if context_text:
                prompt += f"\n\nRelevant Context:\n{context_text}"

        prompt += "\n\nGenerate the complete scene with authentic voice and compressed phrasing."

        # Mock generation for now - in real implementation, use agent_pool
        logger.info(f"Generating scene with {model_name}")

        # Placeholder scene
        scene = f"""# Generated Scene

[Scene generated from outline with {model_name}]

{outline_data['raw_outline']}

[This is a placeholder. In production, this would be generated by the selected model.]
"""

        return scene

    async def execute(self) -> WorkflowResult:
        """Execute the workflow with all steps.

        Returns:
            WorkflowResult containing generated scene
        """
        started_at = datetime.now()

        try:
            # Execute steps in dependency order
            for step in self.steps:
                logger.info(f"Executing step: {step.name}")
                result = await step.execute(self.context)
                self.context[step.name] = result

            # Get final result (generated scene)
            final_scene = self.context.get("generate_scene", "")

            return WorkflowResult(
                workflow_id=self.workflow_id,
                status=WorkflowStatus.COMPLETED,
                started_at=started_at,
                completed_at=datetime.now(),
                steps_completed=len(self.steps),
                steps_total=len(self.steps),
                outputs={"scene": final_scene},
                metadata={
                    "model": self.context.get("model_name"),
                    "outline_words": self.context.get("parse_outline", {}).get("word_count", 0)
                }
            )

        except Exception as e:
            return WorkflowResult(
                workflow_id=self.workflow_id,
                status=WorkflowStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                steps_total=len(self.steps),
                steps_completed=sum(1 for s in self.steps if s.status.value == "completed"),
                errors=[str(e)],
                outputs={}
            )
