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
    document_position: int = 0  # Position in resolved document for proper sorting

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
        content, line_sources = self._resolve_includes_with_sources(root_file, 0)
        sections = self._parse_structure_with_sources(content, line_sources)

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
    
    def _resolve_includes_with_sources(self, file_path: Path, depth: int) -> Tuple[str, List[str]]:
        """Resolve include directives recursively while tracking source files for each line
        
        Returns:
            Tuple of (content, line_sources)
            - content: Resolved content string
            - line_sources: List where line_sources[i] is the source file path for line i
        """
        if depth >= self.max_include_depth or str(file_path) in self.processed_files:
            error_line = f"// Include depth limit reached or circular reference: {file_path}\n"
            return error_line, [str(file_path)]
        
        self.processed_files.add(str(file_path))
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            error_line = f"// Error reading file: {file_path}\n"
            return error_line, [str(file_path)]
        
        # Handle AsciiDoc includes: include::file.adoc[]
        include_pattern = r'include::([^[\]]+)\[\]'
        lines = content.split('\n')
        result_lines = []
        result_sources = []
        
        for line in lines:
            match = re.match(include_pattern, line)
            if match:
                include_file = match.group(1)
                include_path = file_path.parent / include_file
                included_content, included_sources = self._resolve_includes_with_sources(include_path, depth + 1)
                
                # Add included lines and their sources
                included_lines = included_content.split('\n')
                result_lines.extend(included_lines)
                result_sources.extend(included_sources)
            else:
                result_lines.append(line)
                result_sources.append(str(file_path))
        
        return '\n'.join(result_lines), result_sources
    
    def _parse_structure(self, content: str, source_file: str) -> Dict[str, Section]:
        """Parse document structure into hierarchical sections"""
        lines = content.split('\n')
        sections = {}
        section_stack = []
        current_content = []
        line_num = 0

        # Code block tracking (Issue #49)
        in_code_block = False
        code_block_delimiter = None

        # Convert to relative path for portability
        try:
            from pathlib import Path
            rel_source_file = str(Path(source_file).relative_to(self.root_path))
        except (ValueError, AttributeError):
            # If relative_to fails or root_path not set, use source_file as-is
            rel_source_file = source_file

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            # Track code block boundaries (Issue #49)
            # Detect block attributes: [source,python], [plantuml], etc.
            if stripped_line.startswith('[') and (
                'source' in stripped_line or
                'plantuml' in stripped_line or
                'listing' in stripped_line
            ):
                # Next delimiter will start a code block
                current_content.append(line)
                continue

            # Detect code block delimiters: ----, ...., etc.
            if stripped_line in ['----', '....', '====', '****']:
                if in_code_block and stripped_line == code_block_delimiter:
                    # Exit code block
                    in_code_block = False
                    code_block_delimiter = None
                elif not in_code_block:
                    # Enter code block
                    in_code_block = True
                    code_block_delimiter = stripped_line
                current_content.append(line)
                continue

            # Skip header parsing if inside code block (Issue #49)
            if in_code_block:
                current_content.append(line)
                continue

            # AsciiDoc headers: = Title, == Title, etc.
            # Markdown headers: # Title, ## Title, etc.
            header_match = re.match(r'^(=+|#+)\s+(.+)$', stripped_line)

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
    
    def _parse_structure_with_sources(self, content: str, line_sources: List[str]) -> Dict[str, Section]:
        """Parse document structure using source file mapping for each line"""
        lines = content.split('\n')
        sections = {}
        section_stack = []
        current_content = []

        # Code block tracking (Issue #49)
        in_code_block = False
        code_block_delimiter = None

        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Get source file for this line (with bounds checking)
            line_source_file = line_sources[i] if i < len(line_sources) else line_sources[-1] if line_sources else "unknown"

            # Track code block boundaries (Issue #49)
            # Detect block attributes: [source,python], [plantuml], etc.
            if stripped_line.startswith('[') and (
                'source' in stripped_line or
                'plantuml' in stripped_line or
                'listing' in stripped_line
            ):
                # Next delimiter will start a code block
                current_content.append(line)
                continue

            # Detect code block delimiters: ----, ...., etc.
            if stripped_line in ['----', '....', '====', '****']:
                if in_code_block and stripped_line == code_block_delimiter:
                    # Exit code block
                    in_code_block = False
                    code_block_delimiter = None
                elif not in_code_block:
                    # Enter code block
                    in_code_block = True
                    code_block_delimiter = stripped_line
                current_content.append(line)
                continue

            # Skip header parsing if inside code block (Issue #49)
            if in_code_block:
                current_content.append(line)
                continue

            # AsciiDoc headers: = Title, == Title, etc.
            # Markdown headers: # Title, ## Title, etc.
            header_match = re.match(r'^(=+|#+)\s+(.+)$', stripped_line)

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
                
                # Use the source file for this specific line (the header line)
                section_source_file = line_source_file
                
                # Create new section with proper source file
                section = Section(
                    id=section_id,
                    title=title,
                    level=level,
                    content="",
                    line_start=i,
                    line_end=i,
                    source_file=section_source_file,
                    children=[],
                    document_position=i
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
