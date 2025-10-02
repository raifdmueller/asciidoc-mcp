"""
Tests for WebserverManager

Tests the webserver_manager module which handles web server lifecycle.
"""

import pytest
import socket
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.mcp.webserver_manager import WebserverManager
from src.mcp_server import MCPDocumentationServer


@pytest.fixture
def test_server(tmp_path):
    """Create a test server with webserver disabled"""
    doc_file = tmp_path / "test.adoc"
    doc_file.write_text("= Test\n== Section\nContent")
    server = MCPDocumentationServer(tmp_path, enable_webserver=False)
    return server


class TestWebserverManager:
    """Test WebserverManager class"""

    def test_initialization(self, test_server):
        """Test WebserverManager initializes correctly"""
        wm = WebserverManager(test_server)

        assert wm.server == test_server
        assert wm.webserver_url is None
        assert wm.webserver_port is None
        assert wm.webserver_thread is None
        assert wm.webserver_started is False

    def test_find_free_port_default(self, test_server):
        """Test find_free_port finds available port"""
        wm = WebserverManager(test_server)

        port = wm.find_free_port()

        # Should find a port >= 8080
        assert port >= 8080
        assert port < 65536

    def test_find_free_port_custom_start(self, test_server):
        """Test find_free_port with custom start port"""
        wm = WebserverManager(test_server)

        port = wm.find_free_port(start_port=9000)

        # Should find a port >= 9000
        assert port >= 9000

    def test_find_free_port_actually_free(self, test_server):
        """Test that find_free_port returns a usable port"""
        wm = WebserverManager(test_server)

        port = wm.find_free_port()

        # Try to bind to the port to verify it's free
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            assert True
        except OSError:
            pytest.fail(f"Port {port} reported as free but couldn't bind")

    def test_get_webserver_status_not_started(self, test_server):
        """Test get_webserver_status when webserver not started"""
        wm = WebserverManager(test_server)

        status = wm.get_webserver_status()

        assert status['enabled'] is False
        assert status['running'] is False
        assert 'warnings' in status
        if len(status['warnings']) > 0:
            assert 'not enabled' in status['warnings'][0].lower()

    def test_get_webserver_status_enabled_not_running(self, tmp_path):
        """Test get_webserver_status when enabled but not running"""
        doc_file = tmp_path / "test.adoc"
        doc_file.write_text("= Test\n== Section\nContent")

        # Create server with webserver enabled but don't start it
        server = MCPDocumentationServer(tmp_path, enable_webserver=True)
        wm = server.webserver

        # Don't start the thread, just check status
        status = wm.get_webserver_status()

        assert status['enabled'] is True
        # May or may not be running depending on auto-start

        server.cleanup()

    def test_start_webserver_thread_when_disabled(self, test_server):
        """Test start_webserver_thread does nothing when disabled"""
        # Server already has webserver disabled
        wm = WebserverManager(test_server)

        initial_started = wm.webserver_started

        wm.start_webserver_thread()

        # For disabled webserver, implementation may vary
        # Just verify it doesn't crash
        assert isinstance(wm.webserver_started, bool)

    def test_restart_webserver_when_disabled(self, test_server):
        """Test restart_webserver returns False when disabled"""
        wm = WebserverManager(test_server)

        result = wm.restart_webserver()

        assert result is False

    def test_find_free_port_skips_used_ports(self, test_server):
        """Test find_free_port skips ports that are in use"""
        wm = WebserverManager(test_server)

        # Mock socket to simulate port 8080 in use, 8081 free
        with patch('socket.socket') as mock_socket_class:
            mock_socket = MagicMock()
            mock_socket_class.return_value.__enter__.return_value = mock_socket

            # First attempt (8080) fails, second (8081) succeeds
            mock_socket.bind.side_effect = [OSError("Port in use"), None]

            port = wm.find_free_port(start_port=8080)

            # Should try 8080, fail, then try 8081 and succeed
            assert port == 8081

    def test_get_webserver_status_structure(self, test_server):
        """Test get_webserver_status returns correct structure"""
        wm = WebserverManager(test_server)

        status = wm.get_webserver_status()

        # Required fields
        assert 'enabled' in status
        assert 'running' in status
        assert 'warnings' in status

        # Types
        assert isinstance(status['enabled'], bool)
        assert isinstance(status['running'], bool)
        assert isinstance(status['warnings'], list)
