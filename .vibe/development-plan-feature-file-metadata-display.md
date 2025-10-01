# Development Plan: asciidoc-mcp-q (feature-file-metadata-display branch)

*Generated on 2025-10-01 by Vibe Feature MCP*
*Workflow: [epcc](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/epcc)*

## Goal
Implement file metadata display and content filtering in web interface:
1. **Content Filtering**: Show only AsciiDoc (.adoc) and Markdown (.md) files
2. **Source Metadata Display**: Display file path and line numbers for each section

**User Request**: "zu viel wird angezeigt" → only show relevant document types, make source file and line numbers visible for better traceability

## Explore
### Phase Entrance Criteria
- [x] Feature branch created
- [x] Specification extended (PRD updated)
- [x] Ready to explore codebase

### Tasks
- [x] Analyze Section dataclass structure
- [x] Check if source_file is stored in Section
- [x] Analyze API endpoints for metadata support
- [x] Analyze web interface display logic
- [x] Document requirements
- [x] Define entrance criteria for Plan phase

### Completed
- [x] Created development plan file
- [x] Extended PRD: Added "Content Filtering" and "Source Metadata Display" requirements
- [x] Analyzed Section class in src/document_parser.py
- [x] Found: line_start/line_end exist, but source_file is MISSING
- [x] Found: _parse_structure receives source_file but doesn't store it
- [x] Analyzed API endpoint /api/section: returns id, title, level, content, children (NO metadata)
- [x] Analyzed web UI createSectionElement: displays title + children_count (NO file/line info)

### Requirements

**Requirement 1: Content Filtering**
- Filter sections to show only .adoc and .md files
- Hide other document types from web interface tree
- Apply filter at data level (not just UI visibility)

**Requirement 2: Source Metadata Display**
- Display file path for each section
- Display line number range (line_start - line_end)
- Format: "file.adoc:10-25" or similar
- Should be visible in section tree (not just on click)
- Enable traceability: user should quickly see which file and lines a section comes from

**Technical Findings:**
- Section has: id, title, level, content, line_start, line_end, children, parent_id
- Section MISSING: source_file field
- DocumentParser._parse_structure(content, source_file) receives file path but doesn't store it
- API /api/section doesn't return line numbers or file path
- Web UI doesn't display metadata

**Data Flow:**
1. DocumentParser._parse_structure(content, source_file) → creates Section instances
2. MCPDocumentServer.sections dict stores all Section objects
3. get_main_chapters() filters and organizes for web display
4. API /api/structure returns section data
5. Web UI displayStructure() + createSectionElement() renders tree

## Plan
### Phase Entrance Criteria
- [x] Requirements are documented
- [x] Technical findings are analyzed
- [x] Data flow is understood
- [x] Implementation approach is designed
- [x] Tasks are broken down

### Implementation Strategy

**Approach**: Bottom-up implementation - Data model → Parser → API → UI

#### Component 1: Data Model Enhancement
**File**: `src/document_parser.py`
- Add `source_file: str` field to Section dataclass (after line_end)
- Modify `_parse_structure()` to store source_file in Section instances
- Ensure source_file is relative path (for portability)

#### Component 2: Content Filtering
**Files**: `src/document_parser.py`, `src/mcp_server.py`
- Filter root_files to only .adoc and .md extensions
- Apply filter in DocumentParser initialization
- Alternative: Filter in get_main_chapters() if root_files can't be filtered early

#### Component 3: API Metadata Support
**File**: `src/web_server.py`
- Update `/api/structure` endpoint to include metadata in section data
- Add fields: `source_file`, `line_start`, `line_end` to response
- Update `/api/section/{section_id}` similarly for consistency

#### Component 4: UI Metadata Display
**File**: `src/web_server.py` (inline HTML/CSS/JS)
- Modify `createSectionElement()` to display metadata
- Format: `[filename.adoc:10-25]` after section title
- Style: smaller font, gray color, monospace
- Example: `Section Title (3) [test.adoc:45-67]`

### Design Decisions

**Decision 1: Source File Storage**
- **Choice**: Store relative path in Section.source_file
- **Reason**: Portability (project can be moved), shorter strings
- **Implementation**: Use pathlib.Path.relative_to() or os.path.relpath()

