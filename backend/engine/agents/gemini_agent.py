"""
Gemini Agent Implementation

Google Gemini API integration for creative writing tasks.
"""

from typing import Dict, List, Optional
from datetime import datetime
import google.generativeai as genai

from .base_agent import BaseAgent, AgentResponse


class GeminiAgent(BaseAgent):
    """Agent for Google's Gemini models."""

    # Pricing per million tokens (as of 2025)
    PRICING = {
        'gemini-pro': {'input': 0.50, 'output': 1.50},
        'gemini-1.5-pro': {'input': 3.50, 'output': 10.50},
        'gemini-1.5-flash': {'input': 0.075, 'output': 0.30}
    }

    def __init__(self, agent_name: str = "Gemini",
                 api_key: Optional[str] = None,
                 model: str = "gemini-1.5-pro"):
        """
        Initialize Gemini agent.

        Args:
            agent_name: Descriptive name for this agent
            api_key: Google API key
            model: Model identifier
        """
        super().__init__(agent_name, "google", api_key)
        self.model_name = model
        self.model = None

        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)

    def generate(self, prompt: str, context: Optional[str] = None,
                system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = 4000,
                temperature: float = 0.7) -> AgentResponse:
        """
        Generate content using Gemini.

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

        if not self.model:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

        # Build full prompt with context
        full_prompt = self.build_full_prompt(prompt, context)

        # Add system prompt to beginning if provided
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{full_prompt}"

        try:
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )

            # Call Gemini API
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            # Extract content
            content = response.text

            # Estimate tokens (Gemini doesn't always provide token counts)
            # Rough estimate: ~4 characters per token
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
                    'model': self.model_name,
                    'prompt': prompt,
                    'has_context': context is not None,
                    'input_tokens_estimated': input_tokens,
                    'output_tokens_estimated': output_tokens
                },
                timestamp=datetime.now().isoformat(),
                tokens_used=total_tokens,
                cost=cost
            )

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise

    def critique(self, content: str, criteria: List[str]) -> AgentResponse:
        """
        Critique content using Gemini.

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
        if self.model_name not in self.PRICING:
            pricing = self.PRICING['gemini-1.5-pro']
        else:
            pricing = self.PRICING[self.model_name]

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


def create_gemini_agent(config, model: str = "gemini-1.5-pro") -> GeminiAgent:
    """
    Factory function to create Gemini agent from config.

    Args:
        config: GoogleStoreConfig instance
        model: Gemini model to use

    Returns:
        Configured GeminiAgent
    """
    api_key = config.get_ai_api_key('google')

    if not api_key:
        raise ValueError("No API key found for Google in configuration")

    return GeminiAgent(api_key=api_key, model=model)
