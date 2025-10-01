import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Section:
    id: str
    title: str
    level: int
    content: str
    line_start: int
    line_end: int
    source_file: str  # Relative path to source file
    children: List[str]  # Store child IDs instead of Section objects
    parent_id: Optional[str] = None  # Store parent ID instead of Section object

class DocumentParser:
    def __init__(self, max_include_depth: int = 4):
        self.max_include_depth = max_include_depth
        self.processed_files = set()
        
    def parse_project(self, root_file: Path) -> Tuple[Dict[str, Section], set]:
        """Parse a documentation project starting from root file

        Returns:
            Tuple of (sections_dict, included_files_set)
            - sections_dict: Dictionary mapping section IDs to Section objects
            - included_files_set: Set of Path objects for files that were included (excluding root_file)
        """
        self.processed_files.clear()
        content = self._resolve_includes(root_file, 0)
        sections = self._parse_structure(content, str(root_file))

        # Get included files (all processed files except the root file itself)
        included_files = {Path(f) for f in self.processed_files if Path(f) != root_file}

        return sections, included_files
    
    def _resolve_includes(self, file_path: Path, depth: int) -> str:
        """Resolve include directives recursively"""
        if depth >= self.max_include_depth or str(file_path) in self.processed_files:
            return f"// Include depth limit reached or circular reference: {file_path}\n"
        
        self.processed_files.add(str(file_path))
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return f"// Error reading file: {file_path}\n"
        
        # Handle AsciiDoc includes: include::file.adoc[]
        include_pattern = r'include::([^[\]]+)\[\]'
        
        def replace_include(match):
            include_file = match.group(1)
            include_path = file_path.parent / include_file
            return self._resolve_includes(include_path, depth + 1)
        
        return re.sub(include_pattern, replace_include, content)
    
    def _parse_structure(self, content: str, source_file: str) -> Dict[str, Section]:
        """Parse document structure into hierarchical sections"""
        lines = content.split('\n')
        sections = {}
        section_stack = []
        current_content = []
        line_num = 0
        
        # Convert to relative path for portability
        try:
            from pathlib import Path
            rel_source_file = str(Path(source_file).relative_to(self.root_path))
        except (ValueError, AttributeError):
            # If relative_to fails or root_path not set, use source_file as-is
            rel_source_file = source_file
        
        for i, line in enumerate(lines):
            # AsciiDoc headers: = Title, == Title, etc.
            # Markdown headers: # Title, ## Title, etc.
            header_match = re.match(r'^(=+|#+)\s+(.+)$', line.strip())
            
            if header_match:
                # Save previous section content
                if section_stack:
                    section_stack[-1].content = '\n'.join(current_content).strip()
                    section_stack[-1].line_end = i - 1
                
                # Determine level
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                # Generate section ID
                section_id = self._generate_section_id(title, level, section_stack)
                
                # Create new section
                section = Section(
                    id=section_id,
                    title=title,
                    level=level,
                    content="",
                    line_start=i,
                    line_end=i,
                    source_file=rel_source_file,
                    children=[]
                )
                
                # Manage hierarchy
                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()
                
                if section_stack:
                    section.parent_id = section_stack[-1].id
                    section_stack[-1].children.append(section_id)
                
                section_stack.append(section)
                sections[section_id] = section
                current_content = []
            else:
                current_content.append(line)
        
        # Handle last section
        if section_stack:
            section_stack[-1].content = '\n'.join(current_content).strip()
            section_stack[-1].line_end = len(lines) - 1
        
        return sections
    
    def _generate_section_id(self, title: str, level: int, section_stack: List[Section]) -> str:
        """Generate hierarchical section ID"""
        # Clean title for ID
        clean_title = re.sub(r'[^\w\s-]', '', title.lower()).replace(' ', '-')
        
        # Build hierarchical path
        path_parts = []
        for section in section_stack:
            if section.level < level:
                path_parts.append(section.id.split('.')[-1])
        
        path_parts.append(clean_title)
        return '.'.join(path_parts)
