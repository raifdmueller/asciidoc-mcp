# Agent Guidelines for asciidoc-mcp-q

## Build/Test Commands
- **Run all tests:** `pytest`
- **Run single test:** `pytest tests/test_file.py::test_function`
- **Run with coverage:** `pytest --cov=src`
- **Run specific test pattern:** `pytest -k "pattern"`
- **Run by marker:** `pytest -m unit` (markers: unit, integration, slow, web, parser, watcher)

## Code Style Guidelines
- **Imports:** Standard library → third-party → local (src.module_name)
- **Type hints:** Always use typing module annotations (Dict, List, Optional, Tuple)
- **File paths:** Use pathlib.Path objects, not strings
- **Classes:** Use dataclasses for data structures
- **Docstrings:** Include for public methods and classes
- **Error handling:** Specific exceptions with descriptive messages
- **Naming:** snake_case for functions/variables, PascalCase for classes
- **Architecture:** Dependency injection pattern, modular components

## Development
- **Python:** 3.8+ required
- **Dependencies:** Install with `pip install -r requirements.txt`
- **Testing:** pytest.ini configures test discovery and coverage reporting
- **Structure:** Core logic in src/, tests in tests/, async support with pytest-asyncio