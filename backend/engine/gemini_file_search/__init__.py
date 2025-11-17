"""
Gemini File Search Integration

Semantic knowledge graph for The Explants trilogy using Gemini File Search API.
Enables natural language queries across all story documents with vector embeddings.
"""

from .store_manager import FileSearchStoreManager
from .bulk_upload import BulkUploader, FileMetadataExtractor
from .agent_querier import ExplantsKnowledgeGraph
from .config import GeminiFileSearchConfig

__all__ = [
    'FileSearchStoreManager',
    'BulkUploader',
    'FileMetadataExtractor',
    'ExplantsKnowledgeGraph',
    'GeminiFileSearchConfig'
]
