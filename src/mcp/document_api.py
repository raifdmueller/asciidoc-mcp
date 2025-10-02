"""
Document API Module

Handles all document structure, sections, metadata, and search operations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from src.document_parser import Section
from src.content_editor import ContentEditor
from src.diff_engine import DiffEngine
import os
import re


class DocumentAPI:
    """Manages document structure, sections, and metadata operations"""

    def __init__(self, server: 'MCPDocumentationServer'):
        """
        Initialize DocumentAPI with reference to server instance

        Args:
            server: MCPDocumentationServer instance for accessing shared state
        """
        self.server = server

    def get_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """Get hierarchical table of contents up to max_depth, sorted by document position"""

        # Build hierarchical structure with proper sorting
        structure = {}
        section_map = {}  # For quick lookup

        # First, collect all sections at the requested depth
        filtered_sections = [(section_id, section) for section_id, section in self.server.sections.items()
                           if section.level <= max_depth]

        # Sort by a combination of factors to get proper document order:
        # 1. Extract chapter number from title if present
        # 2. Fall back to line_start
        # 3. Fall back to title alphabetically
        def get_sort_key(item):
            section_id, section = item
            title = section.title

            # Try to extract chapter number from title (e.g., "1. Introduction", "10. Quality")
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

        # First get the full hierarchical structure with deeper depth for ADRs
        full_structure = self.get_structure(max_depth=4)

        # Find all numbered chapters (level 2 in arc42 structure) AND other top-level documents
        main_chapters = {}

        for section_id, section in self.server.sections.items():
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

    def get_root_files_structure(self) -> Dict[str, Any]:
        """Get structure grouped by root files - shows files as top level with their sections"""
        from pathlib import Path

        structure = {}

        # Iterate over each root file (skip included files)
        for root_file in self.server.root_files:
            # Skip files that are included by other files
            if root_file in self.server.included_files:
                continue

            # Get absolute path for matching
            abs_path = str(root_file)

            # Also get relative path for display
            try:
                rel_path = str(root_file.relative_to(self.server.project_root))
            except ValueError:
                rel_path = str(root_file)

            # Find all sections belonging to this file
            # Sections may have either absolute or relative paths
            file_sections = []
            for section_id, section in self.server.sections.items():
                # Try matching both absolute and relative paths
                if section.source_file == abs_path or section.source_file == rel_path:
                    # Get section data
                    children_count = len(section.children) if hasattr(section, 'children') and section.children else 0

                    section_data = {
                        'title': section.title,
                        'level': section.level,
                        'id': section_id,
                        'children_count': children_count,
                        'line_start': section.line_start,
                        'line_end': section.line_end,
                        'source_file': section.source_file,
                        'children': []
                    }
                    file_sections.append((section_id, section_data))

            # Sort sections by line_start to maintain document order
            file_sections.sort(key=lambda x: self.server.sections[x[0]].line_start)

            # Build hierarchical structure for sections within this file
            section_map = {}
            root_sections = []

            for section_id, section_data in file_sections:
                section_map[section_id] = section_data

                # Determine parent within same file
                if '.' in section_id:
                    parent_id = '.'.join(section_id.split('.')[:-1])
                    if parent_id in section_map:
                        section_map[parent_id]['children'].append(section_data)
                    else:
                        # Parent not in same file, treat as root-level
                        root_sections.append(section_data)
                else:
                    # Top-level section
                    root_sections.append(section_data)

            # Create file entry
            if file_sections:  # Only add files that have sections
                total_sections = len(file_sections)
                structure[rel_path] = {
                    'filename': root_file.name,
                    'path': rel_path,
                    'section_count': total_sections,
                    'sections': root_sections
                }

        return structure

    def get_section(self, path: str) -> Optional[Dict[str, Any]]:
        """Get specific section content"""
        if path in self.server.sections:
            section = self.server.sections[path]
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
        for section in self.server.sections.values():
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

        for section in self.server.sections.values():
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
        for section in self.server.sections.values():
            if section.level == level:
                result.append({
                    'id': section.id,
                    'title': section.title,
                    'content': section.content
                })
        return result

    def get_metadata(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Get metadata for section or entire project"""

        if path:
            # Metadata for specific section
            if path not in self.server.sections:
                return {'error': f'Section not found: {path}'}

            section = self.server.sections[path]
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
            total_sections = len(self.server.sections)
            total_words = sum(len(s.content.split()) if s.content else 0 for s in self.server.sections.values())

            file_info = []
            for root_file in self.server.root_files:
                stat = os.stat(root_file)
                file_info.append({
                    'file': str(root_file.relative_to(self.server.project_root)),
                    'size': stat.st_size,
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

            return {
                'project_root': str(self.server.project_root),
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
        for root_file in self.server.root_files:
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

                dependencies['includes'][str(root_file.relative_to(self.server.project_root))] = includes
            except Exception:
                pass

        # Find orphaned sections
        all_section_ids = set(self.server.sections.keys())
        referenced_sections = set()

        for section in self.server.sections.values():
            for child in section.children:
                if isinstance(child, str):
                    referenced_sections.add(child)
                else:
                    referenced_sections.add(child.id)

        dependencies['orphaned_sections'] = list(all_section_ids - referenced_sections)
        return dependencies

    def validate_structure(self) -> Dict[str, Any]:
        """Validate document structure consistency"""

        issues = []
        warnings = []

        # Check for missing sections
        for section in self.server.sections.values():
            for child in section.children:
                child_id = child.id if hasattr(child, 'id') else str(child)
                if child_id not in self.server.sections:
                    issues.append(f"Missing child section: {child_id} (referenced by {section.id})")

        # Check level consistency
        for section in self.server.sections.values():
            if '.' in section.id:
                parent_id = '.'.join(section.id.split('.')[:-1])
                if parent_id in self.server.sections:
                    parent_section = self.server.sections[parent_id]
                    if section.level != parent_section.level + 1:
                        warnings.append(f"Level inconsistency: {section.id} (level {section.level}) under {parent_id} (level {parent_section.level})")

        # Check for empty sections
        empty_sections = [s.id for s in self.server.sections.values() if not s.content and not s.children]
        if empty_sections:
            warnings.extend([f"Empty section: {sid}" for sid in empty_sections])

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_sections': len(self.server.sections),
            'validation_timestamp': datetime.now().isoformat()
        }

    def refresh_index(self) -> Dict[str, Any]:
        """Manually refresh the document index"""
        old_count = len(self.server.sections)

        # Re-discover and re-parse
        self.server._discover_root_files()
        self.server._parse_project()

        new_count = len(self.server.sections)

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
        if path not in self.server.sections:
            return False

        section = self.server.sections[path]

        # Update in-memory section first
        section.content = content

        # Try to update source file
        for root_file in self.server.root_files:
            if self.server.editor.update_section(section, content, root_file):
                return True

        # Even if file update fails, in-memory update succeeded
        return True

    def insert_section(self, parent_path: str, title: str, content: str, position: str = "append") -> bool:
        """Insert new section"""
        if parent_path not in self.server.sections:
            return False

        parent_section = self.server.sections[parent_path]
        # Find source file for parent section
        for root_file in self.server.root_files:
            if self.server.editor.insert_section(parent_section, title, content, position, root_file):
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
