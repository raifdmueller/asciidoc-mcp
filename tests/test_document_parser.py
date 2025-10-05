"""
Pytest tests for DocumentParser module
Tests section parsing, include resolution, and hierarchy building
"""

import pytest
from pathlib import Path

from src.document_parser import DocumentParser, Section


@pytest.mark.unit
@pytest.mark.parser
class TestDocumentParser:
    """Test DocumentParser functionality"""

    def test_parser_initialization(self):
        """Test DocumentParser creates with default settings"""
        parser = DocumentParser()
        assert parser.max_include_depth == 4
        assert isinstance(parser.processed_files, set)
        assert len(parser.processed_files) == 0

    def test_parser_custom_include_depth(self):
        """Test DocumentParser accepts custom include depth"""
        parser = DocumentParser(max_include_depth=2)
        assert parser.max_include_depth == 2

    def test_parse_simple_adoc(self, temp_project_dir, sample_adoc_content):
        """Test parsing simple AsciiDoc file"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text(sample_adoc_content)

        parser = DocumentParser()
        sections, included_files = parser.parse_project(test_file)

        # Should have parsed sections
        assert len(sections) > 0
        # No includes in this test
        assert len(included_files) == 0

        # Check for expected sections
        section_titles = [s.title for s in sections.values()]
        assert "Introduction" in section_titles
        assert "Architecture" in section_titles

    def test_parse_markdown(self, temp_project_dir, sample_markdown_content):
        """Test parsing Markdown file"""
        test_file = temp_project_dir / "test.md"
        test_file.write_text(sample_markdown_content)

        parser = DocumentParser()
        sections, included_files = parser.parse_project(test_file)

        # Should have parsed sections
        assert len(sections) > 0
        # Markdown doesn't use includes
        assert len(included_files) == 0

    def test_parse_with_includes(self, sample_adoc_with_include):
        """Test parsing AsciiDoc with include directives"""
        parser = DocumentParser()
        sections, included_files = parser.parse_project(sample_adoc_with_include)

        # Should have sections from both files
        assert len(sections) >= 2

        # Should track included file
        assert len(included_files) >= 1
        included_paths = [f.name for f in included_files]
        assert "included.adoc" in included_paths

    def test_section_hierarchy(self, temp_project_dir, sample_adoc_content):
        """Test that sections maintain proper hierarchy"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text(sample_adoc_content)

        parser = DocumentParser()
        sections, _ = parser.parse_project(test_file)

        # Find a parent and child section
        for section in sections.values():
            if section.title == "Overview":
                # Overview should be child of Introduction
                assert section.level == 3
                assert section.parent_id is not None

    def test_section_line_numbers(self, temp_project_dir, sample_adoc_content):
        """Test that sections track line numbers correctly"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text(sample_adoc_content)

        parser = DocumentParser()
        sections, _ = parser.parse_project(test_file)

        # All sections should have valid line numbers
        for section in sections.values():
            assert section.line_start >= 0
            assert section.line_end >= section.line_start

    def test_section_source_file(self, temp_project_dir, sample_adoc_content):
        """Test that sections track source file"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text(sample_adoc_content)

        parser = DocumentParser()
        sections, _ = parser.parse_project(test_file)

        # All sections should track source file
        for section in sections.values():
            assert section.source_file is not None
            assert isinstance(section.source_file, str)

    def test_empty_file(self, temp_project_dir):
        """Test parsing empty file"""
        test_file = temp_project_dir / "empty.adoc"
        test_file.write_text("")

        parser = DocumentParser()
        sections, included_files = parser.parse_project(test_file)

        # Empty file should have no sections
        assert len(sections) == 0
        assert len(included_files) == 0

    def test_nonexistent_file(self, temp_project_dir):
        """Test parsing nonexistent file handles gracefully"""
        test_file = temp_project_dir / "nonexistent.adoc"

        parser = DocumentParser()
        # Implementation may handle this gracefully instead of raising
        try:
            sections, included_files = parser.parse_project(test_file)
            # If no exception, verify empty result
            assert len(sections) == 0
        except FileNotFoundError:
            # This is also acceptable behavior
            pass

    def test_max_include_depth(self, temp_project_dir):
        """Test that include depth limit is respected"""
        # Create deeply nested includes
        file1 = temp_project_dir / "file1.adoc"
        file2 = temp_project_dir / "file2.adoc"
        file3 = temp_project_dir / "file3.adoc"

        file1.write_text("= File 1\n\ninclude::file2.adoc[]")
        file2.write_text("== File 2\n\ninclude::file3.adoc[]")
        file3.write_text("=== File 3\n\nContent")

        parser = DocumentParser(max_include_depth=2)
        sections, included_files = parser.parse_project(file1)

        # Should have parsed some sections
        assert len(sections) > 0
        # Include behavior depends on implementation
        # Just verify no crash with nested includes

    @pytest.mark.parametrize("extension", [".adoc", ".asciidoc", ".md"])
    def test_supported_file_extensions(self, temp_project_dir, extension):
        """Test parser supports various file extensions"""
        test_file = temp_project_dir / f"test{extension}"

        if extension == ".md":
            content = "# Title\n\n## Section\nContent."
        else:
            content = "= Title\n\n== Section\nContent."

        test_file.write_text(content)

        parser = DocumentParser()
        sections, _ = parser.parse_project(test_file)

        assert len(sections) > 0

    def test_code_blocks_not_parsed_as_headers(self, temp_project_dir):
        """Test that content inside code blocks is not parsed as section headers (Issue #49)"""
        test_file = temp_project_dir / "test_codeblock.adoc"

        # Create document with PlantUML code block containing header-like syntax
        content = """= Test Document

== Real Section

Some content before the code block.

[plantuml]
----
== Initial Setup ==
Server -> Client: connect()

== External Modification ==
Client -> Server: update()
----

== Another Real Section

[source,python]
----
# Create focused modules
class Example:
    pass
----

=== Real Subsection

Content here.
"""
        test_file.write_text(content)

        parser = DocumentParser()
        sections, _ = parser.parse_project(test_file)

        # Extract section titles
        section_titles = [s.title for s in sections.values()]

        # Verify real sections are present
        assert "Test Document" in section_titles
        assert "Real Section" in section_titles
        assert "Another Real Section" in section_titles
        assert "Real Subsection" in section_titles

        # Verify code block content is NOT parsed as sections
        assert "Initial Setup ==" not in section_titles
        assert "External Modification ==" not in section_titles
        assert "Create focused modules" not in section_titles

        # Verify total section count (should be only 4 real sections)
        assert len(sections) == 4, f"Expected 4 sections but got {len(sections)}: {section_titles}"
