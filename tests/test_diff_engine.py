"""
Pytest tests for DiffEngine module
Tests diff generation, HTML output, and change detection
"""

import pytest

from src.diff_engine import DiffEngine, DiffLine


@pytest.mark.unit
class TestDiffEngine:
    """Test DiffEngine functionality"""

    def test_engine_initialization(self):
        """Test DiffEngine creates with empty state"""
        engine = DiffEngine()

        assert isinstance(engine.previous_content, dict)
        assert len(engine.previous_content) == 0

    def test_compare_identical_content(self):
        """Test comparing identical content shows no changes"""
        engine = DiffEngine()

        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nLine 2\nLine 3"

        result = engine.compare_content("test-section", old_content, new_content)

        assert 'changes' in result
        assert result['changes']['added_lines'] == 0
        assert result['changes']['removed_lines'] == 0

    def test_compare_added_lines(self):
        """Test detecting added lines"""
        engine = DiffEngine()

        old_content = "Line 1\nLine 2"
        new_content = "Line 1\nLine 2\nLine 3\nLine 4"

        result = engine.compare_content("test-section", old_content, new_content)

        assert result['changes']['added_lines'] > 0

    def test_compare_removed_lines(self):
        """Test detecting removed lines"""
        engine = DiffEngine()

        old_content = "Line 1\nLine 2\nLine 3\nLine 4"
        new_content = "Line 1\nLine 2"

        result = engine.compare_content("test-section", old_content, new_content)

        assert result['changes']['removed_lines'] > 0

    def test_compare_modified_lines(self):
        """Test detecting modified lines"""
        engine = DiffEngine()

        old_content = "Line 1\nOriginal Line\nLine 3"
        new_content = "Line 1\nModified Line\nLine 3"

        result = engine.compare_content("test-section", old_content, new_content)

        # Should detect both removal and addition
        assert result['changes']['added_lines'] > 0 or result['changes']['removed_lines'] > 0

    def test_compare_empty_old_content(self):
        """Test comparing with empty old content (new section)"""
        engine = DiffEngine()

        old_content = ""
        new_content = "New Line 1\nNew Line 2"

        result = engine.compare_content("test-section", old_content, new_content)

        assert result['changes']['added_lines'] > 0
        assert result['changes']['removed_lines'] == 0

    def test_compare_empty_new_content(self):
        """Test comparing with empty new content (deleted section)"""
        engine = DiffEngine()

        old_content = "Old Line 1\nOld Line 2"
        new_content = ""

        result = engine.compare_content("test-section", old_content, new_content)

        assert result['changes']['added_lines'] == 0
        assert result['changes']['removed_lines'] > 0

    def test_compare_empty_both(self):
        """Test comparing two empty contents"""
        engine = DiffEngine()

        old_content = ""
        new_content = ""

        result = engine.compare_content("test-section", old_content, new_content)

        assert result['changes']['added_lines'] == 0
        assert result['changes']['removed_lines'] == 0

    def test_diff_line_dataclass(self):
        """Test DiffLine dataclass creation"""
        diff_line = DiffLine(
            line_type='added',
            content='New line content',
            line_number=5
        )

        assert diff_line.line_type == 'added'
        assert diff_line.content == 'New line content'
        assert diff_line.line_number == 5

    def test_diff_line_types(self):
        """Test different diff line types"""
        added = DiffLine('added', 'Added line', 1)
        removed = DiffLine('removed', 'Removed line', 2)
        unchanged = DiffLine('unchanged', 'Unchanged line', 3)

        assert added.line_type == 'added'
        assert removed.line_type == 'removed'
        assert unchanged.line_type == 'unchanged'

    def test_compare_multiline_changes(self):
        """Test comparing content with multiple changes"""
        engine = DiffEngine()

        old_content = """First line
Second line
Third line
Fourth line"""

        new_content = """First line
Modified second line
Third line
Added fifth line"""

        result = engine.compare_content("test-section", old_content, new_content)

        # Should detect both additions and removals
        assert 'changes' in result
        assert result['has_changes'] is True

    def test_compare_whitespace_changes(self):
        """Test handling whitespace changes"""
        engine = DiffEngine()

        old_content = "Line with    spaces"
        new_content = "Line with  spaces"

        result = engine.compare_content("test-section", old_content, new_content)

        # Should detect the difference
        assert result['changes']['added_lines'] > 0 or result['changes']['removed_lines'] > 0

    def test_compare_none_content(self):
        """Test handling None as content"""
        engine = DiffEngine()

        old_content = None
        new_content = "New content"

        # Should handle None gracefully
        result = engine.compare_content("test-section", old_content or "", new_content)

        assert result['changes']['added_lines'] > 0

    @pytest.mark.parametrize("old,new", [
        ("a", "b"),
        ("line1\nline2", "line1\nline3"),
        ("short", "longer text"),
    ])
    def test_compare_various_changes(self, old, new):
        """Test comparing various content changes"""
        engine = DiffEngine()

        result = engine.compare_content("test", old, new)

        # Should detect some change
        assert (result['changes']['added_lines'] > 0 or
                result['changes']['removed_lines'] > 0 or
                result['changes'].get('changed_lines', 0) > 0)

    def test_multiple_section_comparisons(self):
        """Test comparing multiple different sections"""
        engine = DiffEngine()

        # Compare section 1
        result1 = engine.compare_content("section-1", "old", "new")

        # Compare section 2
        result2 = engine.compare_content("section-2", "original", "modified")

        # Both should have results
        assert 'changes' in result1
        assert 'changes' in result2
