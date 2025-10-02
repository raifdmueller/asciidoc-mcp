# Development Plan: asciidoc-mcp-q (main branch)

*Generated on 2025-10-02 by Vibe Feature MCP*
*Workflow: [epcc](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/epcc)*

## Goal
**Issue #13: Add pytest test infrastructure**

Setup comprehensive test infrastructure for the asciidoc-mcp project to enable safe refactoring and prevent regressions. This includes pytest installation, test structure creation, and initial test coverage for all 6 core modules.

## Explore
### Tasks
- [x] Analyze current test situation
- [x] Review test files and frameworks
- [x] Check requirements.txt for dependencies
- [x] Check for pytest configuration

### Findings

**Current Test Situation:**
- ✅ **9 test files exist** in `tests/` directory
- ❌ **pytest NOT installed** - tests use mix of unittest and standalone functions
- ❌ **No pytest.ini** or pyproject.toml configuration
- ❌ **pytest NOT in requirements.txt**

**Existing Test Files:**
1. `test_basic.py` - Standalone functions (not unittest)
2. `comprehensive_test.py` - Standalone test runner
3. `test_web_server.py` - unittest.TestCase style
4. `test_coverage_analysis.py` - unittest.TestCase style
5. `test_new_features.py` - unittest.TestCase style
6. `test_playwright_navigation.py` - unittest.TestCase style
7. `test_right_panel_codemirror.py` - unittest.TestCase style
8. `test_web_interface_bugs.py` - unittest.TestCase style
9. `test_webserver_startup.py` - unittest.TestCase style

**Dependencies Status:**
- Current: fastapi, uvicorn, httpx, watchdog
- Missing: pytest, pytest-cov, pytest-asyncio

**Test Coverage:**
- ✅ Web server (multiple test files)
- ✅ MCP server basics (test_basic.py)
- ❌ No dedicated tests for: document_parser.py, file_watcher.py, content_editor.py, diff_engine.py

### Completed
- [x] Created development plan file
- [x] Analyzed existing test infrastructure
- [x] Identified unittest usage (6 files)
- [x] Confirmed pytest not installed
- [x] Identified missing test coverage

## Plan
### Phase Entrance Criteria:
- [x] Current test situation analyzed
- [x] Existing test patterns understood
- [x] Module dependencies mapped
- [x] Test strategy defined

### Strategy

**Goal:** Add pytest infrastructure while preserving existing tests

**Approach: Hybrid Strategy**
1. **Install pytest** - Add to requirements.txt with plugins
2. **Keep existing tests** - pytest runs unittest.TestCase automatically
3. **Add pytest.ini** - Configuration for test discovery and coverage
4. **Fill coverage gaps** - Create pytest-style tests for 4 untested modules
5. **Add test documentation** - README in tests/ directory

### Implementation Plan

#### 1. Pytest Installation & Configuration

**requirements.txt additions:**
```
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-asyncio>=0.23.0
pytest-xdist>=3.5.0  # Parallel test execution
```

