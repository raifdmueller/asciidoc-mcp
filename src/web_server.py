#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from typing import Optional

app = FastAPI(title="MCP Documentation Server Web Interface")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Global server instance (imported at runtime to avoid circular import)
doc_server: Optional["MCPDocumentationServer"] = None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main web interface"""
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/structure")
async def get_structure():
    """Get document structure - shows root files with their sections"""
    if not doc_server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    # Use root files structure for file-based navigation
    return doc_server.get_root_files_structure()

@app.get("/api/metadata")
async def get_metadata(path: Optional[str] = None):
    """Get metadata"""
    if not doc_server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    return doc_server.get_metadata(path)

@app.get("/api/dependencies")
async def get_dependencies():
    """Get dependencies"""
    if not doc_server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    return doc_server.get_dependencies()

@app.get("/api/validate")
async def validate_structure():
    """Validate structure"""
    if not doc_server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    return doc_server.validate_structure()

@app.get("/api/search")
async def search_content(q: str):
    """Search content in sections"""
    if not doc_server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    return doc_server.doc_api.search_content(q)

def _build_base_section_response(section) -> dict:
    """Build the base section response with common fields"""
    return {
        'id': section.id,
        'title': section.title,
        'level': section.level,
        'content': section.content,
        'children': section.children,
        'source_file': section.source_file,
        'line_start': section.line_start,
        'line_end': section.line_end
    }

def _add_full_document_context(response: dict, section) -> None:
    """Add full document content and position metadata to response"""
    source_file_path = Path(section.source_file)
    if not source_file_path.exists():
        return
    
    try:
        full_content = source_file_path.read_text(encoding='utf-8')
        response['full_content'] = full_content
        response['section_position'] = {
            'line_start': section.line_start,
            'line_end': section.line_end
        }
    except (OSError, UnicodeDecodeError) as e:
        # Log error but don't fail the request - continue without full content
        pass

@app.get("/api/section/{section_id:path}")
async def get_section(section_id: str, context: str = "section"):
    """Get specific section with optional full document context"""
    if not doc_server:
        raise HTTPException(status_code=500, detail="Server not initialized")

    if section_id not in doc_server.sections:
        raise HTTPException(status_code=404, detail="Section not found")

    section = doc_server.sections[section_id]
    response = _build_base_section_response(section)
    
    if context == "full":
        _add_full_document_context(response, section)
    
    return response

def init_server(project_root: Path):  
    """Initialize the documentation server"""
    global doc_server
    try:
        # Try relative import first (when used as module)
        from .mcp_server import MCPDocumentationServer
    except ImportError:
        # Fall back to absolute import (when run as script)
        from mcp_server import MCPDocumentationServer
    doc_server = MCPDocumentationServer(project_root, enable_webserver=False)

if __name__ == "__main__":
    import uvicorn
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Start MCP Documentation Web Server')
    parser.add_argument('project_root', help='Path to project root directory')
    parser.add_argument('--port', type=int, default=8082, help='Port to run server on (default: 8082)')
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root)
    if not project_root.exists():
        print(f"Project root does not exist: {project_root}")
        sys.exit(1)
    
    init_server(project_root)
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)