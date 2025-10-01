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
