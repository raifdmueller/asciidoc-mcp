#!/usr/bin/env python3
"""
Simple standalone web server for AsciiDoc MCP without fastmcp dependency
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from document_parser import DocumentParser
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import argparse

app = FastAPI(title="AsciiDoc MCP Server")

# Global parser instance
parser = None

@app.get("/")
async def get_index():
    """Serve the main HTML interface"""
    try:
        with open("src/templates/index.html", "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("<h1>AsciiDoc MCP Server</h1><p>Template not found</p>")

@app.get("/api/structure")
async def get_structure():
    """Get document structure grouped by root files - matches web interface expectations"""
    if not parser or not parser.sections:
        return JSONResponse({})
    
    structure = {}
    
    def get_included_files_set(parser):
        """Extract included files as a normalized set of paths."""
        included_files_set = set()
        if hasattr(parser, 'included_files'):
            for included_file in parser.included_files:
                included_files_set.add(str(Path(included_file)))
        return included_files_set
    
    def identify_root_files(parser, included_files_set):
        """Identify root files that are not included by other files."""
        all_source_files = set(section.source_file for section in parser.sections.values())
        root_files = []
        
        for source_file in all_source_files:
            abs_source = str(Path(source_file))
            is_included = any(abs_source == included or source_file == included 
                            for included in included_files_set)
            if not is_included:
                root_files.append(source_file)
        
        return root_files
    
    def collect_sections_for_root_file(parser, root_file, root_files):
        """Collect all sections belonging to a root file (including from includes)."""
        file_sections = []
        
        for section in parser.sections.values():
            if root_file == section.source_file:
                # Direct sections from the root file
                file_sections.append(section)
            elif len(root_files) == 1:
                # Single root file means it's an aggregator - include all sections
                file_sections.append(section)
        
        return sorted(file_sections, key=lambda s: s.line_start)
    
    def build_section_hierarchy(file_sections):
        """Build hierarchical structure for sections within a file."""
        section_map = {}
        root_sections = []
        
        for section in file_sections:
            section_data = {
                'title': section.title,
                'level': section.level,
                'id': section.id,
                'children_count': len(section.children) if hasattr(section, 'children') and section.children else 0,
                'line_start': section.line_start,
                'line_end': section.line_end,
                'source_file': section.source_file,
                'children': []
            }
            section_map[section.id] = section_data
            
            # Determine parent using dot notation hierarchy
            if '.' in section.id:
                parent_id = '.'.join(section.id.split('.')[:-1])
                if parent_id in section_map:
                    section_map[parent_id]['children'].append(section_data)
                else:
                    root_sections.append(section_data)
            else:
                root_sections.append(section_data)
        
        return root_sections
    
    # Main aggregator file handling logic
    included_files_set = get_included_files_set(parser)
    root_files = identify_root_files(parser, included_files_set)
    
    # Process each root file to build the structure
    for root_file in root_files:
        # Get relative path for display
        try:
            rel_path = str(Path(root_file).relative_to(parser.project_root))
        except ValueError:
            rel_path = root_file
        
        file_sections = collect_sections_for_root_file(parser, root_file, root_files)
        if not file_sections:
            continue
        
        root_sections = build_section_hierarchy(file_sections)
        
        # Create file entry (matches the expected structure from document_api.py)
        structure[rel_path] = {
            'filename': Path(root_file).name,
            'path': rel_path,
            'section_count': len(file_sections),
            'sections': root_sections
        }
    
    return JSONResponse(structure)

@app.get("/api/section/{section_id}")
async def get_section(section_id: str, context: str = None):
    """Get section content, optionally with full document context"""
    if not parser:
        raise HTTPException(status_code=500, detail="Parser not initialized")
    
    if section_id not in parser.sections:
        raise HTTPException(status_code=404, detail="Section not found")
    
    section = parser.sections[section_id]
    
    response = {
        "content": section.content,
        "title": section.title,
        "source_file": section.source_file,
        "line_start": section.line_start,
        "line_end": section.line_end
    }
    
    # Add full document context if requested
    if context == "full":
        try:
            # Read the full source file
            source_path = parser.project_root / section.source_file
            if source_path.exists():
                with open(source_path, 'r', encoding='utf-8') as f:
                    full_content = f.read()
                response["full_content"] = full_content
                response["section_position"] = {
                    "line_start": section.line_start,
                    "line_end": section.line_end
                }
        except Exception as e:
            print(f"Error reading full content: {e}")
    
    return JSONResponse(response)

def init_parser(project_root: Path, root_file: str = "arc42.adoc"):
    """Initialize the document parser"""
    global parser
    
    parser = DocumentParser()
    parser.project_root = project_root
    
    root_path = project_root / root_file
    if not root_path.exists():
        print(f"Warning: Root file {root_path} not found")
        return False
    
    try:
        sections, included_files = parser.parse_project(root_path)
        parser.sections = sections  # Store parsed sections as attribute
        parser.included_files = included_files
        print(f"Parsed {len(parser.sections)} sections from {root_file}")
        return True
    except Exception as e:
        print(f"Error parsing project: {e}")
        return False

def main():
    """Main entry point"""
    parser_args = argparse.ArgumentParser(description="AsciiDoc MCP Simple Server")
    parser_args.add_argument("project_root", help="Project root directory")
    parser_args.add_argument("--port", type=int, default=8080, help="Server port")
    parser_args.add_argument("--root-file", default="arc42.adoc", help="Root AsciiDoc file")
    
    args = parser_args.parse_args()
    
    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"Error: Project root {project_root} does not exist")
        sys.exit(1)
    
    print(f"Initializing parser for {project_root}")
    if not init_parser(project_root, args.root_file):
        print("Failed to initialize parser")
        sys.exit(1)
    
    print(f"Starting server on http://localhost:{args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")

if __name__ == "__main__":
    main()