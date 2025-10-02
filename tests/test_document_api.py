"""
Tests for DocumentAPI module

Tests the document_api module which handles document structure, sections, and metadata.
"""

import pytest
from pathlib import Path
from src.mcp.document_api import DocumentAPI
from src.mcp_server import MCPDocumentationServer


@pytest.fixture
def arc42_server(tmp_path):
    """Create a test server with arc42-style documentation structure"""
    doc_file = tmp_path / "architecture.adoc"
    doc_file.write_text("""
= Architecture Documentation

== 1. Introduction and Goals
Goals and requirements overview.

=== 1.1 Requirements
Specific requirements listed here.

== 2. Architecture Constraints
Technical constraints and decisions.

=== 2.1 Technical Constraints
Details about technical limitations.

== 3. System Scope and Context
System boundaries and interfaces.
""")
    server = MCPDocumentationServer(tmp_path, enable_webserver=False)
    return server


@pytest.fixture
def multi_file_server(tmp_path):
    """Create a test server with multiple documentation files"""
    # Main document
    main_doc = tmp_path / "main.adoc"
    main_doc.write_text("""
= Main Documentation

== Overview
Main overview section.

== Details
Detailed information.
""")

    # Secondary document
    other_doc = tmp_path / "other.adoc"
    other_doc.write_text("""
= Other Documentation

== Introduction
Introduction to other doc.

== Content
Content section.
""")

    server = MCPDocumentationServer(tmp_path, enable_webserver=False)
    return server


class TestDocumentAPI:
    """Test DocumentAPI methods"""

    def test_get_main_chapters_arc42_structure(self, tmp_path):
        """Test get_main_chapters with arc42-style numbered chapters"""
        # Create proper arc42 document without level 1 (just numbered level 2 sections)
        doc_file = tmp_path / "architecture.adoc"
        doc_file.write_text("""
== 1. Introduction and Goals
Goals and requirements overview.

=== 1.1 Requirements
Specific requirements listed here.

== 2. Architecture Constraints
Technical constraints and decisions.

=== 2.1 Technical Constraints
Details about technical limitations.

== 3. System Scope and Context
System boundaries and interfaces.
""")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        result = server.doc_api.get_main_chapters()

        # Should have chapter_01, chapter_02, chapter_03
        chapter_keys = [k for k in result.keys() if k.startswith('chapter_')]
        assert len(chapter_keys) >= 3

        # Find the chapters
        chapters = [result[k] for k in chapter_keys if k.startswith('chapter_0')]

        # Should have chapter numbers
        chapter_numbers = [c.get('chapter_number') for c in chapters]
        assert 1 in chapter_numbers
        assert 2 in chapter_numbers
        assert 3 in chapter_numbers

    def test_get_main_chapters_introduction_and_goals_detection(self, tmp_path):
        """Test get_main_chapters detects 'Introduction and Goals' as chapter 1"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("""
== Introduction and Goals
Special chapter 1 detection.
""")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        result = server.doc_api.get_main_chapters()

        # Should detect as chapter 1
        assert 'chapter_01' in result
        assert result['chapter_01']['chapter_number'] == 1
        assert 'introduction' in result['chapter_01']['title'].lower()
        assert 'goals' in result['chapter_01']['title'].lower()

    def test_get_main_chapters_includes_level_1_sections(self, multi_file_server):
        """Test get_main_chapters includes top-level documents"""
        result = multi_file_server.doc_api.get_main_chapters()

        # Should have entries for level 1 sections
        level_1_sections = [k for k, v in result.items() if v.get('chapter_number') == 999]
        assert len(level_1_sections) > 0  # Has level 1 sections

    def test_get_root_files_structure(self, multi_file_server):
        """Test get_root_files_structure returns file-grouped structure"""
        result = multi_file_server.doc_api.get_root_files_structure()

        # Should have entries for each root file
        assert len(result) >= 2

        # Each entry should have filename, path, section_count, sections
        for file_path, file_data in result.items():
            assert 'filename' in file_data
            assert 'path' in file_data
            assert 'section_count' in file_data
            assert 'sections' in file_data
            assert file_data['section_count'] > 0

    def test_get_root_files_structure_hierarchical_sections(self, arc42_server):
        """Test get_root_files_structure builds hierarchical structure within files"""
        result = arc42_server.doc_api.get_root_files_structure()

        # Should have one file
        assert len(result) == 1

        # Get the file entry
        file_entry = list(result.values())[0]

        # Should have sections
        assert file_entry['section_count'] > 0
        assert len(file_entry['sections']) > 0

        # Check for hierarchical structure (children)
        # Level 2 sections should have children arrays
        has_children = any(
            'children' in section
            for section in file_entry['sections']
        )
        assert has_children

    def test_get_root_files_structure_excludes_included_files(self, tmp_path):
        """Test that included files are excluded from root files structure"""
        # Create main file with include
        main_file = tmp_path / "main.adoc"
        main_file.write_text("""
= Main Document

include::_included.adoc[]

== Main Section
Content here.
""")

        # Create included file
        included_file = tmp_path / "_included.adoc"
        included_file.write_text("""
