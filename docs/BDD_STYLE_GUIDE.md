# BDD Style Guide: Pure Docstring BDD Approach

## Overview

This guide defines the formatting standards for **Pure Docstring BDD** testing approach adopted in ADR-010. This approach combines Gherkin syntax in test docstrings with structured comments in the test implementation.

## Docstring Format

### Feature Structure
```python
def test_example_functionality(self):
    """
    Feature: [Brief Feature Name]
    As a [role/stakeholder]
    I want to [goal/desire]
    So that [benefit/value]
    
    Scenario: [Specific scenario name]
        Given [precondition/context]
        When [action/event]
        Then [expected outcome]
        And [additional expectation]
        But [negative expectation]
    """
```

### Elements Explained

**Feature Line**: Clear, concise description of the functionality being tested
- Format: `Feature: [Name]` 
- Example: `Feature: Document Parser Initialization`

**User Story**: Standard format with role, goal, and benefit
- As a: Define the stakeholder (user, developer, maintainer)
- I want to: State the goal or capability needed
- So that: Explain the business value or benefit

**Scenario**: Specific test case within the feature
- Descriptive name explaining what is being tested
- Focus on the specific condition or flow

**Steps**: Gherkin keywords with clear descriptions
- **Given**: Preconditions, setup, or context
- **When**: Actions, events, or triggers
- **Then**: Expected outcomes or assertions
- **And**: Additional conditions (can follow Given, When, or Then)
- **But**: Negative conditions or exceptions

## Test Implementation Comments

### Structure Comments
Match each Gherkin step with a structured comment in the implementation:

```python
def test_example(self):
    """[BDD Docstring as above]"""
    
    # Given: [step description from docstring]
    setup_code()
    
    # When: [step description from docstring]
    action_code()
    
    # Then: [step description from docstring]
    assert expected_result
    
    # And: [additional step description]
    assert additional_condition
```

### Comment Guidelines

1. **Exact Matching**: Comment descriptions should match docstring steps exactly
2. **Clear Separation**: Use blank line between Given/When/Then sections when logical
3. **Grouping**: Related assertions can be grouped under one comment
4. **Consistency**: Always use `# Given:`, `# When:`, `# Then:` format

## Examples by Test Type

### Unit Test Example
```python
def test_document_parser_initialization(self):
    """
    Feature: Document Parser Initialization
    As a documentation maintainer
    I want to create a DocumentParser with sensible defaults
    So that I can process documentation with predictable behavior
    
    Scenario: Initialize parser with default configuration
        Given I need to parse AsciiDoc documents
        When I create a new DocumentParser instance
        Then it should have max_include_depth of 4
        And it should have an empty processed files set
    """
    # Given: I need to parse AsciiDoc documents
    
    # When: I create a new DocumentParser instance
    parser = DocumentParser()
    
    # Then: it should have max_include_depth of 4
    assert parser.max_include_depth == 4
    
    # And: it should have an empty processed files set
    assert isinstance(parser.processed_files, set)
    assert len(parser.processed_files) == 0
```

### Integration Test Example
```python
def test_section_content_retrieval(self):
    """
    Feature: Section Content API
    As a web application user
    I want to retrieve specific section content
    So that I can display documentation sections in the interface
    
    Scenario: Get existing section content successfully
        Given I have a documentation project with multiple sections
        And the section "introduction" exists in "test.adoc"
        When I request the content for section "introduction"
        Then I should receive the section content
        And the response should include metadata
        But it should not include other sections
    """
    # Given: I have a documentation project with multiple sections
    test_content = """
    = Test Document
    
    == Introduction
    This is the introduction section.
    
    == Details  
    This is the details section.
    """
    project_root = create_test_project({"test.adoc": test_content})
    server = MCPDocumentationServer(project_root, enable_webserver=False)
    
    # And: the section "introduction" exists in "test.adoc"
    sections = server.get_structure()
    assert "test.adoc/introduction" in [s['path'] for s in sections]
    
    # When: I request the content for section "introduction"
    result = server.get_section("test.adoc/introduction")
    
    # Then: I should receive the section content
    assert result['content'] == "This is the introduction section."
    
    # And: the response should include metadata
    assert 'metadata' in result
    assert result['metadata']['title'] == "Introduction"
    
    # But: it should not include other sections
    assert "details section" not in result['content']
```