**pytest.ini configuration:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
asyncio_mode = auto
```

#### 2. New Test Files (Pytest Style)

**tests/test_document_parser.py** (~150 lines)
- Test section parsing
- Test include resolution
- Test hierarchy building
- Test error handling

**tests/test_file_watcher.py** (~100 lines)
- Test file change detection
- Test callback triggering
- Test multiple file changes
- Test start/stop functionality

**tests/test_content_editor.py** (~100 lines)
- Test section updates
- Test section inserts
- Test file modifications
- Test error cases

**tests/test_diff_engine.py** (~100 lines)
- Test diff generation
- Test HTML output
- Test change detection
- Test edge cases

#### 3. Test Structure Organization

**Keep existing structure:**
```
tests/
├── README.md                          # NEW: Test documentation
├── pytest.ini                         # NEW: Pytest config (move to root)
├── conftest.py                        # NEW: Shared fixtures
├── test_basic.py                      # KEEP: Works with pytest
├── comprehensive_test.py              # KEEP: Standalone runner
├── test_web_server.py                 # KEEP: unittest → pytest compatible
├── test_coverage_analysis.py          # KEEP: unittest → pytest compatible
├── test_new_features.py               # KEEP: unittest → pytest compatible
├── test_playwright_navigation.py      # KEEP: unittest → pytest compatible
├── test_right_panel_codemirror.py     # KEEP: unittest → pytest compatible
├── test_web_interface_bugs.py         # KEEP: unittest → pytest compatible
├── test_webserver_startup.py          # KEEP: unittest → pytest compatible
├── test_document_parser.py            # NEW: Pytest style
├── test_file_watcher.py               # NEW: Pytest style
├── test_content_editor.py             # NEW: Pytest style
└── test_diff_engine.py                # NEW: Pytest style
```

#### 4. Shared Fixtures (conftest.py)

Common fixtures for all tests:
- `temp_project_dir` - Temporary directory with sample docs
- `sample_adoc_content` - Reusable test content
- `mock_parser` - Pre-configured DocumentParser
- `test_sections` - Sample section data

### Tasks
- [ ] Update requirements.txt with pytest dependencies
- [ ] Create pytest.ini configuration file
- [ ] Create tests/conftest.py with shared fixtures
- [ ] Create test_document_parser.py
- [ ] Create test_file_watcher.py
- [ ] Create test_content_editor.py
- [ ] Create test_diff_engine.py
- [ ] Create tests/README.md documentation
- [ ] Verify all existing tests still work with pytest
- [ ] Run pytest and verify coverage

### Completed
*None yet*

## Code
### Phase Entrance Criteria:
- [x] Test infrastructure plan approved
- [x] pytest dependencies defined
- [x] Test structure designed
- [x] Test file templates ready

### Tasks
- [x] Update requirements.txt with pytest dependencies
- [x] Create pytest.ini configuration file
- [x] Create tests/conftest.py with shared fixtures
- [x] Create test_document_parser.py (14 tests)
- [x] Create test_file_watcher.py (10 tests, 4 skipped)
- [x] Create test_content_editor.py (10 tests)
- [x] Create test_diff_engine.py (17 tests)
- [x] Create tests/README.md documentation
- [x] Install pytest and run tests
- [x] Fix API mismatches in tests
- [x] Verify all tests pass

### Results
- **Tests Created:** 51 tests total (47 passing, 4 skipped)
- **Coverage Achieved:**
  - document_parser.py: 100%
  - file_watcher.py: 81%
  - diff_engine.py: 69%
  - content_editor.py: 61%
  - **Average: 77.75%** (exceeds 70% target)

### Completed
- [x] All test infrastructure implemented
- [x] All 4 new test files created
- [x] Tests passing successfully
- [x] Coverage target exceeded

## Commit
### Phase Entrance Criteria:
- [x] All test files created
- [x] pytest runs successfully
- [x] Initial tests passing
- [x] Code coverage measured

### Tasks
- [x] Check for debug statements and TODOs
- [x] Update development plan
- [ ] Create git commit
- [ ] Push to remote
- [ ] Update GitHub Issue #13

### Completed
- [x] Code cleanup verified (no debug statements)
- [x] Development plan updated with results

## Key Decisions

### 1. Hybrid Strategy: Keep Existing Tests
**Decision:** Preserve all 9 existing test files rather than rewriting them
**Rationale:** pytest automatically runs unittest.TestCase tests, so no migration needed
**Benefit:** Zero risk of losing existing test coverage, faster implementation

### 2. Pytest-Style for New Tests Only
**Decision:** Write new tests (4 modules) in pytest style with fixtures
**Rationale:** Modern pytest features (fixtures, parametrize) are more maintainable
**Benefit:** Gradual migration path, showcases pytest benefits

### 3. Coverage Target: 70%
**Decision:** Target 70% code coverage as acceptance criteria
**Rationale:** Realistic goal given time constraints, focus on critical paths
**Benefit:** Achievable milestone, provides safety for refactoring Issues #11/#12

### 4. pytest.ini at Project Root
**Decision:** Place pytest.ini in project root, not in tests/
**Rationale:** Standard pytest convention, easier CI/CD integration
**Benefit:** Better discoverability, follows best practices

## Notes
*Additional context and observations*

---
*This plan is maintained by the LLM. Tool responses provide guidance on which section to focus on and what tasks to work on.*
