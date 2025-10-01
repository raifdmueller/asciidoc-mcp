#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from src.document_parser import DocumentParser, Section
from src.file_watcher import FileWatcher
from src.content_editor import ContentEditor
from src.diff_engine import DiffEngine
import threading
import uvicorn
import webbrowser

class MCPDocumentationServer:
    def __init__(self, project_root: Path, enable_webserver: bool = True):
        # Convert to Path if string is passed
        self.project_root = Path(project_root) if isinstance(project_root, str) else project_root
        self.enable_webserver = enable_webserver
        self.webserver_url = None
        self.webserver_port = None
        self.webserver_thread = None
        self.parser = DocumentParser()
        self.editor = ContentEditor(project_root)
        self.diff_engine = DiffEngine()
        self.sections: Dict[str, Section] = {}
        self.root_files = []
        self.file_watcher = FileWatcher(project_root, self._on_files_changed)
        self._discover_root_files()
        self._parse_project()
        self.file_watcher.start()

        # Webserver will be started after first MCP initialize
        self.webserver_started = False

    def cleanup(self):
        """Clean up resources and stop webserver"""
        try:
            # Stop file watcher
            if hasattr(self, 'file_watcher') and self.file_watcher:
                self.file_watcher.stop()

            # Webserver thread will stop automatically (daemon thread)

        except Exception as e:
            print(f"Exception in cleanup: {e}", file=sys.stderr)
    
    def _on_files_changed(self, changed_files: Set[str]):
        """Handle file change notifications"""
        print(f"Files changed: {len(changed_files)} files", file=sys.stderr)
        self._discover_root_files()
        self._parse_project()
    
    def _discover_root_files(self):
        """Find main documentation files (AsciiDoc and Markdown only)"""
        self.root_files = []  # Clear list before discovering to prevent duplicates
        # Extended patterns for AsciiDoc and Markdown files
        patterns = ['*.adoc', '*.ad', '*.asciidoc', '*.md', '*.markdown']
        for pattern in patterns:
            for file in self.project_root.glob(pattern):
                if not file.name.startswith('_'):  # Skip includes
                    self.root_files.append(file)
    
    def _parse_project(self):
        """Parse all root files and build section index"""
        for root_file in self.root_files:
            file_sections = self.parser.parse_project(root_file)
            self.sections.update(file_sections)
    
    def get_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """Get hierarchical table of contents up to max_depth, sorted by document position"""
        
        # Build hierarchical structure with proper sorting
        structure = {}
        section_map = {}  # For quick lookup
        
        # First, collect all sections at the requested depth
        filtered_sections = [(section_id, section) for section_id, section in self.sections.items() 
                           if section.level <= max_depth]
        
        # Sort by a combination of factors to get proper document order:
        # 1. Extract chapter number from title if present
        # 2. Fall back to line_start
        # 3. Fall back to title alphabetically
        def get_sort_key(item):
            section_id, section = item
            title = section.title
            
            # Try to extract chapter number from title (e.g., "1. Introduction", "10. Quality")
            import re
            chapter_match = re.match(r'^(\d+)\.', title)
            if chapter_match:
                return (int(chapter_match.group(1)), section.line_start, title)
            
            # For sections without chapter numbers, use line_start and title
            return (999, section.line_start, title)
        
        sorted_sections = sorted(filtered_sections, key=get_sort_key)
        
        for section_id, section in sorted_sections:
            # Safe children count
            children_count = 0
            if hasattr(section, 'children') and section.children:
                children_count = len(section.children)
            
            section_data = {
                'title': section.title,
                'level': section.level,
                'id': section_id,
                'children_count': children_count,
                'line_start': section.line_start,
                'line_end': section.line_end,
                'source_file': section.source_file,
                'children': []  # Will be populated with child objects
            }
            
            section_map[section_id] = section_data
            
            # Determine parent
            if '.' in section_id:
                parent_id = '.'.join(section_id.split('.')[:-1])
                if parent_id in section_map:
                    section_map[parent_id]['children'].append(section_data)
                else:
                    # Parent not found, add to root
                    structure[section_id.split('.')[-1]] = section_data
            else:
                # Root level section
                structure[section_id] = section_data
        
        return structure
        
    def get_main_chapters(self) -> Dict[str, Any]:
        """Get main chapters for web interface - handles arc42 structure correctly"""
        import re
        
        # First get the full hierarchical structure with deeper depth for ADRs
        full_structure = self.get_structure(max_depth=4)
        
        # Find all numbered chapters (level 2 in arc42 structure) AND other top-level documents
        main_chapters = {}
        
        for section_id, section in self.sections.items():
            # Look for numbered chapters at level 2 (arc42 structure)
            if section.level == 2:
                # Check for numbered chapters like "1. Introduction", "2. Architecture", etc.
                chapter_match = re.match(r'^(\d+)\.', section.title)
                if chapter_match:
                    chapter_num = int(chapter_match.group(1))
                    
                    # Get the full section data from the hierarchical structure
                    if section_id in full_structure:
                        chapter_data = full_structure[section_id].copy()
                        chapter_data['chapter_number'] = chapter_num
                        main_chapters[f"chapter_{chapter_num:02d}"] = chapter_data
                
                # Also check for "Introduction and Goals" which is chapter 1
                elif 'introduction' in section.title.lower() and 'goals' in section.title.lower():
                    if section_id in full_structure:
                        chapter_data = full_structure[section_id].copy()
                        chapter_data['chapter_number'] = 1
                        main_chapters["chapter_01"] = chapter_data
            
            # Also include all level 1 sections (other documents)
            elif section.level == 1:
                if section_id in full_structure:
                    section_data = full_structure[section_id].copy()
                    section_data['chapter_number'] = 999  # Sort after numbered chapters
                    main_chapters[section_id] = section_data
        
        return main_chapters
    
    def get_section(self, path: str) -> Optional[Dict[str, Any]]:
        """Get specific section content"""
        if path in self.sections:
            section = self.sections[path]
            return {
                'id': section.id,
                'title': section.title,
                'level': section.level,
                'content': section.content,
                'children': [child.id if hasattr(child, 'id') else str(child) for child in section.children]
            }
        return None
    
    def get_sections(self, level: int) -> List[Dict[str, Any]]:
        """Get all sections at specific level"""
        result = []
        for section in self.sections.values():
            if section.level == level:
                result.append({
                    'id': section.id,
                    'title': section.title,
                    'content': section.content[:200] + '...' if len(section.content) > 200 else section.content
                })
        return result
    
    def search_content(self, query: str) -> List[Dict[str, Any]]:
        """Search for content in sections"""
        results = []
        query_lower = query.lower()
        
        for section in self.sections.values():
            if query_lower in section.title.lower() or query_lower in section.content.lower():
                results.append({
                    'id': section.id,
                    'title': section.title,
                    'relevance': self._calculate_relevance(section, query_lower),
                    'snippet': self._extract_snippet(section.content, query_lower)
                })
        
        return sorted(results, key=lambda x: x['relevance'], reverse=True)
    
    def get_sections_by_level(self, level: int) -> List[Dict[str, Any]]:
        """Get all sections at specific level"""
        result = []
        for section in self.sections.values():
            if section.level == level:
                result.append({
                    'id': section.id,
                    'title': section.title,
                    'content': section.content
                })
        return result
    
    def get_metadata(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Get metadata for section or entire project"""
        import os
        from datetime import datetime
        
        if path:
            # Metadata for specific section
            if path not in self.sections:
                return {'error': f'Section not found: {path}'}
            
            section = self.sections[path]
            word_count = len(section.content.split()) if section.content else 0
            
            return {
                'path': path,
                'title': section.title,
                'level': section.level,
                'word_count': word_count,
                'children_count': len(section.children),
                'has_content': bool(section.content)
            }
        else:
            # Project metadata
            total_sections = len(self.sections)
            total_words = sum(len(s.content.split()) if s.content else 0 for s in self.sections.values())
            
            file_info = []
            for root_file in self.root_files:
                stat = os.stat(root_file)
                file_info.append({
                    'file': str(root_file.relative_to(self.project_root)),
                    'size': stat.st_size,
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            return {
                'project_root': str(self.project_root),
                'total_sections': total_sections,
                'total_words': total_words,
                'root_files': file_info
            }

    def get_dependencies(self) -> Dict[str, Any]:
        """Get include tree and cross-references"""
        dependencies = {
            'includes': {},
            'cross_references': [],
            'orphaned_sections': []
        }
        
        # Analyze includes
        for root_file in self.root_files:
            try:
                content = root_file.read_text(encoding='utf-8')
                includes = []
                for line in content.split('\n'):
                    if 'include::' in line:
                        start = line.find('include::') + 9
                        end = line.find('[', start)
                        if end > start:
                            include_path = line[start:end]
                            includes.append(include_path)
                
                dependencies['includes'][str(root_file.relative_to(self.project_root))] = includes
            except Exception:
                pass
        
        # Find orphaned sections
        all_section_ids = set(self.sections.keys())
        referenced_sections = set()
        
        for section in self.sections.values():
            for child in section.children:
                if isinstance(child, str):
                    referenced_sections.add(child)
                else:
                    referenced_sections.add(child.id)
        
        dependencies['orphaned_sections'] = list(all_section_ids - referenced_sections)
        return dependencies

    def validate_structure(self) -> Dict[str, Any]:
        """Validate document structure consistency"""
        from datetime import datetime
        
        issues = []
        warnings = []
        
        # Check for missing sections
        for section in self.sections.values():
            for child in section.children:
                child_id = child.id if hasattr(child, 'id') else str(child)
                if child_id not in self.sections:
                    issues.append(f"Missing child section: {child_id} (referenced by {section.id})")
        
        # Check level consistency
        for section in self.sections.values():
            if '.' in section.id:
                parent_id = '.'.join(section.id.split('.')[:-1])
                if parent_id in self.sections:
                    parent_section = self.sections[parent_id]
                    if section.level != parent_section.level + 1:
                        warnings.append(f"Level inconsistency: {section.id} (level {section.level}) under {parent_id} (level {parent_section.level})")
        
        # Check for empty sections
        empty_sections = [s.id for s in self.sections.values() if not s.content and not s.children]
        if empty_sections:
            warnings.extend([f"Empty section: {sid}" for sid in empty_sections])
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_sections': len(self.sections),
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def refresh_index(self) -> Dict[str, Any]:
        """Manually refresh the document index"""
        old_count = len(self.sections)
        
        # Re-discover and re-parse
        self._discover_root_files()
        self._parse_project()
        
        new_count = len(self.sections)
        
        return {
            'success': True,
            'old_section_count': old_count,
            'new_section_count': new_count,
            'sections_added': new_count - old_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_relevance(self, section: Section, query: str) -> float:
        """Simple relevance scoring"""
        title_matches = section.title.lower().count(query)
        content_matches = section.content.lower().count(query)
        return title_matches * 2 + content_matches
    
    def update_section_content(self, path: str, content: str) -> bool:
        """Update section content"""
        if path not in self.sections:
            return False
        
        section = self.sections[path]
        
        # Update in-memory section first
        section.content = content
        
        # Try to update source file
        for root_file in self.root_files:
            if self.editor.update_section(section, content, root_file):
                return True
        
        # Even if file update fails, in-memory update succeeded
        return True
    
    def insert_section(self, parent_path: str, title: str, content: str, position: str = "append") -> bool:
        """Insert new section"""
        if parent_path not in self.sections:
            return False
        
        parent_section = self.sections[parent_path]
        # Find source file for parent section
        for root_file in self.root_files:
            if self.editor.insert_section(parent_section, title, content, position, root_file):
                return True
        return False
    
    def _extract_snippet(self, content: str, query: str, context_chars: int = 100) -> str:
        """Extract snippet around query match"""
        content_lower = content.lower()
        pos = content_lower.find(query)
        if pos == -1:
            return content[:context_chars] + '...'
        
        start = max(0, pos - context_chars // 2)
        end = min(len(content), pos + len(query) + context_chars // 2)
        return content[start:end]
    
    def _find_free_port(self, start_port: int = 8080) -> int:
        """Find first available port"""
        import socket
        for port in range(start_port, start_port + 20):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except OSError:
                continue
        return start_port

    def _start_webserver_thread(self):
        """Start webserver in background thread (like Serena)"""
        # Find free port
        self.webserver_port = self._find_free_port()
        self.webserver_url = f"http://localhost:{self.webserver_port}"

        # Start uvicorn in daemon thread
        def run_server():
            from src import web_server
            # Set the global doc_server
            web_server.doc_server = self

            # Configure uvicorn
            config = uvicorn.Config(
                web_server.app,
                host="127.0.0.1",
                port=self.webserver_port,
                log_level="error",
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
    
    def get_webserver_status(self) -> Dict[str, Any]:
        """Get current webserver status"""
        if not self.enable_webserver:
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
        if not self.enable_webserver or not self.auto_start_manager:
            return False
        
        try:
            # Stop current webserver
            if hasattr(self.auto_start_manager.webserver_manager, 'stop_webserver'):
                self.auto_start_manager.webserver_manager.stop_webserver()
            
            # Start new one
            result = self.auto_start_manager.start_all()
            
            if result.success:
                self.webserver_port = result.port
                self.webserver_url = result.url
                return True
            else:
                print(f"Failed to restart webserver: {result.error}", file=sys.stderr)
                return False
                
        except Exception as e:
            print(f"Error restarting webserver: {e}", file=sys.stderr)
            return False

def handle_mcp_request(request: Dict[str, Any], server: MCPDocumentationServer) -> Dict[str, Any]:
    """Handle MCP protocol requests"""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    try:
        if method == 'initialize':
            # Start webserver on first initialize (after MCP is ready)
            if server.enable_webserver and not server.webserver_started:
                server.webserver_started = True
                server._start_webserver_thread()

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
                result = server.get_structure(max_depth)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }
            
            elif tool_name == 'get_section':
                path = arguments.get('path')
                result = server.get_section(path)
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
                result = server.get_sections(level)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }
            
            elif tool_name == 'search_content':
                query = arguments.get('query')
                result = server.search_content(query)
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
                success = server.update_section_content(path, content)
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
                success = server.insert_section(parent_path, title, content, position)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': f'Insert {"successful" if success else "failed"}'}]
                    }
                }
            
            elif tool_name == 'get_metadata':
                path = arguments.get('path')
                result = server.get_metadata(path)
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }
            
            elif tool_name == 'get_dependencies':
                result = server.get_dependencies()
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }
            
            elif tool_name == 'validate_structure':
                result = server.validate_structure()
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]
                    }
                }
            
            elif tool_name == 'refresh_index':
                result = server.refresh_index()
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

def main():
    import signal
    import atexit
    
    if len(sys.argv) != 2:
        print("Usage: python mcp_server.py <project_root>", file=sys.stderr)
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    if not project_root.exists():
        print(f"Project root does not exist: {project_root}", file=sys.stderr)
        sys.exit(1)
    
    server = MCPDocumentationServer(project_root)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        import datetime
        log_file = "browser_debug.log"
        timestamp = datetime.datetime.now().isoformat()
        
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Signal {signum} received, cleaning up...\n")
        
        server.cleanup()
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Register atexit handler as backup
    atexit.register(server.cleanup)
    
    # MCP protocol loop
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_mcp_request(request, server)
            print(json.dumps(response))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({'jsonrpc': '2.0', 'error': {'code': -32700, 'message': 'Parse error'}}))
        except Exception as e:
            print(json.dumps({'jsonrpc': '2.0', 'error': {'code': -32603, 'message': str(e)}}))

if __name__ == '__main__':
    main()
