#!/usr/bin/env python3
"""
TDD Test Suite for New Features
Tests written FIRST, then implementation will be fixed to pass
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
import sys

sys.path.append('../src')

from src.mcp_server import MCPDocumentationServer
from src.diff_engine import DiffEngine

class TestMetaInformationAPI(unittest.TestCase):
    """Test Meta-Information API - TDD Style"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test document
        test_doc = self.test_dir / "test.adoc"
        test_doc.write_text("""= Test Document

== Section 1
Content for section 1.

== Section 2  
Content for section 2.
""")
        
        self.server = MCPDocumentationServer(self.test_dir)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_web_interface_sorted_subsections(self):
        """Test that web interface returns sections in document order"""
        # Create test document with specific section order
        test_doc = self.test_dir / "ordered.adoc"
        test_doc.write_text("""= Document

== Section B
Content B.

== Section A  
Content A.

== Section C
Content C.
""")
        
        server = MCPDocumentationServer(self.test_dir)
        structure = server.get_structure(start_level=2)  # Get level-2 sections
        
        # Debug: see what sections we actually get
        print("Available sections:", list(structure.keys()))
        
        # Filter to only sections from ordered.adoc (document.section-*)
        # Exclude sections from test.adoc (test-document.section-*)
        level2_sections = [s for s in structure.keys() if s.startswith('document.')]
        
        print("Level 2 sections:", level2_sections)
        
        # Should have 3 level-2 sections from ordered.adoc
        self.assertEqual(len(level2_sections), 3)
        
        # For now, just verify we have sections - order test comes next
        self.assertGreater(len(level2_sections), 0)
    
    def test_get_metadata_for_section(self):
        """Test get_metadata() with path returns section metadata"""
        # Find a section to test
        sections = list(self.server.sections.keys())
        if sections:
            section_path = sections[0]
            result = self.server.get_metadata(section_path)
            
            self.assertIn('path', result)
            self.assertIn('title', result)
            self.assertIn('level', result)
            self.assertIn('word_count', result)
            self.assertIn('children_count', result)
            self.assertEqual(result['path'], section_path)
    
    def test_get_dependencies(self):
        """Test get_dependencies() returns include tree"""
        result = self.server.get_dependencies()
        
        self.assertIn('includes', result)
        self.assertIn('cross_references', result)
        self.assertIn('orphaned_sections', result)
        self.assertIsInstance(result['includes'], dict)
        self.assertIsInstance(result['orphaned_sections'], list)
    
    def test_validate_structure(self):
        """Test validate_structure() returns validation results"""
        result = self.server.validate_structure()
        
        self.assertIn('valid', result)
        self.assertIn('issues', result)
        self.assertIn('warnings', result)
        self.assertIn('total_sections', result)
        self.assertIn('validation_timestamp', result)
        self.assertIsInstance(result['valid'], bool)
        self.assertIsInstance(result['issues'], list)
    
    def test_refresh_index(self):
        """Test refresh_index() re-indexes documents"""
        old_count = len(self.server.sections)
        
        # Add new file
        new_file = self.test_dir / "new.adoc"
        new_file.write_text("= New Document\n\nNew content.")
        
        result = self.server.refresh_index()
        
        self.assertIn('success', result)
        self.assertIn('old_section_count', result)
        self.assertIn('new_section_count', result)
        self.assertTrue(result['success'])
        self.assertEqual(result['old_section_count'], old_count)


class TestDiffEngine(unittest.TestCase):
    """Test Diff Engine - TDD Style"""
    
    def setUp(self):
        self.diff_engine = DiffEngine()
    
    def test_compare_content_no_changes(self):
        """Test diff with identical content"""
        content = "Line 1\nLine 2\nLine 3"
        result = self.diff_engine.compare_content("test", content, content)
        
        self.assertEqual(result['section_id'], "test")
        self.assertFalse(result['has_changes'])
        self.assertEqual(result['changes']['added_lines'], 0)
        self.assertEqual(result['changes']['removed_lines'], 0)
    
    def test_compare_content_with_changes(self):
        """Test diff with actual changes"""
        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nModified Line 2\nLine 3\nNew Line 4"
        
        result = self.diff_engine.compare_content("test", old_content, new_content)
        
        self.assertTrue(result['has_changes'])
        self.assertGreater(result['changes']['added_lines'], 0)
        self.assertGreater(result['change_percentage'], 0)
    
    def test_track_change(self):
        """Test change tracking functionality"""
        content1 = "Original content"
        content2 = "Modified content"
        
        # First call - no previous content
        result1 = self.diff_engine.track_change("section1", content1)
        self.assertTrue(result1['has_changes'])  # First time is always a change
        
        # Second call - compare with previous
        result2 = self.diff_engine.track_change("section1", content2)
        self.assertTrue(result2['has_changes'])
    
    def test_get_html_diff(self):
        """Test HTML diff generation"""
        old_content = "Line 1\nLine 2"
        new_content = "Line 1\nModified Line 2"
        
        html = self.diff_engine.get_html_diff("test", old_content, new_content)
        
        self.assertIn('<div class="diff-container">', html)
        self.assertIn('Changes in test', html)
        self.assertIn('diff-', html)  # Should contain diff CSS classes


class TestCoreAPIFixes(unittest.TestCase):
    """Test fixes for failing Core API tests - TDD Style"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        
        test_doc = self.test_dir / "test.adoc"
        test_doc.write_text("""= Test Document

== Section 1
Content for section 1.

=== Subsection 1.1
Subsection content.

== Section 2
Content for section 2.
""")
        
        self.server = MCPDocumentationServer(self.test_dir)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_get_sections_by_level(self):
        """Test get_sections() method exists and works"""
        # This should work - if not, we need to implement it
        result = self.server.get_sections_by_level(2)
        
        self.assertIsInstance(result, list)
        for section in result:
            self.assertIn('id', section)
            self.assertIn('title', section)
            self.assertIn('content', section)
    
    def test_update_section_content(self):
        """Test update_section_content() works with existing sections"""
        # Find an existing section
        sections = list(self.server.sections.keys())
        if sections:
            section_id = sections[0]
            original_content = self.server.sections[section_id].content
            new_content = "Updated test content"
            
            success = self.server.update_section_content(section_id, new_content)
            
            self.assertTrue(success)
            # Verify content was updated
            updated_section = self.server.sections[section_id]
            self.assertEqual(updated_section.content, new_content)


if __name__ == '__main__':
    # Run tests and show detailed output
    unittest.main(verbosity=2)
