"""
Shared pytest fixtures for all tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict

from src.document_parser import DocumentParser, Section


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for tests"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_adoc_content():
    """Reusable AsciiDoc content for tests"""
    return """= Main Document

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


@pytest.fixture
def sample_markdown_content():
    """Reusable Markdown content for tests"""
    return """# Main Document

## Introduction
This is the introduction section.

### Overview
Overview content here.

## Architecture
Architecture details.

### Components
Component descriptions.

#### Database
Database component info.

## Conclusion
Final thoughts."""


@pytest.fixture
def sample_adoc_with_include(temp_project_dir):
    """Create AsciiDoc file with include directive"""
    main_file = temp_project_dir / "main.adoc"
    included_file = temp_project_dir / "included.adoc"

    main_content = """= Main Document

== Introduction
Introduction text.

include::included.adoc[]

== Conclusion
Final text."""

    included_content = """== Included Section
This content is from an included file.

=== Subsection
Subsection content."""

    main_file.write_text(main_content)
    included_file.write_text(included_content)

    return main_file


@pytest.fixture
def document_parser():
    """Create a DocumentParser instance"""
    return DocumentParser()


@pytest.fixture
def test_sections() -> Dict[str, Section]:
    """Sample section data for testing"""
    return {
        "main.intro": Section(
            id="main.intro",
            title="Introduction",
            level=2,
            content="Intro content",
            line_start=3,
            line_end=5,
            source_file="main.adoc",
            children=[],
            parent_id=None
        ),
        "main.intro.overview": Section(
            id="main.intro.overview",
            title="Overview",
            level=3,
            content="Overview content",
            line_start=7,
            line_end=9,
            source_file="main.adoc",
            children=[],
            parent_id="main.intro"
        ),
    }


@pytest.fixture
def mock_file_content():
    """Mock file content for file watcher tests"""
    return {
        "test.adoc": "= Test\n\n== Section\nContent here.",
        "README.md": "# README\n\n## Getting Started\nInstructions.",
    }
