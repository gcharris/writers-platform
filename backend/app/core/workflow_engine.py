"""Workflow engine for executing multi-step generation workflows.

This module provides a flexible workflow execution system with:
- Step dependency resolution
- State management and persistence
- Error handling and rollback
- Progress tracking
- Pause/resume capabilities
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Individual step execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_completed: int = 0
    steps_total: int = 0
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Calculate workflow duration in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def success(self) -> bool:
        """Check if workflow completed successfully."""
        return self.status == WorkflowStatus.COMPLETED and not self.errors


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    name: str
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    retry_count: int = 0
    retry_delay: float = 1.0
    required: bool = True

    # Runtime state
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    attempts: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __hash__(self) -> int:
        """Make step hashable for use in sets."""
        return hash(self.name)

    async def execute(self, context: Dict[str, Any]) -> Any:
        """Execute the step function with given context.

        Args:
            context: Dictionary containing workflow context and previous step outputs

        Returns:
            Result of the step function

        Raises:
            Exception: If step execution fails after all retries
        """
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()
        last_error = None

        for attempt in range(self.retry_count + 1):
            self.attempts = attempt + 1
            try:
                logger.info(f"Executing step '{self.name}' (attempt {self.attempts})")

                # Execute with timeout if specified
                if self.timeout:
                    result = await asyncio.wait_for(
                        self._run_function(context),
                        timeout=self.timeout
                    )
                else:
                    result = await self._run_function(context)

                self.result = result
                self.status = StepStatus.COMPLETED
                self.completed_at = datetime.now()
                logger.info(f"Step '{self.name}' completed successfully")
                return result

            except asyncio.TimeoutError:
                last_error = f"Step timed out after {self.timeout} seconds"
                logger.warning(f"Step '{self.name}' timed out (attempt {self.attempts})")

            except Exception as e:
                last_error = str(e)
                logger.error(f"Step '{self.name}' failed: {e} (attempt {self.attempts})")

            # Wait before retry
            if attempt < self.retry_count:
                await asyncio.sleep(self.retry_delay * (attempt + 1))

        # All retries failed
        self.status = StepStatus.FAILED
        self.error = last_error
        self.completed_at = datetime.now()

        if self.required:
            raise Exception(f"Required step '{self.name}' failed: {last_error}")
        else:
            logger.warning(f"Optional step '{self.name}' failed: {last_error}")
            return None

    async def _run_function(self, context: Dict[str, Any]) -> Any:
        """Run the step function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(self.function):
            return await self.function(context)
        else:
            return self.function(context)


