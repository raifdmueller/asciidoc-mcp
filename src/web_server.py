#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
from typing import Optional

app = FastAPI(title="MCP Documentation Server Web Interface")

# Global server instance (imported at runtime to avoid circular import)
doc_server: Optional["MCPDocumentationServer"] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP Documentation Server</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/diff/diff.min.js"></script>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: Arial, sans-serif; height: 100vh; overflow: hidden; }
            
            .header { 
                height: 60px; 
                background: #f8f9fa; 
                border-bottom: 1px solid #dee2e6; 
                display: flex; 
                align-items: center; 
                padding: 0 20px; 
                position: fixed; 
                top: 0; 
                left: 0; 
                right: 0; 
                z-index: 1000;
            }
            
            .header h1 { margin-right: 20px; font-size: 1.5em; }
            .header button { 
                margin-right: 10px; 
                padding: 8px 16px; 
                border: 1px solid #007acc; 
                background: white; 
                color: #007acc; 
                border-radius: 4px; 
                cursor: pointer; 
            }
            .header button:hover { background: #007acc; color: white; }

            #search-input {
                margin-right: 5px;
                padding: 8px 12px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                width: 250px;
                font-size: 14px;
            }
            #search-input:focus {
                outline: none;
                border-color: #007acc;
            }

            #clear-search {
                margin-left: -30px;
                margin-right: 10px;
                padding: 4px 8px;
                border: none;
                background: transparent;
                color: #666;
                cursor: pointer;
                font-size: 18px;
            }
            #clear-search:hover {
                color: #dc3545;
                background: transparent;
            }

            .search-highlight {
                background-color: #fff3cd !important;
            }

            .search-match {
                font-weight: bold;
            }

            .hidden {
                display: none !important;
            }

            .main-container { 
                display: flex; 
                height: 100vh; 
                padding-top: 60px; 
            }
            
            .left-panel { 
                width: 40%; 
                min-width: 200px; 
                background: #f8f9fa; 
                border-right: 1px solid #dee2e6; 
                overflow-y: auto; 
                padding: 20px; 
            }
            
            .resize-handle { 
                width: 5px; 
                background: #dee2e6; 
                cursor: col-resize; 
                position: relative; 
            }
            .resize-handle:hover { background: #007acc; }
            
            .right-panel { 
                flex: 1; 
                display: flex; 
                flex-direction: column; 
                background: white; 
            }
            
            .right-header { 
                padding: 15px 20px; 
                background: #f8f9fa; 
                border-bottom: 1px solid #dee2e6; 
                font-weight: bold; 
            }
            
            .right-content { 
                flex: 1; 
                padding: 20px; 
                overflow-y: auto; 
            }
            
            .section { 
                margin: 5px 0; 
                border-left: 3px solid #007acc; 
                background: white; 
                border-radius: 4px; 
            }
            .level-1 { border-left-color: #007acc; }
            .level-2 { border-left-color: #28a745; margin-left: 15px; }
            .level-3 { border-left-color: #ffc107; margin-left: 30px; }
            .level-4 { border-left-color: #dc3545; margin-left: 45px; }
            
            .section-title { 
                font-weight: bold; 
                cursor: pointer; 
                padding: 10px 15px; 
                display: flex; 
                align-items: center; 
                transition: background-color 0.2s; 
            }
            .section-title:hover { background-color: #e9ecef; }
            .section-title.selected { background-color: #007acc; color: white; }
            
            .expand-icon { 
                width: 20px; 
                font-family: monospace; 
                color: #666; 
                transition: transform 0.2s; 
                margin-right: 8px; 
            }
            
            .section-children { display: none; }
            .section-children.expanded { display: block; }
            
            .CodeMirror { height: 100%; font-size: 14px; }
            
            .loading { 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                height: 200px; 
                color: #666; 
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>MCP Documentation Server</h1>
            <button onclick="loadStructure()">Load Structure</button>
            <button onclick="loadMetadata()">Load Metadata</button>
            <button onclick="validateStructure()">Validate Structure</button>
            <input type="text" id="search-input" placeholder="Search sections..." />
            <button id="clear-search" style="display: none;">×</button>
        </div>
        
        <div class="main-container">
            <div class="left-panel" id="left-panel">
                <div id="navigation-content">
                    <div class="loading">Click "Load Structure" to begin</div>
                </div>
            </div>
            
            <div class="resize-handle" id="resize-handle"></div>
            
            <div class="right-panel">
                <div class="right-header">Section Content</div>
                <div class="right-content" id="right-content">
                    <div class="loading">Select a section to view content</div>
                </div>
            </div>
        </div>
        
        <script>
            let currentEditor = null;
            let selectedSection = null;
            
            // Resize functionality
            const leftPanel = document.getElementById('left-panel');
            const resizeHandle = document.getElementById('resize-handle');
            let isResizing = false;
            
            // Load saved position from cookie
            const savedWidth = getCookie('panelWidth');
            if (savedWidth) {
                leftPanel.style.width = savedWidth + '%';
            }
            
            resizeHandle.addEventListener('mousedown', (e) => {
                isResizing = true;
                document.addEventListener('mousemove', handleResize);
                document.addEventListener('mouseup', stopResize);
                e.preventDefault();
            });
            
            function handleResize(e) {
                if (!isResizing) return;
                const containerWidth = document.querySelector('.main-container').offsetWidth;
                const newWidth = (e.clientX / containerWidth) * 100;
                if (newWidth > 20 && newWidth < 80) {
                    leftPanel.style.width = newWidth + '%';
                    setCookie('panelWidth', newWidth, 365);
                }
            }
            
            function stopResize() {
                isResizing = false;
                document.removeEventListener('mousemove', handleResize);
                document.removeEventListener('mouseup', stopResize);
            }
            
            async function loadStructure() {
                const navContent = document.getElementById('navigation-content');
                navContent.innerHTML = '<div class="loading">Loading structure...</div>';
                
                try {
                    const response = await fetch('/api/structure');
                    const data = await response.json();
                    displayStructure(data);
                } catch (error) {
                    navContent.innerHTML = '<div class="loading">Error loading structure</div>';
                }
            }
            
            async function loadMetadata() {
                const rightContent = document.getElementById('right-content');
                rightContent.innerHTML = '<div class="loading">Loading metadata...</div>';
                
                try {
                    const response = await fetch('/api/metadata');
                    const data = await response.json();
                    rightContent.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    rightContent.innerHTML = '<div class="loading">Error loading metadata</div>';
                }
            }
            
            async function validateStructure() {
                const rightContent = document.getElementById('right-content');
                rightContent.innerHTML = '<div class="loading">Validating structure...</div>';
                
                try {
                    const response = await fetch('/api/validate');
                    const data = await response.json();
                    rightContent.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    rightContent.innerHTML = '<div class="loading">Error validating structure</div>';
                }
            }
            
            function displayStructure(structure) {
                const navContent = document.getElementById('navigation-content');
                navContent.innerHTML = '';
                
                const sortedSections = Object.entries(structure).sort((a, b) => {
                    const aChapterNum = a[1].chapter_number || 999;
                    const bChapterNum = b[1].chapter_number || 999;
                    
                    if (aChapterNum === bChapterNum) {
                        return a[1].title.localeCompare(b[1].title);
                    }
                    
                    return aChapterNum - bChapterNum;
                });
                
                for (const [id, section] of sortedSections) {
                    const div = createSectionElement(section);
                    navContent.appendChild(div);
                }
            }
            
            function createSectionElement(section) {
                const div = document.createElement('div');
                div.className = `section level-${section.level}`;
                
                const hasChildren = section.children && section.children.length > 0;
                const expandIcon = hasChildren ? '▶' : '•';
                
                const titleDiv = document.createElement('div');
                titleDiv.className = 'section-title';
                titleDiv.innerHTML = `
                    <span class="expand-icon">${expandIcon}</span>
                    <span>${section.title} (${section.children_count || 0})</span>
                `;
                
                titleDiv.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (hasChildren) {
                        toggleSection(section.id, titleDiv);
                    }
                    selectSection(section.id, titleDiv);
                });
                
                div.appendChild(titleDiv);
                
                if (hasChildren) {
                    const childrenDiv = document.createElement('div');
                    childrenDiv.className = 'section-children';
                    childrenDiv.id = `children-${section.id}`;
                    
                    section.children.forEach(child => {
                        const childElement = createSectionElement(child);
                        childrenDiv.appendChild(childElement);
                    });
                    
                    div.appendChild(childrenDiv);
                }
                
                return div;
            }
            
            function toggleSection(sectionId, titleElement) {
                const childrenDiv = document.getElementById(`children-${sectionId}`);
                const expandIcon = titleElement.querySelector('.expand-icon');
                
                if (childrenDiv.classList.contains('expanded')) {
                    childrenDiv.classList.remove('expanded');
                    expandIcon.textContent = '▶';
                } else {
                    childrenDiv.classList.add('expanded');
                    expandIcon.textContent = '▼';
                }
            }
            
            function selectSection(sectionId, titleElement) {
                // Remove previous selection
                if (selectedSection) {
                    selectedSection.classList.remove('selected');
                }
                
                // Add new selection
                titleElement.classList.add('selected');
                selectedSection = titleElement;
                
                // Load content
                loadSectionContent(sectionId);
            }
            
            async function loadSectionContent(sectionId) {
                const rightContent = document.getElementById('right-content');
                rightContent.innerHTML = '<div class="loading">Loading content...</div>';

                try {
                    const response = await fetch(`/api/section/${sectionId}`);
                    const data = await response.json();

                    // Clean up existing CodeMirror instance BEFORE clearing DOM
                    if (currentEditor && typeof currentEditor.toTextArea === 'function') {
                        currentEditor.toTextArea();
                    }

                    // Now it's safe to clear the DOM
                    rightContent.innerHTML = '';

                    currentEditor = CodeMirror(rightContent, {
                        value: data.content || 'No content available',
                        mode: 'text/plain',
                        readOnly: true,
                        lineNumbers: true,
                        lineWrapping: true,
                        theme: 'default'
                    });

                } catch (error) {
                    console.error('Error loading section content:', error);
                    rightContent.innerHTML = '<div class="loading">Error loading content</div>';
                }
            }

            // Search functionality
            let searchDebounceTimer = null;
            const searchInput = document.getElementById('search-input');
            const clearButton = document.getElementById('clear-search');

            // Event listeners for search
            searchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Escape') {
                    clearSearch();
                    return;
                }

                const searchTerm = searchInput.value.trim();

                // Show/hide clear button
                if (searchTerm) {
                    clearButton.style.display = 'inline-block';
                } else {
                    clearButton.style.display = 'none';
                }

                // Debounced filtering
                clearTimeout(searchDebounceTimer);
                searchDebounceTimer = setTimeout(() => {
                    filterSections(searchTerm);
                }, 300);
            });

            clearButton.addEventListener('click', clearSearch);

            function clearSearch() {
                searchInput.value = '';
                clearButton.style.display = 'none';
                filterSections('');
            }

            function filterSections(searchTerm) {
                const navContent = document.getElementById('navigation-content');
                const allSections = navContent.querySelectorAll('.section');

                if (!searchTerm) {
                    // Show all sections, remove highlights
                    allSections.forEach(section => {
                        section.classList.remove('hidden', 'search-highlight', 'search-match');
                    });
                    return;
                }

                const lowerSearchTerm = searchTerm.toLowerCase();

                // Process each section
                allSections.forEach(section => {
                    const shouldShow = isMatchOrHasMatchingChild(section, lowerSearchTerm);

                    if (shouldShow) {
                        section.classList.remove('hidden');
                    } else {
                        section.classList.add('hidden');
                    }
                });
            }

            function isMatchOrHasMatchingChild(sectionElement, searchTerm) {
                // Get section title text
                const titleElement = sectionElement.querySelector('.section-title span:last-child');
                if (!titleElement) return false;

                const titleText = titleElement.textContent.toLowerCase();
                const isMatch = titleText.includes(searchTerm);

                // Apply highlight if match
                if (isMatch) {
                    sectionElement.classList.add('search-highlight');
                    titleElement.classList.add('search-match');
                } else {
                    sectionElement.classList.remove('search-highlight');
                    titleElement.classList.remove('search-match');
                }

                // Check if any child matches (recursive)
                const childrenContainer = sectionElement.querySelector('.section-children');
                if (childrenContainer) {
                    const childSections = Array.from(childrenContainer.children);
                    const hasMatchingChild = childSections.some(child =>
                        isMatchOrHasMatchingChild(child, searchTerm)
                    );

                    return isMatch || hasMatchingChild;
                }

                return isMatch;
            }

            // Cookie functions
            function setCookie(name, value, days) {
                const expires = new Date();
                expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
                document.cookie = name + '=' + value + ';expires=' + expires.toUTCString() + ';path=/';
            }
            
            function getCookie(name) {
                const nameEQ = name + '=';
                const ca = document.cookie.split(';');
                for (let i = 0; i < ca.length; i++) {
                    let c = ca[i];
                    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
                }
                return null;
            }
        </script>
    </body>
    </html>
    """

@app.get("/api/structure")
async def get_structure():
    """Get document structure - shows main chapters for arc42 documents"""
    if not doc_server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    # Use main chapters method for better arc42 support
    return doc_server.get_main_chapters()

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

@app.get("/api/section/{section_id:path}")
async def get_section(section_id: str):
    """Get specific section"""
    if not doc_server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    if section_id not in doc_server.sections:
        raise HTTPException(status_code=404, detail="Section not found")
    
    section = doc_server.sections[section_id]
    return {
        'id': section.id,
        'title': section.title,
        'level': section.level,
        'content': section.content,
        'children': section.children
    }

def init_server(project_root: Path):
    """Initialize the documentation server"""
    global doc_server
    from .mcp_server import MCPDocumentationServer
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