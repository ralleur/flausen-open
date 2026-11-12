# Screenshot-Galerie

`../screenshot-gallery.patch` baut auf `../capture-menu.patch` auf.
Die alte Dateiliste wird durch ein scrollbareres Vorschauraster ersetzt:

- Zwei Spalten im kompakten Capture-Popout, drei bei mehr verfügbarer Breite.
- Neueste PNGs zuerst; kleine asynchron geladene Vorschauen zeigen das ganze Bild.
- Einzelklick kopiert PNG-Bilddaten mit `wl-copy`, danach erscheint für 2,2 Sekunden
  eine dezente Bestätigung im Galerie-Kopf. Fehler erhalten eine eigene Rückmeldung.
- Einzelklick wartet auf das systemweite Doppelklick-Zeitfenster. Doppelklick
  verwirft den ausstehenden Kopiervorgang und öffnet das Original mit `xdg-open`.
- Standardmäßig zwei, aufgeklappt vier sichtbare Reihen; weitere Bilder per Scrollen.
- Ordnerzugriff im Kopf, Löschen mit Bestätigung direkt auf der jeweiligen Kachel.

Der Capture-Popout erhält außerdem die bisher fehlende Eigenschaft
`screenshotListExpanded`, damit Aufklappen zuverlässig funktioniert.

Anwenden nach dem Capture-Menü-Patch:

```bash
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < kde-customizations/taskbar/screenshot-gallery.patch
systemctl --user restart caelestia-shell.service
```

Geprüft in der echten laufenden Shell: 26 Bilder gefunden, alle geladenen
Vorschauen bereit, Einzelklick-Handler inklusive Timer/Process ausgelöst,
PNG-Zwischenablage bytegenau mit dem ausgewählten Original verglichen,
Bestätigung und aufgeklappte Galerie per Screenshot kontrolliert. Der ursprüngliche
Zwischenablageninhalt wurde danach wiederhergestellt. Doppelklick-Routing im Code
geprüft; kein automatisierter physischer Doppelklick. Temporäre IPC-Hooks entfernt.

Sicherung des vorherigen QML-Stands: `/home/USER/.local/state/ralleur-taskbar-backups/20261102T143402Z-screenshot-gallery`.
