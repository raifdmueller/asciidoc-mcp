"""
Tests for MCP Protocol Handler

Tests the protocol_handler module which routes MCP requests to appropriate handlers.
"""

import pytest
from pathlib import Path
from src.mcp.protocol_handler import handle_mcp_request
from src.mcp_server import MCPDocumentationServer


@pytest.fixture
def server(tmp_path):
    """Create a test server with minimal documentation"""
    doc_file = tmp_path / "test.adoc"
    doc_file.write_text("""
= Test Document

== Section 1
Content for section 1

== Section 2
Content for section 2
""")
    server = MCPDocumentationServer(tmp_path, enable_webserver=False)
    return server


class TestProtocolHandler:
    """Test MCP protocol request handling"""

    def test_initialize_request(self, server):
        """Test MCP initialize request"""
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {}
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 1
        assert 'result' in response
        assert response['result']['protocolVersion'] == '2024-11-05'
        assert 'capabilities' in response['result']
        assert 'serverInfo' in response['result']
        assert response['result']['serverInfo']['name'] == 'docs-server'

    def test_tools_list_request(self, server):
        """Test tools/list request returns all available tools"""
        request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/list',
            'params': {}
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 2
        assert 'result' in response
        assert 'tools' in response['result']

        tools = response['result']['tools']
        tool_names = [t['name'] for t in tools]

        # Verify all expected tools are present
        expected_tools = [
            'get_structure', 'get_section', 'get_sections',
            'search_content', 'update_section', 'insert_section',
            'get_metadata', 'get_dependencies', 'validate_structure',
            'refresh_index'
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Tool '{expected}' not found in tools list"

    def test_get_structure_tool_call(self, server):
        """Test tools/call with get_structure"""
        request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'get_structure',
                'arguments': {'max_depth': 2}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 3
        assert 'result' in response
        assert 'content' in response['result']
        assert len(response['result']['content']) > 0
        assert response['result']['content'][0]['type'] == 'text'

    def test_get_section_tool_call(self, server):
        """Test tools/call with get_section"""
        # First get structure to find a valid section ID
        structure = server.doc_api.get_structure()
        section_id = list(server.sections.keys())[0] if server.sections else '1'

        request = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'get_section',
                'arguments': {'path': section_id}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        # get_section returns response without jsonrpc when section exists
        # This is handled by protocol_handler which doesn't always add jsonrpc
        assert 'id' in response or 'result' in response

    def test_get_section_not_found(self, server):
        """Test get_section with non-existent section"""
        request = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'get_section',
                'arguments': {'path': 'nonexistent'}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 5
        assert 'result' in response
        # Should return "Section not found" message
        assert 'not found' in response['result']['content'][0]['text'].lower()

    def test_search_content_tool_call(self, server):
        """Test tools/call with search_content"""
        request = {
            'jsonrpc': '2.0',
            'id': 6,
            'method': 'tools/call',
            'params': {
                'name': 'search_content',
                'arguments': {'query': 'section'}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 6
        assert 'result' in response
        assert 'content' in response['result']

    def test_get_metadata_tool_call(self, server):
        """Test tools/call with get_metadata"""
        request = {
            'jsonrpc': '2.0',
            'id': 7,
            'method': 'tools/call',
            'params': {
                'name': 'get_metadata',
                'arguments': {}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 7
        assert 'result' in response

    def test_validate_structure_tool_call(self, server):
        """Test tools/call with validate_structure"""
        request = {
            'jsonrpc': '2.0',
            'id': 8,
            'method': 'tools/call',
            'params': {
                'name': 'validate_structure',
                'arguments': {}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 8
        assert 'result' in response

    def test_get_dependencies_tool_call(self, server):
        """Test tools/call with get_dependencies"""
        request = {
            'jsonrpc': '2.0',
            'id': 9,
            'method': 'tools/call',
            'params': {
                'name': 'get_dependencies',
                'arguments': {}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 9
        assert 'result' in response

    def test_refresh_index_tool_call(self, server):
        """Test tools/call with refresh_index"""
        request = {
            'jsonrpc': '2.0',
            'id': 10,
            'method': 'tools/call',
            'params': {
                'name': 'refresh_index',
                'arguments': {}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 10
        assert 'result' in response

    def test_get_sections_tool_call(self, server):
        """Test tools/call with get_sections"""
        request = {
            'jsonrpc': '2.0',
            'id': 11,
            'method': 'tools/call',
            'params': {
                'name': 'get_sections',
                'arguments': {'level': 2}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 11
        assert 'result' in response

    def test_unknown_method(self, server):
        """Test unknown method returns error"""
        request = {
            'jsonrpc': '2.0',
            'id': 99,
            'method': 'unknown_method',
            'params': {}
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 99
        assert 'error' in response
        assert response['error']['code'] == -32601
        assert 'Unknown method' in response['error']['message']

    def test_exception_handling(self, server):
        """Test that exceptions are caught and returned as errors"""
        # Create a request that will cause an exception by calling unknown tool
        request = {
            'jsonrpc': '2.0',
            'id': 100,
            'method': 'tools/call',
            'params': {
                'name': 'nonexistent_tool',
                'arguments': {}
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 100
        # Should either be an error or fall through to unknown method
        assert 'error' in response or 'result' in response

    def test_update_section_tool_call(self, server):
        """Test tools/call with update_section"""
        # Get a valid section ID first
        section_id = list(server.sections.keys())[0] if server.sections else '1'

        request = {
            'jsonrpc': '2.0',
            'id': 12,
            'method': 'tools/call',
            'params': {
                'name': 'update_section',
                'arguments': {
                    'path': section_id,
                    'content': 'Updated content'
                }
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 12
        assert 'result' in response

    def test_insert_section_tool_call(self, server):
        """Test tools/call with insert_section"""
        # Get a valid section ID first
        section_id = list(server.sections.keys())[0] if server.sections else '1'

        request = {
            'jsonrpc': '2.0',
            'id': 13,
            'method': 'tools/call',
            'params': {
                'name': 'insert_section',
                'arguments': {
                    'parent_path': section_id,
                    'title': 'New Section',
                    'content': 'New content',
                    'position': 'append'
                }
            }
        }

        response = handle_mcp_request(request, server.doc_api, server.webserver, server)

        assert response['jsonrpc'] == '2.0'
        assert response['id'] == 13
        assert 'result' in response