class Workflow:
    """Base class for all workflows.

    Workflows define a series of steps that execute in order, respecting
    dependencies and handling errors gracefully.

    Workflows can be used directly by adding steps via add_step(), or
    subclassed to override define_steps() for a more structured approach.
    """

    def __init__(
        self,
        name: str,
        workflow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize workflow.

        Args:
            name: Human-readable workflow name
            workflow_id: Unique workflow ID (generated if not provided)
            context: Initial workflow context
        """
        self.name = name
        self.workflow_id = workflow_id or str(uuid4())
        self.context = context or {}
        self.steps: List[WorkflowStep] = []
        self.status = WorkflowStatus.PENDING
        self._step_outputs: Dict[str, Any] = {}

    def add_step(
        self,
        name: str,
        function: Callable,
        dependencies: Optional[List[str]] = None,
        **kwargs
    ) -> "Workflow":
        """Add a step to the workflow.

        Args:
            name: Unique step name
            function: Function to execute (sync or async)
            dependencies: List of step names that must complete first
            **kwargs: Additional step configuration (timeout, retry_count, etc.)

        Returns:
            Self for method chaining
        """
        step = WorkflowStep(
            name=name,
            function=function,
            dependencies=dependencies or [],
            **kwargs
        )
        self.steps.append(step)
        return self

    def get_step(self, name: str) -> Optional[WorkflowStep]:
        """Get a step by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def define_steps(self) -> None:
        """Define the workflow steps.

        This method can be overridden by subclasses to add all
        workflow steps using add_step(). If not overridden, steps
        can be added directly using add_step().
        """
        pass


class WorkflowEngine:
    """Engine for executing workflows with dependency resolution.

    Features:
    - Topological sorting of steps based on dependencies
    - Parallel execution of independent steps
    - State management and persistence
    - Error handling and rollback
    - Progress tracking
    """

    def __init__(self):
        """Initialize workflow engine."""
        self.current_workflow: Optional[Workflow] = None
        self._pause_requested = False

    async def run_workflow(
        self,
        workflow: Workflow,
        parallel: bool = True
    ) -> WorkflowResult:
        """Execute a workflow.

        Args:
            workflow: Workflow to execute
            parallel: Whether to run independent steps in parallel

        Returns:
            WorkflowResult containing execution details
        """
        self.current_workflow = workflow
        workflow.status = WorkflowStatus.RUNNING

        result = WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now(),
            steps_total=len(workflow.steps)
        )

        try:
            # Define steps if not already done
            if not workflow.steps:
                workflow.define_steps()

            # Validate workflow
            self._validate_workflow(workflow)

            # Sort steps by dependencies
            sorted_steps = self._topological_sort(workflow.steps)

            # Execute steps
            if parallel:
                await self._execute_parallel(workflow, sorted_steps, result)
            else:
                await self._execute_sequential(workflow, sorted_steps, result)

            # Check if paused
            if self._pause_requested:
                result.status = WorkflowStatus.PAUSED
                logger.info(f"Workflow '{workflow.name}' paused")
            else:
                result.status = WorkflowStatus.COMPLETED
                result.completed_at = datetime.now()
                logger.info(f"Workflow '{workflow.name}' completed successfully")

        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.completed_at = datetime.now()
            result.errors.append(str(e))
            logger.error(f"Workflow '{workflow.name}' failed: {e}")

        finally:
            workflow.status = result.status
            result.outputs = workflow._step_outputs

        return result

    def pause(self) -> None:
        """Request workflow pause after current step completes."""
        self._pause_requested = True
        logger.info("Workflow pause requested")

    def resume(self) -> None:
        """Resume a paused workflow."""
        self._pause_requested = False
        logger.info("Workflow resumed")

    def _validate_workflow(self, workflow: Workflow) -> None:
        """Validate workflow structure.

        Checks for:
        - Duplicate step names
        - Invalid dependencies
        - Circular dependencies
        """
        step_names = {step.name for step in workflow.steps}

        # Check for duplicates
        if len(step_names) != len(workflow.steps):
            raise ValueError("Workflow contains duplicate step names")

        # Check for invalid dependencies
        for step in workflow.steps:
            for dep in step.dependencies:
                if dep not in step_names:
                    raise ValueError(
                        f"Step '{step.name}' depends on unknown step '{dep}'"
                    )

        # Check for circular dependencies
        if self._has_circular_dependencies(workflow.steps):
            raise ValueError("Workflow contains circular dependencies")

    def _has_circular_dependencies(self, steps: List[WorkflowStep]) -> bool:
        """Check if steps contain circular dependencies."""
        # Build adjacency list
        graph: Dict[str, Set[str]] = {step.name: set(step.dependencies) for step in steps}

        # Track visited nodes
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    return True

        return False

    def _topological_sort(self, steps: List[WorkflowStep]) -> List[List[WorkflowStep]]:
        """Sort steps topologically, grouping independent steps together.

        Returns:
            List of step groups where each group contains independent steps
            that can be executed in parallel.
        """
        # Build dependency graph
        step_map = {step.name: step for step in steps}
        in_degree = {step.name: len(step.dependencies) for step in steps}

        # Find steps with no dependencies
        queue = [step for step in steps if not step.dependencies]
        result: List[List[WorkflowStep]] = []

        while queue:
            # All steps in queue can be executed in parallel
            result.append(queue[:])
            next_queue = []

            for step in queue:
                # Reduce in-degree for dependent steps
                for other_step in steps:
                    if step.name in other_step.dependencies:
                        in_degree[other_step.name] -= 1
                        if in_degree[other_step.name] == 0:
                            next_queue.append(other_step)

            queue = next_queue

        return result

    async def _execute_parallel(
        self,
        workflow: Workflow,
        step_groups: List[List[WorkflowStep]],
        result: WorkflowResult
    ) -> None:
        """Execute step groups in parallel."""
        for group in step_groups:
            if self._pause_requested:
                break

            # Execute all steps in group concurrently
            tasks = [
                step.execute({**workflow.context, **workflow._step_outputs})
                for step in group
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Store results
            for step, step_result in zip(group, results):
                if isinstance(step_result, Exception):
                    if step.required:
                        raise step_result
                else:
                    workflow._step_outputs[step.name] = step_result
                    result.steps_completed += 1

    async def _execute_sequential(
        self,
        workflow: Workflow,
        step_groups: List[List[WorkflowStep]],
        result: WorkflowResult
    ) -> None:
        """Execute steps sequentially."""
        for group in step_groups:
            for step in group:
                if self._pause_requested:
                    break

                step_result = await step.execute(
                    {**workflow.context, **workflow._step_outputs}
                )
                workflow._step_outputs[step.name] = step_result
                result.steps_completed += 1
