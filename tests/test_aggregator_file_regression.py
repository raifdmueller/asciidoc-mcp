"""
Regression test for aggregator file bug fix.

This test ensures that aggregator files (files with include:: statements)
show all their sections correctly in the web interface, not just one section.

Bug fixed: https://github.com/example/asciidoc-mcp-q/issues/XXX
Root cause: 
1. Build directory files were overriding docs files in file discovery
2. Aggregator file logic was not correctly matching sections to source files
"""

import pytest
from pathlib import Path
from src.mcp_server import MCPDocumentationServer


class TestAggregatorFileRegressionFix:
    """Test suite to prevent regression of the aggregator file bug."""
    
    def test_docs_arc42_shows_all_sections(self):
        """Test that docs/arc42.adoc shows all sections, not just one."""
        server = MCPDocumentationServer(Path("."), enable_webserver=False)
        
        # Get the file structure
        structure = server.doc_api.get_root_files_structure()
        
        # Find docs/arc42.adoc in the structure
        arc42_file = None
        for file_path, file_data in structure.items():
            if file_data['path'] == 'docs/arc42.adoc':
                arc42_file = file_data
                break
        
        # Ensure we found the file
        assert arc42_file is not None, "docs/arc42.adoc should be found in file structure"
        
        # Check that it has multiple sections (not just 1)
        sections = arc42_file.get('sections', [])
        assert len(sections) > 1, f"docs/arc42.adoc should have multiple sections, found {len(sections)}"
        
        # Count all sections recursively (including children)
        def count_all_sections(sections_list):
            count = 0
            for section in sections_list:
                count += 1  # Count this section
                children = section.get('children', [])
                count += count_all_sections(children)  # Count children recursively
            return count
            
        total_sections = count_all_sections(sections)
        
        # Should have around 69 sections based on the fix
        # Allow some flexibility in case content changes
        assert total_sections >= 50, f"docs/arc42.adoc should have at least 50 total sections, found {total_sections}"
        
        # Check hierarchical structure exists
        def collect_levels(sections_list, level_counts=None):
            if level_counts is None:
                level_counts = {}
            for section in sections_list:
                level = section.get('level', 0)
                level_counts[level] = level_counts.get(level, 0) + 1
                children = section.get('children', [])
                collect_levels(children, level_counts)
            return level_counts
            
        level_counts = collect_levels(sections)
        
        # Should have sections at multiple levels
        assert len(level_counts) >= 3, f"Should have sections at multiple levels, found levels: {level_counts.keys()}"
        
        # Should have at least some level-2 sections (arc42 chapters)
        assert level_counts.get(2, 0) >= 5, f"Should have at least 5 level-2 sections, found {level_counts.get(2, 0)}"
        
        server.cleanup()
    
    def test_build_directory_excluded(self):
        """Test that build directory files don't override docs files."""
        server = MCPDocumentationServer(Path("."), enable_webserver=False)
        
        # Get discovered root files
        root_files = server.root_files
        
        # Ensure no files from build directory are included  
        # The test found docs/arc42/05_building_blocks.adoc which contains "build" but is not in build/ directory
        build_dir_files = [f for f in root_files if str(f).startswith('build/')]
        assert len(build_dir_files) == 0, f"Build directory files should be excluded, found: {build_dir_files}"
        
        server.cleanup()
    
    def test_aggregator_file_section_matching(self):
        """Test that aggregator files properly show sections from included files."""
        server = MCPDocumentationServer(Path("."), enable_webserver=False)
        
        # Parse the arc42 file specifically
        arc42_path = Path("docs/arc42.adoc")
        if not arc42_path.exists():
            pytest.skip("docs/arc42.adoc not found - skipping aggregator test")
        
        # Parse the project to get sections (includes all files)
        sections_dict, included_files = server.parser.parse_project(arc42_path)
        
        # Should have many sections from included files
        assert len(sections_dict) > 50, f"Parsed sections should include content from all includes, found {len(sections_dict)}"
        
        # Check that sections have proper source_file references
        source_files = set()
        for section in sections_dict.values():
            if hasattr(section, 'source_file') and section.source_file:
                source_files.add(section.source_file)
        
        # Should have at least one source file (the aggregator file itself)
        assert len(source_files) >= 1, f"Should have source file references, found: {source_files}"
        
        # Should have multiple included files parsed
        assert len(included_files) > 5, f"Should have multiple included files parsed, found: {len(included_files)}"
        
        # Should include arc42 subdirectory files
        arc42_includes = [f for f in included_files if 'arc42/' in str(f)]
        assert len(arc42_includes) > 0, f"Should include files from arc42/ directory, found included files: {list(included_files)}"
        
        server.cleanup()


class TestAggregatorFileEdgeCases:
    """Test edge cases for aggregator files."""
    
    def test_empty_aggregator_file(self, tmp_path):
        """Test handling of empty aggregator files."""
        # Create a temporary empty file
        empty_file = tmp_path / "empty.adoc"
        empty_file.write_text("")
        
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        sections_dict, included_files = server.parser.parse_project(empty_file)
        
        # Should handle empty files gracefully
        assert isinstance(sections_dict, dict), "Should return a dict for empty files"
        assert len(sections_dict) == 0, "Empty file should have no sections"
        
        server.cleanup()
    
    def test_aggregator_file_without_includes(self, tmp_path):
        """Test handling of regular AsciiDoc files without includes."""
        # Create a regular AsciiDoc file with sections
        content = """= Test Document

== Section 1
Some content for section 1.

== Section 2
Some content for section 2.

=== Subsection 2.1
Nested content.
"""
        regular_file = tmp_path / "regular.adoc"
        regular_file.write_text(content)
        
        server = MCPDocumentationServer(tmp_path, enable_webserver=False)
        structure = server.doc_api.get_root_files_structure()
        
        # Find our test file
        test_file = None
        for file_path, file_data in structure.items():
            if file_data['path'] == 'regular.adoc':
                test_file = file_data
                break
        
        if test_file:
            sections = test_file.get('sections', [])
            
            # Count all sections recursively (hierarchical structure)
            def count_sections_recursive(sections_list):
                count = 0
                for section in sections_list:
                    count += 1  # Count this section
                    count += count_sections_recursive(section.get('children', []))  # Count children recursively
                return count
            
            total_sections = count_sections_recursive(sections)
            # Should show all sections from the regular file (1 root + 2 level2 + 1 level3 = 4 total)
            assert total_sections >= 3, f"Should show all sections from regular file, found {total_sections} total sections"
        
        server.cleanup()