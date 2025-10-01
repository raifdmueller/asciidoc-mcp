# Development Plan: asciidoc-mcp-q (feature/issue-5-hide-includes branch)

*Generated on 2025-10-01 by Vibe Feature MCP*
*Workflow: [bugfix](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/bugfix)*

## Goal
**Issue #5**: Hide included files from navigation (https://github.com/raifdmueller/asciidoc-mcp/issues/5)

**Problem**:
- Dateien mit `_` Prefix werden ausgeblendet (funktioniert)
- Aber: Dateien die via `include::` in anderen Dateien included werden, erscheinen trotzdem separat
- **IST**: All 27 Files werden angezeigt, auch included ones
- **SOLL**: Nur Top-Level Files (nicht included) sollen angezeigt werden

## Reproduce
### Phase Entrance Criteria:
*Keine - initiale Phase*

### Aktuelle Situation:
- `src/mcp_server.py:57-74`: `_discover_root_files()` filtert nur `_*` Files aus
- `src/document_parser.py:22-48`: Parser tracked `processed_files` während include resolution
- **Problem**: `processed_files` wird bei jedem `parse_project()` Call gecleart (Zeile 26)
- **Keine persistente Tracking** welche Files included sind

### Tasks
- [x] Feature Branch erstellt: feature/issue-5-hide-includes
- [x] Code analysiert: Parser, MCP Server, Include-Logik
- [x] Problem identifiziert: Fehlendes persistentes Include-Tracking

### Completed
- [x] Created development plan file
- [x] Problem reproduziert und analysiert

## Analyze
### Root Cause Analysis:

**Was passiert:**
1. `MCPDocumentationServer.__init__()` ruft `_discover_root_files()` auf
2. `_discover_root_files()` findet alle *.adoc/*.md Files (außer `_*` Files)
3. `_parse_project()` parst jedes root_file via `parser.parse_project()`
4. **DocumentParser löst Includes auf** (Zeile 27-48) und tracked `processed_files`
5. **ABER**: `processed_files` wird bei jedem `parse_project()` Call gecleart!
6. `get_root_files_structure()` iteriert über ALLE `self.root_files` und zeigt sie an

**Warum das Problem existiert:**
- `root_files` Liste enthält ALLE Files (auch included ones)
- Keine Unterscheidung zwischen "Top-Level Files" und "Included Files"
- Parser weiß welche Files included sind, aber diese Info wird nicht gespeichert

**Root Cause:**
Fehlende Persistierung der Include-Information. Parser trackt temporär `processed_files`, aber MCP Server nutzt diese Info nicht um `root_files` zu filtern.

### Fix-Strategie:

**Ansatz 1: Parser-Rückgabe erweitern** ⭐ (Empfohlen)
- Parser gibt `included_files: Set[Path]` zusätzlich zurück
- MCP Server sammelt alle included files über alle parse_project() Calls
- `get_root_files_structure()` filtert included files aus

**Ansatz 2: Post-Processing in get_root_files_structure()**
- Analysiere alle Sections, sammle unique source_files
- Vergleiche mit root_files, finde Files ohne eigene Sections
- Problematisch: Files könnten Sections UND included sein

**Entscheidung: Ansatz 1**
- Saubere Separation: Parser weiß was included ist
- MCP Server hält `included_files` Set persistent
- Minimal invasiv, klare Verantwortlichkeiten

### Implementierung:

**Schritt 1: Parser erweitern**
- `DocumentParser.parse_project()` gibt Tuple zurück: `(sections, included_files)`
- `included_files` = alle Files außer dem root_file selbst aus `processed_files`

**Schritt 2: MCP Server erweitern**
- Neues Attribut: `self.included_files: Set[Path] = set()`
- In `_parse_project()`: Sammle included_files
- In `get_root_files_structure()`: Filter `if root_file not in self.included_files`

**Code-Locations:**
- `src/document_parser.py:24-28`: parse_project() Rückgabewert ändern
- `src/mcp_server.py:27`: Neues Attribut `self.included_files`
- `src/mcp_server.py:76-80`: `_parse_project()` Update
- `src/mcp_server.py:192`: Filter in Loop einfügen

### Tasks
- [x] Root Cause identifiziert: Fehlende Include-Info Persistierung
- [x] Fix-Strategie definiert: Parser erweitern + MCP Server filtern
- [x] Implementierungsplan erstellt

### Completed
- [x] Root Cause Analyse abgeschlossen
- [x] Fix-Strategie dokumentiert

## Fix
### Implementierung:

**Schritt 1: Parser erweitern** (src/document_parser.py)
- Zeile 24-39: `parse_project()` gibt jetzt Tuple zurück: `(sections, included_files)`
- `included_files` = Set aller processedierten Files außer root_file

**Schritt 2: MCP Server erweitern** (src/mcp_server.py)
- Zeile 29: Neues Attribut `self.included_files = set()`
- Zeile 78-82: `_parse_project()` sammelt included_files von allen root_files
- Zeile 196-197: Filter in `get_root_files_structure()` - skippt included files

**Schritt 3: Tests angepasst**
- test_basic.py: parse_project() Rückgabewert unpacked
- comprehensive_test.py: 2x parse_project() Aufrufe angepasst

### Test-Ergebnisse:
- ✅ 27 root files entdeckt
- ✅ 16 included files tracked
- ✅ **Nur 15 files in structure angezeigt** (12 versteckt!)
- ✅ Tests laufen (43 tests, nur alte HTML-ID Tests schlagen fehl - nicht durch diese Änderung)

### Tasks
- [x] Parser erweitern (Tuple-Rückgabe)
- [x] MCP Server included_files Attribut hinzufügen
- [x] _parse_project() Update
- [x] get_root_files_structure() Filter implementieren
- [x] Tests angepasst

### Completed
- [x] Fix vollständig implementiert und getestet

## Verify
### Verifikation:

**Test 1: Programmatischer Test**
```python
server = MCPDocumentationServer(project_root, enable_webserver=False)
# Ergebnis: 27 root files, 16 included, 15 shown (12 hidden) ✅
```

**Test 2: Web API Test**
```bash
curl http://localhost:8082/api/structure | python3 -m json.tool
# Ergebnis: 15 files in structure ✅
```

**Test 3: Gezeigte Files**
- test-web.adoc ✅
- test-mcp.adoc ✅
- arc42.adoc ✅
- manual.adoc ✅
- README.md ✅
- etc. (Top-Level Docs)

**Test 4: Versteckte Files**
- Alle via `include::` referenzierten Files wurden korrekt ausgeblendet
- Kapitel-Files die in arc42.adoc included werden: NICHT einzeln gezeigt ✅
- Funktioniert wie erwartet!

**Test 5: Keine Regressionen**
- ✅ Bestehende Tests laufen (43 tests, 38 passed)
- ✅ Nur Tests mit alten HTML-IDs schlagen fehl (nicht durch diese Änderung)
- ✅ Parser-API Änderung wurde in allen Tests übernommen

### Tasks
- [x] Programmatischer Test durchgeführt
- [x] Web API Test durchgeführt
- [x] Manuelle Verifikation der Filelist
- [x] Regression Tests laufen
- [x] Fix verifiziert

### Completed
- [x] Fix erfolgreich verifiziert - included files werden korrekt ausgeblendet!

## Finalize
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
