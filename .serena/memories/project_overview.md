# MCP Documentation Server - Project Overview

## Purpose
Model Context Protocol (MCP) server for efficient LLM interaction with large AsciiDoc and Markdown documentation projects. Enables hierarchical navigation, content search, and section-based editing without loading entire files.

## Tech Stack
- **Language:** Python 3
- **Web Framework:** FastAPI (for web interface)
- **Protocol:** Model Context Protocol (MCP)
- **Document Formats:** AsciiDoc (.adoc), Markdown (.md)
- **Testing:** unittest, TDD approach
- **Architecture:** Modular design with separate components

## Key Features
- Hierarchical document navigation
- Include resolution for AsciiDoc
- Content search across documentation
- Section-based content manipulation
- Real-time file watching
- Web interface for visualization
- Token-efficient LLM interaction

## Project Status
- **Production Ready:** ✅ 90% test coverage
- **Core Features:** All PRD requirements implemented
- **Web Interface:** Functional but needs UI/UX improvements
- **Documentation:** Comprehensive (manual.adoc, testreport.adoc)

## Core Components
1. **DocumentParser** - AsciiDoc/Markdown parsing and include resolution
2. **MCPDocumentationServer** - MCP protocol implementation
3. **WebServer** - FastAPI-based visualization interface
4. **DiffEngine** - Change detection and visualization
5. **FileWatcher** - Real-time file monitoring
6. **ContentEditor** - Safe file modification