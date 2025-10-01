#!/usr/bin/env python3
import sys
sys.path.append('../src')
from pathlib import Path
from src.mcp_server import MCPDocumentationServer

server = MCPDocumentationServer(Path("."))

print("Testing updated get_main_chapters():")
result = server.get_main_chapters()
print(f"Found {len(result)} sections:")

# Sort by chapter number for display
sorted_chapters = sorted(result.items(), key=lambda x: x[1].get('chapter_number', 999))
for chapter_key, chapter_data in sorted_chapters:
    chapter_num = chapter_data.get('chapter_number', '?')
    if chapter_num == 999:
        print(f"- Document: {chapter_data['title']}")
    else:
        print(f"- Chapter {chapter_num}: {chapter_data['title']}")
