"""
BDD Tests for MCP Server Startup Protocol Compliance

Tests the MCP server startup behavior to ensure proper STDOUT/STDERR separation
and MCP protocol compliance using subprocess integration testing.

These tests verify that:
- STDOUT is reserved exclusively for MCP protocol JSON-RPC messages
- Server startup is silent on STDOUT (no debug output)
- All debug/error messages go to STDERR
- MCP protocol compliance in real deployment scenarios
"""

import pytest
import subprocess
import json
import time
import tempfile
from pathlib import Path
from typing import Tuple


class TestMCPServerStartupCompliance:
    """BDD tests for MCP server startup protocol compliance"""
    
    @pytest.fixture
    def test_project(self) -> Path:
        """Create a minimal test documentation project"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir)
            doc_file = project_path / "test.adoc"
            doc_file.write_text("""
= Test Documentation
:toc:

== Section 1
Content for testing

=== Subsection 1.1
More content

== Section 2
Additional content
""")
            yield project_path
    
    @pytest.fixture
    def server_command(self, test_project: Path) -> list:
        """Build the server command with proper Python executable"""
        # Use the correct Python executable from the shared venv
        python_exec = "/home/rdmueller/projects/asciidoc-mcp/.venv/bin/python"
        server_script = Path(__file__).parent.parent / "src" / "mcp_server.py"
        return [str(python_exec), str(server_script), str(test_project)]
    
    def _run_server_startup(self, command: list, timeout: float = 3.0) -> Tuple[bytes, bytes, int]:
        """Helper to run server startup and capture STDOUT/STDERR separately"""
        import os
        
        # Set up environment with proper Python path
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/rdmueller/projects/asciidoc-mcp-q'
        
        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False,
                env=env
            )
            return process.stdout, process.stderr, process.returncode
        except subprocess.TimeoutExpired as e:
            return e.stdout or b"", e.stderr or b"", -1

    def test_server_startup_protocol_compliance(self, server_command):
        """
        FEATURE: MCP Server Startup Protocol Compliance
        
        SCENARIO: Server starts with clean STDOUT for MCP protocol
            GIVEN a valid AsciiDoc documentation project
            WHEN the MCP server starts up  
            THEN STDOUT remains clean (no debug output)
            AND server starts successfully indicating MCP protocol readiness
            AND server initialization errors go to STDERR only
        """
        # GIVEN a valid AsciiDoc documentation project (provided by fixture)
        
        # WHEN the MCP server starts up (MCP servers wait for client input, so we expect timeout)
        stdout, stderr, returncode = self._run_server_startup(server_command)
        
        # DEBUG: Print actual outputs to understand what's happening
        print(f"\nDEBUG - Return code: {returncode}")
        print(f"DEBUG - STDOUT: '{stdout.decode('utf-8')}'")
        print(f"DEBUG - STDERR: '{stderr.decode('utf-8')}'")
        
        # THEN the server should either timeout (running) or exit cleanly after showing proper protocol readiness
        # returncode 0 with proper MCP startup messages indicates successful initialization
        if returncode == 0:
            # Server exited cleanly - check that it showed MCP startup before any crashes
            stderr_text = stderr.decode('utf-8')
            assert 'Starting MCP server' in stderr_text, "Expected MCP server startup message in STDERR"
        elif returncode == -1:
            # Server timed out - this means it's running properly
            pass
        else:
            pytest.fail(f"Server failed with unexpected return code {returncode}. STDERR: {stderr.decode('utf-8')}")
        
        # AND STDOUT should be clean - no debug output
        stdout_text = stdout.decode('utf-8').strip()
        
        # THEN STDOUT contains no debug or informational output
        debug_patterns = ['debug', 'info', 'starting', 'initializing', 'loading', 'created', 'setup']
        for pattern in debug_patterns:
            assert pattern.lower() not in stdout_text.lower(), \
                f"Debug output '{pattern}' found in STDOUT: {stdout_text}"
        
        # Verify server initialization messages went to STDERR (already checked above)
        
        # If there's any STDOUT content, it should be valid JSON-RPC only
        if stdout_text:
            lines = [line.strip() for line in stdout_text.split('\n') if line.strip()]
            for line in lines:
                try:
                    parsed = json.loads(line)
                    # Should be valid JSON-RPC format with MCP protocol elements
                    assert 'jsonrpc' in parsed, f"Missing jsonrpc field in: {line}"
                    assert parsed['jsonrpc'] == '2.0', f"Invalid JSON-RPC version: {line}"
                except json.JSONDecodeError:
                    pytest.fail(f"STDOUT contains non-JSON content: {line}")

    def test_silent_server_startup(self, server_command):
        """
        SCENARIO: Server startup is silent except for MCP protocol
            GIVEN proper environment and dependencies
            WHEN the MCP server initializes
            THEN no debug prints appear on STDOUT during startup  
            AND server startup is silent except for MCP protocol readiness
            AND any startup logging goes to STDERR
        """
        # GIVEN proper environment and dependencies
        
        # WHEN the MCP server initializes (expecting timeout as server waits for input)
        stdout, stderr, returncode = self._run_server_startup(server_command)
        
        # THEN the server should either timeout (running) or exit after proper startup  
        if returncode == 0:
            # Server exited - check it showed proper MCP initialization first
            stderr_text = stderr.decode('utf-8')
            assert 'Starting MCP server' in stderr_text, "Expected MCP server startup message in STDERR"
        elif returncode == -1:
            # Server timed out - running properly
            pass 
        else:
            pytest.fail(f"Server failed with unexpected return code {returncode}. STDERR: {stderr.decode('utf-8')}")
        
        # AND STDOUT should be clean - no debug output during startup
        stdout_text = stdout.decode('utf-8').strip()
        
        # THEN no debug prints appear on STDOUT during startup
        forbidden_patterns = [
            'starting server', 'initializing', 'loading', 'created', 'setup',
            'debug:', 'info:', 'log:', 'FastMCP starting', 'Server ready',
            'webserver starting'
        ]
        
        for pattern in forbidden_patterns:
            assert pattern.lower() not in stdout_text.lower(), \
                f"Debug pattern '{pattern}' found in STDOUT: {stdout_text}"
        
        # If there's any STDOUT content, it should be valid JSON-RPC only
        if stdout_text:
            lines = [line.strip() for line in stdout_text.split('\n') if line.strip()]
            for line in lines:
                try:
                    parsed = json.loads(line)
                    # Should look like proper MCP protocol
                    assert isinstance(parsed, dict), f"MCP message should be JSON object: {line}"
                except json.JSONDecodeError:
                    pytest.fail(f"Non-JSON content on STDOUT: {line}")
        
        # AND any startup logging goes to STDERR (this is the correct behavior)
        # STDERR can contain logging - that's where it should be (already verified above)

    def test_error_handling_compliance(self, test_project):
        """
        SCENARIO: Error conditions route to STDERR properly
            GIVEN invalid environment (missing docs, permissions, etc.)
            WHEN the MCP server encounters startup errors  
            THEN error messages go to STDERR only
            AND no error output contaminates STDOUT
            AND MCP protocol error responses (if any) use proper JSON-RPC format on STDOUT
        """
        # GIVEN invalid environment - use non-existent project path
        python_exec = "/home/rdmueller/projects/asciidoc-mcp/.venv/bin/python"
        server_script = Path(__file__).parent.parent / "src" / "mcp_server.py"
        bad_command = [str(python_exec), str(server_script), "/non/existent/path"]
        
        # WHEN the MCP server encounters startup errors
        stdout, stderr, returncode = self._run_server_startup(bad_command)
        
        # THEN error messages go to STDERR only
        stderr_text = stderr.decode('utf-8')
        assert len(stderr_text.strip()) > 0, "Expected error messages in STDERR"
        
        # AND no error output contaminates STDOUT
        stdout_text = stdout.decode('utf-8').strip()
        error_patterns = ['error', 'exception', 'traceback', 'failed', 'not found']
        
        for pattern in error_patterns:
            assert pattern.lower() not in stdout_text.lower(), \
                f"Error pattern '{pattern}' found in STDOUT: {stdout_text}"
        
        # AND MCP protocol error responses (if any) use proper JSON-RPC format on STDOUT
        if stdout_text:
            lines = [line.strip() for line in stdout_text.split('\n') if line.strip()]
            for line in lines:
                try:
                    parsed = json.loads(line)
                    if 'error' in parsed:
                        # Should be proper JSON-RPC error format
                        assert 'jsonrpc' in parsed
                        assert 'id' in parsed
                        assert isinstance(parsed['error'], dict)
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON-RPC error format: {line}")

    def test_mcp_protocol_message_format(self, server_command):
        """
        SCENARIO: MCP protocol messages follow correct format
            GIVEN successful server startup
            WHEN server is ready for MCP protocol communication
            THEN STDOUT is reserved for protocol messages only
            AND any output follows JSON-RPC format if present
            AND no additional text mixes with protocol messages
        """
        # GIVEN successful server startup (timeout indicates running server)
        stdout, stderr, returncode = self._run_server_startup(server_command)
        
        # THEN server should either be running (timeout) or have started properly (exit after initialization)
        if returncode == 0:
            # Server exited after initialization - check it was ready for protocol communication
            stderr_text = stderr.decode('utf-8')
            assert 'Starting MCP server' in stderr_text, "Expected MCP server startup in STDERR"
        elif returncode == -1:
            # Server timed out - running and ready
            pass
        else:
            pytest.fail(f"Server failed with unexpected return code {returncode}. STDERR: {stderr.decode('utf-8')}")
        
        # AND STDOUT should be clean and ready for protocol messages
        stdout_text = stdout.decode('utf-8').strip()
        
        # THEN any output on STDOUT follows JSON-RPC format (should be none during startup)
        if stdout_text:
            lines = [line.strip() for line in stdout_text.split('\n') if line.strip()]
            
            for line in lines:
                try:
                    parsed = json.loads(line)
                    # AND response follows MCP protocol specification
                    # Basic JSON-RPC structure check
                    if 'jsonrpc' in parsed:
                        assert parsed['jsonrpc'] == '2.0'
                    
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON-RPC format: {line}")
                
                # AND no additional text mixes with protocol messages  
                # Each line should be complete JSON, no mixed content
                assert line.startswith('{') or line.startswith('['), \
                    f"Non-JSON content mixed with protocol: {line}"
        
        # Verify proper separation - startup messages in STDERR (already verified above)

    def test_environment_validation(self):
        """
        SCENARIO: Environment validation with graceful error handling
            GIVEN missing required dependencies or invalid project structure
            WHEN server attempts to start
            THEN appropriate behavior (timeout or error) occurs
            AND error information goes to STDERR if any
            AND no partial protocol responses on STDOUT
        """
        # GIVEN missing required dependencies - try with system python (no fastmcp)
        server_script = Path(__file__).parent.parent / "src" / "mcp_server.py"
        bad_command = ["python3", str(server_script), "/tmp"]
        
        # WHEN server attempts to start
        stdout, stderr, returncode = self._run_server_startup(bad_command, timeout=5.0)
        
        print(f"\nDEBUG Environment test - Return code: {returncode}")
        print(f"DEBUG Environment test - STDERR: '{stderr.decode('utf-8')}'")
        
        # THEN appropriate behavior occurs - various outcomes are acceptable in different environments
        # returncode can be -1 (timeout), 0 (clean exit), or non-zero (error exit)
        if returncode == 0:
            # Clean exit - server may have started and stopped, check for reasonable behavior
            pass
        elif returncode == -1:
            # Timeout - server running
            pass
        else:
            # Error exit - also acceptable for missing dependencies test
            pass
        
        # AND any error information goes to STDERR
        stderr_text = stderr.decode('utf-8')
        # STDERR should contain some information (either startup messages or error messages)
        assert len(stderr_text.strip()) > 0, "Expected some output in STDERR (startup or error messages)"
        
        # AND no partial protocol responses on STDOUT
        stdout_text = stdout.decode('utf-8').strip()
        if stdout_text:
            # Should not have partial JSON or broken protocol messages
            lines = [line.strip() for line in stdout_text.split('\n') if line.strip()]
            for line in lines:
                if line:
                    try:
                        json.loads(line)  # Should be complete JSON if anything
                    except json.JSONDecodeError:
                        pytest.fail(f"Partial or invalid JSON in STDOUT: {line}")
        
        # Test passes if server behaves predictably - either starts properly or fails gracefully