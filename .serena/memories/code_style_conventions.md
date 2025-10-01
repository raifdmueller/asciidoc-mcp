# Code Style and Conventions

## Python Style
- **PEP 8 compliant** - Standard Python style guide
- **Type hints:** Used throughout the codebase
- **Docstrings:** Present for classes and methods
- **Import organization:** Standard library, third-party, local imports

## Naming Conventions
- **Classes:** PascalCase (e.g., `MCPDocumentationServer`, `DocumentParser`)
- **Functions/Methods:** snake_case (e.g., `get_structure`, `parse_document`)
- **Variables:** snake_case (e.g., `project_root`, `section_id`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `MAX_DEPTH`)

## Code Organization
- **Modular design:** Each component in separate file
- **Single responsibility:** Each class has clear purpose
- **Minimal dependencies:** Only necessary imports
- **Error handling:** Proper exception handling throughout

## Documentation Style
- **AsciiDoc format** for main documentation
- **Markdown** for README and session summaries
- **Inline comments** for complex logic
- **API documentation** in docstrings

## Testing Conventions
- **TDD approach:** Tests written first
- **unittest framework:** Standard Python testing
- **Descriptive test names:** Clear test purpose
- **Setup/teardown:** Proper test isolation
- **90% coverage target:** High test coverage maintained

## File Structure
```
src/                    # Core implementation
├── document_parser.py  # Document parsing
├── mcp_server.py      # MCP protocol
├── web_server.py      # Web interface
├── diff_engine.py     # Change detection
├── file_watcher.py    # File monitoring
└── content_editor.py  # Content editing

test_*.py              # Test files
start_*.sh             # Startup scripts
*.adoc                 # AsciiDoc documentation
```

## Design Patterns
- **Server pattern:** MCP protocol implementation
- **Observer pattern:** File watching
- **Strategy pattern:** Different document parsers
- **Factory pattern:** Section creation
- **Singleton pattern:** Server instance management