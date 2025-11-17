"""
Grok Agent Implementation

xAI Grok API integration for creative writing tasks.
Note: As of 2025, Grok API may use OpenAI-compatible endpoints.
"""

from typing import Dict, List, Optional
from datetime import datetime
import openai

from .base_agent import BaseAgent, AgentResponse


class GrokAgent(BaseAgent):
    """Agent for xAI's Grok models."""

    # Estimated pricing (update when official pricing available)
    PRICING = {
        'grok-2': {'input': 5.00, 'output': 15.00},
        'grok-1': {'input': 3.00, 'output': 9.00}
    }

    def __init__(self, agent_name: str = "Grok",
                 api_key: Optional[str] = None,
                 model: str = "grok-2",
                 base_url: str = "https://api.x.ai/v1"):
        """
        Initialize Grok agent.

        Args:
            agent_name: Descriptive name for this agent
            api_key: xAI API key
            model: Model identifier
            base_url: API base URL
        """
        super().__init__(agent_name, "xai", api_key)
        self.model = model
        self.base_url = base_url
        self.client = None

        if api_key:
            # Grok uses OpenAI-compatible API
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )

    def generate(self, prompt: str, context: Optional[str] = None,
                system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = 4000,
                temperature: float = 0.7) -> AgentResponse:
        """
        Generate content using Grok.

        Args:
            prompt: The main prompt/instruction
            context: Optional context from Google File Store
            system_prompt: Optional system-level instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            AgentResponse object
        """
        if not self.validate_api_key():
            raise ValueError("API key not configured")

        if not self.client:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

        # Build full prompt with context
        full_prompt = self.build_full_prompt(prompt, context)

        # Prepare messages
        messages = []

        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a creative writing assistant."})

        # Add conversation history
        if self.conversation_history:
            for msg in self.conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current prompt
        messages.append({"role": "user", "content": full_prompt})

        try:
            # Call Grok API (OpenAI-compatible)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Extract content
            content = response.choices[0].message.content

            # Get token usage
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = response.usage.total_tokens if response.usage else 0

            # Estimate tokens if not provided
            if total_tokens == 0:
                input_tokens = len(full_prompt) // 4
                output_tokens = len(content) // 4
                total_tokens = input_tokens + output_tokens

            cost = self.estimate_cost_detailed(input_tokens, output_tokens)

            # Add to history
            self.add_to_history("user", full_prompt)
            self.add_to_history("assistant", content)

            # Create response
            return AgentResponse(
                agent_name=self.agent_name,
                platform=self.platform,
                content=content,
                metadata={
                    'model': self.model,
                    'prompt': prompt,
                    'has_context': context is not None,
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens
                },
                timestamp=datetime.now().isoformat(),
                tokens_used=total_tokens,
                cost=cost
            )

        except Exception as e:
            print(f"Error calling Grok API: {e}")
            raise

    def critique(self, content: str, criteria: List[str]) -> AgentResponse:
        """
        Critique content using Grok.

        Args:
            content: Content to critique
            criteria: List of criteria to evaluate

        Returns:
            AgentResponse with critique
        """
        criteria_text = "\n".join([f"- {c}" for c in criteria])

        critique_prompt = f"""Please critique the following creative writing based on these criteria:

{criteria_text}

For each criterion, provide:
1. Score (1-10)
2. Specific observations
3. Actionable suggestions for improvement

CONTENT TO CRITIQUE:
---
{content}
---

Provide your critique in a structured format."""

        return self.generate(
            prompt=critique_prompt,
            system_prompt="You are an expert creative writing editor and critic."
        )

    def estimate_cost_detailed(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost based on input and output tokens.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        if self.model not in self.PRICING:
            pricing = self.PRICING['grok-2']
        else:
            pricing = self.PRICING[self.model]

        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost

    def estimate_cost(self, tokens_used: int) -> float:
        """
        Estimate cost for total tokens.

        Args:
            tokens_used: Total tokens

        Returns:
            Estimated cost in USD
        """
        input_tokens = tokens_used // 4
        output_tokens = tokens_used - input_tokens

        return self.estimate_cost_detailed(input_tokens, output_tokens)


def create_grok_agent(config, model: str = "grok-2") -> GrokAgent:
    """
    Factory function to create Grok agent from config.

    Args:
        config: GoogleStoreConfig instance
        model: Grok model to use

    Returns:
        Configured GrokAgent
    """
    api_key = config.get_ai_api_key('xai')

    if not api_key:
        raise ValueError("No API key found for xAI in configuration")

    return GrokAgent(api_key=api_key, model=model)
