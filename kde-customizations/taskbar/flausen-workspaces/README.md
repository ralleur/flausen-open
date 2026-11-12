# flausen.-Formen für virtuelle Desktops

Die zufälligen Material-Shapes, Quadrate und Punkte der normalen Desktop-Anzeige
werden durch feste flausen.-Formen ersetzt: Play, Everyday-Keil, The-idea-Streifen,
Gegengewicht. Die SVG-Pfade stammen unverändert aus `website/src/geometry.json`.
Die Formen tragen ihre Konzeptfarben: Blau #2563C9, Orange #E56D2F, Petrol
#278F8B und Braun #8F5B40. Auch der aktive Indikator erhält diese Farben.
Der aktive Desktop ist größer und behält den vorhandenen Hintergrundindikator.
Fenstersymbole, Desktop-Auswahl, Kontextmenü und Scroll-Aktionen bleiben erhalten.
Die Größeninterpolation folgt weiterhin dem KWin-Swipe-Fortschritt; zufälliges
Neuzeichnen beim Aktivieren entfällt.

Installation auf der bestehenden angepassten Shell:

```sh
python3 kde-customizations/taskbar/flausen-workspaces/install.py
python3 kde-customizations/taskbar/flausen-workspaces/apply-colors-and-limit.py
systemctl --user restart caelestia-shell.service
```

Das Skript prüft den Patch vorab und sichert die aktuelle `Workspace.qml`.
Der Sicherungspfad steht in `../evidence/flausen-workspaces-backup.txt`.
Zum Rückbau die gesicherte `Workspace.qml` nach
`~/.config/quickshell/caelestia/modules/bar/components/workspaces/Workspace.qml`
kopieren. Anschließend die zusätzlich installierte `FlausenWorkspaceIcon.qml`
und das Verzeichnis `flausen-shapes/` daneben entfernen und die Shell neu starten.
`files.json` in der Sicherung listet die betroffenen Dateien auf.

Live geprüft: Shell nach Neustart aktiv, keine Lade-/QML-Fehler für die geänderten
Komponenten; alle vier Desktops über KWin ausgewählt und Screenshots geprüft.
Der ursprüngliche Desktop wurde wiederhergestellt. Physische Klicks und
Touchpad-Swipes wurden nicht automatisiert getestet. Protokoll:
`../evidence/flausen-workspaces-check.json`; Screenshots:
`../../../branding/flausen/evidence/kinetic-start-button/workspace-*.png`.

## Desktops über die Taskbar verwalten

Ein Rechtsklick auf einen Desktop in der Übersicht öffnet „Create desktop“ und
„Remove desktop N“ sowie die beiden vorhandenen Einstellungslinks. Anlegen hängt
einen Desktop an. Entfernen bezieht sich auf den angeklickten Desktop. In der
Lücke zwischen zwei Symbolen gilt der aktive Desktop. Bei einem Desktop ist
Entfernen ausgegraut, bei acht Desktops ist Anlegen ausgegraut. Die konfigurierte
Zahl gleichzeitig sichtbarer Symbole bestimmt weiterhin die Seiten der Übersicht.

`apply-colors-and-limit.py` installiert das Menü und aktualisiert das bestehende
KWin-Skript `flausen-four-desktops` auf maximal acht Desktops. Die Paket-ID bleibt
erhalten, damit die alte Vierergrenze beim Aktualisieren ersetzt wird. KWin
übernimmt die Fensterzuordnung beim Entfernen per Menü. Falls das Limit-Skript
überschüssige Desktops zusammenführt, bleiben weitere Fensterzuordnungen
erhalten. Die Installation legt keine zusätzlichen Desktops an.

Die alte Vollbild-Automatik, die selbst Desktops erzeugt, wird weiterhin bei der
Installation deaktiviert. Die aktuelle Vollbild-Automatik darf aktiv bleiben,
weil sie nur vorhandene Desktops verwendet.

Der Installer sichert die betroffenen QML-Dateien, das vorherige KWin-Paket,
`kwinrc` und die Desktop- und Fensterzuordnungen. Der Pfad steht in
`color-limit-backup.txt`. Für einen Rückbau die gesicherten QML-Dateien gezielt
zurückkopieren. Das Limit-Skript lässt sich mit dem Plugin-Schlüssel
`flausen-four-desktopsEnabled=false` in `kwinrc` und
`qdbus6 org.kde.KWin /Scripting unloadScript flausen-four-desktops` deaktivieren.
Anschließend die Shell neu starten.
