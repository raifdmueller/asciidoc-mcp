# Development Plan: asciidoc-mcp-q (feature-search-functionality branch)

*Generated on 2025-10-01 by Vibe Feature MCP*
*Workflow: [epcc](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/epcc)*

## Goal
Implement Search Functionality für das Web Interface

**Feature**: Suchfunktion die es Benutzern ermöglicht, Sections nach Titel zu filtern.

**Requirements aus test-web.adoc**:
- Search box im Header
- Filter sections by title (live filtering)
- Highlight matches in tree
- Estimated Time: ~4 hours

## Explore
### Phase Entrance Criteria
- Workflow wurde gestartet
- Goal ist definiert

### Tasks
- [ ] Aktuelles Web-Interface HTML/JS/CSS analysieren
- [ ] Bestehende Section-Tree-Struktur verstehen
- [ ] CodeMirror Integration prüfen (könnte Search beeinflussen)
- [ ] Requirements detaillieren und dokumentieren

### Completed
- [x] Created development plan file
- [x] Web-Interface analysiert (src/web_server.py)
- [x] Section-Tree-Struktur verstanden (rekursive children)
- [x] Bestehende Patterns identifiziert (createSectionElement, displayStructure)

## Plan
### Phase Entrance Criteria
- [x] Codebase wurde analysiert
- [x] Bestehende Patterns sind verstanden
- [x] Requirements sind dokumentiert
- [x] Technische Machbarkeit ist geklärt

### Implementation Strategy

**Approach**: Inline implementation in `src/web_server.py` (konsistent mit aktuellem Pattern)

**Components:**

1. **HTML/CSS (Header)**
   - Add search input field to header (after existing buttons)
   - Add clear button (× icon) inside search field
   - Style: Match existing button styling

2. **JavaScript (Filtering Logic)**
   - `filterSections(searchTerm)` - Main filter function
   - `showSection(element)` / `hideSection(element)` - Toggle visibility
   - `isMatchOrHasMatchingChild(element, term)` - Recursive matching
   - Event listener on input (keyup, debounced 300ms)
   - ESC key listener to clear search

3. **CSS (Highlighting)**
   - `.search-highlight` class for matching sections
   - `.search-match` class for exact title matches
   - Yellow background for matches

**Algorithm (Recursive Filtering):**
```
For each .section element:
  1. Check if title matches search term (case-insensitive)
  2. Check if ANY child matches (recursive)
  3. If match OR has matching child: show section
  4. If match: add highlight class
  5. If no match AND no matching children: hide section
```

### Tasks
- [ ] Design CSS für search box
- [ ] Entscheiden: Debouncing notwendig? (Performance)
- [ ] Edge Cases dokumentieren

### Completed
*None yet*

## Code
### Phase Entrance Criteria
- [x] Implementierungsplan ist erstellt
- [x] Tasks sind definiert und priorisiert
- [x] Design-Entscheidungen sind dokumentiert
- [x] User hat Plan approved

### Implementation Tasks

**Step 1: HTML - Search Input**
- [x] Add `<input>` field to header HTML
- [x] Add clear button (×) next to input
- [x] Set placeholder text ("Search sections...")

**Step 2: CSS - Styling**
- [x] Style search input box (border, padding, width)
- [x] Style clear button (position: relative, right side)
- [x] Add `.search-highlight` class (yellow background)
- [x] Add `.search-match` class (bold text)
- [x] Add `.hidden` class (display: none)

**Step 3: JavaScript - Filter Logic**
- [x] Implement `filterSections(searchTerm)` function
- [x] Implement `isMatchOrHasMatchingChild(section, term)` (recursive)
- [x] Add event listener on search input (keyup)
- [x] Add ESC key listener to clear search
- [x] Add click listener on clear button

**Step 4: Testing**
- [x] Test with empty search (show all)
- [x] Test with partial match (case-insensitive)
- [x] Test with parent/child matching
- [x] Test clear functionality
- [x] Test with many sections (performance)

### Completed
- [x] Added search input and clear button to header HTML (src/web_server.py:149-150)
- [x] Styled search box with focus state and clear button (src/web_server.py:56-94)
- [x] Implemented complete filter logic with recursive matching (src/web_server.py:406-497)
- [x] Tested all functionality with Playwright: filtering, highlighting, clear, case-insensitive
- [x] Created commit: 85f8bd1 - feat: Add search functionality to web interface

