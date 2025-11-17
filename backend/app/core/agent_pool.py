"""Agent pool manager for multi-model orchestration.

This module provides a centralized pool for managing multiple LLM agents:
- Dynamic registration and discovery
- Enable/disable agents per session
- Load balancing across agents
- Cost tracking and analytics
- Parallel execution support
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Response from an agent generation."""

    agent_name: str
    output: str
    tokens_input: int
    tokens_output: int
    cost: float
    response_time_ms: int
    model_version: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if generation was successful."""
        return self.error is None

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.tokens_input + self.tokens_output


@dataclass
class ParallelResult:
    """Result from parallel agent execution."""

    session_id: str
    prompt: str
    responses: List[AgentResponse]
    started_at: datetime
    completed_at: datetime
    total_cost: float
    total_tokens: int

    @property
    def duration_ms(self) -> int:
        """Total duration in milliseconds."""
        return int((self.completed_at - self.started_at).total_seconds() * 1000)

    @property
    def successful_responses(self) -> List[AgentResponse]:
        """Get only successful responses."""
        return [r for r in self.responses if r.success]

    @property
    def failed_responses(self) -> List[AgentResponse]:
        """Get only failed responses."""
        return [r for r in self.responses if not r.success]


class AgentPool:
    """Manage a pool of LLM agents for multi-model generation.

    Features:
    - Dynamic agent registration
    - Enable/disable per session
    - Parallel execution
    - Cost tracking
    - Load balancing
    """

    def __init__(self):
        """Initialize agent pool."""
        self._agents: Dict[str, Any] = {}  # name -> agent instance
        self._enabled: Set[str] = set()
        self._stats: Dict[str, Dict[str, Any]] = {}  # agent -> stats
        self._lock = asyncio.Lock()

    def register_agent(self, name: str, agent: Any, enabled: bool = True) -> None:
        """Register an agent with the pool.

        Args:
            name: Unique agent identifier
            agent: Agent instance (must have generate() method)
            enabled: Whether agent is enabled by default
        """
        if not hasattr(agent, "generate"):
            raise ValueError(f"Agent '{name}' must have a generate() method")

        self._agents[name] = agent
        if enabled:
            self._enabled.add(name)

        # Initialize stats
        self._stats[name] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "total_response_time_ms": 0,
        }

        logger.info(f"Registered agent '{name}' (enabled={enabled})")

    def unregister_agent(self, name: str) -> None:
        """Remove an agent from the pool.

        Args:
            name: Agent identifier
        """
        if name in self._agents:
            del self._agents[name]
            self._enabled.discard(name)
            logger.info(f"Unregistered agent '{name}'")

    def get_agent(self, name: str) -> Optional[Any]:
        """Get an agent by name.

        Args:
            name: Agent identifier

        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(name)

    def list_agents(self, enabled_only: bool = False) -> List[str]:
        """List all registered agents.

        Args:
            enabled_only: If True, only return enabled agents

        Returns:
            List of agent names
        """
        if enabled_only:
            return sorted(list(self._enabled))
        return sorted(list(self._agents.keys()))

    def is_enabled(self, name: str) -> bool:
        """Check if an agent is enabled.

        Args:
            name: Agent identifier

        Returns:
            True if agent is enabled
        """
        return name in self._enabled

    def enable_agent(self, name: str) -> None:
        """Enable an agent.

        Args:
            name: Agent identifier
        """
        if name not in self._agents:
            raise ValueError(f"Unknown agent '{name}'")
        self._enabled.add(name)
        logger.info(f"Enabled agent '{name}'")

    def disable_agent(self, name: str) -> None:
        """Disable an agent.

        Args:
            name: Agent identifier
        """
        self._enabled.discard(name)
        logger.info(f"Disabled agent '{name}'")

    def get_enabled_agents(self) -> List[str]:
        """Get list of enabled agent names.

        Returns:
            Sorted list of enabled agent names
        """
        return sorted(list(self._enabled))

    async def execute_single(
        self,
        agent_name: str,
        prompt: str,
        **kwargs
    ) -> AgentResponse:
        """Execute generation with a single agent.

        Args:
            agent_name: Name of agent to use
            prompt: Generation prompt
            **kwargs: Additional parameters for agent

        Returns:
            AgentResponse with generation result

        Raises:
            ValueError: If agent not found or not enabled
        """
        if agent_name not in self._agents:
            raise ValueError(f"Unknown agent '{agent_name}'")

        if agent_name not in self._enabled:
            raise ValueError(f"Agent '{agent_name}' is not enabled")

        agent = self._agents[agent_name]
        start_time = datetime.now()

        try:
            # Execute generation
            result = await agent.generate(prompt, **kwargs)

            # Calculate response time
            response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Create response
            response = AgentResponse(
                agent_name=agent_name,
                output=result.get("output", ""),
                tokens_input=result.get("tokens_input", 0),
                tokens_output=result.get("tokens_output", 0),
                cost=result.get("cost", 0.0),
                response_time_ms=response_time_ms,
                model_version=result.get("model_version", "unknown"),
                metadata=result.get("metadata", {}),
            )

            # Update stats
            await self._update_stats(agent_name, response)

            return response

        except Exception as e:
            logger.error(f"Agent '{agent_name}' failed: {e}")

            # Calculate response time
            response_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Create error response
            response = AgentResponse(
                agent_name=agent_name,
                output="",
                tokens_input=0,
                tokens_output=0,
                cost=0.0,
                response_time_ms=response_time_ms,
                model_version="unknown",
                error=str(e),
            )

            # Update stats
            await self._update_stats(agent_name, response)

            return response

    async def execute_parallel(
        self,
        prompt: str,
        agents: Optional[List[str]] = None,
        **kwargs
    ) -> ParallelResult:
        """Execute generation across multiple agents in parallel.

        Args:
            prompt: Generation prompt
            agents: List of agent names (None = all enabled agents)
            **kwargs: Additional parameters for agents

        Returns:
            ParallelResult with all agent responses
        """
        session_id = str(uuid4())
        started_at = datetime.now()

        # Determine which agents to use
        if agents is None:
            agent_names = self.get_enabled_agents()
        else:
            agent_names = [a for a in agents if a in self._enabled]

        if not agent_names:
            raise ValueError("No enabled agents available")

        logger.info(f"Starting parallel execution with {len(agent_names)} agents")

        # Execute all agents concurrently
        tasks = [
            self.execute_single(agent_name, prompt, **kwargs)
            for agent_name in agent_names
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=False)

        completed_at = datetime.now()

        # Calculate totals
        total_cost = sum(r.cost for r in responses if r.success)
        total_tokens = sum(r.total_tokens for r in responses if r.success)

        result = ParallelResult(
            session_id=session_id,
            prompt=prompt,
            responses=responses,
            started_at=started_at,
            completed_at=completed_at,
            total_cost=total_cost,
            total_tokens=total_tokens,
        )

        logger.info(
            f"Parallel execution complete: {len(result.successful_responses)}/{len(responses)} "
            f"successful, ${total_cost:.4f} cost, {result.duration_ms}ms"
        )

        return result

    async def _update_stats(self, agent_name: str, response: AgentResponse) -> None:
        """Update agent statistics.

        Args:
            agent_name: Agent identifier
            response: Response to record
        """
        async with self._lock:
            stats = self._stats[agent_name]
            stats["total_requests"] += 1

            if response.success:
                stats["successful_requests"] += 1
                stats["total_tokens"] += response.total_tokens
                stats["total_cost"] += response.cost
                stats["total_response_time_ms"] += response.response_time_ms
            else:
                stats["failed_requests"] += 1

    def get_stats(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get agent statistics.

        Args:
            agent_name: Specific agent name, or None for all agents

        Returns:
            Dictionary of statistics
        """
        if agent_name:
            if agent_name not in self._stats:
                raise ValueError(f"Unknown agent '{agent_name}'")
            return self._stats[agent_name].copy()

        return {name: stats.copy() for name, stats in self._stats.items()}

    def reset_stats(self, agent_name: Optional[str] = None) -> None:
        """Reset agent statistics.

        Args:
            agent_name: Specific agent name, or None for all agents
        """
        if agent_name:
            if agent_name not in self._stats:
                raise ValueError(f"Unknown agent '{agent_name}'")
            self._stats[agent_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "total_response_time_ms": 0,
            }
            logger.info(f"Reset stats for agent '{agent_name}'")
        else:
            for name in self._stats:
                self.reset_stats(name)
            logger.info("Reset stats for all agents")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics across all agents.

        Returns:
            Dictionary with aggregate statistics
        """
        total_requests = sum(s["total_requests"] for s in self._stats.values())
        successful_requests = sum(s["successful_requests"] for s in self._stats.values())
        failed_requests = sum(s["failed_requests"] for s in self._stats.values())
        total_tokens = sum(s["total_tokens"] for s in self._stats.values())
        total_cost = sum(s["total_cost"] for s in self._stats.values())
        total_response_time = sum(s["total_response_time_ms"] for s in self._stats.values())

        return {
            "total_agents": len(self._agents),
            "enabled_agents": len(self._enabled),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_response_time_ms": (
                total_response_time / successful_requests if successful_requests > 0 else 0
            ),
        }
