"""
Test cases for Issue #39: Hash syntax support in get_section() API
"""
import pytest
from pathlib import Path
from src.mcp_internal.document_api import DocumentAPI
from src.mcp_server import MCPDocumentationServer


class TestHashSyntaxSupport:
    """Test hash syntax support in get_section API"""
    
    def test_hash_syntax_parsing(self):
        """Test _parse_section_path method with various inputs"""
        # Mock minimal server for testing
        class MockServer:
            sections = {}
        
        api = DocumentAPI(MockServer())
        
        # Test cases: (input, expected_output)
        test_cases = [
            # Hash syntax conversion
            ('file.adoc#section-name', 'file.section-name'),
            ('path/to/file.adoc#section', 'file.section'),
            ('document.adoc#nested.section.id', 'document.nested.section.id'),
            
            # Backward compatibility (no hash)
            ('existing.dot.notation', 'existing.dot.notation'),
            ('file.section-name', 'file.section-name'),
            
            # Edge cases
            ('file.adoc#section#with#multiple#hashes', 'file.section#with#multiple#hashes'),
            ('file.adoc#', 'file.'),  # Empty section after hash
        ]
        
        for input_path, expected in test_cases:
            result = api._parse_section_path(input_path)
            assert result == expected, f"Failed for {input_path}: expected {expected}, got {result}"


    def test_hash_syntax_integration(self, docs_server):
        """Integration test with real document server"""
        api = DocumentAPI(docs_server)
        
        # Find a real section to test with
        available_sections = list(docs_server.sections.keys())
        test_section = None
        
        for section_id in available_sections:
            if '.' in section_id:  # Find nested section
                test_section = section_id
                break
        
        if not test_section:
            pytest.skip("No nested sections available for testing")
        
        # Split section ID to create hash syntax test
        file_part, section_part = test_section.split('.', 1)
        hash_syntax_path = f"{file_part}.adoc#{section_part}"
        
        # Test hash syntax
        hash_result = api.get_section(hash_syntax_path)
        assert hash_result is not None, f"Hash syntax failed for {hash_syntax_path}"
        
        # Test dot notation (backward compatibility)
        dot_result = api.get_section(test_section)
        assert dot_result is not None, f"Dot notation failed for {test_section}"
        
        # Results should be identical
        assert hash_result['id'] == dot_result['id']
        assert hash_result['title'] == dot_result['title']


    def test_backward_compatibility(self, docs_server):
        """Ensure existing dot notation still works"""
        api = DocumentAPI(docs_server)
        
        # Test with known section
        test_section = 'todos.issues'  # Known to exist in test environment
        
        result = api.get_section(test_section)
        assert result is not None, "Backward compatibility broken - dot notation should still work"
        assert 'id' in result
        assert 'title' in result


@pytest.fixture
def docs_server():
    """Fixture providing DocumentServer with docs directory"""
    return MCPDocumentationServer(Path('docs'))