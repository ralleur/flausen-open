# Capture-Menü: Kürzel und toleranter Mausweg

`../capture-menu.patch` ergänzt die installierte Caelestia-Shell:

- Alle sechs Capture-Aktionen zeigen das aktuelle globale Kürzel und einen Stift.
- Der vorhandene KeyCaptureDialog wird im Ersetzen-Modus verwendet, inklusive
  Konflikthinweis und Entfernen. Andere Shortcut-Dialoge behalten ihren Hinzufügen-Modus.
- Fullscreen, aktives Fenster und Spectacle erhalten dauerhaft registrierte Aktionen.
  Region, OCR und Bildsuche nutzen die bestehenden Aktionen und Kürzel.
- Der Capture-Popout wartet vor dem Schließen 650 statt 150 ms. Der Übergang vom
  Symbol zur Karte erhält einen breiteren Korridor und Randtoleranz. Ein offenes
  Dropdown oder ein Shortcut-Dialog hält den Popout offen, bis es geschlossen wird.
- Das Dropdown wird innerhalb des Bildschirms gehalten und zeigt alle sechs Einträge.

Anwenden (auf den bisherigen angepassten Stand):

```bash
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < kde-customizations/taskbar/capture-menu.patch
systemctl --user restart caelestia-shell.service
```

Kürzel speichert die vorhandene zentrale Verwaltung in `~/.config/caelestia/keybinds.json`.
Der Patch setzt keine neuen Standardkombinationen.

Validierung: echte laufende Shell geladen, Dropdown und Dialog per Screenshot
kontrolliert; Bestätigen-Button mit einem temporären Testkürzel ausgelöst,
Speicherung und Wiederladen nach Shell-Neustart geprüft. Danach wurde das zuvor
zugewiesene Fullscreen-Kürzel wiederhergestellt. Die Test-IPC-Hooks sind entfernt.
Der Mausweg wurde über den Code geprüft; kein automatisierter physischer Mauslauf.

Sicherung des vorherigen QML-Stands: `/home/USER/.local/state/ralleur-taskbar-backups/20261102T141414Z-capture-menu`.
