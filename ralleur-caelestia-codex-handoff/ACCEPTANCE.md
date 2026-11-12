# Abnahme und Testmatrix

## A. Vollständigkeit

- [ ] 1. Wallpaper: jeweils echtes Light- und Dark-Wallpaper ohne abfotografierte UI.
- [ ] 2. Rahmen: Gaps/Rundungen/Blur/Shadows wirken wie die Referenz.
- [ ] 3. Navigation: Top-Bar und Dock mit funktionalen Interaktionen.
- [ ] 4. Widgets: Uhr, MPRIS-Media, CPU/RAM/Disk mit echten Daten oder korrekten Empty States.
- [ ] 5. Fensterverwaltung: alltagstaugliche Tiling-/Floating-/Fullscreen-Regeln.
- [ ] 6. Apps: kohärentes Light/Dark in Browser, Terminal, Dateimanager – soweit technisch unterstützt.
- [ ] 7. Designsystem: zentrale Tokens und authentisches Ralleur-Brand-Asset.

## B. Visuelle Gegenprüfung

- [ ] Light Screenshot erstellt und direkt mit `reference/desktop-light.png` verglichen.
- [ ] Dark Screenshot erstellt und direkt mit `reference/desktop-dark.png` verglichen.
- [ ] Positionen/Flächen, Kontrast, Widgets, Dock, Typografie, Farben, Transparenzen geprüft und sichtbare Abweichungen korrigiert.
- [ ] Keine Dummy-Statuswerte oder statischen Foto-Widgets im fertigen Desktop.

## C. Funktion

- [ ] Workspace-Navigation und App-Switch funktionieren.
- [ ] Dock öffnet Apps / zeigt aktiven Zustand.
- [ ] Light ↔ Dark ohne manuelle Dateiedits; konsistent über Shell und Wallpaper.
- [ ] Media-Steuerung reagiert auf echte Player / Empty State bei keinem Player.
- [ ] CPU/RAM/Disk-Werte plausibel; kein übermäßiges Polling.
- [ ] Keine Interaktions-/Rendering-Störungen in Fullscreen-Spielen.
- [ ] Kein Keyboard-Trap; lesbarer Fokus; Shortcut zum Ein-/Ausblenden der Widgets.

## D. Bildschirmgrößen

- [ ] Laptop/kleiner Screen: Widgets verschwindend oder einklappbar, Fenster nutzbar.
- [ ] 1920×1080: keine Kollisionen.
- [ ] 2560×1600 / 16:10: stimmiges Layout.
- [ ] 3440×1440 Ultrawide: Widgets dauerhaft möglich, ohne die Fensterfläche zu dominieren.
- [ ] HiDPI und mindestens ein Multi-Monitor-Szenario geprüft, sofern Testumgebung verfügbar.

## E. Wartbarkeit

- [ ] Upstream-Kompatibilität berücksichtigt, keine unkontrollierten Core-Overrides.
- [ ] Installationsprozess idempotent; existierende Configs gesichert.
- [ ] Rollback/Deinstallation dokumentiert und nach Möglichkeit getestet.
- [ ] Syntax-/Build-/Formatchecks ohne Fehler.
- [ ] `IMPLEMENTATION.md` benennt alle tatsächlich getesteten Punkte und verbleibende Lücken.

**Ehrliche Testregel:** Ein nicht ausführbarer GUI-Test wird als *nicht ausgeführt* protokolliert, niemals als erfolgreich.
