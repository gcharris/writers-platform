"""
Ollama Integration for FREE Local AI
Uses Llama 3.3 (70B) for setup wizard and knowledge extraction
"""
import os
import httpx
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = "llama3.3:70b"


class OllamaClient:
    """Client for interacting with local Ollama instance"""

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)

    async def is_available(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    async def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    async def generate(
        self,
        prompt: str,
        model: str = DEFAULT_MODEL,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """Generate completion using Ollama"""
        try:
            payload: Dict[str, Any] = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }

            if system:
                payload["system"] = system

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.error(f"Ollama generation failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """Chat completion using Ollama"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }

            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            else:
                logger.error(f"Ollama chat failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error chatting with Ollama: {e}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get or create global Ollama client"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


async def wizard_chat(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
) -> Optional[str]:
    """
    Convenience function for wizard chat
    Uses FREE local Llama 3.3 via Ollama
    """
    client = get_ollama_client()

    # Check if Ollama is available
    if not await client.is_available():
        logger.warning("Ollama not available, wizard chat will fail")
        return None

    return await client.chat(messages, temperature=temperature)


async def extract_knowledge(
    text: str,
    extraction_prompt: str,
    temperature: float = 0.3,
) -> Optional[str]:
    """
    Extract structured knowledge from text
    Uses FREE local Llama 3.3 via Ollama
    """
    client = get_ollama_client()

    if not await client.is_available():
        logger.warning("Ollama not available, knowledge extraction will fail")
        return None

    return await client.generate(
        prompt=text,
        system=extraction_prompt,
        temperature=temperature,
    )
