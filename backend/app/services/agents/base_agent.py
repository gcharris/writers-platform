"""Base agent class for all LLM integrations.

This module provides an abstract base class that all LLM agents must implement.
It standardizes the interface for generation, cost tracking, and token counting.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an agent."""

    name: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    context_window: int = 4096
    max_output: int = 2048
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    timeout: int = 120
    retry_attempts: int = 3
    retry_delay: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Result from an agent generation."""

    output: str
    tokens_input: int
    tokens_output: int
    cost: float
    model_version: str
    response_time_ms: int
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Total tokens used in generation."""
        return self.tokens_input + self.tokens_output


class BaseAgent(ABC):
    """Abstract base class for all LLM agents.

    All agent implementations must inherit from this class and implement
    the generate() method. The base class provides common functionality
    for cost tracking, token counting, and error handling.
    """

    def __init__(self, config: AgentConfig):
        """Initialize agent with configuration.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.name = config.name
        self.model = config.model
        self._request_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0

        logger.info(f"Initialized agent '{self.name}' with model '{self.model}'")

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text from a prompt.

        This method must be implemented by all subclasses. It should:
        1. Call the LLM API with the given prompt and parameters
        2. Parse the response
        3. Count tokens
        4. Calculate cost
        5. Return a dictionary with the result

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (None = use config default)
            **kwargs: Additional model-specific parameters

        Returns:
            Dictionary with keys:
                - output: Generated text
                - tokens_input: Input tokens used
                - tokens_output: Output tokens generated
                - cost: Cost in USD
                - model_version: Actual model version used
                - metadata: Additional metadata

        Raises:
            Exception: If generation fails
        """
        pass

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text.

        This is a simple estimation. Subclasses should override this
        with provider-specific tokenization if available.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1000) * self.config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * self.config.cost_per_1k_output
        return input_cost + output_cost

    def update_stats(self, tokens_input: int, tokens_output: int, cost: float) -> None:
        """Update agent statistics.

        Args:
            tokens_input: Input tokens used
            tokens_output: Output tokens generated
            cost: Cost incurred
        """
        self._request_count += 1
        self._total_tokens += tokens_input + tokens_output
        self._total_cost += cost

        logger.debug(
            f"Agent '{self.name}' - Request #{self._request_count}: "
            f"{tokens_input} + {tokens_output} tokens, ${cost:.4f}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "name": self.name,
            "model": self.model,
            "request_count": self._request_count,
            "total_tokens": self._total_tokens,
            "total_cost": self._total_cost,
            "avg_tokens_per_request": (
                self._total_tokens / self._request_count if self._request_count > 0 else 0
            ),
            "avg_cost_per_request": (
                self._total_cost / self._request_count if self._request_count > 0 else 0
            ),
        }

    def reset_stats(self) -> None:
        """Reset agent statistics."""
        self._request_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        logger.info(f"Reset statistics for agent '{self.name}'")

    async def generate_with_retry(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with automatic retry on failure.

        Args:
            prompt: The input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generation result dictionary

        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None

        for attempt in range(self.config.retry_attempts):
            try:
                start_time = time.time()

                result = await self.generate(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

                # Add response time
                response_time_ms = int((time.time() - start_time) * 1000)
                result["response_time_ms"] = response_time_ms

                # Update stats
                self.update_stats(
                    result["tokens_input"],
                    result["tokens_output"],
                    result["cost"]
                )

                return result

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Agent '{self.name}' generation failed (attempt {attempt + 1}): {e}"
                )

                if attempt < self.config.retry_attempts - 1:
                    # Wait before retry (exponential backoff)
                    import asyncio
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))

        # All retries failed
        raise Exception(
            f"Agent '{self.name}' failed after {self.config.retry_attempts} attempts: {last_error}"
        )

    def validate_config(self) -> None:
        """Validate agent configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config.name:
            raise ValueError("Agent name is required")

        if not self.config.model:
            raise ValueError("Model name is required")

        if self.config.context_window <= 0:
            raise ValueError("Context window must be positive")

        if self.config.max_output <= 0:
            raise ValueError("Max output must be positive")

        if self.config.max_output > self.config.context_window:
            raise ValueError("Max output cannot exceed context window")

    def __str__(self) -> str:
        """String representation of agent."""
        return f"{self.name} ({self.model})"

    def __repr__(self) -> str:
        """Detailed representation of agent."""
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.name}' "
            f"model='{self.model}' "
            f"requests={self._request_count} "
            f"tokens={self._total_tokens} "
            f"cost=${self._total_cost:.4f}>"
        )
