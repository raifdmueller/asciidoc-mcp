"""
MCP Server Modules

This package contains modular components for the MCP Documentation Server:
- document_api: Document structure, sections, and metadata operations
- protocol_handler: MCP protocol request routing and tool dispatch
- webserver_manager: Web server lifecycle management
"""

from src.mcp.document_api import DocumentAPI
from src.mcp.protocol_handler import handle_mcp_request
from src.mcp.webserver_manager import WebserverManager

__all__ = ['DocumentAPI', 'handle_mcp_request', 'WebserverManager']
