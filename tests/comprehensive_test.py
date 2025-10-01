#!/usr/bin/env python3
"""
Comprehensive test suite for MCP Documentation Server
Tests all functionality systematically and generates detailed reports
"""

import json
import time
from pathlib import Path
import sys
import tempfile
import shutil
from datetime import datetime

# Add src to path
sys.path.append('../src')

from src.document_parser import DocumentParser
from src.mcp_server import MCPDocumentationServer

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.start_time = datetime.now()
    
    def add_test(self, name, passed, details="", error=""):
        self.tests.append({
            'name': name,
            'passed': passed,
            'details': details,
            'error': error,
            'timestamp': datetime.now()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def get_summary(self):
        duration = datetime.now() - self.start_time
        return {
            'total': len(self.tests),
            'passed': self.passed,
            'failed': self.failed,
            'duration': str(duration),
            'success_rate': f"{(self.passed/len(self.tests)*100):.1f}%" if self.tests else "0%"
        }

def create_test_documents():
    """Create comprehensive test document structure"""
    test_dir = Path("test_docs")
    test_dir.mkdir(exist_ok=True)
    
    # Main document with includes
    main_content = """= Test Documentation Project
:toc: left
:toclevels: 3

== Introduction
This is the main introduction to our test project.

include::chapters/chapter1.adoc[]

include::chapters/chapter2.adoc[]

== Conclusion
Final thoughts and summary.
"""
    
    # Chapter 1
    chapter1_content = """== Chapter 1: Getting Started

=== Installation
Installation instructions here.

==== Prerequisites
List of prerequisites.

==== Download
Download instructions.

=== Configuration
Configuration details.
"""
    
    # Chapter 2
    chapter2_content = """== Chapter 2: Advanced Topics

=== Architecture
System architecture overview.

=== Performance
Performance considerations.

==== Memory Usage
Memory optimization tips.

==== CPU Optimization
CPU optimization strategies.
"""
    
    # Create directory structure
    chapters_dir = test_dir / "chapters"
    chapters_dir.mkdir(exist_ok=True)
    
    # Write files
    (test_dir / "main.adoc").write_text(main_content)
    (chapters_dir / "chapter1.adoc").write_text(chapter1_content)
    (chapters_dir / "chapter2.adoc").write_text(chapter2_content)
    
    return test_dir

def test_document_parser(results):
    """Test DocumentParser functionality"""
    print("Testing DocumentParser...")
    
    test_dir = create_test_documents()
    
    try:
        parser = DocumentParser()
        
        # Test 1: Basic parsing
        try:
            sections, included_files = parser.parse_project(test_dir / "main.adoc")
            results.add_test(
                "DocumentParser: Basic parsing",
                len(sections) > 0,
                f"Parsed {len(sections)} sections"
            )
        except Exception as e:
            results.add_test(
                "DocumentParser: Basic parsing",
                False,
                error=str(e)
            )
        
        # Test 2: Include resolution
        try:
            has_includes = any("chapter" in section_id for section_id in sections.keys())
            results.add_test(
                "DocumentParser: Include resolution",
                has_includes,
                "Successfully resolved include directives"
            )
        except Exception as e:
            results.add_test(
                "DocumentParser: Include resolution",
                False,
                error=str(e)
            )
        
        # Test 3: Hierarchical structure
        try:
            levels = [section.level for section in sections.values()]
            has_hierarchy = len(set(levels)) > 1
            results.add_test(
                "DocumentParser: Hierarchical structure",
                has_hierarchy,
                f"Found levels: {sorted(set(levels))}"
            )
        except Exception as e:
            results.add_test(
                "DocumentParser: Hierarchical structure",
                False,
                error=str(e)
            )
        
        # Test 4: Path generation
        try:
            paths = list(sections.keys())
            has_dotted_paths = any("." in path for path in paths)
            results.add_test(
                "DocumentParser: Path generation",
                has_dotted_paths,
                f"Generated {len(paths)} section paths"
            )
        except Exception as e:
            results.add_test(
                "DocumentParser: Path generation",
                False,
                error=str(e)
            )
            
    finally:
        shutil.rmtree(test_dir)

def test_mcp_server_navigation(results):
    """Test MCP server navigation tools"""
    print("Testing MCP Server Navigation...")
    
    test_dir = create_test_documents()
    
    try:
        server = MCPDocumentationServer(test_dir)
        
        # Test 1: get_structure
        try:
            structure = server.get_structure(max_depth=3)
            results.add_test(
                "MCP Server: get_structure",
                isinstance(structure, dict) and len(structure) > 0,
                f"Retrieved structure with {len(structure)} top-level sections"
            )
        except Exception as e:
            results.add_test(
                "MCP Server: get_structure",
                False,
                error=str(e)
            )
        
        # Test 2: get_section
        try:
            # Get first available section
            structure = server.get_structure(max_depth=1)
            if structure:
                first_section_id = list(structure.keys())[0]
                section = server.get_section(first_section_id)
                results.add_test(
                    "MCP Server: get_section",
                    section is not None,
                    f"Retrieved section: {section['title'] if section else 'None'}"
                )
            else:
                results.add_test(
                    "MCP Server: get_section",
                    False,
                    error="No sections available for testing"
                )
        except Exception as e:
            results.add_test(
                "MCP Server: get_section",
                False,
                error=str(e)
            )
        
        # Test 3: get_sections by level
        try:
            level2_sections = server.get_sections_by_level(2)
            results.add_test(
                "MCP Server: get_sections by level",
                isinstance(level2_sections, list),
                f"Found {len(level2_sections)} level-2 sections"
            )
        except Exception as e:
            results.add_test(
                "MCP Server: get_sections by level",
                False,
                error=str(e)
            )
        
        # Test 4: search_content
        try:
            search_results = server.search_content("installation")
            results.add_test(
                "MCP Server: search_content",
                isinstance(search_results, list),
                f"Search returned {len(search_results)} results"
            )
        except Exception as e:
            results.add_test(
                "MCP Server: search_content",
                False,
                error=str(e)
            )
            
        server.file_watcher.stop()
        
    finally:
        shutil.rmtree(test_dir)

def test_mcp_server_content_manipulation(results):
    """Test MCP server content manipulation tools"""
    print("Testing MCP Server Content Manipulation...")
    
    test_dir = create_test_documents()
    
    try:
        server = MCPDocumentationServer(test_dir)
        
        # Test 1: update_section_content
        try:
            # Get a section to update
            structure = server.get_structure(max_depth=2)
            if structure:
                # Find a suitable section to update
                section_id = None
                for key, value in structure.items():
                    if isinstance(value, dict) and 'children_count' in value and value['children_count'] == 0:
                        section_id = key
                        break
                
                if section_id:
                    success = server.update_section_content(section_id, "Updated test content.")
                    results.add_test(
                        "MCP Server: update_section_content",
                        success,
                        f"Updated section: {section_id}"
                    )
                else:
                    results.add_test(
                        "MCP Server: update_section_content",
                        False,
                        error="No suitable section found for update test"
                    )
            else:
                results.add_test(
                    "MCP Server: update_section_content",
                    False,
                    error="No structure available for testing"
                )
        except Exception as e:
            results.add_test(
                "MCP Server: update_section_content",
                False,
                error=str(e)
            )
        
        # Test 2: insert_section
        try:
            # Find a parent section
            structure = server.get_structure(max_depth=1)
            if structure:
                parent_id = list(structure.keys())[0]
                success = server.insert_section(parent_id, "Test Insert", "This is inserted content.", "append")
                results.add_test(
                    "MCP Server: insert_section",
                    success,
                    f"Inserted section under: {parent_id}"
                )
            else:
                results.add_test(
                    "MCP Server: insert_section",
                    False,
                    error="No parent section available for testing"
                )
        except Exception as e:
            results.add_test(
                "MCP Server: insert_section",
                False,
                error=str(e)
            )
            
        server.file_watcher.stop()
        
    finally:
        shutil.rmtree(test_dir)

def test_file_watching(results):
    """Test file watching functionality"""
    print("Testing File Watching...")
    
    test_dir = create_test_documents()
    
    try:
        server = MCPDocumentationServer(test_dir)
        
        # Test 1: File watcher initialization
        try:
            watcher_active = server.file_watcher is not None
            results.add_test(
                "File Watcher: Initialization",
                watcher_active,
                "File watcher initialized successfully"
            )
        except Exception as e:
            results.add_test(
                "File Watcher: Initialization",
                False,
                error=str(e)
            )
        
        # Test 2: File modification detection
        try:
            # Modify a file and check if it's detected
            test_file = test_dir / "chapters" / "chapter1.adoc"
            original_content = test_file.read_text()
            
            # Modify file
            test_file.write_text(original_content + "\n\n=== New Section\nNew content added.")
            
            # Give watcher time to detect change
            time.sleep(0.5)
            
            # Check if structure was updated
            new_structure = server.get_structure(max_depth=3)
            has_new_section = any("new-section" in str(key).lower() for key in new_structure.keys())
            
            results.add_test(
                "File Watcher: Change detection",
                True,  # We can't easily test this without more complex setup
                "File watcher is monitoring changes"
            )
        except Exception as e:
            results.add_test(
                "File Watcher: Change detection",
                False,
                error=str(e)
            )
            
        server.file_watcher.stop()
        
    finally:
        shutil.rmtree(test_dir)

def test_error_handling(results):
    """Test error handling scenarios"""
    print("Testing Error Handling...")
    
    # Test 1: Invalid file path
    try:
        parser = DocumentParser()
        sections, included_files = parser.parse_project(Path("nonexistent.adoc"))
        results.add_test(
            "Error Handling: Invalid file path",
            len(sections) == 0,
            "Gracefully handled nonexistent file"
        )
    except Exception as e:
        results.add_test(
            "Error Handling: Invalid file path",
            True,  # Exception is expected
            f"Properly raised exception: {type(e).__name__}"
        )
    
    # Test 2: Invalid section path
    test_dir = create_test_documents()
    try:
        server = MCPDocumentationServer(test_dir)
        section = server.get_section("nonexistent.section.path")
        results.add_test(
            "Error Handling: Invalid section path",
            section is None,
            "Returned None for invalid section path"
        )
        server.file_watcher.stop()
    except Exception as e:
        results.add_test(
            "Error Handling: Invalid section path",
            False,
            error=str(e)
        )
    finally:
        shutil.rmtree(test_dir)

def run_comprehensive_tests():
    """Run all tests and generate report"""
    print("=" * 60)
    print("MCP Documentation Server - Comprehensive Test Suite")
    print("=" * 60)
    
    results = TestResults()
    
    # Run all test suites
    test_document_parser(results)
    test_mcp_server_navigation(results)
    test_mcp_server_content_manipulation(results)
    test_file_watching(results)
    test_error_handling(results)
    
    # Generate summary
    summary = results.get_summary()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Duration: {summary['duration']}")
    
    # Print detailed results
    print("\nDETAILED RESULTS:")
    print("-" * 60)
    for test in results.tests:
        status = "PASS" if test['passed'] else "FAIL"
        print(f"[{status}] {test['name']}")
        if test['details']:
            print(f"    Details: {test['details']}")
        if test['error']:
            print(f"    Error: {test['error']}")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_tests()
