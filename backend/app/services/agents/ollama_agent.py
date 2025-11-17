"""Ollama local model agent for Writers Factory.

Provides integration with locally-running Ollama models for cost-free
inference on creative writing tasks.
"""

import requests
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class OllamaAgent:
    """Agent for local Ollama models."""

    def __init__(
        self,
        model_name: str,
        endpoint: str = "http://localhost:11434",
        **kwargs
    ):
        """Initialize Ollama agent.

        Args:
            model_name: Name of the Ollama model (e.g., "llama3.2:3b")
            endpoint: Ollama API endpoint (default: localhost:11434)
            **kwargs: Additional configuration options
        """
        self.model_name = model_name
        self.endpoint = endpoint
        self.is_local = True
        self.cost_per_1k_input = 0.0
        self.cost_per_1k_output = 0.0

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate text using local Ollama model.

        Args:
            prompt: The text prompt
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation options

        Returns:
            Generated text

        Raises:
            requests.exceptions.RequestException: If Ollama is not running
        """
        try:
            response = requests.post(
                f"{self.endpoint}/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to Ollama at {self.endpoint}")
            raise RuntimeError(
                f"Ollama is not running. Start it with: brew services start ollama"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    def generate_with_metadata(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text with metadata (cost, timing, etc).

        Returns dictionary with:
        - output: The generated text
        - cost: Cost in dollars (always $0.00 for local)
        - model: Model name
        - tokens: Token counts
        """
        import time
        start_time = time.time()

        output = self.generate(prompt, **kwargs)
        elapsed = time.time() - start_time

        # Estimate token counts (rough approximation)
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(output.split()) * 1.3

        return {
            "output": output,
            "cost": 0.0,
            "model": self.model_name,
            "is_local": True,
            "tokens": {
                "input": int(input_tokens),
                "output": int(output_tokens),
                "total": int(input_tokens + output_tokens)
            },
            "timing": {
                "elapsed_seconds": round(elapsed, 2)
            }
        }

    @staticmethod
    def is_available() -> bool:
        """Check if Ollama is running and accessible.

        Returns:
            True if Ollama service is running, False otherwise
        """
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def list_models() -> List[Dict[str, Any]]:
        """Get list of installed Ollama models.

        Returns:
            List of model info dicts with keys: name, size, modified
        """
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                models = []

                for model in data.get("models", []):
                    models.append({
                        "name": model["name"],
                        "size": model.get("size", 0),
                        "size_gb": round(model.get("size", 0) / (1024**3), 1),
                        "modified": model.get("modified_at", ""),
                        "is_local": True,
                        "cost": 0.0
                    })

                return models

            return []

        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    @staticmethod
    def pull_model(model_name: str) -> bool:
        """Pull/download a model from Ollama registry.

        Args:
            model_name: Name of model to pull (e.g., "llama3.2:3b")

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                "http://localhost:11434/api/pull",
                json={"name": model_name},
                timeout=600  # 10 minute timeout for large models
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False


def get_ollama_agent(model_name: str = "llama3.2:3b") -> Optional[OllamaAgent]:
    """Get an Ollama agent instance if Ollama is available.

    Args:
        model_name: Name of model to use

    Returns:
        OllamaAgent instance if Ollama is running, None otherwise
    """
    if not OllamaAgent.is_available():
        logger.warning("Ollama is not running")
        return None

    return OllamaAgent(model_name)
