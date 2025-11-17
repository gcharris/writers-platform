"""Doubao (豆包) API integration by ByteDance.

Doubao is ByteDance's large language model with strong Chinese capabilities.
"""

import logging
from typing import Any, Dict, Optional

import httpx

from factory.agents.base_agent import BaseAgent, AgentConfig

logger = logging.getLogger(__name__)


class DoubaoAgent(BaseAgent):
    """Doubao (豆包) agent for text generation.

    ByteDance's LLM accessible via Volcengine API.
    """

    def __init__(self, config: AgentConfig):
        """Initialize Doubao agent.

        Args:
            config: Agent configuration including API key
        """
        super().__init__(config)

        if not config.api_key:
            raise ValueError("Doubao API key is required")

        self.api_key = config.api_key
        self.base_url = config.base_url or "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

        logger.info(f"Initialized Doubao agent with model '{self.model}'")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Doubao API.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Doubao parameters

        Returns:
            Dictionary containing generation result

        Raises:
            Exception: If API call fails
        """
        max_tokens = max_tokens or self.config.max_output

        # Prepare request payload (OpenAI-compatible format)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": kwargs.get("top_p", 0.9),
            "stream": False,
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
                    f"Doubao API error: {response.status_code} - {response.text}"
                )

            data = response.json()

            # Extract output
            choices = data.get("choices", [])
            if not choices:
                raise Exception("Doubao API returned no choices")

            output_text = choices[0].get("message", {}).get("content", "")

            # Extract usage info
            usage = data.get("usage", {})
            tokens_input = usage.get("prompt_tokens", self.count_tokens(prompt))
            tokens_output = usage.get("completion_tokens", self.count_tokens(output_text))

            # Calculate cost
            cost = self.calculate_cost(tokens_input, tokens_output)

            return {
                "output": output_text,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "cost": cost,
                "model_version": data.get("model", self.model),
                "metadata": {
                    "finish_reason": choices[0].get("finish_reason", ""),
                    "request_id": data.get("id", ""),
                }
            }
