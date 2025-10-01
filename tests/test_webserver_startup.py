#!/usr/bin/env python3
"""
Test for webserver startup bug
Tests that webserver can start successfully when triggered by MCP initialize
"""

import unittest
import json
import time
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mcp_server import MCPDocumentationServer, handle_mcp_request


class TestWebserverStartup(unittest.TestCase):
    """Test webserver startup functionality"""

    def setUp(self):
        """Setup test environment"""
        self.project_root = Path(".")

    def test_webserver_starts_on_initialize(self):
        """Test that webserver starts when MCP initialize is called"""
        # Create server instance
        server = MCPDocumentationServer(self.project_root, enable_webserver=True)

        # Verify webserver hasn't started yet
        self.assertFalse(server.webserver_started)
        self.assertIsNone(server.webserver_url)

        # Send initialize request (like MCP client would)
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {}
        }

        # Handle the request
        response = handle_mcp_request(request, server)

        # Verify response is successful
        self.assertEqual(response['jsonrpc'], '2.0')
        self.assertEqual(response['id'], 1)
        self.assertIn('result', response)

        # Verify webserver was started
        self.assertTrue(server.webserver_started)
        self.assertIsNotNone(server.webserver_url)
        self.assertIsNotNone(server.webserver_port)

        # Give webserver a moment to start
        time.sleep(2)

        # Verify webserver is accessible
        import urllib.request
        try:
            with urllib.request.urlopen(server.webserver_url, timeout=5) as response:
                self.assertEqual(response.status, 200)
                html = response.read().decode('utf-8')
                self.assertIn('MCP Documentation Server', html)
        except Exception as e:
            self.fail(f"Webserver not accessible at {server.webserver_url}: {e}")

        # Cleanup
        server.cleanup()

    def test_webserver_disabled_flag(self):
        """Test that webserver doesn't start when disabled"""
        server = MCPDocumentationServer(self.project_root, enable_webserver=False)

        # Send initialize request
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {}
        }

        handle_mcp_request(request, server)

        # Verify webserver was NOT started
        self.assertFalse(server.webserver_started)
        self.assertIsNone(server.webserver_url)

        # Cleanup
        server.cleanup()

    def test_server_initializes_without_crash(self):
        """Test that server can initialize without crashing"""
        try:
            server = MCPDocumentationServer(self.project_root)
            self.assertIsNotNone(server)
            self.assertGreater(len(server.sections), 0)
            server.cleanup()
        except Exception as e:
            self.fail(f"Server initialization failed: {e}")


if __name__ == '__main__':
    print("Running Webserver Startup Tests...")
    unittest.main(verbosity=2)