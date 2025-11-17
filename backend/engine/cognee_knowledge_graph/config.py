"""
Configuration management for Cognee Knowledge Graph integration.

This module handles configuration for:
- Vector database selection (LanceDB, Qdrant, PGVector, Weaviate)
- Graph database selection (NetworkX, Neo4j, KuzuDB)
- LLM provider configuration
- Document processing settings
- API credentials
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class VectorDBConfig:
    """Configuration for vector database."""
    provider: str = "lancedb"  # lancedb, qdrant, pgvector, weaviate, chromadb
    url: Optional[str] = None
    port: Optional[int] = None
    api_key: Optional[str] = None
    collection_name: str = "explants_vectors"


@dataclass
class GraphDBConfig:
    """Configuration for graph database."""
    provider: str = "networkx"  # networkx, neo4j, kuzu, falkordb
    url: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: str = "explants_graph"


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    provider: str = "gemini"  # gemini, claude, openai, ollama
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    max_tokens: int = 8000


@dataclass
class ProcessingConfig:
    """Configuration for document processing."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    extract_entities: bool = True
    extract_relationships: bool = True
    generate_summaries: bool = True
    batch_size: int = 10


class CogneeConfig:
    """
    Manages Cognee Knowledge Graph configuration.

    Configuration can be loaded from:
    1. Environment variables (highest priority)
    2. Config file (.cognee_config.json)
    3. Default values (lowest priority)

    Example:
        >>> config = CogneeConfig()
        >>> vector_db = config.vector_db
        >>> print(vector_db.provider)  # "lancedb"
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config_data = self._load_config()

        # Initialize configuration sections
        self.vector_db = self._init_vector_db()
        self.graph_db = self._init_graph_db()
        self.llm = self._init_llm()
        self.processing = self._init_processing()

    def _get_default_config_path(self) -> Path:
        """Get default configuration file path."""
        return Path.home() / ".cognee_config.json"

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file if it exists."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}

    def _init_vector_db(self) -> VectorDBConfig:
        """Initialize vector database configuration."""
        config_data = self.config_data.get('vector_db', {})

        return VectorDBConfig(
            provider=os.getenv('VECTOR_DB_PROVIDER', config_data.get('provider', 'lancedb')),
            url=os.getenv('VECTOR_DB_URL', config_data.get('url')),
            port=int(os.getenv('VECTOR_DB_PORT', config_data.get('port', 0))) or None,
            api_key=os.getenv('VECTOR_DB_KEY', config_data.get('api_key')),
            collection_name=config_data.get('collection_name', 'explants_vectors'),
        )

    def _init_graph_db(self) -> GraphDBConfig:
        """Initialize graph database configuration."""
        config_data = self.config_data.get('graph_db', {})

        return GraphDBConfig(
            provider=os.getenv('GRAPH_DB_PROVIDER', config_data.get('provider', 'networkx')),
            url=os.getenv('GRAPH_DB_URL', config_data.get('url')),
            port=int(os.getenv('GRAPH_DB_PORT', config_data.get('port', 0))) or None,
            username=os.getenv('GRAPH_DB_USERNAME', config_data.get('username')),
            password=os.getenv('GRAPH_DB_PASSWORD', config_data.get('password')),
            database_name=config_data.get('database_name', 'explants_graph'),
        )

    def _init_llm(self) -> LLMConfig:
        """Initialize LLM configuration."""
        config_data = self.config_data.get('llm', {})

        # Try to get API key from environment
        provider = os.getenv('LLM_PROVIDER', config_data.get('provider', 'gemini'))
        api_key = None

        if provider == 'gemini':
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        elif provider == 'claude':
            api_key = os.getenv('ANTHROPIC_API_KEY')
        elif provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')

        return LLMConfig(
            provider=provider,
            api_key=api_key or config_data.get('api_key'),
            model_name=os.getenv('LLM_MODEL', config_data.get('model_name')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', config_data.get('max_tokens', 8000))),
        )

    def _init_processing(self) -> ProcessingConfig:
        """Initialize processing configuration."""
        config_data = self.config_data.get('processing', {})

        return ProcessingConfig(
            chunk_size=int(os.getenv('CHUNK_SIZE', config_data.get('chunk_size', 1000))),
            chunk_overlap=int(os.getenv('CHUNK_OVERLAP', config_data.get('chunk_overlap', 200))),
            extract_entities=os.getenv('EXTRACT_ENTITIES', str(config_data.get('extract_entities', True))).lower() == 'true',
            extract_relationships=os.getenv('EXTRACT_RELATIONSHIPS', str(config_data.get('extract_relationships', True))).lower() == 'true',
            generate_summaries=os.getenv('GENERATE_SUMMARIES', str(config_data.get('generate_summaries', True))).lower() == 'true',
            batch_size=int(os.getenv('BATCH_SIZE', config_data.get('batch_size', 10))),
        )

    def save(self):
        """Save current configuration to file."""
        config_dict = {
            'vector_db': asdict(self.vector_db),
            'graph_db': asdict(self.graph_db),
            'llm': asdict(self.llm),
            'processing': asdict(self.processing),
        }

        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

    def get_env_variables(self) -> Dict[str, str]:
        """
        Get environment variables for Cognee configuration.

        Returns dictionary of environment variables that should be set.
        """
        env_vars = {}

        # Vector DB
        if self.vector_db.provider:
            env_vars['VECTOR_DB_PROVIDER'] = self.vector_db.provider
        if self.vector_db.url:
            env_vars['VECTOR_DB_URL'] = self.vector_db.url
        if self.vector_db.port:
            env_vars['VECTOR_DB_PORT'] = str(self.vector_db.port)
        if self.vector_db.api_key:
            env_vars['VECTOR_DB_KEY'] = self.vector_db.api_key

        # Graph DB
        if self.graph_db.provider:
            env_vars['GRAPH_DB_PROVIDER'] = self.graph_db.provider
        if self.graph_db.url:
            env_vars['GRAPH_DB_URL'] = self.graph_db.url
        if self.graph_db.port:
            env_vars['GRAPH_DB_PORT'] = str(self.graph_db.port)
        if self.graph_db.username:
            env_vars['GRAPH_DB_USERNAME'] = self.graph_db.username
        if self.graph_db.password:
            env_vars['GRAPH_DB_PASSWORD'] = self.graph_db.password

        # LLM
        if self.llm.provider:
            env_vars['LLM_PROVIDER'] = self.llm.provider
        if self.llm.api_key:
            if self.llm.provider == 'gemini':
                env_vars['GOOGLE_API_KEY'] = self.llm.api_key
            elif self.llm.provider == 'claude':
                env_vars['ANTHROPIC_API_KEY'] = self.llm.api_key
            elif self.llm.provider == 'openai':
                env_vars['OPENAI_API_KEY'] = self.llm.api_key

        return env_vars

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check LLM API key
        if not self.llm.api_key:
            errors.append(f"Missing API key for LLM provider '{self.llm.provider}'")

        # Check vector DB configuration
        if self.vector_db.provider not in ['lancedb', 'qdrant', 'pgvector', 'weaviate', 'chromadb']:
            errors.append(f"Invalid vector DB provider: {self.vector_db.provider}")

        # Check graph DB configuration
        if self.graph_db.provider not in ['networkx', 'neo4j', 'kuzu', 'falkordb']:
            errors.append(f"Invalid graph DB provider: {self.graph_db.provider}")

        # Check processing configuration
        if self.processing.chunk_size < 100:
            errors.append("Chunk size must be at least 100")

        if self.processing.chunk_overlap >= self.processing.chunk_size:
            errors.append("Chunk overlap must be less than chunk size")

        return len(errors) == 0, errors

    def __str__(self) -> str:
        """String representation of configuration."""
        return f"""CogneeConfig:
  Vector DB: {self.vector_db.provider}
  Graph DB: {self.graph_db.provider}
  LLM: {self.llm.provider} ({self.llm.model_name or 'default model'})
  Chunk Size: {self.processing.chunk_size}
  Extract Entities: {self.processing.extract_entities}
  Extract Relationships: {self.processing.extract_relationships}
"""


def create_default_config() -> CogneeConfig:
    """
    Create a default configuration with recommended settings.

    Returns:
        CogneeConfig with default settings
    """
    config = CogneeConfig()

    # Set recommended defaults
    config.vector_db.provider = "lancedb"  # File-based, no server needed
    config.graph_db.provider = "networkx"  # In-memory, good for development
    config.llm.provider = "gemini"
    config.processing.chunk_size = 1000
    config.processing.chunk_overlap = 200

    return config


if __name__ == "__main__":
    # Test configuration
    config = create_default_config()
    print(config)

    # Validate
    is_valid, errors = config.validate()
    if is_valid:
        print("\n✓ Configuration is valid")
    else:
        print("\n✗ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