### Edge Cases & Considerations

1. **Empty Search**: Show all sections, remove highlights
2. **No Matches**: Show "No results found" message? Or just empty tree?
3. **Collapsed Sections**: Expand parent if child matches?
4. **Performance**: 100+ sections - debounce 300ms should be enough
5. **Special Characters**: Escape regex special chars in search term
6. **Unicode**: Support UTF-8 section titles (should work with toLowerCase())
7. **Search History**: Not implemented (future enhancement)

## Commit
### Phase Entrance Criteria
- [x] Code ist implementiert
- [x] Alle Tasks sind completed
- [x] Feature funktioniert wie erwartet
- [x] Tests sind grün (31 passed, 7 pre-existing failures, 0 new failures)

### Tasks
- [x] Code Cleanup: Check for debug output, TODOs, commented code
- [x] Documentation Review: Check requirements, architecture, design docs
- [x] Final Validation: Run tests to ensure no regressions

### Completed
- [x] Code cleanup verified: No debug output, no TODOs, no commented code blocks
- [x] Production error logging preserved (console.error for section loading)
- [x] All comments are helpful documentation, not temporary debug code
- [x] Documentation reviewed: All docs are placeholders (requirements tracked in plan file)
- [x] Tests run: 31 passed, 7 pre-existing failures, 5 pre-existing errors
- [x] No regressions introduced by search functionality
- [x] Commit created: 85f8bd1 - feat: Add search functionality to web interface

## Key Decisions

### Decision 1: Inline Implementation
**Choice**: Implement search in `src/web_server.py` (not separate JS file)
**Reason**: Consistent with current architecture, no build step needed
**Impact**: File grows to ~500-550 lines (still manageable)

### Decision 2: Client-Side Filtering
**Choice**: Filter sections in browser, not via API
**Reason**: Fast, no server load, works offline
**Impact**: All sections loaded upfront (current behavior)

### Decision 3: Debouncing
**Choice**: 300ms debounce on keyup
**Reason**: Prevents excessive filtering on fast typing
**Impact**: Slightly delayed response, but smoother UX

### Decision 4: Parent Visibility
**Choice**: Show parent if ANY child matches
**Reason**: Maintains tree context, intuitive UX
**Impact**: Recursive algorithm required (complexity O(n))

### Decision 5: No "Expand on Match"
**Choice**: Don't auto-expand collapsed sections
**Reason**: Simpler implementation, user keeps control
**Impact**: User may need to manually expand to see matching children (acceptable trade-off)

## Notes

### Explore Phase - Findings

**Current Architecture:**
- Single-file web interface in `src/web_server.py` (inline HTML/CSS/JS)
- No external JS files - everything in `root()` function
- File size: ~400 lines

**Key Functions:**
1. `loadStructure()` - Fetches `/api/structure`, calls `displayStructure()`
2. `displayStructure(structure)` - Sorts sections, creates DOM elements
3. `createSectionElement(section)` - Recursive function creating section divs with children
4. `toggleSection()` - Expands/collapses children
5. `selectSection()` - Loads content for selected section

**Section Structure:**
```javascript
section = {
  id: "section-id",
  title: "Section Title",
  level: 1,
  children: [...],  // Recursive structure
  children_count: 5
}
```

**DOM Structure:**
- `.section` divs with `.level-{N}` classes
- `.section-title` contains expand icon + title text
- `.section-children` container with `id="children-{section-id}"`
- Nested recursively via `createSectionElement()`

**Header Layout:**
- Fixed header (60px height) with h1 + buttons
- Flexbox layout: `display: flex; align-items: center;`
- Buttons styled with blue border/hover effect

**Search Requirements (from analysis):**
1. **Input Field**: Add search input to header (after buttons)
2. **Live Filtering**: Filter on keyup, case-insensitive
3. **Show/Hide Sections**: Toggle `.section` visibility based on match
4. **Highlight Matches**: Add class to matching sections
5. **Parent Visibility**: If child matches, show parent too
6. **Clear Search**: Button or ESC key to reset

---
*This plan is maintained by the LLM. Tool responses provide guidance on which section to focus on and what tasks to work on.*
