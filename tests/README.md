# Test Suite Documentation

This directory contains the complete test suite for the asciidoc-mcp project using pytest.

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_document_parser.py -v
```

### Run Tests by Marker
```bash
pytest -m unit              # Run only unit tests
pytest -m integration       # Run only integration tests
pytest -m "not slow"        # Skip slow tests
```

## New Pytest-Style Tests (Issue #13)

### Core Module Tests
- **`test_document_parser.py`** - DocumentParser tests (parsing, includes, hierarchy)
- **`test_file_watcher.py`** - FileWatcher tests (change detection, callbacks)
- **`test_content_editor.py`** - ContentEditor tests (section updates, caching)
- **`test_diff_engine.py`** - DiffEngine tests (diff generation, change detection)

### Shared Fixtures
- **`conftest.py`** - Shared pytest fixtures for all tests

## Existing Test Suites (unittest style)

These tests are automatically discovered and run by pytest:

- `test_new_features.py` - Main TDD test suite (18 tests)
- `test_web_server.py` - Web server API tests (10 tests)
- `test_right_panel_codemirror.py` - Right panel CodeMirror tests (4 tests)
- `test_basic.py` - Basic functionality tests
- `test_coverage_analysis.py` - Coverage analysis tool
- `test_web_interface_bugs.py` - Web interface bug tests
- `test_playwright_navigation.py` - Browser navigation tests
- `test_webserver_startup.py` - Server startup tests
- `comprehensive_test.py` - Legacy comprehensive test suite

## Configuration

### pytest.ini (Project Root)
- Test discovery: `tests/` directory
- Coverage reporting: HTML + terminal
- Asyncio mode: Auto-enabled
- Test markers: unit, integration, slow, web, parser, watcher

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.web` - Web server tests
- `@pytest.mark.parser` - Parser tests
- `@pytest.mark.watcher` - File watcher tests

## Coverage Goals

- **Target:** 70% minimum code coverage
- **Focus:** Core parsing, file ops, content manipulation, change detection

## Running Legacy Tests (Pre-pytest)

```bash
# From project root
cd tests
../venv/bin/python test_new_features.py
../venv/bin/python test_web_server.py
```

Note: All tests can now be run via pytest for unified test execution.