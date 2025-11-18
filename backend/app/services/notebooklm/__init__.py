"""
NotebookLM MCP Integration Service

Provides MCP client for querying NotebookLM notebooks and extracting
research-grounded entities for the knowledge graph.
"""

from .mcp_client import NotebookLMMCPClient, get_mcp_client

__all__ = ["NotebookLMMCPClient", "get_mcp_client"]
