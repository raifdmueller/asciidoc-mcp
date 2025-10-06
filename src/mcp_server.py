#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Dict, Set, Optional

try:
    from src.document_parser import DocumentParser
    from src.file_watcher import FileWatcher
    from src.content_editor import ContentEditor
    from src.diff_engine import DiffEngine
    from src.mcp.document_api import DocumentAPI
    from src.mcp.webserver_manager import WebserverManager
except ImportError:
    # Fallback for when run as script without src module in path
    from document_parser import DocumentParser
    from file_watcher import FileWatcher
    from content_editor import ContentEditor
    from diff_engine import DiffEngine
    from mcp.document_api import DocumentAPI
    from mcp.webserver_manager import WebserverManager
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("docs-server")

class MCPDocumentationServer:
    def __init__(self, project_root: Path, enable_webserver: bool = True):
        # Convert to Path if string is passed
        self.project_root = Path(project_root) if isinstance(project_root, str) else project_root
        self.enable_webserver = enable_webserver

        # Core components
        self.parser = DocumentParser()
        self.editor = ContentEditor(project_root)
        self.diff_engine = DiffEngine()
        self.sections = {}
        self.root_files = []
        self.included_files = set()  # Track files that are included by other files

        # Modular components (dependency injection)
        self.doc_api = DocumentAPI(self)
        self.webserver = WebserverManager(self)

        # File watching
        self.file_watcher = FileWatcher(project_root, self._on_files_changed)
        self._discover_root_files()
        self._parse_project()
        self.file_watcher.start()

        # Start webserver after initialization (moved from protocol_handler.py:23)
        if self.enable_webserver and not self.webserver.webserver_started:
            self.webserver.start_webserver_thread()

    def cleanup(self):
        """Clean up resources and stop webserver"""
        try:
            # Stop file watcher
            if hasattr(self, 'file_watcher') and self.file_watcher:
                self.file_watcher.stop()

            # Webserver thread will stop automatically (daemon thread)

        except Exception as e:
            print(f"Exception in cleanup: {e}", file=sys.stderr)

    def _on_files_changed(self, changed_files: Set[str]):
        """Handle file change notifications"""
        print(f"Files changed: {len(changed_files)} files", file=sys.stderr)
        self._discover_root_files()
        self._parse_project()

    def _discover_root_files(self):
        """Find main documentation files (AsciiDoc and Markdown, including subdirectories)"""
        self.root_files = []  # Clear list before discovering to prevent duplicates

        # Directories to exclude from search
        exclude_dirs = {'.venv', 'venv', '.git', '.pytest_cache', '__pycache__',
                       'node_modules', '.tox', '.mypy_cache', '.ruff_cache',
                       '.amazonq', '.serena', '.vibe', 'build'}

        # Extended patterns for AsciiDoc and Markdown files (recursive search)
        patterns = ['**/*.adoc', '**/*.ad', '**/*.asciidoc', '**/*.md', '**/*.markdown']
        for pattern in patterns:
            for file in self.project_root.glob(pattern):
                # Skip files in excluded directories
                if any(excluded in file.parts for excluded in exclude_dirs):
                    continue
                # Skip include files (starting with _)
                if file.name.startswith('_'):
                    continue
                self.root_files.append(file)

    def _parse_project(self):
        """Parse all root files and build section index"""
        self.included_files.clear()  # Clear before re-parsing
        for root_file in self.root_files:
            file_sections, included = self.parser.parse_project(root_file)
            self.sections.update(file_sections)
            self.included_files.update(included)

    # ============================================================================
    # DocumentAPI and WebserverManager methods have been extracted to modules
    # Delegation methods below provide backward compatibility
    # ============================================================================

    # DocumentAPI delegation methods
    def get_structure(self, start_level: int = 1, parent_id: str = None, limit: int = None, offset: int = 0):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_structure(start_level, parent_id, limit, offset)

    def get_main_chapters(self):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_main_chapters()

    def get_root_files_structure(self):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_root_files_structure()

    def get_section(self, path: str):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_section(path)

    def get_sections(self, level: int):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_sections(level)

    def get_sections_by_level(self, level: int):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_sections_by_level(level)

    def search_content(self, query: str):
        """Delegate to DocumentAPI"""
        return self.doc_api.search_content(query)

    def get_metadata(self, path: str = None):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_metadata(path)

    def get_dependencies(self):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_dependencies()

    def validate_structure(self):
        """Delegate to DocumentAPI"""
        return self.doc_api.validate_structure()

    def refresh_index(self):
        """Delegate to DocumentAPI"""
        return self.doc_api.refresh_index()

    def update_section_content(self, path: str, content: str):
        """Delegate to DocumentAPI"""
        return self.doc_api.update_section_content(path, content)

    def insert_section(self, parent_path: str, title: str, content: str, position: str = "append"):
        """Delegate to DocumentAPI"""
        return self.doc_api.insert_section(parent_path, title, content, position)

    # WebserverManager delegation methods
    def get_webserver_status(self):
        """Delegate to WebserverManager"""
        return self.webserver.get_webserver_status()

    def restart_webserver(self):
        """Delegate to WebserverManager"""
        return self.webserver.restart_webserver()


# Global server instance (initialized in main())
_server: Optional[MCPDocumentationServer] = None


# ============================================================================
# MCP Tools - Registered with FastMCP decorators
# ============================================================================

@mcp.tool()
def get_section(path: str) -> dict:
    """Get specific section content"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.get_section(path)


@mcp.tool()
def get_metadata(path: str | None = None) -> dict:
    """Get metadata for section or entire project"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.get_metadata(path)


@mcp.tool()
def get_sections(level: int) -> list:
    """Get all sections at specific level"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.get_sections(level)


@mcp.tool()
def get_dependencies() -> dict:
    """Get include tree and cross-references"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.get_dependencies()


@mcp.tool()
def validate_structure() -> dict:
    """Validate document structure consistency"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.validate_structure()


@mcp.tool()
def refresh_index() -> dict:
    """Refresh document index to detect new files"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.refresh_index()


@mcp.tool()
def get_structure(start_level: int = 1, parent_id: str | None = None) -> dict:
    """Get sections at a specific hierarchy level (depth=1 to avoid token limits). Use start_level to navigate through levels progressively."""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.get_structure(start_level, parent_id)


@mcp.tool()
def search_content(query: str) -> list:
    """Search for content in documentation"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.search_content(query)


@mcp.tool()
def update_section(path: str, content: str) -> bool:
    """Update section content"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.update_section_content(path, content)


@mcp.tool()
def insert_section(parent_path: str, title: str, content: str, position: str = 'append') -> bool:
    """Insert new section"""
    if _server is None:
        raise RuntimeError("Server not initialized")
    return _server.doc_api.insert_section(parent_path, title, content, position)


def main():
    global _server
    import signal
    import atexit

    if len(sys.argv) != 2:
        print("Usage: python mcp_server.py <project_root>", file=sys.stderr)
        sys.exit(1)

    project_root = Path(sys.argv[1])
    if not project_root.exists():
        print(f"Project root does not exist: {project_root}", file=sys.stderr)
        sys.exit(1)

    # Initialize server
    _server = MCPDocumentationServer(project_root)

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        import datetime
        log_file = "browser_debug.log"
        timestamp = datetime.datetime.now().isoformat()

        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Signal {signum} received, cleaning up...\n")

        _server.cleanup()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Register atexit handler as backup
    atexit.register(_server.cleanup)

    # Run FastMCP server (replaces manual stdin/stdout loop)
    mcp.run()


if __name__ == '__main__':
    main()
