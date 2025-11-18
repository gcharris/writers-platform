"""
Adapters to use existing engine agents with the factory-core agent pool.

This module wraps the engine agents (claude_agent.py, chatgpt_agent.py, etc.)
to work with the BaseAgent interface expected by AgentPool.
"""

import logging
from typing import Optional, Dict, Any

from app.services.agents.base_agent import BaseAgent, AgentConfig

# Import engine agents
from engine.agents.claude_agent import ClaudeAgent as EngineClaudeAgent
from engine.agents.chatgpt_agent import ChatGPTAgent as EngineChatGPTAgent
from engine.agents.gemini_agent import GeminiAgent as EngineGeminiAgent
from engine.agents.grok_agent import GrokAgent as EngineGrokAgent
from engine.agents.deepseek_agent import DeepSeekAgent as EngineDeepSeekAgent

logger = logging.getLogger(__name__)


class ClaudeAgentAdapter(BaseAgent):
    """Adapter for engine Claude agent."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.engine_agent = EngineClaudeAgent(
            agent_name=config.name,
            api_key=config.api_key,
            model=config.model
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> dict:
        """Generate using Claude API."""
        try:
            # Call engine agent (sync)
            response = self.engine_agent.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                **kwargs
            )

            # Adapt response format
            return {
                "output": response.content,
                "tokens_input": response.tokens_used.get('input', 0),
                "tokens_output": response.tokens_used.get('output', 0),
                "cost": response.cost,
                "model_version": self.model,
                "metadata": response.metadata or {}
            }

        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise


class GPTAgentAdapter(BaseAgent):
    """Adapter for engine ChatGPT agent."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.engine_agent = EngineChatGPTAgent(
            agent_name=config.name,
            api_key=config.api_key,
            model=config.model
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> dict:
        """Generate using GPT API."""
        try:
            response = self.engine_agent.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                **kwargs
            )

            return {
                "output": response.content,
                "tokens_input": response.tokens_used.get('input', 0),
                "tokens_output": response.tokens_used.get('output', 0),
                "cost": response.cost,
                "model_version": self.model,
                "metadata": response.metadata or {}
            }

        except Exception as e:
            logger.error(f"GPT generation failed: {e}")
            raise


class GeminiAgentAdapter(BaseAgent):
    """Adapter for engine Gemini agent."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.engine_agent = EngineGeminiAgent(
            agent_name=config.name,
            api_key=config.api_key,
            model=config.model
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> dict:
        """Generate using Gemini API."""
        try:
            response = self.engine_agent.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                **kwargs
            )

            return {
                "output": response.content,
                "tokens_input": response.tokens_used.get('input', 0),
                "tokens_output": response.tokens_used.get('output', 0),
                "cost": response.cost,
                "model_version": self.model,
                "metadata": response.metadata or {}
            }

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise


class GrokAgentAdapter(BaseAgent):
    """Adapter for engine Grok agent."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.engine_agent = EngineGrokAgent(
            agent_name=config.name,
            api_key=config.api_key,
            model=config.model
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> dict:
        """Generate using Grok API."""
        try:
            response = self.engine_agent.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                **kwargs
            )

            return {
                "output": response.content,
                "tokens_input": response.tokens_used.get('input', 0),
                "tokens_output": response.tokens_used.get('output', 0),
                "cost": response.cost,
                "model_version": self.model,
                "metadata": response.metadata or {}
            }

        except Exception as e:
            logger.error(f"Grok generation failed: {e}")
            raise


class DeepSeekAgentAdapter(BaseAgent):
    """Adapter for engine DeepSeek agent."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.engine_agent = EngineDeepSeekAgent(
            agent_name=config.name,
            api_key=config.api_key,
            model=config.model
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> dict:
        """Generate using DeepSeek API."""
        try:
            response = self.engine_agent.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens or 4000,
                **kwargs
            )

            return {
                "output": response.content,
                "tokens_input": response.tokens_used.get('input', 0),
                "tokens_output": response.tokens_used.get('output', 0),
                "cost": response.cost,
                "model_version": self.model,
                "metadata": response.metadata or {}
            }

        except Exception as e:
            logger.error(f"DeepSeek generation failed: {e}")
            raise
