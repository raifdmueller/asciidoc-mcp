# Repository Structure and Architecture

## Directory Structure
```
/home/rdmueller/projects/asciidoc-mcp-q/
├── src/                          # Core implementation
│   ├── document_parser.py        # Document parsing engine
│   ├── mcp_server.py            # MCP protocol server
│   ├── web_server.py            # Web interface (FastAPI)
│   ├── diff_engine.py           # Change detection
│   ├── file_watcher.py          # File monitoring
│   └── content_editor.py        # Content modification
├── test_new_features.py         # TDD test suite (18 tests)
├── test_web_server.py           # Web server tests (7 tests)
├── test_coverage_analysis.py    # Coverage monitoring
├── comprehensive_test.py        # Legacy test suite
├── test_basic.py               # Basic functionality tests
├── start_server.sh             # MCP server startup
├── start_web_server.sh         # Web server startup
├── mcp_config.json            # MCP configuration example
├── todos.adoc                 # Current requirements and TODOs
├── SESSION_SUMMARY.md         # Latest session summary
├── AmazonQ.md                 # Project overview for Amazon Q
├── README.md                  # Basic project documentation
├── manual.adoc                # Comprehensive user manual (4,500+ lines)
├── testreport.adoc           # Detailed test report (2,000+ lines)
├── arc42.adoc                # Main architecture document
├── 01_introduction.adoc      # Arc42 chapter 1
├── 02_constraints.adoc       # Arc42 chapter 2
├── ...                       # Other arc42 chapters (03-12)
├── test-docs/                # Test documentation directory
├── venv/                     # Python virtual environment
└── .serena/                  # Serena configuration
```

## Core Components Architecture

### 1. DocumentParser (`src/document_parser.py`)
- **Purpose:** Parse AsciiDoc and Markdown files
- **Features:** Include resolution, section hierarchy extraction
- **Dependencies:** Handles include directives up to 4 levels deep

### 2. MCPDocumentationServer (`src/mcp_server.py`)
- **Purpose:** MCP protocol implementation
- **API Tools:** get_structure, get_section, search_content, update_section, etc.
- **Integration:** Main entry point for MCP clients

### 3. WebServer (`src/web_server.py`)
- **Purpose:** FastAPI-based web interface
- **Features:** Document visualization, real-time diffs
- **Port:** Default localhost:8082

### 4. DiffEngine (`src/diff_engine.py`)
- **Purpose:** Change detection and visualization
- **Features:** HTML diff generation, before/after comparison

### 5. FileWatcher (`src/file_watcher.py`)
- **Purpose:** Real-time file monitoring
- **Features:** Automatic re-indexing on file changes

### 6. ContentEditor (`src/content_editor.py`)
- **Purpose:** Safe file modification
- **Features:** Section-based editing, backup creation

## Data Flow
1. **Document Discovery:** Find .adoc/.md files in project
2. **Parsing:** Extract section hierarchy and content
3. **Indexing:** Build searchable section database
4. **API Serving:** Respond to MCP protocol requests
5. **Web Interface:** Provide visual document browser
6. **File Watching:** Monitor changes and re-index

## Key Files for Development
- **Main Implementation:** `src/mcp_server.py`
- **Current Requirements:** `todos.adoc`
- **Test Suite:** `test_new_features.py`
- **Session History:** `SESSION_SUMMARY.md`
- **Project Overview:** `AmazonQ.md`