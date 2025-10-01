# Development Plan: asciidoc-mcp-q (feature/issue-8-auto-load branch)

*Generated on 2025-10-01 by Vibe Feature MCP*
*Workflow: [bugfix](https://mrsimpson.github.io/responsible-vibe-mcp/workflows/bugfix)*

## Goal
**Issue #8**: Auto-load structure on page load (https://github.com/raifdmueller/asciidoc-mcp/issues/8)

**Problem**: Benutzer muss "Load Structure" Button manuell klicken
**Lösung**: JavaScript soll Struktur automatisch beim Laden der Seite aufrufen

## Reproduce
### Reproduktionsschritte:
1. Web Server starten: `python3 -m src.web_server /home/rdmueller/projects/asciidoc-mcp-q`
2. Browser öffnen: http://localhost:8000
3. **IST**: Seite zeigt "Click 'Load Structure' to begin" - Benutzer muss Button klicken
4. **SOLL**: Struktur wird automatisch beim Laden der Seite geladen

### Code-Analyse:
- **src/web_server.py:244**: Button mit `onclick="loadStructure()"`
- **src/web_server.py:254**: Placeholder "Click 'Load Structure' to begin"
- **src/web_server.py:306-317**: `loadStructure()` Funktion existiert
- **Problem**: Kein automatischer Aufruf (fehlt DOMContentLoaded event)

### Tasks
- [x] Feature Branch erstellt: feature/issue-8-auto-load
- [x] Problem in src/web_server.py identifiziert
- [x] Reproduktionsschritte dokumentiert

### Completed
- [x] Created development plan file
- [x] Bug erfolgreich reproduziert

## Analyze
### Root Cause Analysis:

**Was passiert aktuell:**
- HTML zeigt Button "Load Structure" (Zeile 244) mit `onclick="loadStructure()"`
- JavaScript definiert `loadStructure()` Funktion (Zeile 306-317)
- Funktion wird NUR bei Button-Click aufgerufen, nicht beim Seitenladen
- Placeholder-Text fordert Benutzer auf: "Click 'Load Structure' to begin" (Zeile 254)

**Warum passiert das:**
- Es existiert KEIN Event Listener für `DOMContentLoaded` oder `window.onload`
- Andere Event Listener existieren (z.B. für Search ab Zeile 524, für Resize ab Zeile 283)
- `loadStructure()` wird nur bei explizitem Button-Click ausgeführt

**Root Cause:**
Fehlende Auto-Initialisierung beim Seitenladen - kein Event Listener ruft `loadStructure()` automatisch auf.

### Fix-Strategie:

**Lösung:** Event Listener für `DOMContentLoaded` hinzufügen, der `loadStructure()` aufruft

**Implementierung:**
1. Nach den bestehenden Event Listeners (nach Zeile 546) einen neuen Listener hinzufügen
2. Event: `DOMContentLoaded` (wird gefeuert wenn DOM bereit ist, vor `load`)
3. Action: `loadStructure()` aufrufen
4. Optionale Änderung: Placeholder-Text anpassen von "Click..." zu "Loading structure..."

**Code-Location:** src/web_server.py nach Zeile 546 (nach clearButton.addEventListener)

**Blast Radius:** Minimal - betrifft nur UI-Initialisierung, keine Backend-Logik

### Tasks
- [x] Root Cause identifiziert: Fehlender DOMContentLoaded Listener
- [x] Fix-Strategie definiert: Event Listener hinzufügen
- [x] Code-Location bestimmt: nach Zeile 546

### Completed
- [x] Root Cause Analyse durchgeführt
- [x] Fix-Strategie dokumentiert

## Fix
### Implementierung:

**Änderungen:**
1. **src/web_server.py:549-551**: DOMContentLoaded Event Listener hinzugefügt
   ```javascript
   document.addEventListener('DOMContentLoaded', () => {
       loadStructure();
   });
   ```
2. **src/web_server.py:254**: Placeholder-Text geändert von "Click 'Load Structure' to begin" zu "Loading structure..."

**Entscheidungen:**
- `DOMContentLoaded` statt `window.onload` gewählt (schnellere UX - wartet nicht auf alle Ressourcen)
- Minimaler Fix - nur Event Listener hinzugefügt, bestehende `loadStructure()` Funktion wiederverwendet
- Placeholder angepasst für konsistente UX

### Tasks
- [x] DOMContentLoaded Event Listener hinzugefügt (Zeile 549-551)
- [x] Placeholder-Text angepasst (Zeile 254)

### Completed
- [x] Fix implementiert

## Verify
### Verifikation:

**Test durchgeführt:**
1. Web Server gestartet auf Port 8082
2. Browser geöffnet: http://localhost:8082
3. **Ergebnis**: ✅ Struktur wurde AUTOMATISCH geladen!
   - 27 Dokumentationsdateien sofort sichtbar (01_introduction.adoc bis todos.adoc)
   - Kein manueller Button-Click erforderlich
   - Placeholder "Loading structure..." wurde korrekt durch Dateiliste ersetzt

**Verifikation erfolgreich:**
- ✅ Original-Bug behoben: Struktur lädt automatisch
- ✅ Keine Regressionen: Bestehende Funktionalität (Search, Resize, Manual Load) intakt
- ✅ UX verbessert: Sofortige Anzeige der Dokumentation

### Tasks
- [x] Web Server gestartet und getestet
- [x] Auto-Load Funktionalität verifiziert
- [x] Keine Regressionen festgestellt

### Completed
- [x] Fix erfolgreich verifiziert

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
