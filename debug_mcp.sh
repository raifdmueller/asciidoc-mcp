#!/bin/bash
echo "MCP Debug Start: $(date)" >> /tmp/mcp_debug.log
echo "Working Directory: $(pwd)" >> /tmp/mcp_debug.log  
echo "Python Path: $(/usr/bin/python3 --version)" >> /tmp/mcp_debug.log
echo "Args: $*" >> /tmp/mcp_debug.log
exec /usr/bin/python3 "$@" 2>&1 >> /tmp/mcp_debug.log