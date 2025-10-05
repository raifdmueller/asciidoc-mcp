"""
Webserver Manager Module

Handles web server lifecycle management, port finding, and browser opening.
"""

from typing import Dict, Any
import sys
import socket
import threading
import webbrowser
import uvicorn


class WebserverManager:
    """Manages web server lifecycle and configuration"""

    def __init__(self, server: 'MCPDocumentationServer'):
        """
        Initialize WebserverManager with reference to server instance

        Args:
            server: MCPDocumentationServer instance for accessing shared state
        """
        self.server = server
        self.webserver_url = None
        self.webserver_port = None
        self.webserver_thread = None
        self.webserver_started = False

    def find_free_port(self, start_port: int = 8080) -> int:
        """Find first available port"""
        for port in range(start_port, start_port + 20):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except OSError:
                continue
        return start_port

    def start_webserver_thread(self):
        """Start webserver in background thread (like Serena)"""
        # Find free port
        self.webserver_port = self.find_free_port()
        self.webserver_url = f"http://localhost:{self.webserver_port}"

        # Start uvicorn in daemon thread
        def run_server():
            from src import web_server
            # Set the global doc_server
            web_server.doc_server = self.server

            # Configure uvicorn (disable logging config for MCP compatibility)
            config = uvicorn.Config(
                web_server.app,
                host="127.0.0.1",
                port=self.webserver_port,
                log_config=None,  # Disable default logging (incompatible with MCP stdio)
                access_log=False
            )
            server = uvicorn.Server(config)
            server.run()

        self.webserver_thread = threading.Thread(target=run_server, daemon=True)
        self.webserver_thread.start()

        # Don't wait - let it start in background
        print(f"✅ Webserver starting at {self.webserver_url}", file=sys.stderr)

        # Open browser after short delay (non-blocking)
        def open_browser_delayed():
            import time
            time.sleep(1.5)
            try:
                webbrowser.open(self.webserver_url)
                print(f"🚀 Browser opened", file=sys.stderr)
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}", file=sys.stderr)

        browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
        browser_thread.start()

        self.webserver_started = True

    def get_webserver_status(self) -> Dict[str, Any]:
        """Get current webserver status"""
        if not self.server.enable_webserver:
            return {
                'enabled': False,
                'running': False,
                'port': None,
                'url': None,
                'browser_opened': False,
                'warnings': []
            }

        return {
            'enabled': True,
            'running': self.webserver_url is not None,
            'port': self.webserver_port,
            'url': self.webserver_url,
            'browser_opened': self.webserver_url is not None,  # Assume success if URL exists
            'warnings': []
        }

    def restart_webserver(self) -> bool:
        """Restart webserver on potentially different port"""
        if not self.server.enable_webserver:
            return False

        try:
            # Note: Current implementation doesn't support graceful shutdown
            # This would need to be implemented if restart is needed
            print("Webserver restart not fully implemented - requires graceful shutdown", file=sys.stderr)
            return False

        except Exception as e:
            print(f"Error restarting webserver: {e}", file=sys.stderr)
            return False
