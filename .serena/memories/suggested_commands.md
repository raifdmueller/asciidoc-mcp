# Suggested Commands - MCP Documentation Server

## Development Commands

### Testing
```bash
# Run TDD test suite (18 tests)
.venv/bin/python test_new_features.py

# Run web server tests (7 tests)  
.venv/bin/python test_web_server.py

# Run basic functionality tests
python3 test_basic.py

# Check test coverage
python3 test_coverage_analysis.py

# Run comprehensive legacy tests
python3 comprehensive_test.py
```

### Server Operations
```bash
# Start MCP server
./start_server.sh [project_root]
./start_server.sh .

# Start web interface
./start_web_server.sh [project_root]
./start_web_server.sh .
# Access: http://localhost:8082

# Alternative web server (legacy)
./start_web.sh [project_root] [port]
```

### Development Tools
```bash
# Debug document structure
python3 debug_structure.py

# Check project structure
ls -la src/
ls -la test-docs/

# View logs
tail -f web_server.log
```

### Git Operations
```bash
# Standard git workflow
git status
git add .
git commit -m "Description"
git push

# View recent changes
git log --oneline -10
git diff HEAD~1
```

### File Operations
```bash
# Find files
find . -name "*.adoc" -type f
find . -name "*.py" -type f

# Search content
grep -r "pattern" src/
grep -r "pattern" *.adoc

# List directory structure
tree -I 'venv|.pytest_cache|__pycache__'
```

### Python Environment
```bash
# Activate virtual environment (if exists)
source venv/bin/activate

# Install dependencies (if requirements.txt exists)
pip install -r requirements.txt

# Run Python modules
python3 -m src.mcp_server
python3 -c "import src.document_parser; print('OK')"
```