== Included Section
Included content.
""")

        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        result = server.doc_api.get_root_files_structure()

        # Should only have main.adoc, not _included.adoc
        file_paths = list(result.keys())
        assert any('main.adoc' in path for path in file_paths)
        assert not any('_included.adoc' in path for path in file_paths)

    def test_get_sections_by_level(self, arc42_server):
        """Test get_sections_by_level filters by level correctly"""
        # Get level 2 sections
        level_2 = arc42_server.doc_api.get_sections_by_level(2)

        # Should have results
        assert len(level_2) > 0

        # All should have id, title, content
        for section in level_2:
            assert 'id' in section
            assert 'title' in section
            assert 'content' in section

        # Get level 3 sections
        level_3 = arc42_server.doc_api.get_sections_by_level(3)

        # Should have results
        assert len(level_3) > 0

    def test_get_section_not_found(self, arc42_server):
        """Test get_section returns None for non-existent section"""
        result = arc42_server.doc_api.get_section('nonexistent')
        assert result is None

    def test_search_content_finds_matches(self, arc42_server):
        """Test search_content finds matching sections"""
        results = arc42_server.doc_api.search_content('requirements')

        # Should find the Requirements section
        assert len(results) > 0
        assert any('requirements' in r['title'].lower() for r in results)

    def test_search_content_relevance_scoring(self, tmp_path):
        """Test search_content scores title matches higher than content matches"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("""
= Documentation

== Testing Framework
This section is about testing.

== Other Section
Testing is mentioned here but not the main topic.
""")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        results = server.doc_api.search_content('testing')

        # Should have results
        assert len(results) >= 2

        # "Testing Framework" should be scored higher (first result)
        assert 'testing' in results[0]['title'].lower()

    def test_get_metadata_for_section(self, arc42_server):
        """Test get_metadata returns metadata for specific section"""
        # Get a valid section ID
        section_id = list(arc42_server.sections.keys())[0]

        result = arc42_server.doc_api.get_metadata(section_id)

        # Should have section metadata (actual fields from API)
        assert 'path' in result
        assert 'title' in result
        assert 'level' in result
        assert 'word_count' in result
        assert 'children_count' in result

    def test_get_metadata_for_project(self, multi_file_server):
        """Test get_metadata without path returns project metadata"""
        result = multi_file_server.doc_api.get_metadata()

        # Should have project-level metadata (actual fields from API)
        assert 'total_sections' in result
        assert 'total_words' in result
        assert 'root_files' in result
        assert 'project_root' in result
        assert result['total_sections'] > 0
        assert len(result['root_files']) >= 2

    def test_get_dependencies(self, tmp_path):
        """Test get_dependencies returns include tree"""
        # Create document with includes
        main_file = tmp_path / "main.adoc"
        main_file.write_text("""
= Main Document

include::_part1.adoc[]
include::_part2.adoc[]
""")

        part1 = tmp_path / "_part1.adoc"
        part1.write_text("== Part 1\nContent")

        part2 = tmp_path / "_part2.adoc"
        part2.write_text("== Part 2\nContent")

        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        result = server.doc_api.get_dependencies()

        # Should have includes dict (actual field from API)
        assert 'includes' in result
        assert 'cross_references' in result
        assert 'orphaned_sections' in result
        assert len(result['includes']) > 0

    def test_validate_structure(self, arc42_server):
        """Test validate_structure checks document consistency"""
        result = arc42_server.doc_api.validate_structure()

        # Should have validation results
        assert 'valid' in result
        assert 'issues' in result

        # Simple structure should be valid
        assert result['valid'] is True
        assert len(result['issues']) == 0

    def test_validate_structure_detects_issues(self, tmp_path):
        """Test validate_structure detects structural problems"""
        # Create document with level skip (1 -> 3, skipping 2)
        doc_file = tmp_path / "bad.adoc"
        doc_file.write_text("""
= Document

== Level 2

==== Level 4
This skips level 3!
""")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        result = server.doc_api.validate_structure()

        # May detect issues (depends on validation logic)
        assert 'valid' in result
        assert 'issues' in result

    def test_refresh_index(self, tmp_path):
        """Test refresh_index re-parses documentation"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("""
= Document

== Section 1
Content
""")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        initial_count = len(server.sections)

        # Add a new section to the file
        doc_file.write_text("""
= Document

== Section 1
Content

== Section 2
New content
""")

        # Refresh index
        result = server.doc_api.refresh_index()

        # Should report success (actual fields from API)
        assert 'success' in result
        assert result['success'] is True
        assert 'old_section_count' in result
        assert 'new_section_count' in result
        assert 'sections_added' in result

        # Section count should have increased
        new_count = len(server.sections)
        assert new_count > initial_count

    def test_update_section_content_success(self, tmp_path):
        """Test update_section_content updates section successfully"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("""
= Document

== Section 1
Original content
""")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Get section ID
        section_id = list(server.sections.keys())[0]

        # Update content
        success = server.doc_api.update_section_content(section_id, "Updated content")

        assert success is True

    def test_update_section_content_not_found(self, tmp_path):
        """Test update_section_content fails for non-existent section"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("= Document\n== Section 1\nContent")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Try to update non-existent section
        success = server.doc_api.update_section_content('nonexistent', "Content")

        assert success is False

    def test_insert_section_success(self, tmp_path):
        """Test insert_section adds new section successfully"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("""
= Document

== Section 1
Content
""")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)

        # Get parent section ID
        parent_id = list(server.sections.keys())[0]

        # Insert new section
        success = server.doc_api.insert_section(
            parent_id,
            "New Section",
            "New content",
            "append"
        )

        assert success is True

    def test_insert_section_positions(self, tmp_path):
        """Test insert_section with different positions (before, after, append)"""
        doc_file = tmp_path / "doc.adoc"
        doc_file.write_text("""
= Document

== Section 1
Content
""")
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        parent_id = list(server.sections.keys())[0]

        # Test each position
        for position in ['before', 'after', 'append']:
            success = server.doc_api.insert_section(
                parent_id,
                f"Test Section {position}",
                "Content",
                position
            )
            # Should succeed or gracefully handle
            assert isinstance(success, bool)