**Decision 2: Content Filtering Location**
- **Choice**: Filter root_files early (DocumentParser.__init__)
- **Reason**: Prevents parsing non-doc files, saves memory
- **Fallback**: If root_files filtering breaks includes, filter in get_main_chapters()

**Decision 3: Metadata Display Format**
- **Choice**: `[filename.adoc:10-25]` after title, before children count
- **Reason**: Compact, standard format (similar to compiler errors), easy to parse visually
- **Alternative considered**: Tooltip on hover (rejected: less visible, requires interaction)

**Decision 4: File Extension Filter**
- **Choice**: `.adoc`, `.ad`, `.asciidoc`, `.md`, `.markdown`
- **Reason**: Cover common AsciiDoc and Markdown extensions
- **Implementation**: Use tuple for `filename.endswith()`

### Tasks
- [x] Design source_file storage approach
- [x] Design content filtering approach
- [x] Plan API changes for metadata
- [x] Plan UI changes for display
- [x] Break down implementation steps
- [x] Document edge cases

### Completed
- [x] Defined bottom-up implementation approach
- [x] Documented 4 key design decisions
- [x] Planned changes for all 4 components

## Code
### Phase Entrance Criteria
- [x] Implementation strategy is documented
- [x] Design decisions are made
- [x] Tasks are broken down
- [x] User has approved plan
- [x] All implementation steps completed
- [x] Tests passed successfully

### Implementation Tasks

**Step 1: Data Model - Add source_file field**
- [x] Add `source_file: str` to Section dataclass (src/document_parser.py:6-15)
- [x] Update Section instantiation in _parse_structure() to include source_file
- [x] Store relative path using pathlib

**Step 2: Content Filtering - Filter file types**
- [x] Extended patterns in _discover_root_files() to include .ad, .markdown
- [x] Content filtering works at discovery level (MCPDocumentServer)
- [x] Only .adoc, .ad, .asciidoc, .md, .markdown files are processed

**Step 3: API Enhancement - Return metadata**
- [x] Updated get_structure() to include source_file, line_start, line_end
- [x] Updated /api/section/{section_id} endpoint to return metadata
- [x] Tested API responses contain new fields

**Step 4: UI Display - Show metadata**
- [x] Modified createSectionElement() to display metadata
- [x] Added CSS for .section-metadata class (gray, monospace, 0.8em)
- [x] Format: [filename:start-end] after title
- [x] Tested UI displays correctly

**Step 5: Testing**
- [x] Tested with test-docs (AsciiDoc file)
- [x] API returns correct metadata: source_file, line_start, line_end
- [x] UI displays metadata in correct format: [test-docs/mein-test.adoc:0-19]
- [x] Screenshot verified correct styling (gray, monospace)

### Completed
- [x] Added source_file field to Section dataclass (src/document_parser.py:6-16)
- [x] Updated _parse_structure() to store relative path (src/document_parser.py:51-116)
- [x] Extended file patterns in _discover_root_files() (src/mcp_server.py:55-63)
- [x] Updated get_structure() API response with metadata (src/mcp_server.py:70-129)
- [x] Updated /api/section endpoint with metadata (src/web_server.py:554-573)
- [x] Added metadata display in createSectionElement() (src/web_server.py:308-326)
- [x] Added .section-metadata CSS styling (src/web_server.py:96-101)
- [x] Tested implementation successfully

### Edge Cases & Considerations

1. **Include Files**: If included file is filtered out, parent should still work
2. **Absolute vs Relative Paths**: Always store relative to project root
3. **Missing source_file**: Gracefully handle sections without source_file (legacy data)
4. **Long Filenames**: Truncate in UI if > 30 chars? Or wrap?
5. **Line Numbers = 0**: Some sections might have line_start=0, display as [file.adoc:0-0]?
6. **Empty Extensions**: Files like "README" without extension - exclude or include?
7. **Case Sensitivity**: .ADOC vs .adoc - use case-insensitive comparison
8. **Symlinks**: Follow symlinks or treat as regular files?

## Commit
### Tasks
- [ ] *To be added when this phase becomes active*

### Completed
*None yet*

## Key Decisions
*Important decisions will be documented here as they are made*

## Notes
*Additional context and observations*

---
*This plan is maintained by the LLM. Tool responses provide guidance on which section to focus on and what tasks to work on.*
