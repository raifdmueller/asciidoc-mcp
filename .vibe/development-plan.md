# Development Plan: asciidoc-mcp-q (main branch)

*Generated on 2025-10-01 by Vibe Feature MCP*
*Workflow: [epcc](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/epcc)*

## Goal
Web-Interface soll Root-Files (nicht-includierte AsciiDoc/Markdown-Dateien) als oberste Ebene zeigen. Beim Aufklappen werden die enthaltenen Sections angezeigt - passend zur MCP-Server Navigation, damit LLMs leicht durch die Dokumentation navigieren können.

## Explore
### Tasks
- [x] Aktuelle Web-Interface Struktur analysieren
- [x] MCP-Server get_structure() Implementierung verstehen
- [x] Root-Files Discovery-Mechanismus dokumentieren
- [x] Unterschiede zwischen IST und SOLL identifizieren

### Completed
- [x] Created development plan file

### Findings

**Aktuelle Implementierung:**
- Web-Interface ruft `get_main_chapters()` auf (src/web_server.py:539)
- `get_main_chapters()` filtert nach arc42-Kapiteln (Level 2 mit Nummern) + Level 1 Sections
- Zeigt hierarchische Section-Struktur, NICHT Root-Files

**MCP-Server Navigation:**
- `_discover_root_files()` findet Root-Files: `*.adoc`, `*.ad`, `*.asciidoc`, `*.md`, `*.markdown` (ohne `_` Prefix)
- `root_files` Liste wird in `__init__` befüllt (src/mcp_server.py:30)
- `get_structure()` zeigt hierarchische Section-Struktur bis max_depth

**Problem:**
- Web-Interface zeigt Sections (z.B. arc42-Kapitel), nicht Root-Files
- User erwartet: Root-Files als oberste Ebene, darunter deren Sections
- Aktuell: Sections ohne File-Kontext

**IST-Zustand:**
```
Web-Interface Hierarchie:
├── Section "1. Introduction" (Level 2)
│   └── Children Sections
├── Section "2. Architecture" (Level 2)
│   └── Children Sections
└── Other Level 1 Sections
```

**SOLL-Zustand:**
```
Web-Interface Hierarchie (wie MCP-Navigation):
├── Root-File: "index.adoc"
│   ├── Section "1. Introduction"
│   └── Section "2. Architecture"
├── Root-File: "architecture.adoc"
│   └── Sections in architecture.adoc
└── Root-File: "README.md"
    └── Sections in README.md
```

**Kern-Unterschied:**
- IST: `get_main_chapters()` gruppiert nach Section-Level/Nummern
- SOLL: Neue Methode `get_root_files_structure()` gruppiert nach source_file
- Sections haben bereits `source_file` Feld (seit letztem Feature)
- Nutze `self.root_files` Liste für Root-Ebene

**Tatsächliche Web-Ansicht (Port 8081):**
```
Aktuell werden alle Sections FLACH gemischt angezeigt:
├── ... rest of init (2) [test-mcp.adoc:309-311]
├── Access: http://localhost:8082 (3) [AmazonQ.md:242-244]
├── Check coverage (1) [AmazonQ.md:231-234]
├── Find specific content (0) [AmazonQ.md:200-202]
├── MCP Documentation Server (9) [README.md:0-3]
├── MCP Documentation Server - Repository Overview (3) [AmazonQ.md:0-6]
└── ... weitere Sections aus verschiedenen Files

Problem: Markdown-Files wie AmazonQ.md haben viele kleine Sections
auf verschiedenen Levels, die alle einzeln als Top-Level erscheinen.
```

**Gewünschte Struktur:**
```
├── README.md
│   └── MCP Documentation Server (9)
├── AmazonQ.md
│   ├── MCP Documentation Server - Repository Overview (3)
│   ├── Navigate large documentation (0)
│   ├── Find specific content (0)
│   └── ... weitere Sections aus diesem File
└── test-mcp.adoc
    ├── MCP Server Test Report (5)
    └── ... rest of init (2)
```

## Plan

### Phase Entrance Criteria
- [x] Aktuelle Web-Interface-Implementierung ist verstanden
- [x] MCP-Server Navigation-Struktur ist analysiert
- [x] Root-Files Discovery-Mechanismus ist dokumentiert
- [x] Unterschiede zwischen aktueller und gewünschter Funktionalität sind klar

### Implementation Strategy

**Ansatz: Root-Files als Top-Level**
1. **Backend (MCP-Server)**: Neue Methode `get_root_files_structure()`
   - Iteriere über `self.root_files` Liste
   - Für jedes Root-File: Finde alle Sections mit matching `source_file`
   - Gruppiere Sections nach Root-File
   - Sortiere Sections innerhalb jedes Files nach `line_start`

2. **API (Web-Server)**: Ersetze `get_main_chapters()` Aufruf
   - `/api/structure` soll `get_root_files_structure()` aufrufen
   - Response-Format: `{filename: {file_info, sections: [...]}}`

3. **Frontend (JavaScript)**: Anpassung der Hierarchie-Darstellung
   - Root-Ebene: Files (nicht Sections)
   - Zweite Ebene: Top-Level Sections des Files
   - Weitere Ebenen: Section-Children wie bisher

### Tasks
- [x] Neue Methode `get_root_files_structure()` in MCPDocumentationServer implementieren
- [x] Web-Server API-Endpoint anpassen
- [x] JavaScript UI-Code für File-Level anpassen
- [x] CSS für File-Darstellung hinzufügen
- [x] Testen mit Browser

### Completed
- [x] Backend: get_root_files_structure() implementiert (src/mcp_server.py:173-238)
- [x] API: /api/structure Endpoint updated (src/web_server.py:532-539)
- [x] Frontend: createFileElement() + displayStructure() (src/web_server.py:294-362)
- [x] CSS: File-Level Styles hinzugefügt (src/web_server.py:179-228)
- [x] Browser-Tests erfolgreich - Root-Files werden korrekt angezeigt

## Code

### Phase Entrance Criteria
- [x] Implementierungsplan ist erstellt und aufgeteilt in Schritte
- [x] Design-Entscheidungen sind dokumentiert
- [x] Abhängigkeiten zwischen Komponenten sind klar

### Implementation Results

**Kern-Problem gelöst:**
- Sections hatten absolute Pfade, Root-Files ebenfalls
- `get_root_files_structure()` vergleicht jetzt beide (absolut + relativ)
- Matching funktioniert nun korrekt

**Dateien geändert:**
1. `src/mcp_server.py`: Neue Methode `get_root_files_structure()` (66 Zeilen)
2. `src/web_server.py`:
   - API-Endpoint `/api/structure` updated (Zeile 537)
   - JavaScript: `createFileElement()`, `toggleFile()`, `displayStructure()` neu
   - CSS: File-Level Styles (.file-item, .file-title, .file-sections)

### Completed
- [x] Alle Tasks aus Plan-Phase implementiert
- [x] Browser-Tests erfolgreich
- [x] Feature funktioniert wie gewünscht

## Commit

### Phase Entrance Criteria
- [ ] Alle Code-Änderungen sind implementiert und funktionieren
- [ ] Tests sind grün
- [ ] Feature-Funktionalität entspricht den Anforderungen

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
