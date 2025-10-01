#!/usr/bin/env python3
"""
TDD Tests for Right Panel with CodeMirror Integration
London School approach - test behavior, not implementation
"""

import unittest
from unittest.mock import Mock, patch
import json
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.append('../src')

from src.mcp_server import MCPDocumentationServer
from src.web_server import app, init_server
from fastapi.testclient import TestClient

class TestRightPanelCodeMirror(unittest.TestCase):
    """Test right panel functionality with CodeMirror"""
    
    def setUp(self):
        """Setup test environment with temporary docs"""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test document with sections
        test_doc = self.test_dir / "test.adoc"
        test_doc.write_text("""= Test Document

== Section 1
Content for section 1.
Some more content here.

== Section 2  
Content for section 2.
With multiple lines.
""")
        
        # Initialize server properly
        init_server(self.test_dir)
        self.client = TestClient(app)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_api_get_section_content_endpoint(self):
        """Test API endpoint for getting section content"""
        response = self.client.get("/api/section/test-document.section-1")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should return section content
        self.assertIn('content', data)
        self.assertIn('title', data)
        self.assertIn('id', data)
        
        # Content should include the section text
        self.assertIn('Content for section 1', data['content'])
        self.assertEqual(data['title'], 'Section 1')
        self.assertEqual(data['id'], 'test-document.section-1')
    
    def test_web_interface_has_right_panel_container(self):
        """Test that web interface HTML includes right panel container"""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        html = response.text
        
        # Should have right panel container
        self.assertIn('id="right-panel"', html)
        self.assertIn('id="section-content"', html)
        
        # Should include CodeMirror CSS and JS
        self.assertIn('codemirror', html.lower())
        self.assertIn('mode/diff', html.lower())
    
    def test_web_interface_section_click_loads_content(self):
        """Test that clicking section loads content in right panel"""
        response = self.client.get("/")
        html = response.text
        
        # Should have JavaScript function for section clicks
        self.assertIn('loadSectionContent', html)
        self.assertIn('onclick=', html)
        
        # Should have CodeMirror initialization
        self.assertIn('CodeMirror', html)
    
    def test_api_section_not_found_returns_404(self):
        """Test API returns 404 for non-existent sections"""
        response = self.client.get("/api/section/nonexistent.section")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('detail', data)

if __name__ == '__main__':
    unittest.main()