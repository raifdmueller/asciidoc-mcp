# Task Completion Checklist

## When a Task is Completed

### 1. Testing
```bash
# Run all test suites
.venv/bin/python test_new_features.py
.venv/bin/python test_web_server.py
python3 test_basic.py

# Check test coverage
python3 test_coverage_analysis.py
# Target: Maintain 90%+ coverage
```

### 2. Code Quality
- **Type hints:** Ensure all new functions have type hints
- **Docstrings:** Add docstrings for new classes/methods
- **Error handling:** Proper exception handling
- **Code style:** Follow PEP 8 conventions

### 3. Documentation Updates
```bash
# Update relevant documentation
vim todos.adoc          # Update status of completed items
vim SESSION_SUMMARY.md  # Document changes made
vim README.md          # Update if API changes
```

### 4. Integration Testing
```bash
# Test MCP server functionality
./start_server.sh .
# Test in separate terminal with MCP client

# Test web interface
./start_web_server.sh .
# Access http://localhost:8082 and verify functionality
```

### 5. Git Workflow
```bash
# Stage and commit changes
git add .
git status
git commit -m "Descriptive commit message"

# Optional: Push to remote
git push origin main
```

### 6. Verification Steps
- [ ] All tests pass
- [ ] Test coverage maintained (90%+)
- [ ] MCP server starts without errors
- [ ] Web interface loads correctly
- [ ] Documentation updated
- [ ] Changes committed to git

### 7. Session Documentation
- Update `SESSION_SUMMARY.md` with:
  - What was accomplished
  - Any issues encountered
  - Next steps
  - Important files changed

### 8. Clean Up
```bash
# Remove temporary files
rm -f *.log
rm -rf __pycache__/
rm -rf .pytest_cache/

# Check for any uncommitted changes
git status
```

## Quality Gates
- **No failing tests**
- **No regression in functionality**
- **Documentation reflects changes**
- **Code follows project conventions**
- **All changes committed**