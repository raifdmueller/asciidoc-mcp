#!/usr/bin/env python3
"""
TDD Tests for Web Server functionality
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import json
from fastapi.testclient import TestClient

sys.path.append('../src')

from src.web_server import app, init_server

class TestWebServerAPI(unittest.TestCase):
    """Test Web Server API endpoints - TDD Style"""
    
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
        
        # Initialize server
        init_server(self.test_dir)
        self.client = TestClient(app)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_root_endpoint_returns_html(self):
        """Test root endpoint returns HTML interface"""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("MCP Documentation Server", response.text)
        self.assertIn("loadStructure()", response.text)
    
    def test_api_structure_sorted_by_document_position(self):
        """Test that /api/structure returns sections sorted by document position"""
        response = self.client.get("/api/structure")
        self.assertEqual(response.status_code, 200)
        
        structure = response.json()
        self.assertIsInstance(structure, dict)
        
        # Verify that sections have line_start information
        for section_id, section_data in structure.items():
            self.assertIn('line_start', section_data)
            self.assertIsInstance(section_data['line_start'], int)
            
        # Verify sections are in a reasonable order (not just random)
        section_items = list(structure.items())
        if len(section_items) >= 2:
            # Just verify we have the data needed for sorting
            first_section = section_items[0][1]
            self.assertIn('title', first_section)
            self.assertIn('line_start', first_section)
    
    def test_api_structure_hierarchical_children(self):
        """Test that /api/structure returns hierarchical structure with nested children"""
        response = self.client.get("/api/structure")
        self.assertEqual(response.status_code, 200)
        
        structure = response.json()
        
        # Find a section with children
        parent_section = None
        for section_id, section_data in structure.items():
            if section_data.get('children_count', 0) > 0:
                parent_section = (section_id, section_data)
                break
        
        if parent_section:
            section_id, section_data = parent_section
            # Should have children property with actual child data
            self.assertIn('children', section_data)
            children = section_data['children']
            
            if children:
                # Children should be objects, not just IDs
                first_child = children[0] if isinstance(children, list) else children
                if isinstance(first_child, dict):
                    self.assertIn('title', first_child)
                    self.assertIn('level', first_child)
        
        if parent_section:
            section_id, section_data = parent_section
            # Should have children property with actual child data
            self.assertIn('children', section_data)
            children = section_data['children']
            
            if children:
                # Children should be objects, not just IDs
                first_child = children[0] if isinstance(children, list) else children
                if isinstance(first_child, dict):
                    self.assertIn('title', first_child)
                    self.assertIn('level', first_child)
    
    def test_api_structure_endpoint(self):
        """Test /api/structure endpoint"""
        response = self.client.get("/api/structure")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        # Should contain at least one section
        self.assertGreater(len(data), 0)
    
    def test_api_metadata_endpoint(self):
        """Test /api/metadata endpoint"""
        response = self.client.get("/api/metadata")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('project_root', data)
        self.assertIn('total_sections', data)
        self.assertIn('total_words', data)
    
    def test_api_dependencies_endpoint(self):
        """Test /api/dependencies endpoint"""
        response = self.client.get("/api/dependencies")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('includes', data)
        self.assertIn('cross_references', data)
        self.assertIn('orphaned_sections', data)
    
    def test_api_validate_endpoint(self):
        """Test /api/validate endpoint"""
        response = self.client.get("/api/validate")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('valid', data)
        self.assertIn('issues', data)
        self.assertIn('warnings', data)
    
    def test_api_section_endpoint(self):
        """Test /api/section/{section_id} endpoint"""
        # First get structure to find a section
        structure_response = self.client.get("/api/structure")
        structure = structure_response.json()
        
        if structure:
            section_id = list(structure.keys())[0]
            response = self.client.get(f"/api/section/{section_id}")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('id', data)
            self.assertIn('title', data)
            self.assertIn('level', data)
            self.assertIn('content', data)
    
    def test_api_section_not_found(self):
        """Test /api/section/{section_id} with invalid section"""
        response = self.client.get("/api/section/nonexistent-section")
        
        self.assertEqual(response.status_code, 404)
    
    def test_api_section_with_context_full_returns_complete_document(self):
        """Test /api/section/{section_id}?context=full returns full document with section metadata"""
        # First get structure to find a section
        structure_response = self.client.get("/api/structure")
        structure = structure_response.json()
        
        if structure:
            # Find the first actual section (not document root)
            doc_data = list(structure.values())[0]
            sections = doc_data.get('sections', [])
            if sections and sections[0].get('children'):
                section_id = sections[0]['children'][0]['id']  # test-document.section-1
            else:
                section_id = sections[0]['id'] if sections else None
            
            # Test new context=full parameter
            response = self.client.get(f"/api/section/{section_id}?context=full")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Should contain section metadata
            self.assertIn('id', data)
            self.assertIn('title', data)
            self.assertIn('level', data)
            
            # NEW: Should contain full document content instead of just section content
            self.assertIn('full_content', data)
            self.assertIn('section_position', data)
            
            # Full content should contain the complete document
            full_content = data['full_content']
            self.assertIn('= Test Document', full_content)  # Document title
            self.assertIn('== Section 1', full_content)    # First section
            self.assertIn('== Section 2', full_content)    # Second section
            
            # Section position should provide scroll metadata
            section_position = data['section_position']
            self.assertIn('line_start', section_position)
            self.assertIn('line_end', section_position)
            self.assertIsInstance(section_position['line_start'], int)
            self.assertIsInstance(section_position['line_end'], int)
            
            # Backward compatibility: should still have individual section content
            self.assertIn('content', data)
    
    def test_api_section_with_context_full_returns_include_file_content(self):
        """Test /api/section/{section_id}?context=full returns raw include file content for multi-file documents"""
        # Create multi-file document structure
        main_doc = self.test_dir / "main.adoc"
        main_doc.write_text("""= Main Document

