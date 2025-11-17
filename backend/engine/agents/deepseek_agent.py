"""
DeepSeek Agent

OpenAI-compatible API interface for DeepSeek models.
"""

import requests
from typing import Optional
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentResponse


@dataclass
class DeepSeekAgent(BaseAgent):
    """Agent for DeepSeek models via OpenAI-compatible API."""

    # Pricing per million tokens (estimated - DeepSeek is very cheap)
    PRICING = {
        'deepseek-chat': {'input': 0.14, 'output': 0.28},
        'deepseek-coder': {'input': 0.14, 'output': 0.28}
    }

    def __init__(self, agent_name: str = "DeepSeek",
                 api_key: Optional[str] = None,
                 model: str = "deepseek-chat",
                 api_base: str = "https://api.deepseek.com"):
        """
        Initialize DeepSeek agent.

        Args:
            agent_name: Descriptive name for this agent
            api_key: DeepSeek API key
            model: Model identifier (deepseek-chat or deepseek-coder)
            api_base: API base URL
        """
        super().__init__(agent_name, "deepseek", api_key)
        self.model = model
        self.api_base = api_base

    def generate(self, prompt: str, context: Optional[str] = None,
                system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = 4000,
                temperature: float = 0.7) -> AgentResponse:
        """
        Generate content using DeepSeek.

        Args:
            prompt: The main prompt/instruction
            context: Optional context from knowledge base
            system_prompt: Optional system-level instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            AgentResponse with generated content
        """
        if not self.api_key:
            raise ValueError("DeepSeek API key not configured")

        # Build messages
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Combine context and prompt if both provided
        user_content = prompt
        if context:
            user_content = f"Context:\n{context}\n\n{prompt}"

        messages.append({"role": "user", "content": user_content})

        # Make API request
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()

            result = response.json()

            # Extract content
            content = result['choices'][0]['message']['content']

            # Extract token usage
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)

            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens)

            return AgentResponse(
                agent_name=self.agent_name,
                platform="deepseek",
                content=content,
                metadata={
                    "model": self.model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                },
                timestamp="",  # Will be set by dataclass
                tokens_used=input_tokens + output_tokens,
                cost=cost
            )

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"DeepSeek API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected DeepSeek API response format: {e}")

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage."""
        pricing = self.PRICING.get(self.model, self.PRICING['deepseek-chat'])

        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost

    def critique(self, content: str, criteria: Optional[str] = None) -> AgentResponse:
        """
        Critique content based on criteria.

        Args:
            content: Content to critique
            criteria: Optional specific criteria to focus on

        Returns:
            AgentResponse with critique
        """
        prompt = f"Critique the following content:\n\n{content}"
        if criteria:
            prompt += f"\n\nFocus on: {criteria}"

        return self.generate(
            prompt=prompt,
            system_prompt="You are a professional editor providing constructive feedback.",
            max_tokens=1000
        )
