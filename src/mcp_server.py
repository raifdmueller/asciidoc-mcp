#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from typing import Dict, Set
from src.document_parser import DocumentParser
from src.file_watcher import FileWatcher
from src.content_editor import ContentEditor
from src.diff_engine import DiffEngine
from src.mcp.document_api import DocumentAPI
from src.mcp.webserver_manager import WebserverManager
from src.mcp.protocol_handler import handle_mcp_request

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
                       '.amazonq', '.serena', '.vibe'}

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
    def get_structure(self, start_level: int = 1, parent_id: str = None):
        """Delegate to DocumentAPI"""
        return self.doc_api.get_structure(start_level, parent_id)

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


def main():
    import signal
    import atexit

    if len(sys.argv) != 2:
        print("Usage: python mcp_server.py <project_root>", file=sys.stderr)
        sys.exit(1)

    project_root = Path(sys.argv[1])
    if not project_root.exists():
        print(f"Project root does not exist: {project_root}", file=sys.stderr)
        sys.exit(1)

    server = MCPDocumentationServer(project_root)

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        import datetime
        log_file = "browser_debug.log"
        timestamp = datetime.datetime.now().isoformat()

        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Signal {signum} received, cleaning up...\n")

        server.cleanup()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Register atexit handler as backup
    atexit.register(server.cleanup)

    # MCP protocol loop
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            # Pass doc_api, webserver, and server to handle_mcp_request
            response = handle_mcp_request(request, server.doc_api, server.webserver, server)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({'jsonrpc': '2.0', 'error': {'code': -32700, 'message': 'Parse error'}}))
        except Exception as e:
            print(json.dumps({'jsonrpc': '2.0', 'error': {'code': -32603, 'message': str(e)}}))

if __name__ == '__main__':
    main()
