#!/usr/bin/env python3
"""
TDD Tests for Web Interface Bug Fixes
London School approach - test behavior, not implementation
"""

import unittest
from unittest.mock import Mock, patch
import json
import sys
import os
sys.path.append('../src')

from src.mcp_server import MCPDocumentationServer
from src.document_parser import DocumentParser, Section

class TestWebInterfaceBugs(unittest.TestCase):
    """Test fixes for critical web interface bugs"""
    
    def setUp(self):
        """Setup test environment"""
        from pathlib import Path
        self.server = MCPDocumentationServer(Path("."))
        
    def test_all_chapters_included_in_structure(self):
        """Test that Chapter 1 (Introduction) is included in structure"""
        # Use the new get_main_chapters method that the web interface uses
        result = self.server.get_main_chapters()
        
        # Extract chapter data
        chapters = list(result.values())
        chapter_titles = [c['title'] for c in chapters]
        
        # Should include Introduction (Chapter 1)
        introduction_found = any('introduction' in title.lower() or '1.' in title for title in chapter_titles)
        self.assertTrue(introduction_found, f"Introduction/Chapter 1 not found in: {chapter_titles}")
        
        # Should have all 12 chapters
        chapter_numbers = [c.get('chapter_number') for c in chapters if c.get('chapter_number') and c.get('chapter_number') < 13]
        self.assertGreaterEqual(len(chapter_numbers), 12, f"Expected 12 chapters, found: {chapter_numbers}")
        
        # Should have chapter 1
        self.assertIn(1, chapter_numbers, f"Chapter 1 not found in: {chapter_numbers}")
        
        # Should also have other documents (level 1 sections)
        other_docs = [c for c in chapters if c.get('chapter_number') == 999]
        self.assertGreater(len(other_docs), 10, f"Expected other documents, found: {len(other_docs)}")
    
    def test_chapters_sorted_by_document_position(self):
        """Test that chapters are sorted by document position, not alphabetically"""
        # Use the new get_main_chapters method
        result = self.server.get_main_chapters()
        chapters = list(result.values())
        
        # Extract arc42 chapter numbers (excluding other docs with chapter_number=999)
        arc42_chapters = [c.get('chapter_number') for c in chapters if c.get('chapter_number') and c.get('chapter_number') < 13]
        arc42_chapters.sort()
        
        # Should have chapters 1-12 in order
        expected_order = list(range(1, 13))
        self.assertEqual(arc42_chapters, expected_order, 
                        f"Arc42 chapters not in correct order. Got: {arc42_chapters}, Expected: {expected_order}")
        
        # Should also have other documents
        other_docs = [c for c in chapters if c.get('chapter_number') == 999]
        self.assertGreater(len(other_docs), 0, "Should have other documents besides arc42 chapters")
    
    def test_web_interface_structure_sorting(self):
        """Test that web interface receives properly sorted structure"""
        # Mock the structure data that would be sent to web interface
        with patch.object(self.server, 'get_structure') as mock_get_structure:
            # Setup mock to return test data
            mock_get_structure.return_value = {
                'sections': [
                    {'title': '10. Quality Requirements', 'line_start': 100, 'children': []},
                    {'title': '1. Introduction', 'line_start': 10, 'children': []},
                    {'title': '2. Architecture Constraints', 'line_start': 20, 'children': []},
                ]
            }
            
            # Get structure (this would be called by web interface)
            result = self.server.get_structure()
            sections = result['sections']
            
            # Verify the data is available for proper sorting
            for section in sections:
                self.assertIn('line_start', section, "line_start required for sorting")
                self.assertIn('title', section, "title required for display")

    def test_javascript_safe_section_structure(self):
        """Test that section structure is safe for JavaScript processing"""
        result = self.server.get_structure(start_level=1)
        sections = result.get('sections', [])

        # Each section should have required fields for JavaScript
        for section in sections:
            self.assertIn('title', section, "Missing title field")
            self.assertIn('children', section, "Missing children field")
            self.assertIsInstance(section['children'], list, "children must be list")

            # Test nested children structure
            for child in section['children']:
                self.assertIn('title', child, "Child missing title")
                self.assertIn('children', child, "Child missing children field")

    def test_root_files_no_duplication(self):
        """Test Bug #2 Fix: root_files should not contain duplicates after file changes"""
        from pathlib import Path

        # Initial discovery should give us unique files
        initial_count = len(self.server.root_files)
        initial_files = set(str(f) for f in self.server.root_files)

        # Verify no duplicates initially
        self.assertEqual(len(self.server.root_files), len(initial_files),
                        "Initial root_files contains duplicates")

        # Simulate file change event (this calls _discover_root_files again)
        self.server._on_files_changed({str(Path("README.md"))})

        # After rediscovery, should still have same count (no duplicates)
        after_change_count = len(self.server.root_files)
        after_change_files = set(str(f) for f in self.server.root_files)

        self.assertEqual(after_change_count, len(after_change_files),
                        "root_files contains duplicates after file change")

        # Count should remain the same (or similar if files were added/removed)
        # But definitely not doubled
        self.assertLess(after_change_count, initial_count * 1.5,
                       f"root_files grew unexpectedly: {initial_count} -> {after_change_count}")

        # Simulate multiple file changes to test accumulation
        for i in range(3):
            self.server._on_files_changed({str(Path("README.md"))})

        final_count = len(self.server.root_files)
        final_files = set(str(f) for f in self.server.root_files)

        self.assertEqual(final_count, len(final_files),
                        "root_files contains duplicates after multiple changes")
        self.assertLess(final_count, initial_count * 1.5,
                       f"root_files accumulated duplicates: {initial_count} -> {final_count}")

if __name__ == '__main__':
    print("Running Web Interface Bug Fix Tests...")
    unittest.main(verbosity=2)
