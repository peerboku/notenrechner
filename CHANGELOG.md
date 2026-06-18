# Änderungsprotokoll

Alle wichtigen Änderungen pro Version auf einen Blick. Neueste Version zuerst.

---

## [Unveröffentlicht]

### Notentabelle in der Schüleransicht überarbeitet
- Aufgeklappte Detailansicht zeigt jetzt eine echte Tabelle: eine Zeile pro Datum
- Spalten: Notiz | Datum | [Kategorien] — Werte liegen direkt unter den Spaltenköpfen der Hauptliste
- Mehrere Noten derselben Kategorie am gleichen Datum erscheinen als separate Zeilen (kein Überschreiben)
- Noten aus verschiedenen Einträgen am gleichen Datum (unterschiedliche Kategorien) werden zusammengeführt
- Sortierung: neueste Einträge oben; Einträge ohne Datum ganz unten
- Bugfix: Standard-Vorlage „Standard" wurde bei neuen Datenbanken mit veralteten englischen Kategorienamen angelegt

---

## [v0.5.2]

### Neue Noteneingabe (Flow-Rework)
- Kein separater „Noten eintragen"-Dialog mehr
- Klick auf Spaltenkopf einer Kategorie startet direkt den Eingabemodus für diese Kategorie
- Datum und Notiz editierbar direkt in der Bearbeitungsleiste (Datum vorausgefüllt mit heute)
- Notationshinweis in der Leiste bei kontinuierlichen Kategorien

### Schüleransicht
- Klick auf Schülernamen klappt Detailansicht aller Noten auf (ersetzt Hover-Tooltip)
- Aktionsmenü (Noten anzeigen / Entfernen) über ⋯-Button am Zeilenende
- Hover-Tooltips entfernt

### Notennotation (Kurzschreibweisen)
- `2+` wird als 1,75 gewertet
- `2-` wird als 2,25 gewertet
- `2-3` oder `2/3` wird als 2,5 gewertet
- Komma als Dezimaltrennzeichen (`2,5` = 2.5)
- Live-Validierung: Eingabefeld wird rot bei ungültigem Wert; Umrechnung bei Fokusverlust

### Diskrete Kategorien
- Hausübungen und Tests zeigen Symbole `+` / `~` / `−` statt Zahlenwerte 1 / 3 / 5
- Werte bleiben intern als Zahlen gespeichert

### Sprache
- Vollständig deutschsprachige Oberfläche
- Alle Texte zentral in `i18n.py` — Sprachenwechsel ist eine Zeile
- Standardkategorien auf Deutsch: Schularbeiten, Mündlich, Hausübungen, Tests

### Weitere Verbesserungen
- „Schüler hinzufügen"-Button immer sichtbar (vorher versteckt)
- Leere Klasse: zentrierte Meldung + prominenter Hinzufügen-Button
- Gewichtungsfelder akzeptieren Komma als Dezimaltrennzeichen

---

## [v0.5.0] — Erstes Release mit neuem Design

Komplette Neugestaltung der Oberfläche. Das alte Design (v0.3.x) war zu komplex für den Unterrichtsalltag und wurde ersetzt.

### Neu
- Einzelner Hauptbildschirm: Klasse auswählen, Noten eintragen, Ergebnisse sehen
- Klassenliste mit Dropdown (Klasse · Fach · Schuljahr)
- Neue Klasse anlegen über geführtes Formular
- Gewichtungsbereich mit Vorlagen-System (laden, speichern, umbenennen, löschen)
- Ereignisbasierte Noteneingabe: eine Note pro Schüler auf einmal für die ganze Klasse
- Schülerliste mit live berechneten Kategoriedurchschnitten und Endnote
- Einträge-Panel: alle gespeicherten Noteneinträge anzeigen und löschen
- Einstellungen-Modal: Gewichtungsvorlagen verwalten
- Undo/Redo: Cmd+Z / Ctrl+Z macht den letzten Noten-Eintrag rückgängig (sitzungsweit)

### Technisch
- Build-Pipeline via GitHub Actions: `.exe` für Windows und `.app` für Mac werden automatisch gebaut
- SQLite-Datenbank mit dynamischen Kategorien und Gewichtungen (ersetzt feste Spalten aus v0.3.x)
