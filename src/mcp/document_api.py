"""
Document API Module

Handles all document structure, sections, metadata, and search operations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from src.document_parser import Section
    from src.content_editor import ContentEditor
    from src.diff_engine import DiffEngine
except ImportError:
    # Fallback for when run as script without src module in path
    from document_parser import Section
    from content_editor import ContentEditor
    from diff_engine import DiffEngine
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

    def _paginate(self, items: list, limit: Optional[int] = None, offset: int = 0) -> Dict[str, Any]:
        """
        Apply pagination to a list of items

        Args:
            items: List of items to paginate
            limit: Maximum number of items to return (None or 0 = all)
            offset: Number of items to skip

        Returns:
            Dict with 'results' and 'pagination' metadata
        """
        total = len(items)

        # If limit is None or 0, return all items (backward compatible)
        if limit is None or limit == 0:
            return {
                'results': items,
                'pagination': {
                    'total': total,
                    'limit': 0,
                    'offset': 0,
                    'has_next': False,
                    'has_previous': False
                }
            }

        # Apply pagination
        start = offset
        end = offset + limit
        paginated_items = items[start:end]

        return {
            'results': paginated_items,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_next': end < total,
                'has_previous': offset > 0
            }
        }

    def get_structure(self, start_level: int = 1, parent_id: Optional[str] = None, limit: Optional[int] = None, offset: int = 0) -> Dict[str, Any]:
        """
        Get sections at a specific level (always depth=1 to avoid token limits)

        Args:
            start_level: Which hierarchy level to return (default: 1)
            parent_id: Optional filter - only return children of this section
            limit: Maximum results to return (None/0 = all)
            offset: Number of results to skip

        Returns:
            Dict with section data for the requested level, or paginated response if limit specified
        """

        # Collect all sections at the requested level
        filtered_sections = [
            (section_id, section)
            for section_id, section in self.server.sections.items()
            if section.level == start_level
        ]

        # If parent_id is specified, filter to only children of that parent
        if parent_id:
            filtered_sections = [
                (section_id, section)
                for section_id, section in filtered_sections
                if section_id.startswith(parent_id + '.')
            ]

        # Sort by chapter number (if present), then line_start, then title
        def get_sort_key(item):
            section_id, section = item
            chapter_match = re.match(r'^(\d+)\.', section.title)
            chapter_num = int(chapter_match.group(1)) if chapter_match else 999
            return (chapter_num, section.line_start, section.title)

        sorted_sections = sorted(filtered_sections, key=get_sort_key)

        # Build section data list
        section_list = []
        for section_id, section in sorted_sections:
            children_count = len(section.children) if hasattr(section, 'children') and section.children else 0

            section_list.append({
                'title': section.title,
                'level': section.level,
                'id': section_id,
                'children_count': children_count,
                'line_start': section.line_start,
                'line_end': section.line_end,
                'source_file': section.source_file
            })

        # Return paginated if limit specified, else return dict for backward compatibility
        if limit is not None:
            return self._paginate(section_list, limit, offset)
        else:
            # Convert list back to dict for backward compatibility
            return {item['id']: item for item in section_list}

    def get_main_chapters(self) -> Dict[str, Any]:
        """Get main chapters for web interface - handles arc42 structure correctly"""

        # Build structure from all levels since we can't use max_depth anymore
        # We'll get level 1 and level 2 separately
        level_1_structure = self.get_structure(start_level=1)
        level_2_structure = self.get_structure(start_level=2)

        # Combine them for backward compatibility
        full_structure = {**level_1_structure, **level_2_structure}

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

        # Helper function to determine if a file is an aggregator file
        def is_aggregator_file(file_path: Path) -> bool:
            """Check if a file contains only includes and no content sections."""
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Filter out metadata lines (starting with :) and comments
                content_lines = [line for line in lines 
                               if not line.startswith(':') and not line.startswith('//')]
                
                # Check if most lines are includes
                include_lines = [line for line in content_lines if line.startswith('include::')]
                
                # It's an aggregator if it has includes and very little other content
                return len(include_lines) > 0 and len(content_lines) - len(include_lines) <= 3
            except Exception:
                return False

        # Helper function to collect sections for a root file (including from includes)
        def collect_sections_for_root_file(root_file: Path) -> list:
            """Collect all sections belonging to a root file (including from includes)."""
            file_sections = []
            root_file_str = str(root_file)
            root_file_rel = str(root_file.relative_to(self.server.project_root))
            
            # Check if this is an aggregator file
            if is_aggregator_file(root_file):
                # For aggregator files, collect sections from all included files
                # Get all sections that come from files included by this root file
                for section_id, section in self.server.sections.items():
                    section_file_path = Path(section.source_file)
                    
                    # Check if this section comes from a file that's included
                    if section_file_path in self.server.included_files:
                        file_sections.append((section_id, section))
                    elif section.source_file == root_file_str or section.source_file == root_file_rel:
                        # Also include direct sections from the root file itself
                        file_sections.append((section_id, section))
            else:
                # For non-aggregator files, only collect direct sections  
                for section_id, section in self.server.sections.items():
                    if section.source_file == root_file_str or section.source_file == root_file_rel:
                        file_sections.append((section_id, section))
            
            return file_sections

        # Iterate over each root file (skip included files)
        for root_file in self.server.root_files:
            # Skip files that are included by other files
            if root_file in self.server.included_files:
                continue

            # Get relative path for display
            try:
                rel_path = str(root_file.relative_to(self.server.project_root))
            except ValueError:
                rel_path = str(root_file)

            # Collect sections for this root file
            file_sections = collect_sections_for_root_file(root_file)
            
            if not file_sections:
                continue

            # Build hierarchical structure for sections within this file
            section_map = {}
            root_sections = []

            for section_id, section in file_sections:
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
                section_map[section_id] = section_data

                # Determine parent using dot notation hierarchy
                if '.' in section_id:
                    parent_id = '.'.join(section_id.split('.')[:-1])
                    if parent_id in section_map:
                        section_map[parent_id]['children'].append(section_data)
                    else:
                        root_sections.append(section_data)
                else:
                    root_sections.append(section_data)

            # Sort root sections by line_start to maintain document order
            root_sections.sort(key=lambda x: self.server.sections[x['id']].line_start)

            # Create file entry in the expected format
            structure[rel_path] = {
                'filename': root_file.name,
                'path': rel_path,
                'section_count': len(file_sections),
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

    def get_sections(self, level: int, limit: Optional[int] = None, offset: int = 0) -> Dict[str, Any]:
        """
        Get all sections at specific level

        Args:
            level: Section level to filter by
            limit: Maximum results to return (None/0 = all)
            offset: Number of results to skip

        Returns:
            Dict with 'results' list and 'pagination' metadata, or just list if limit not specified
        """
        result = []
        for section in self.server.sections.values():
            if section.level == level:
                result.append({
                    'id': section.id,
                    'title': section.title,
                    'content': section.content[:200] + '...' if len(section.content) > 200 else section.content
                })

        # Return paginated if limit specified, else return list for backward compatibility
        if limit is not None:
            return self._paginate(result, limit, offset)
        else:
            return result

    def search_content(self, query: str, limit: Optional[int] = None, offset: int = 0) -> Dict[str, Any]:
        """
        Search for content in sections

        Args:
            query: Search query string
            limit: Maximum results to return (None/0 = all, for backward compatibility)
            offset: Number of results to skip

        Returns:
            Dict with 'results' list and 'pagination' metadata, or just list if limit not specified
        """
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

        sorted_results = sorted(results, key=lambda x: x['relevance'], reverse=True)

        # Return paginated if limit specified, else return list for backward compatibility
        if limit is not None:
            return self._paginate(sorted_results, limit, offset)
        else:
            return sorted_results

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

        # Track cross-references
        cross_refs = []

        # Regex patterns for different reference types
        # Pattern 1: <<section-id>> or <<section-id,link text>>
        simple_ref_pattern = r'<<([^>,\]]+)(?:,[^>]*)?>>'
        # Pattern 2: xref:section-id[] or xref:section-id[link text]
        xref_pattern = r'xref:([^\[\]]+)\['

        for section_id, section in self.server.sections.items():
            content = section.content
            if not content:
                continue

            # Find all <<>> style references
            for match in re.finditer(simple_ref_pattern, content):
                target = match.group(1).strip()

                # Normalize target to match section IDs (convert to lowercase, replace spaces with dashes)
                normalized_target = re.sub(r'[^\w\s-]', '', target.lower()).replace(' ', '-')

                # Check if target exists in our sections
                target_exists = any(normalized_target in sid or sid.endswith(normalized_target) for sid in self.server.sections.keys())

                cross_refs.append({
                    'from_section': section_id,
                    'to_section': normalized_target,
                    'reference_type': '<<>>',
                    'valid': target_exists
                })

            # Find all xref: style references
            for match in re.finditer(xref_pattern, content):
                target = match.group(1).strip()
                # Remove file path if present (e.g., "file.adoc#section" -> "section")
                if '#' in target:
                    target = target.split('#')[1]

                normalized_target = re.sub(r'[^\w\s-]', '', target.lower()).replace(' ', '-')
                target_exists = any(normalized_target in sid or sid.endswith(normalized_target) for sid in self.server.sections.keys())

                cross_refs.append({
                    'from_section': section_id,
                    'to_section': normalized_target,
                    'reference_type': 'xref',
                    'valid': target_exists
                })

        dependencies['cross_references'] = cross_refs

        # Find orphaned sections (sections without proper parent references)
        # Note: Top-level sections (level 1) are NOT considered orphaned even if they have no parent
        all_section_ids = set(self.server.sections.keys())
        referenced_sections = set()

        # Collect all sections that are referenced as children
        for section in self.server.sections.values():
            for child in section.children:
                if isinstance(child, str):
                    referenced_sections.add(child)
                else:
                    referenced_sections.add(child.id)

        # A section is orphaned if:
        # 1. It is NOT referenced as anyone's child, AND
        # 2. It is NOT a top-level section (level 1)
        orphaned = []
        for section_id in (all_section_ids - referenced_sections):
            section = self.server.sections[section_id]
            if section.level > 1:  # Only non-top-level sections can be orphaned
                orphaned.append(section_id)

        dependencies['orphaned_sections'] = orphaned
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

        # Check level consistency (tolerance mode - allow level skips)
        # Only warn if child level is NOT greater than parent level (actual hierarchy violation)
        for section in self.server.sections.values():
            if '.' in section.id:
                parent_id = '.'.join(section.id.split('.')[:-1])
                if parent_id in self.server.sections:
                    parent_section = self.server.sections[parent_id]
                    # Child must be deeper than parent (allow skips like 1→3, but not 3→2)
                    if section.level <= parent_section.level:
                        warnings.append(f"Level hierarchy violation: {section.id} (level {section.level}) should be deeper than parent {parent_id} (level {parent_section.level})")

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