### Web API Test Example
```python
def test_api_section_endpoint(self):
    """
    Feature: Web API Section Endpoint  
    As a web client application
    I want to access section content via HTTP API
    So that I can build dynamic documentation interfaces
    
    Scenario: Successfully retrieve section via API
        Given I have a running web server with documentation
        When I make a GET request to "/api/section/test.adoc/introduction"
        Then I should receive HTTP status 200
        And the response should contain section content as JSON
    """
    # Given: I have a running web server with documentation
    with self.setup_test_server() as client:
        
        # When: I make a GET request to "/api/section/test.adoc/introduction"
        response = client.get("/api/section/test.adoc/introduction")
        
        # Then: I should receive HTTP status 200
        assert response.status_code == 200
        
        # And: the response should contain section content as JSON
        data = response.json()
        assert "content" in data
        assert isinstance(data["content"], str)
```

## Formatting Rules

### Indentation
- Use 4 spaces for Gherkin step indentation in docstrings
- Match Python code indentation for comments (usually 4 spaces)

### Line Length
- Keep docstring lines under 80 characters when possible
- Break long steps across multiple lines with proper indentation

### Language Style
- Use active voice in step descriptions
- Be specific about what is being tested
- Focus on behavior, not implementation details
- Use business-friendly language in Feature/User Story
- Use technical precision in Given/When/Then steps

### Naming Conventions
- Feature names: Title Case ("Document Parser Initialization")
- Scenario names: Descriptive, action-focused
- Step descriptions: Clear, specific, testable

## Testing Markers Integration

Combine BDD approach with existing pytest markers:

```python
@pytest.mark.integration
@pytest.mark.web
def test_web_interface_navigation(self):
    """
    Feature: Web Interface Navigation
    As a documentation browser
    I want to navigate between sections easily
    So that I can explore documentation efficiently
    
    Scenario: Navigate from table of contents to section
        Given I am on the documentation homepage
        When I click on a section link in the table of contents
        Then I should be taken to that section
        And the section content should be displayed
    """
    # Implementation with structured comments...
```

## Quality Checklist

Before committing BDD tests, verify:

- [ ] Feature describes business value clearly
- [ ] User story follows "As a... I want... So that..." format
- [ ] Scenario name is descriptive and specific
- [ ] Each Gherkin step is testable and clear
- [ ] Implementation comments match docstring steps exactly
- [ ] Code groups logically follow Given/When/Then structure
- [ ] Appropriate pytest markers are applied
- [ ] File remains under 500 lines (per coding standards)

## Migration Guidelines

### Converting Existing Tests

1. **Identify the Feature**: What business capability does this test verify?
2. **Define the User Story**: Who benefits and how?
3. **Map Current Assertions**: Which are Given (setup), When (action), Then (verification)?
4. **Add BDD Docstring**: Write comprehensive feature description
5. **Insert Structured Comments**: Match implementation to Gherkin steps
6. **Verify Behavior**: Ensure test still passes and covers same functionality

### Priority for Conversion

1. **Integration tests**: Benefit most from business context
2. **API tests**: User-facing functionality
3. **Complex workflows**: Multi-step processes
4. **Unit tests**: Convert during refactoring

## Tools and Validation

### IDE Support
- Configure syntax highlighting for Gherkin in Python docstrings
- Use spell checkers for business language in Feature descriptions
- Set up automatic formatting for consistent indentation

### Review Criteria
- Business stakeholders can understand Feature/Scenario without technical knowledge
- Developers can implement from Given/When/Then descriptions
- Tests serve as living documentation of system behavior
- Implementation matches specified behavior exactly

This style guide ensures consistency and quality in our Pure Docstring BDD approach while maintaining the technical precision needed for effective testing.