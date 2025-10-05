"""
MCP Server Modules

This package contains modular components for the MCP Documentation Server:
- document_api: Document structure, sections, and metadata operations
- webserver_manager: Web server lifecycle management

Note: MCP protocol handling is now managed by FastMCP SDK (mcp.server.fastmcp)
"""

from src.mcp.document_api import DocumentAPI
from src.mcp.webserver_manager import WebserverManager

__all__ = ['DocumentAPI', 'WebserverManager']
