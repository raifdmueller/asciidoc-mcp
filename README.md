# MCP Documentation Server

A Model Context Protocol (MCP) server for efficient LLM interaction with large AsciiDoc and Markdown documentation projects.

## Features

- **Hierarchical Navigation**: Access document structure without loading entire files
- **Include Resolution**: Automatically resolves AsciiDoc include directives
- **Content Search**: Search across all documentation content
- **Structured Access**: Get specific sections by path notation
- **Content Manipulation**: Update and insert sections directly
- **File Watching**: Automatic updates when files change
- **Web Interface**: Visual document structure browser
- **Token Efficient**: Only load the content you need

## Quick Start

1. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Test the implementation:**
   ```bash
   python3 test_basic.py
   ```

3. **Configure in Claude Code:**
   Add to your `~/.claude.json`:
   ```json
   {
     "mcpServers": {
       "asciidoc-docs-server": {
         "command": "/path/to/asciidoc-mcp/venv/bin/python3",
         "args": ["-m", "src.mcp_server", "/path/to/your/docs"],
         "env": {
           "ENABLE_WEBSERVER": "true"
         }
       }
     }
   }
   ```

4. **Use the tools:**
   The server will automatically:
   - Start on first MCP initialize request
   - Launch a web interface on http://localhost:8080 (or next available port)
   - Open your default browser to view the documentation structure
   - Provide MCP tools for document navigation and manipulation

## API Tools

### Navigation Tools

#### `get_structure`
Get document table of contents up to specified depth.
```json
{"max_depth": 3}
```

#### `get_section`
Get specific section content by path.
```json
{"path": "introduction.overview"}
```

#### `get_sections`
Get all sections at a specific level.
```json
{"level": 2}
```

#### `search_content`
Search for content across all documentation.
```json
{"query": "architecture"}
```

### Content Manipulation Tools

#### `update_section`
Update section content directly in source files.
```json
{"path": "introduction.overview", "content": "New content here"}
```

#### `insert_section`
Insert new section relative to existing section.
```json
{
  "parent_path": "introduction", 
  "title": "New Section", 
  "content": "Section content",
  "position": "append"
}
```

## Web API Endpoints

The server provides REST API endpoints for the web interface and external integration:

### Navigation Endpoints

#### `GET /api/structure`
Get complete document structure with files and sections.
```bash
curl http://localhost:8080/api/structure
```

Response:
```json
{
  "document.adoc": {
    "file_info": {...},
    "sections": [...]
  }
}
```

#### `GET /api/section/{section_id}`
Get specific section content with optional full document context.

**Parameters:**
- `context`: Optional parameter controlling response format
  - `"section"` (default): Returns only the specific section content
  - `"full"`: Returns the complete document with section positioning metadata

**Basic usage:**
```bash
curl http://localhost:8080/api/section/document.section-1
```

**Enhanced usage (Issue #57):**
```bash
curl http://localhost:8080/api/section/document.section-1?context=full
```

**Response formats:**

*Standard response (`context=section`):*
```json
{
  "id": "document.section-1",
  "title": "Section Title",
  "level": 2,
  "content": "Section content only...",
  "children": [...],
  "source_file": "/path/to/document.adoc",
  "line_start": 10,
  "line_end": 25
}
```

*Full context response (`context=full`):*
```json
{
  "id": "document.section-1",
  "title": "Section Title", 
  "level": 2,
  "content": "Section content only...",
  "children": [...],
  "source_file": "/path/to/document.adoc",
  "line_start": 10,
  "line_end": 25,
  "full_content": "Complete document content...",
  "section_position": {
    "line_start": 10,
    "line_end": 25
  }
}
```

The `context=full` parameter enables advanced navigation features:
- **Complete document view**: Shows the section within its full document context
- **Auto-scrolling**: Frontend can use `section_position` to scroll to the specific section
- **Section highlighting**: Visual emphasis of the selected section within the document

### Metadata Endpoints

#### `GET /api/metadata`
Get project metadata and document information.
```bash
curl http://localhost:8080/api/metadata
```

#### `GET /api/dependencies`
Get document include dependencies and cross-references.
```bash
curl http://localhost:8080/api/dependencies
```

#### `GET /api/validate`
Validate document structure consistency.
```bash
curl http://localhost:8080/api/validate
```

## Path Notation

Sections are accessed using dot notation:
- `"introduction"` - Section with title "Introduction"
- `"introduction.overview"` - Subsection "Overview" under "Introduction"
- `"1.2.3"` - Third subsection of second section of first chapter

## Supported Formats

- **AsciiDoc**: `.adoc`, `.asciidoc` files
- **Markdown**: `.md` files
- **Includes**: AsciiDoc `include::file.adoc[]` directives

## Configuration

- **Include Depth**: Maximum 4 levels (configurable)
- **File Discovery**: Automatically finds main documentation files
- **File Watching**: Real-time updates on file changes
- **Web Interface**: Available on localhost:8080 (configurable)

## Project Structure

```
src/
├── document_parser.py    # Core parsing engine
├── mcp_server.py        # MCP protocol implementation
├── file_watcher.py      # File change monitoring
├── content_editor.py    # Content manipulation
├── web_server.py        # Web visualization (auto-starts with MCP server)
test_basic.py            # Basic functionality tests
.mcp.json               # MCP configuration example
```

## Development

The implementation follows the PRD requirements with minimal, focused code. Core components:

1. **DocumentParser**: Handles AsciiDoc/Markdown parsing and include resolution
2. **MCPDocumentationServer**: Implements the MCP protocol and API tools, auto-starts webserver
3. **FileWatcher**: Monitors file changes for automatic updates
4. **ContentEditor**: Handles direct file modifications
5. **WebServer**: Provides visual document structure browser (runs as daemon thread)
6. **Section**: Data structure for hierarchical document representation

## Testing

Run the basic test suite:
```bash
python3 test_basic.py
```

This creates temporary test documents and verifies:
- Document parsing and structure extraction
- Section hierarchy and path generation
- MCP server API functionality
- Content search capabilities
- Content manipulation features
- File watching capabilities
