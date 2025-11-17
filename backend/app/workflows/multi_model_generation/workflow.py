"""Multi-model generation workflow.

Generates content with multiple models in parallel and compares results.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from factory.core.agent_pool import AgentPool, ParallelResult
from factory.core.workflow_engine import WorkflowResult, WorkflowStatus
from factory.workflows.base_workflow import BaseWorkflow

logger = logging.getLogger(__name__)


class MultiModelGenerationWorkflow(BaseWorkflow):
    """Generate content with multiple models for comparison.

    This workflow:
    1. Accepts a prompt and list of agents
    2. Executes generation in parallel
    3. Collects and ranks results
    4. Returns comparison data
    """

    def __init__(
        self,
        agent_pool: AgentPool,
        prompt: str,
        agents: List[str],
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize multi-model generation workflow.

        Args:
            agent_pool: Pool of available agents
            prompt: Generation prompt
            agents: List of agent names to use
            context: Additional context for generation
            **kwargs: Additional generation parameters
        """
        super().__init__(
            name="multi-model-generation",
            context=context or {}
        )

        self.agent_pool = agent_pool
        self.prompt = prompt
        self.agents = agents
        self.generation_params = kwargs
        self._result: Optional[ParallelResult] = None

    async def setup(self) -> None:
        """Setup workflow."""
        # Validate agents exist and are enabled
        enabled_agents = self.agent_pool.get_enabled_agents()

        invalid_agents = [a for a in self.agents if a not in enabled_agents]
        if invalid_agents:
            raise ValueError(f"Invalid or disabled agents: {invalid_agents}")

        logger.info(
            f"Setup complete: {len(self.agents)} agents ready for generation"
        )

    async def execute(self) -> WorkflowResult:
        """Execute parallel generation.

        Returns:
            WorkflowResult with all agent outputs
        """
        result = WorkflowResult(
            workflow_id=self.workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now(),
            steps_total=1
        )

        try:
            # Execute parallel generation
            self._result = await self.agent_pool.execute_parallel(
                prompt=self.prompt,
                agents=self.agents,
                **self.generation_params
            )

            # Store results
            result.outputs = {
                "session_id": self._result.session_id,
                "prompt": self._result.prompt,
                "responses": [
                    {
                        "agent": r.agent_name,
                        "output": r.output,
                        "tokens": r.total_tokens,
                        "cost": r.cost,
                        "response_time_ms": r.response_time_ms,
                        "success": r.success,
                        "error": r.error,
                    }
                    for r in self._result.responses
                ],
                "total_cost": self._result.total_cost,
                "total_tokens": self._result.total_tokens,
                "duration_ms": self._result.duration_ms,
            }

            result.status = WorkflowStatus.COMPLETED
            result.completed_at = datetime.now()
            result.steps_completed = 1

            logger.info(
                f"Generation complete: {len(self._result.successful_responses)}/{len(self.agents)} successful"
            )

        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.now()
            logger.error(f"Generation failed: {e}")

        return result

    async def cleanup(self) -> None:
        """Cleanup workflow resources."""
        # No cleanup needed for this workflow
        pass

    def get_ranked_results(
        self,
        scoring_function: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """Get results ranked by score.

        Args:
            scoring_function: Optional function to score outputs
                             Signature: (output: str) -> float

        Returns:
            List of results sorted by score (highest first)
        """
        if not self._result:
            return []

        results = []
        for response in self._result.successful_responses:
            score = 0.0
            if scoring_function:
                score = scoring_function(response.output)

            results.append({
                "agent": response.agent_name,
                "output": response.output,
                "score": score,
                "cost": response.cost,
                "tokens": response.total_tokens,
                "response_time_ms": response.response_time_ms,
            })

        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)

        return results
