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
    
    # Group sections by source file
    files_sections = {}
    for section in parser.sections.values():
        source_file = section.source_file
        if source_file not in files_sections:
            files_sections[source_file] = []
        files_sections[source_file].append(section)
    
    # Build file-based structure
    for source_file, sections_list in files_sections.items():
        # Convert absolute paths to relative paths for display
        try:
            rel_path = str(Path(source_file).relative_to(parser.project_root))
        except ValueError:
            rel_path = source_file
        
        # Sort sections by line_start to maintain document order
        sections_list.sort(key=lambda s: s.line_start)
        
        # Build hierarchical structure for sections within this file
        section_map = {}
        root_sections = []
        
        for section in sections_list:
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
            
            # Determine parent within same file using dot notation
            if '.' in section.id:
                parent_id = '.'.join(section.id.split('.')[:-1])
                if parent_id in section_map:
                    section_map[parent_id]['children'].append(section_data)
                else:
                    # Parent not in same file, treat as root-level
                    root_sections.append(section_data)
            else:
                # Top-level section
                root_sections.append(section_data)
        
        # Create file entry (matches the expected structure from document_api.py)
        if sections_list:  # Only add files that have sections
            structure[rel_path] = {
                'filename': Path(source_file).name,
                'path': rel_path,
                'section_count': len(sections_list),
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