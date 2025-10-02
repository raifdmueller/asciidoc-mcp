"""
MCP Protocol Handler Module

Handles MCP protocol request routing and tool dispatch.
"""

from typing import Dict, Any
import json
from src.mcp.document_api import DocumentAPI
from src.mcp.webserver_manager import WebserverManager


def handle_mcp_request(request: Dict[str, Any], doc_api: DocumentAPI, webserver: WebserverManager, server: 'MCPDocumentationServer') -> Dict[str, Any]:
    """Handle MCP protocol requests"""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')

    try:
        if method == 'initialize':
            # Start webserver on first initialize (after MCP is ready)
            if server.enable_webserver and not webserver.webserver_started:
                webserver.start_webserver_thread()

            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {
                        'tools': {}
                    },
                    'serverInfo': {
                        'name': 'docs-server',
                        'version': '1.0.0'
                    }
                }
            }

        elif method == 'tools/list':
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': {
                    'tools': [
                    {
                        'name': 'get_structure',
                        'description': 'Get document structure/table of contents',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'max_depth': {'type': 'integer', 'default': 3}
                            }
                        }
                    },
                    {
                        'name': 'get_section',
                        'description': 'Get specific section content',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'path': {'type': 'string'}
                            },
                            'required': ['path']
                        }
                    },
                    {
                        'name': 'get_sections',
                        'description': 'Get all sections at specific level',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'level': {'type': 'integer'}
                            },
                            'required': ['level']
                        }
                    },
                    {
                        'name': 'search_content',
                        'description': 'Search for content in documentation',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'query': {'type': 'string'}
                            },
                            'required': ['query']
                        }
                    },
                    {
                        'name': 'update_section',
                        'description': 'Update section content',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'path': {'type': 'string'},
                                'content': {'type': 'string'}
                            },
                            'required': ['path', 'content']
                        }
                    },
                    {
                        'name': 'insert_section',
                        'description': 'Insert new section',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'parent_path': {'type': 'string'},
                                'title': {'type': 'string'},
                                'content': {'type': 'string'},
                                'position': {'type': 'string', 'enum': ['before', 'after', 'append'], 'default': 'append'}
                            },
                            'required': ['parent_path', 'title', 'content']
                        }
                    },
                    {
                        'name': 'get_metadata',
                        'description': 'Get metadata for section or entire project',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'path': {'type': 'string'}
                            }
                        }
                    },
                    {
                        'name': 'get_dependencies',
                        'description': 'Get include tree and cross-references',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {}
                        }
                    },
                    {
                        'name': 'validate_structure',
                        'description': 'Validate document structure consistency',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {}
                        }
                    },
                    {
                        'name': 'refresh_index',
                        'description': 'Refresh document index to detect new files',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {}
                        }
                    }
                ]
                }
            }

        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})

            if tool_name == 'get_structure':
                max_depth = arguments.get('max_depth', 3)
                result = doc_api.get_structure(max_depth)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }

            elif tool_name == 'get_section':
                path = arguments.get('path')
                result = doc_api.get_section(path)
                if result:
                    return {
                        'id': request_id,
                        'result': {
                            'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                        }
                    }
                else:
                    return {
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'result': {
                            'content': [{'type': 'text', 'text': f'Section not found: {path}'}]
                        }
                    }

            elif tool_name == 'get_sections':
                level = arguments.get('level')
                result = doc_api.get_sections(level)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }

            elif tool_name == 'search_content':
                query = arguments.get('query')
                result = doc_api.search_content(query)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }

            elif tool_name == 'update_section':
                path = arguments.get('path')
                content = arguments.get('content')
                success = doc_api.update_section_content(path, content)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': f'Update {"successful" if success else "failed"}'}]
                    }
                }

            elif tool_name == 'insert_section':
                parent_path = arguments.get('parent_path')
                title = arguments.get('title')
                content = arguments.get('content')
                position = arguments.get('position', 'append')
                success = doc_api.insert_section(parent_path, title, content, position)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': f'Insert {"successful" if success else "failed"}'}]
                    }
                }

            elif tool_name == 'get_metadata':
                path = arguments.get('path')
                result = doc_api.get_metadata(path)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }

            elif tool_name == 'get_dependencies':
                result = doc_api.get_dependencies()
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }

            elif tool_name == 'validate_structure':
                result = doc_api.validate_structure()
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }

            elif tool_name == 'refresh_index':
                result = doc_api.refresh_index()
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }

        return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32601, 'message': f'Unknown method: {method}'}}

    except Exception as e:
        return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32603, 'message': str(e)}}
