"""
Claude Agent Implementation

Anthropic Claude API integration for creative writing tasks.
"""

from typing import Dict, List, Optional
from datetime import datetime
import anthropic

from .base_agent import BaseAgent, AgentResponse


class ClaudeAgent(BaseAgent):
    """Agent for Anthropic's Claude models."""

    # Pricing per million tokens (as of 2025)
    PRICING = {
        'claude-sonnet-4-5-20250929': {'input': 3.00, 'output': 15.00},
        'claude-3-5-sonnet-20241022': {'input': 3.00, 'output': 15.00},
        'claude-3-opus-20240229': {'input': 15.00, 'output': 75.00},
        'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25}
    }

    def __init__(self, agent_name: str = "Claude",
                 api_key: Optional[str] = None,
                 model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize Claude agent.

        Args:
            agent_name: Descriptive name for this agent
            api_key: Anthropic API key
            model: Model identifier
        """
        super().__init__(agent_name, "claude", api_key)
        self.model = model
        self.client = None

        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, context: Optional[str] = None,
                system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = 4000,
                temperature: float = 0.7) -> AgentResponse:
        """
        Generate content using Claude.

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
            self.client = anthropic.Anthropic(api_key=self.api_key)

        # Build full prompt with context
        full_prompt = self.build_full_prompt(prompt, context)

        # Prepare messages
        messages = [
            {"role": "user", "content": full_prompt}
        ]

        # Add conversation history if present
        if self.conversation_history:
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.conversation_history
            ] + messages

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "You are a creative writing assistant.",
                messages=messages
            )

            # Extract content
            content = response.content[0].text

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
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
            print(f"Error calling Claude API: {e}")
            raise

    def critique(self, content: str, criteria: List[str]) -> AgentResponse:
        """
        Critique content using Claude.

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

    def compare_variations(self, variations: List[Dict[str, str]],
                          criteria: List[str]) -> AgentResponse:
        """
        Compare multiple variations of the same scene.

        Args:
            variations: List of dicts with 'author' and 'content' keys
            criteria: Criteria for comparison

        Returns:
            AgentResponse with comparison analysis
        """
        variations_text = "\n\n".join([
            f"=== VARIATION {i+1} (by {v['author']}) ===\n{v['content']}"
            for i, v in enumerate(variations)
        ])

        criteria_text = "\n".join([f"- {c}" for c in criteria])

        compare_prompt = f"""Compare these variations of the same scene based on the following criteria:

{criteria_text}

VARIATIONS:
{variations_text}

For each variation:
1. Rate it on each criterion (1-10)
2. Identify unique strengths
3. Note what it does better than others

Then provide an overall recommendation on which elements from each variation should be combined for the strongest final version."""

        return self.generate(
            prompt=compare_prompt,
            system_prompt="You are an expert at analyzing and comparing creative writing."
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
            return 0.0

        pricing = self.PRICING[self.model]
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']

        return input_cost + output_cost

    def estimate_cost(self, tokens_used: int) -> float:
        """
        Estimate cost for total tokens (rough estimate).

        Args:
            tokens_used: Total tokens

        Returns:
            Estimated cost in USD
        """
        # Assume 1:3 ratio of input:output
        input_tokens = tokens_used // 4
        output_tokens = tokens_used - input_tokens

        return self.estimate_cost_detailed(input_tokens, output_tokens)


def create_claude_agent(config, model: str = "claude-sonnet-4-5-20250929") -> ClaudeAgent:
    """
    Factory function to create Claude agent from config.

    Args:
        config: GoogleStoreConfig instance
        model: Claude model to use

    Returns:
        Configured ClaudeAgent
    """
    api_key = config.get_ai_api_key('claude')
    if not api_key:
        api_key = config.get_ai_api_key('anthropic')  # Try alternate name

    if not api_key:
        raise ValueError("No API key found for Claude/Anthropic in configuration")

    return ClaudeAgent(api_key=api_key, model=model)