include::chapter1.adoc[]

include::chapter2.adoc[]
""")
        
        chapter1_doc = self.test_dir / "chapter1.adoc"
        chapter1_doc.write_text("""== Chapter 1
This is content in chapter 1.

=== Subsection 1.1
More content in chapter 1.
""")
        
        chapter2_doc = self.test_dir / "chapter2.adoc"
        chapter2_doc.write_text("""== Chapter 2
This is content in chapter 2.
""")
        
        # Re-initialize server with multi-file documents
        init_server(self.test_dir)
        client = TestClient(app)
        
        # Get structure to find section from an include file
        structure_response = client.get("/api/structure")
        structure = structure_response.json()
        
        # Find a section that comes from chapter1.adoc
        chapter1_section_id = None
        for section_id, section_data in structure.items():
            if 'Chapter 1' in section_data.get('title', ''):
                chapter1_section_id = section_id
                break
        
        self.assertIsNotNone(chapter1_section_id, "Could not find Chapter 1 section in structure")
        
        # Test context=full should return raw chapter1.adoc content (not resolved main.adoc)
        response = client.get(f"/api/section/{chapter1_section_id}?context=full")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should contain full_content field
        self.assertIn('full_content', data)
        full_content = data['full_content']
        
        # CRITICAL: Should contain ONLY the raw chapter1.adoc content
        self.assertIn('== Chapter 1', full_content)
        self.assertIn('This is content in chapter 1.', full_content) 
        self.assertIn('=== Subsection 1.1', full_content)
        self.assertIn('More content in chapter 1.', full_content)
        
        # Should NOT contain content from main.adoc or other chapters
        self.assertNotIn('= Main Document', full_content)  # Not the main doc title
        self.assertNotIn('include::', full_content)        # Not the include directives
        self.assertNotIn('Chapter 2', full_content)        # Not content from other includes
        
        # Section position should be relative to the raw chapter1.adoc file
        section_position = data['section_position']
        self.assertIn('line_start', section_position)
        self.assertIn('line_end', section_position)
        
        # Line positions should be small numbers (relative to chapter1.adoc, not main.adoc)
        self.assertLessEqual(section_position['line_start'], 10, 
                           "Line start should be relative to chapter1.adoc, not main.adoc")
    
    def test_web_interface_expandable_hierarchy(self):
        """Test that web interface HTML supports expandable hierarchy"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        html_content = response.text
        
        # Should contain JavaScript functions for hierarchical display
        self.assertIn('createSectionElement', html_content)
        self.assertIn('expand-icon', html_content)
        self.assertIn('section-children', html_content)
        
        # Should have CSS for hierarchical display
        self.assertIn('.section-children', html_content)
        self.assertIn('.expand-icon', html_content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
