#!/usr/bin/env python3

from pathlib import Path
import sys
import time

from src.document_parser import DocumentParser
from src.mcp_server import MCPDocumentationServer

# Create test document
test_content = """= Main Document

== Introduction
This is the introduction section.

=== Overview
Overview content here.

== Architecture
Architecture details.

=== Components
Component descriptions.

==== Database
Database component info.

== Conclusion
Final thoughts."""

def test_parser():
    print("Testing DocumentParser...")
    
    # Create test file
    test_file = Path("test_doc.adoc")
    test_file.write_text(test_content)
    
    try:
        parser = DocumentParser()
        sections = parser.parse_project(test_file)
        
        print(f"Found {len(sections)} sections:")
        for section_id, section in sections.items():
            print(f"  {section_id}: {section.title} (level {section.level})")
        
        # Test specific section access
        if "main-document.introduction" in sections:
            intro = sections["main-document.introduction"]
            print(f"\nIntroduction content: {intro.content[:50]}...")
        
    finally:
        test_file.unlink()

def test_mcp_server():
    print("\nTesting MCP Server...")
    
    # Create test directory structure
    test_dir = Path("test_project")
    test_dir.mkdir(exist_ok=True)
    
    main_doc = test_dir / "main.adoc"
    main_doc.write_text(test_content)
    
    try:
        server = MCPDocumentationServer(test_dir)
        
        # Test structure
        structure = server.get_structure(max_depth=2)
        print(f"Structure keys: {list(structure.keys())}")
        
        # Test section access
        section = server.get_section("main-document.introduction")
        if section:
            print(f"Section 'introduction': {section['title']}")
        
        # Test search
        results = server.search_content("architecture")
        print(f"Search results for 'architecture': {len(results)} found")
        
        # Test content manipulation
        success = server.update_section_content("main-document.introduction", "Updated introduction content.")
        print(f"Content update: {'success' if success else 'failed'}")
        
        # Test file watching (brief test)
        print("Testing file watching...")
        time.sleep(0.1)  # Brief pause
        
        server.file_watcher.stop()
        
    finally:
        main_doc.unlink()
        test_dir.rmdir()

if __name__ == "__main__":
    test_parser()
    test_mcp_server()
    print("\nBasic tests completed!")
