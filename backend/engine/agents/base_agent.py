"""
Base Agent Class

Abstract base class for all AI platform agents.
Defines the common interface for scene generation, critique, and context handling.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentResponse:
    """Standardized response from an agent."""
    agent_name: str
    platform: str
    content: str
    metadata: Dict[str, Any]
    timestamp: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'agent_name': self.agent_name,
            'platform': self.platform,
            'content': self.content,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'tokens_used': self.tokens_used,
            'cost': self.cost
        }


class BaseAgent(ABC):
    """Abstract base class for AI agents."""

    def __init__(self, agent_name: str, platform: str, api_key: Optional[str] = None):
        """
        Initialize agent.

        Args:
            agent_name: Descriptive name for this agent instance
            platform: Platform identifier (claude, openai, google, xai)
            api_key: API key for the platform
        """
        self.agent_name = agent_name
        self.platform = platform
        self.api_key = api_key
        self.conversation_history = []

    @abstractmethod
    def generate(self, prompt: str, context: Optional[str] = None,
                system_prompt: Optional[str] = None,
                max_tokens: Optional[int] = None,
                temperature: float = 0.7) -> AgentResponse:
        """
        Generate content based on prompt and context.

        Args:
            prompt: The main prompt/instruction
            context: Optional context from Google File Store
            system_prompt: Optional system-level instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            AgentResponse object
        """
        pass

    @abstractmethod
    def critique(self, content: str, criteria: List[str]) -> AgentResponse:
        """
        Critique existing content based on criteria.

        Args:
            content: Content to critique
            criteria: List of criteria to evaluate (voice, pacing, etc.)

        Returns:
            AgentResponse with critique
        """
        pass

    def build_full_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Build a complete prompt with context.

        Args:
            prompt: Main prompt
            context: Optional context from Google File Store

        Returns:
            Complete prompt string
        """
        if context:
            return f"{context}\n\n---\n\n{prompt}"
        return prompt

    def add_to_history(self, role: str, content: str):
        """
        Add message to conversation history.

        Args:
            role: Role of the speaker (user, assistant, system)
            content: Message content
        """
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history

    def estimate_cost(self, tokens_used: int) -> float:
        """
        Estimate cost for API usage.

        Args:
            tokens_used: Number of tokens used

        Returns:
            Estimated cost in USD
        """
        # Override in platform-specific implementations
        return 0.0

    def validate_api_key(self) -> bool:
        """
        Validate that API key is configured.

        Returns:
            True if API key is valid, False otherwise
        """
        if not self.api_key:
            print(f"Error: No API key configured for {self.platform}")
            return False
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.agent_name}', platform='{self.platform}')"
