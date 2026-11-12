# Zwischenablage in der Topbar

Die Büroklammer rechts neben der Screenshot-Control öffnet einen eigenen
Zwischenablage-Popout direkt an der Topbar. Er verwendet dieselbe Popout-Hülle,
Kartenfarbe, Rundung, Abstände und Kopfzeilen-Gestaltung wie das Screenshot-Menü.
Text- und Bildvorschauen erscheinen in einer scrollbaren Liste. Ein Klick kopiert
den Eintrag; über die Pinnadel lassen sich Einträge anheften oder lösen.
Eine kurze Bestätigung erscheint in der Kopfzeile. Ein erneuter Klick auf die
Büroklammer schließt das Menü. Super+V öffnet weiterhin die bisherige Suchansicht.

Installation auf dem Shell-Stand vor der Büroklammer:

```bash
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < kde-customizations/taskbar/clipboard-control.patch
```

In `~/.config/caelestia/shell.json` unter `bar.entries` direkt nach
`screencapture` den Eintrag `{"enabled": true, "id": "clipboard", "zone": "left"}`
einfügen. Danach `systemctl --user restart caelestia-shell.service` ausführen.
Der Patch ersetzt die frühere Version mit Startmenü-Verknüpfung.

Geprüft: Darstellung mit echten Text- und Bildvorschauen per Screenshot;
Öffnen und Schließen über den tatsächlichen QML-Klickhandler via temporärem
Prüf-IPC, dabei bleibt der Launcher geschlossen. Keine QML-Fehler beim Öffnen.
Prüf-IPC anschließend entfernt. Kopieren und Anheften wurden nicht automatisiert
betätigt, um die bestehende Zwischenablage nicht zu ändern.

Sicherung vor der Büroklammer: `/home/USER/.local/state/ralleur-taskbar-backups/20261102T143953Z-clipboard-control`.
Sicherung vor dem eigenen Popout: `/home/USER/.local/state/ralleur-taskbar-backups/20261102T144502Z-clipboard-popout`.
Zum vollständigen Rückbau `Bar.qml` und `BarWidgets.qml` aus der ersten Sicherung,
`popouts/Content.qml` aus der zweiten Sicherung wiederherstellen. Die neuen Dateien
`components/ClipboardWidget.qml` und `popouts/ClipboardHistory.qml` entfernen
(Pfade unter `modules/bar/`), den `clipboard`-Eintrag aus `bar.entries` entfernen
und die Shell neu starten.

## Hover-Wechsel zum Screenshot-Menü

`../clipboard-hover.patch` entfernt die 80-Pixel-Sperre für den Wechsel
innerhalb der Topbar. Die bestehende Brücke zum Screenshot-Popout und dessen
Schließverzögerung bleiben erhalten. Nach `clipboard-control.patch` anwenden,
dann die Shell neu starten.

Mit echten Mausbewegungen über ein temporäres uinput-Gerät ohne Klick geprüft:
Büroklammer → Screenshot → Büroklammer öffnet jeweils das passende Popout.
Sicherung der vorherigen `modules/drawers/Interactions.qml`:
Pfad in `hover-backup.txt`. Zum Rückbau diese Datei wiederherstellen und die
Shell neu starten.
