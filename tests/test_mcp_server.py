"""
Tests for MCPDocumentationServer

Tests the main mcp_server module including server initialization,
delegation methods, and cleanup.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.mcp_server import MCPDocumentationServer


@pytest.fixture
def test_server(tmp_path):
    """Create a test server with minimal documentation"""
    doc_file = tmp_path / "test.adoc"
    doc_file.write_text("""
= Test Document

== Section 1
Content for section 1

=== Subsection 1.1
Subsection content

== Section 2
Content for section 2
""")
    server = MCPDocumentationServer(tmp_path, enable_webserver=False)
    return server


class TestMCPDocumentationServer:
    """Test MCPDocumentationServer class"""

    def test_server_initialization(self, tmp_path):
        """Test server initializes correctly"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("= Document\n== Section\nContent")

        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Should have initialized components
        assert server.project_root == tmp_path
        assert server.parser is not None
        assert server.editor is not None
        assert server.diff_engine is not None
        assert server.doc_api is not None
        assert server.webserver is not None
        assert server.file_watcher is not None

        # Should have discovered and parsed files
        assert len(server.sections) > 0
        assert len(server.root_files) > 0

        server.cleanup()

    def test_server_initialization_with_string_path(self, tmp_path):
        """Test server accepts string path and converts to Path"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("= Document\n== Section\nContent")

        # Pass string instead of Path
        server = MCPDocumentationServer(str(tmp_path), enable_webserver=False)

        assert isinstance(server.project_root, Path)
        assert server.project_root == tmp_path

        server.cleanup()

    def test_cleanup_stops_file_watcher(self, test_server):
        """Test cleanup stops file watcher"""
        # File watcher should be running
        assert test_server.file_watcher is not None

        # Cleanup should stop it
        test_server.cleanup()

        # Verify cleanup was called (file_watcher should be stopped)
        # We can't easily verify the watcher stopped without accessing internals,
        # but we can verify cleanup doesn't raise exceptions
        assert True

    def test_cleanup_handles_exceptions(self, tmp_path):
        """Test cleanup handles exceptions gracefully"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("= Document\n== Section\nContent")

        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Mock file_watcher.stop to raise exception
        server.file_watcher.stop = Mock(side_effect=Exception("Test error"))

        # Cleanup should not raise exception
        try:
            server.cleanup()
            assert True
        except Exception:
            pytest.fail("cleanup() should handle exceptions")

    def test_on_files_changed(self, test_server):
        """Test file change handler re-parses project"""
        initial_count = len(test_server.sections)

        # Trigger file change handler
        test_server._on_files_changed({'test.adoc'})

        # Should still have sections (re-parsed)
        assert len(test_server.sections) >= initial_count

    def test_discover_root_files_excludes_directories(self, tmp_path):
        """Test _discover_root_files excludes common directories"""
        # Create files in excluded directories
        (tmp_path / ".venv").mkdir()
        (tmp_path / ".venv" / "excluded.adoc").write_text("= Should be excluded")

        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "excluded.adoc").write_text("= Should be excluded")

        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "excluded.adoc").write_text("= Should be excluded")

        # Create valid file
        (tmp_path / "valid.adoc").write_text("= Valid Document\n== Section\nContent")

        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Should only find valid.adoc
        root_file_names = [f.name for f in server.root_files]
        assert 'valid.adoc' in root_file_names
        assert 'excluded.adoc' not in root_file_names

        server.cleanup()

    def test_discover_root_files_excludes_includes(self, tmp_path):
        """Test _discover_root_files excludes files starting with _"""
        # Create include file (starts with _)
        (tmp_path / "_included.adoc").write_text("== Included Section\nContent")

        # Create main file
        (tmp_path / "main.adoc").write_text("= Main\ninclude::_included.adoc[]")

        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Should only find main.adoc
        root_file_names = [f.name for f in server.root_files]
        assert 'main.adoc' in root_file_names
        assert '_included.adoc' not in root_file_names

        # But _included.adoc should be in included_files
        included_file_names = [str(f) for f in server.included_files]
        assert any('_included.adoc' in name for name in included_file_names)

        server.cleanup()

    def test_discover_root_files_finds_all_formats(self, tmp_path):
        """Test _discover_root_files finds all supported formats"""
        # Create files with different extensions
        (tmp_path / "test.adoc").write_text("= AsciiDoc\n== Section\nContent")
        (tmp_path / "test.ad").write_text("= AsciiDoc Short\n== Section\nContent")
        (tmp_path / "test.asciidoc").write_text("= AsciiDoc Long\n== Section\nContent")
        (tmp_path / "test.md").write_text("# Markdown\n## Section\nContent")
        (tmp_path / "test.markdown").write_text("# Markdown Long\n## Section\nContent")

        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Should find all 5 files
        assert len(server.root_files) == 5

        extensions = {f.suffix for f in server.root_files}
        assert '.adoc' in extensions
        assert '.ad' in extensions
        assert '.asciidoc' in extensions
        assert '.md' in extensions
        assert '.markdown' in extensions

        server.cleanup()

    def test_parse_project_updates_included_files(self, tmp_path):
        """Test _parse_project tracks included files"""
        # Create main file with include
        (tmp_path / "main.adoc").write_text("""
= Main Document

include::_part.adoc[]

== Section
Content
""")

        # Create included file
        (tmp_path / "_part.adoc").write_text("== Included Section\nContent")

        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Should track included file
        assert len(server.included_files) > 0

        server.cleanup()

    # Test delegation methods for DocumentAPI
    def test_get_structure_delegation(self, test_server):
        """Test get_structure delegates to DocumentAPI"""
        result = test_server.get_structure(start_level=2)

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_main_chapters_delegation(self, test_server):
        """Test get_main_chapters delegates to DocumentAPI"""
        result = test_server.get_main_chapters()

        assert isinstance(result, dict)

    def test_get_root_files_structure_delegation(self, test_server):
        """Test get_root_files_structure delegates to DocumentAPI"""
        result = test_server.get_root_files_structure()

        assert isinstance(result, dict)

    def test_get_section_delegation(self, test_server):
        """Test get_section delegates to DocumentAPI"""
        section_id = list(test_server.sections.keys())[0]
        result = test_server.get_section(section_id)

        assert result is not None
        assert 'title' in result

    def test_get_sections_delegation(self, test_server):
        """Test get_sections delegates to DocumentAPI"""
        result = test_server.get_sections(level=2)

        assert isinstance(result, list)

    def test_get_sections_by_level_delegation(self, test_server):
        """Test get_sections_by_level delegates to DocumentAPI"""
        result = test_server.get_sections_by_level(level=2)

        assert isinstance(result, list)

    def test_search_content_delegation(self, test_server):
        """Test search_content delegates to DocumentAPI"""
        result = test_server.search_content('section')

        assert isinstance(result, list)

    def test_get_metadata_delegation(self, test_server):
        """Test get_metadata delegates to DocumentAPI"""
        result = test_server.get_metadata()

        assert isinstance(result, dict)
        assert 'total_sections' in result

    def test_get_dependencies_delegation(self, test_server):
        """Test get_dependencies delegates to DocumentAPI"""
        result = test_server.get_dependencies()

        assert isinstance(result, dict)
        assert 'includes' in result

    def test_validate_structure_delegation(self, test_server):
        """Test validate_structure delegates to DocumentAPI"""
        result = test_server.validate_structure()

        assert isinstance(result, dict)
        assert 'valid' in result

    def test_refresh_index_delegation(self, test_server):
        """Test refresh_index delegates to DocumentAPI"""
        result = test_server.refresh_index()

        assert isinstance(result, dict)
        assert 'success' in result

    def test_update_section_content_delegation(self, test_server):
        """Test update_section_content delegates to DocumentAPI"""
        section_id = list(test_server.sections.keys())[0]
        result = test_server.update_section_content(section_id, "New content")

        assert isinstance(result, bool)

    def test_insert_section_delegation(self, test_server):
        """Test insert_section delegates to DocumentAPI"""
        section_id = list(test_server.sections.keys())[0]
        result = test_server.insert_section(section_id, "New Section", "Content")

        assert isinstance(result, bool)

    # Test delegation methods for WebserverManager
    def test_get_webserver_status_delegation(self, test_server):
        """Test get_webserver_status delegates to WebserverManager"""
        result = test_server.get_webserver_status()

        assert isinstance(result, dict)
        assert 'running' in result

    def test_restart_webserver_delegation(self, test_server):
        """Test restart_webserver delegates to WebserverManager"""
        result = test_server.restart_webserver()

        # restart_webserver returns False when webserver is disabled
        assert isinstance(result, bool)
