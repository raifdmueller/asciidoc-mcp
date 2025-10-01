from pathlib import Path
from typing import Dict, Optional, List
from .document_parser import Section

class ContentEditor:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root) if isinstance(project_root, str) else project_root
        self.file_contents: Dict[str, List[str]] = {}
    
    def load_file_content(self, file_path: Path) -> List[str]:
        """Load file content as list of lines"""
        file_key = str(file_path)
        if file_key not in self.file_contents:
            try:
                content = file_path.read_text(encoding='utf-8')
                self.file_contents[file_key] = content.split('\n')
            except Exception:
                self.file_contents[file_key] = []
        return self.file_contents[file_key]
    
    def update_section(self, section: Section, new_content: str, source_file: Path) -> bool:
        """Update section content in source file"""
        lines = self.load_file_content(source_file)
        
        if section.line_start >= len(lines) or section.line_end >= len(lines):
            return False
        
        # Keep header line, replace content
        header_line = lines[section.line_start]
        content_lines = new_content.split('\n')
        
        # Replace section content
        new_lines = lines[:section.line_start + 1] + content_lines + lines[section.line_end + 1:]
        
        try:
            source_file.write_text('\n'.join(new_lines), encoding='utf-8')
            self.file_contents[str(source_file)] = new_lines
            return True
        except Exception:
            return False
    
    def insert_section(self, parent_section: Section, title: str, content: str, 
                      position: str, source_file: Path) -> bool:
        """Insert new section relative to parent"""
        lines = self.load_file_content(source_file)
        
        # Determine header level
        level_char = '=' if source_file.suffix in ['.adoc', '.asciidoc'] else '#'
        header_prefix = level_char * (parent_section.level + 1)
        
        # Create new section lines
        new_section_lines = [
            f"{header_prefix} {title}",
            content
        ]
        
        # Determine insertion point
        if position == "append":
            insert_pos = parent_section.line_end + 1
        elif position == "before":
            insert_pos = parent_section.line_start
        else:  # after
            insert_pos = parent_section.line_end + 1
        
        # Insert new content
        new_lines = lines[:insert_pos] + new_section_lines + lines[insert_pos:]
        
        try:
            source_file.write_text('\n'.join(new_lines), encoding='utf-8')
            self.file_contents[str(source_file)] = new_lines
            return True
        except Exception:
            return False
