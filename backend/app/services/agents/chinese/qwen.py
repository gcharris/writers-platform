"""Qwen (通义千问) API integration by Alibaba Cloud.

Qwen is Alibaba's large language model series with strong Chinese and English capabilities.
"""

import logging
from typing import Any, Dict, Optional

import httpx

from factory.agents.base_agent import BaseAgent, AgentConfig

logger = logging.getLogger(__name__)


class QwenAgent(BaseAgent):
    """Qwen (通义千问) agent for text generation.

    Supports Qwen-Max, Qwen-Plus, and Qwen-Turbo models via DashScope API.
    """

    def __init__(self, config: AgentConfig):
        """Initialize Qwen agent.

        Args:
            config: Agent configuration including API key
        """
        super().__init__(config)

        if not config.api_key:
            raise ValueError("Qwen API key is required")

        self.api_key = config.api_key
        self.base_url = config.base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

        logger.info(f"Initialized Qwen agent with model '{self.model}'")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Qwen API.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 2.0 for Qwen)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Qwen parameters (top_p, top_k, etc.)

        Returns:
            Dictionary containing generation result

        Raises:
            Exception: If API call fails
        """
        max_tokens = max_tokens or self.config.max_output

        # Prepare request payload
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": kwargs.get("top_p", 0.8),
                "enable_search": kwargs.get("enable_search", False),
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Make API call
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=headers
            )

            if response.status_code != 200:
                raise Exception(
                    f"Qwen API error: {response.status_code} - {response.text}"
                )

            data = response.json()

            # Check for API errors
            if "code" in data and data["code"] != "":
                raise Exception(f"Qwen API error: {data.get('message', 'Unknown error')}")

            # Extract output
            output_data = data.get("output", {})
            output_text = output_data.get("text", "")

            # Extract usage info
            usage = data.get("usage", {})
            tokens_input = usage.get("input_tokens", self.count_tokens(prompt))
            tokens_output = usage.get("output_tokens", self.count_tokens(output_text))

            # Calculate cost
            cost = self.calculate_cost(tokens_input, tokens_output)

            return {
                "output": output_text,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "cost": cost,
                "model_version": self.model,
                "metadata": {
                    "finish_reason": output_data.get("finish_reason", ""),
                    "request_id": data.get("request_id", ""),
                }
            }
