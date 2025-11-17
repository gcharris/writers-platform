"""
ChatGPT Agent Implementation

OpenAI GPT API integration for creative writing tasks.
"""

from typing import Dict, List, Optional
from datetime import datetime
import openai

from .base_agent import BaseAgent, AgentResponse


class ChatGPTAgent(BaseAgent):
    """Agent for OpenAI's GPT models."""

    # Pricing per million tokens (as of 2025)
    PRICING = {
        'gpt-4': {'input': 30.00, 'output': 60.00},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
        'gpt-4o': {'input': 5.00, 'output': 15.00},
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50}
    }

    def __init__(self, agent_name: str = "ChatGPT",
                 api_key: Optional[str] = None,
                 model: str = "gpt-4o"):
        """
        Initialize ChatGPT agent.

        Args:
            agent_name: Descriptive name for this agent
            api_key: OpenAI API key
            model: Model identifier
        """
        super().__init__(agent_name, "openai", api_key)
        self.model = model
        self.client = None

        if api_key:
            self.client = openai.OpenAI(api_key=api_key)

    def generate(self, prompt: str, context: Optional[str] = None,
                system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = 4000,
                temperature: float = 0.7) -> AgentResponse:
        """
        Generate content using ChatGPT.

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
            self.client = openai.OpenAI(api_key=self.api_key)

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
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            # Extract content
            content = response.choices[0].message.content

            # Calculate tokens and cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
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
                    'output_tokens': output_tokens,
                    'finish_reason': response.choices[0].finish_reason
                },
                timestamp=datetime.now().isoformat(),
                tokens_used=total_tokens,
                cost=cost
            )

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise

    def critique(self, content: str, criteria: List[str]) -> AgentResponse:
        """
        Critique content using ChatGPT.

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
            # Use gpt-4 pricing as default fallback
            pricing = self.PRICING['gpt-4']
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
        # Assume 1:3 ratio of input:output
        input_tokens = tokens_used // 4
        output_tokens = tokens_used - input_tokens

        return self.estimate_cost_detailed(input_tokens, output_tokens)


def create_chatgpt_agent(config, model: str = "gpt-4o") -> ChatGPTAgent:
    """
    Factory function to create ChatGPT agent from config.

    Args:
        config: GoogleStoreConfig instance
        model: GPT model to use

    Returns:
        Configured ChatGPTAgent
    """
    api_key = config.get_ai_api_key('openai')

    if not api_key:
        raise ValueError("No API key found for OpenAI in configuration")

    return ChatGPTAgent(api_key=api_key, model=model)
