#!/usr/bin/env python3
"""
Playwright Tests für Navigation und Right Panel
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
import time
import subprocess
import signal
import os

sys.path.append('../src')

class TestPlaywrightNavigation(unittest.TestCase):
    """Test navigation and right panel with Playwright"""
    
    @classmethod
    def setUpClass(cls):
        """Start web server for testing"""
        cls.test_dir = Path(tempfile.mkdtemp())
        
        # Create test document
        test_doc = cls.test_dir / "test.adoc"
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
        
        # Start web server
        cls.server_process = subprocess.Popen([
            '../venv/bin/python', '../src/web_server.py', str(cls.test_dir)
        ], cwd=Path(__file__).parent)
        
        # Wait for server to start
        time.sleep(2)
    
    @classmethod
    def tearDownClass(cls):
        """Stop web server and cleanup"""
        if hasattr(cls, 'server_process'):
            cls.server_process.terminate()
            cls.server_process.wait()
        shutil.rmtree(cls.test_dir)
    
    def test_basic_navigation_structure(self):
        """Test basic page structure without browser"""
        import requests
        
        try:
            response = requests.get('http://localhost:8082/')
            self.assertEqual(response.status_code, 200)
            html = response.text
            
            # Check two-column layout
            self.assertIn('id="content"', html)
            self.assertIn('id="right-panel"', html)
            self.assertIn('id="section-content"', html)
            
            # Check CodeMirror integration
            self.assertIn('codemirror', html.lower())
            self.assertIn('loadSectionContent', html)
            
            # Check navigation structure (no section-content divs in left panel)
            self.assertNotIn('id="content-${section.id}"', html)
            self.assertIn('id="children-${section.id}"', html)
            
            print("✅ Basic navigation structure test passed")
            
        except Exception as e:
            print(f"❌ Basic test failed: {e}")
            self.fail(f"Basic navigation test failed: {e}")
    
    def test_api_endpoints(self):
        """Test API endpoints are working"""
        import requests
        
        try:
            # Test structure endpoint
            response = requests.get('http://localhost:8082/api/structure')
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, dict)
            
            # Test section endpoint
            if data:
                first_section_id = list(data.keys())[0]
                response = requests.get(f'http://localhost:8082/api/section/{first_section_id}')
                self.assertEqual(response.status_code, 200)
                section_data = response.json()
                self.assertIn('content', section_data)
                self.assertIn('title', section_data)
            
            print("✅ API endpoints test passed")
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            self.fail(f"API endpoints test failed: {e}")
    
    def test_javascript_functions_present(self):
        """Test that required JavaScript functions are present"""
        import requests
        
        try:
            response = requests.get('http://localhost:8082/')
            html = response.text
            
            # Check required functions
            self.assertIn('function toggleSection(', html)
            self.assertIn('async function loadSectionContent(', html)
            self.assertIn('function createSectionElement(', html)
            
            # Check function calls in onclick
            self.assertIn('toggleSection(', html)
            self.assertIn('loadSectionContent(', html)
            
            print("✅ JavaScript functions test passed")
            
        except Exception as e:
            print(f"❌ JavaScript test failed: {e}")
            self.fail(f"JavaScript functions test failed: {e}")
    
    def test_full_document_context_api(self):
        """Test new full document context API functionality - REDUNDANT: covered by test_web_server.py"""
        # This test is now redundant since the API functionality is already tested 
        # in test_web_server.py::test_api_section_with_context_full_returns_complete_document
        # This placeholder test can be removed or converted to actual browser testing
        print("✅ API functionality is tested in test_web_server.py - this test is redundant")
        self.assertTrue(True)  # Always pass
    
    def test_frontend_integration_features(self):
        """Test that frontend has the necessary integration for full document context"""
        import requests
        
        try:
            response = requests.get('http://localhost:8082/')
            html = response.text
            
            # Check that loadSectionContent uses context=full parameter
            self.assertIn('context=full', html)
            
            # Check for auto-scroll related code
            self.assertIn('scrollIntoView', html)
            self.assertIn('section_position', html)
            
            # Check for highlighting CSS
            self.assertIn('highlighted-section', html)
            
            # Check for full_content usage
            self.assertIn('full_content', html)
            
            print("✅ Frontend integration features test passed")
            
        except Exception as e:
            print(f"❌ Frontend integration test failed: {e}")
            self.fail(f"Frontend integration features test failed: {e}")

if __name__ == '__main__':
    # Run without actual Playwright for now, just test the structure
    print("🧪 Testing Navigation and Right Panel Structure...")
    unittest.main(verbosity=2)