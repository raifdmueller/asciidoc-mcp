#!/bin/bash

# MCP Documentation Server Startup Script

PROJECT_ROOT=${1:-.}

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "Error: Project root directory does not exist: $PROJECT_ROOT"
    exit 1
fi

echo "Starting MCP Documentation Server for project: $PROJECT_ROOT"
echo "Use Ctrl+C to stop the server"

cd "$(dirname "$0")"
python3 ../src/mcp_server.py "$PROJECT_ROOT"
