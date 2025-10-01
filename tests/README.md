# Tests

This directory contains all test files:

## Test Suites
- `test_new_features.py` - Main TDD test suite (18 tests)
- `test_web_server.py` - Web server API tests (10 tests)  
- `test_right_panel_codemirror.py` - Right panel CodeMirror tests (4 tests)
- `test_basic.py` - Basic functionality tests
- `comprehensive_test.py` - Legacy comprehensive test suite

## Test Utilities
- `test_coverage_analysis.py` - Coverage analysis tool
- `test_web_interface_bugs.py` - Web interface bug tests
- `debug_structure.py` - Structure debugging utility

## Running Tests
```bash
# From project root
cd tests
../venv/bin/python test_new_features.py
../venv/bin/python test_web_server.py  
../venv/bin/python test_right_panel_codemirror.py
```