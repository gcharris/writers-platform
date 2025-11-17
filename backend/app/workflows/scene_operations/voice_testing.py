"""Voice testing workflow across multiple models."""

import logging
from typing import Dict, List, Any, Optional

from factory.core.workflow_engine import Workflow, WorkflowResult, WorkflowStatus
from datetime import datetime

logger = logging.getLogger(__name__)


class VoiceTestingWorkflow(Workflow):
    """Test voice consistency across multiple models.

    Steps:
    1. Generate outputs from all models
    2. Score voice consistency for each
    3. Compare results
    4. Recommend winner
    """

    def __init__(
        self,
        agent_pool: Optional[Any] = None,
        **kwargs
    ):
        """Initialize voice testing workflow.

        Args:
            agent_pool: Agent pool for multi-model generation
        """
        super().__init__(name="Voice Testing", **kwargs)
        self.agent_pool = agent_pool

    async def run(
        self,
        prompt: str,
        models: List[str],
        character: str = "protagonist"
    ) -> WorkflowResult:
        """Execute voice testing workflow.

        Args:
            prompt: Prompt to test across models
            models: List of model names to compare
            character: Character name for voice consistency

        Returns:
            WorkflowResult with comparison and winner
        """
        self.add_step("generate_all_models", self._generate_all_models)
        self.add_step("score_all_outputs", self._score_all_outputs, dependencies=["generate_all_models"])
        self.add_step("compare_results", self._compare_results, dependencies=["score_all_outputs"])
        self.add_step("recommend_winner", self._recommend_winner, dependencies=["compare_results"])

        self.context.update({
            "prompt": prompt,
            "models": models,
            "character": character
        })

        try:
            self.status = WorkflowStatus.RUNNING
            result = await self.execute_workflow()
            return result
        except Exception as e:
            logger.error(f"Voice testing workflow failed: {e}")
            raise

    async def _generate_all_models(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate outputs from all models."""
        prompt = context["prompt"]
        models = context["models"]

        outputs = {}

        # Mock generation for each model
        for model in models:
            logger.info(f"Generating with {model}")
            outputs[model] = f"""# Output from {model}

[Generated scene based on prompt]

{prompt}

[This is placeholder output from {model}]
"""

        return outputs

    async def _score_all_outputs(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Score voice consistency for all outputs."""
        outputs = context["generate_all_models"]
        character = context["character"]

        scores = {}

        # Mock scoring
        base_scores = {
            "claude-sonnet-4.5": 92.0,
            "claude-opus-4": 88.0,
            "gpt-4o": 85.0,
            "gemini-2-flash": 82.0
        }

        for model, output in outputs.items():
            # Simple mock scoring
            score = base_scores.get(model, 80.0)
            scores[model] = score
            logger.info(f"Voice score for {model}: {score}")

        return scores

    async def _compare_results(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare all results."""
        outputs = context["generate_all_models"]
        scores = context["score_all_outputs"]

        comparison = []

        for model in outputs.keys():
            comparison.append({
                "model": model,
                "output": outputs[model],
                "score": scores[model],
                "word_count": len(outputs[model].split())
            })

        # Sort by score descending
        comparison.sort(key=lambda x: x["score"], reverse=True)

        return comparison

    async def _recommend_winner(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend the best model."""
        comparison = context["compare_results"]

        winner = comparison[0]

        recommendation = {
            "winner": winner["model"],
            "score": winner["score"],
            "reasoning": f"{winner['model']} achieved the highest voice consistency score of {winner['score']:.1f}",
            "top_3": [
                {"model": c["model"], "score": c["score"]}
                for c in comparison[:3]
            ]
        }

        logger.info(f"Winner: {recommendation['winner']} ({recommendation['score']})")
        return recommendation

    async def execute_workflow(self) -> WorkflowResult:
        """Execute the workflow."""
        started_at = datetime.now()

        try:
            for step in self.steps:
                logger.info(f"Executing step: {step.name}")
                result = await step.execute(self.context)
                self.context[step.name] = result

            comparison = self.context.get("compare_results", [])
            recommendation = self.context.get("recommend_winner", {})

            return WorkflowResult(
                workflow_id=self.workflow_id,
                status=WorkflowStatus.COMPLETED,
                started_at=started_at,
                completed_at=datetime.now(),
                steps_completed=len(self.steps),
                steps_total=len(self.steps),
                outputs={
                    "comparison": comparison,
                    "recommendation": recommendation
                },
                metadata={
                    "models_tested": len(self.context.get("models", [])),
                    "character": self.context.get("character")
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
