"""
AI Agent Package

Provides integrations with multiple AI platforms for creative writing tasks.
"""

from .base_agent import BaseAgent, AgentResponse
from .claude_agent import ClaudeAgent, create_claude_agent
from .chatgpt_agent import ChatGPTAgent, create_chatgpt_agent
from .gemini_agent import GeminiAgent, create_gemini_agent
from .grok_agent import GrokAgent, create_grok_agent
from .deepseek_agent import DeepSeekAgent

__all__ = [
    'BaseAgent',
    'AgentResponse',
    'ClaudeAgent',
    'create_claude_agent',
    'ChatGPTAgent',
    'create_chatgpt_agent',
    'GeminiAgent',
    'create_gemini_agent',
    'GrokAgent',
    'create_grok_agent',
    'DeepSeekAgent'
]
