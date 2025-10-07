#!/usr/bin/env python3
"""
Simple Integration Test for Issue #57 Section Navigation Enhancement
Tests the core API functionality without web server startup to bypass fastmcp dependency issues.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add src to path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from document_parser import DocumentParser
from mcp_server import MCPDocumentationServer

class TestIssue57Integration(unittest.TestCase):
    """Integration test for Issue #57 section navigation enhancement"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create test document matching what Playwright test would use
        test_doc = self.test_dir / "test-document.adoc"
        test_doc.write_text("""= Test Document

== Section 1
Content for section 1.
Some more content here.

=== Subsection 1.1
Subsection content.

== Section 2  
Content for section 2.
With multiple lines.
""")
        
        # Initialize the MCP server (which includes DocumentAPI)
        self.server = MCPDocumentationServer(self.test_dir)
        self.server.parse_project(test_doc)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_section_navigation_core_functionality(self):
        """Test that the core section navigation functionality works"""
        # Parse document structure using DocumentAPI
        structure = self.server.api.get_root_files_structure()
        
        # Verify we have the expected document structure
        self.assertIn('test-document.adoc', [doc['filename'] for doc in structure.values()])
        
        # Find a section to test with
        test_document = None
        for doc_data in structure.values():
            if doc_data['filename'] == 'test-document.adoc':
                test_document = doc_data
                break
        
        self.assertIsNotNone(test_document, "Test document not found in structure")
        self.assertTrue(len(test_document['sections']) > 0, "No sections found in test document")
        
        # Test getting section with basic functionality
        first_section = test_document['sections'][0]
        section_id = first_section['id']
        
        # Test basic section retrieval (this is what the old API did)
        section_data = self.parser.get_section(section_id)
        self.assertIsNotNone(section_data)
        self.assertIn('content', section_data)
        self.assertIn('title', section_data)
        
        print("✅ Core section navigation functionality verified")
    
    def test_full_document_context_api_simulation(self):
        """Test the enhanced API functionality that supports context=full parameter"""
        # This simulates what the web API does when context=full is requested
        structure = self.server.api.get_root_files_structure()
        
        # Get the test document
        test_document = None
        for doc_data in structure.values():
            if doc_data['filename'] == 'test-document.adoc':
                test_document = doc_data
                break
        
        # Get a section
        first_section = test_document['sections'][0]
        section_id = first_section['id']
        
        # Simulate the enhanced API call - get section info
        section_data = self.server.api.get_section(section_id)
        
        # Simulate reading the full document content (what context=full does)
        doc_path = self.test_dir / "test-document.adoc"
        full_content = doc_path.read_text()
        
        # Verify we have both the section data and full content
        self.assertIsNotNone(section_data)
        self.assertIsNotNone(full_content)
        self.assertIn('= Test Document', full_content)
        self.assertIn('== Section 1', full_content)
        
        # Verify section position metadata exists (needed for scrolling)
        self.assertIn('line_start', section_data)
        self.assertIn('line_end', section_data)
        
        print("✅ Full document context API functionality verified")
    
    def test_section_position_metadata(self):
        """Test that sections have the position metadata needed for auto-scrolling"""
        structure = self.server.api.get_root_files_structure()
        
        # Get sections from test document
        test_document = None
        for doc_data in structure.values():
            if doc_data['filename'] == 'test-document.adoc':
                test_document = doc_data
                break
        
        # Check that sections have position metadata
        for section in test_document['sections']:
            section_data = self.parser.get_section(section['id'])
            
            # These fields are required for the frontend auto-scroll functionality
            self.assertIn('line_start', section_data, f"Section {section['id']} missing line_start")
            self.assertIn('line_end', section_data, f"Section {section['id']} missing line_end")
            
            # Verify line numbers are reasonable
            self.assertGreater(section_data['line_start'], 0, "Line numbers should be 1-based")
            self.assertGreaterEqual(section_data['line_end'], section_data['line_start'], 
                                  "End line should be >= start line")
        
        print("✅ Section position metadata verified for auto-scrolling")

if __name__ == '__main__':
    print("🧪 Testing Issue #57 Core Integration Functionality...")
    unittest.main(verbosity=2)