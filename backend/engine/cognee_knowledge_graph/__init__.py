"""
Cognee Knowledge Graph Integration for The Explants

This module provides a true knowledge graph implementation using Cognee,
offering entity and relationship extraction, graph traversal, and semantic
search capabilities across the entire trilogy corpus.

Core Features:
- Automatic entity and relationship extraction
- Vector embeddings + graph database storage
- Cross-document context building
- Natural language queries with graph traversal
- Memory layer for AI agents
- Self-hosted deployment (no cloud gatekeeping)

Main Components:
- CogneeConfig: Configuration management
- CogneeKnowledgeGraph: Main query interface
- BulkUploader: Automated document ingestion
- EntityQuerier: Entity and relationship queries
- GraphVisualizer: Knowledge graph visualization

Example Usage:
    >>> from factory.core.cognee_knowledge_graph import CogneeKnowledgeGraph
    >>> kg = CogneeKnowledgeGraph()
    >>> await kg.initialize()
    >>> results = await kg.query("Show Mickey's addiction arc")
"""

from .config import CogneeConfig
from .cognee_graph import CogneeKnowledgeGraph
from .bulk_uploader import BulkUploader
from .entity_queries import EntityQuerier

__all__ = [
    'CogneeConfig',
    'CogneeKnowledgeGraph',
    'BulkUploader',
    'EntityQuerier',
]

__version__ = '1.0.0'
