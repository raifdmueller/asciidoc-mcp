"""
Pytest tests for ContentEditor module
Tests section updates, inserts, and file modifications
"""

import pytest
from pathlib import Path

from src.content_editor import ContentEditor
from src.document_parser import Section


@pytest.mark.unit
class TestContentEditor:
    """Test ContentEditor functionality"""

    def test_editor_initialization(self, temp_project_dir):
        """Test ContentEditor creates with project root"""
        editor = ContentEditor(temp_project_dir)

        assert editor.project_root == temp_project_dir
        assert isinstance(editor.file_contents, dict)
        assert len(editor.file_contents) == 0

    def test_editor_accepts_string_path(self, temp_project_dir):
        """Test ContentEditor accepts string path"""
        editor = ContentEditor(str(temp_project_dir))

        assert editor.project_root == temp_project_dir
        assert isinstance(editor.project_root, Path)

    def test_load_file_content(self, temp_project_dir):
        """Test loading file content as lines"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text("Line 1\nLine 2\nLine 3")

        editor = ContentEditor(temp_project_dir)
        lines = editor.load_file_content(test_file)

        assert len(lines) == 3
        assert lines[0] == "Line 1"
        assert lines[1] == "Line 2"
        assert lines[2] == "Line 3"

    def test_load_file_content_caching(self, temp_project_dir):
        """Test that file content is cached"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text("Original content")

        editor = ContentEditor(temp_project_dir)

        # Load first time
        lines1 = editor.load_file_content(test_file)

        # Modify file
        test_file.write_text("Modified content")

        # Load again - should get cached version
        lines2 = editor.load_file_content(test_file)

        assert lines1 == lines2
        assert "Original" in lines1[0]

    def test_load_nonexistent_file(self, temp_project_dir):
        """Test loading nonexistent file returns empty list"""
        test_file = temp_project_dir / "nonexistent.adoc"

        editor = ContentEditor(temp_project_dir)
        lines = editor.load_file_content(test_file)

        assert lines == []

    def test_update_section_content(self, temp_project_dir):
        """Test updating section content"""
        test_file = temp_project_dir / "test.adoc"
        original_content = """= Document

== Section One
Original content here.

== Section Two
Another section."""

        test_file.write_text(original_content)

        # Create section object
        section = Section(
            id="section-one",
            title="Section One",
            level=2,
            content="Original content here.",
            line_start=2,  # "== Section One" line
            line_end=3,    # End of content
            source_file=str(test_file),
            children=[]
        )

        editor = ContentEditor(temp_project_dir)
        success = editor.update_section(section, "Updated content here.", test_file)

        assert success is True

        # Verify file was updated
        updated_content = test_file.read_text()
        assert "Updated content here." in updated_content
        assert "Original content here." not in updated_content

    def test_update_section_invalid_range(self, temp_project_dir):
        """Test updating section with invalid line range"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text("= Document\n\n== Section\nContent.")

        # Create section with invalid range
        section = Section(
            id="test",
            title="Test",
            level=2,
            content="Content",
            line_start=100,  # Invalid line number
            line_end=110,
            source_file=str(test_file),
            children=[]
        )

        editor = ContentEditor(temp_project_dir)
        success = editor.update_section(section, "New content", test_file)

        assert success is False

    def test_update_section_multiline_content(self, temp_project_dir):
        """Test updating section with multiline content"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text("= Document\n\n== Section\nOld line 1\nOld line 2")

        section = Section(
            id="section",
            title="Section",
            level=2,
            content="Old line 1\nOld line 2",
            line_start=2,
            line_end=4,
            source_file=str(test_file),
            children=[]
        )

        new_content = "New line 1\nNew line 2\nNew line 3"

        editor = ContentEditor(temp_project_dir)
        success = editor.update_section(section, new_content, test_file)

        assert success is True

        updated_text = test_file.read_text()
        assert "New line 1" in updated_text
        assert "New line 2" in updated_text
        assert "New line 3" in updated_text
        assert "Old line 1" not in updated_text

    def test_update_preserves_header(self, temp_project_dir):
        """Test that section header is preserved during update"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text("= Document\n\n== Important Section\nOld content.")

        section = Section(
            id="section",
            title="Important Section",
            level=2,
            content="Old content.",
            line_start=2,
            line_end=3,
            source_file=str(test_file),
            children=[]
        )

        editor = ContentEditor(temp_project_dir)
        success = editor.update_section(section, "New content.", test_file)

        assert success is True

        updated_text = test_file.read_text()
        assert "== Important Section" in updated_text
        assert "New content." in updated_text

    def test_update_section_empty_content(self, temp_project_dir):
        """Test updating section with empty content"""
        test_file = temp_project_dir / "test.adoc"
        test_file.write_text("= Document\n\n== Section\nOld content.")

        section = Section(
            id="section",
            title="Section",
            level=2,
            content="Old content.",
            line_start=2,
            line_end=3,
            source_file=str(test_file),
            children=[]
        )

        editor = ContentEditor(temp_project_dir)
        success = editor.update_section(section, "", test_file)

        assert success is True

        updated_text = test_file.read_text()
        assert "== Section" in updated_text
        # Content should be empty or just whitespace
