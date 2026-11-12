# Dialog-Theme

Qt6-Widgets-Stil auf Grundlage der hellen und dunklen Dialog-Mocks vom
1. November 2026. Der bisherige Stil (aktuell Darkly) bleibt als Basis erhalten;
Anpassungen betreffen QDialog und dessen Bedienelemente. Die Variante folgt der
Anwendungspalette: warmes Offwhite oder Anthrazit, Pillenbuttons, großzügigere
Abstände in Messageboxen und Koralle für destruktive Aktionen im dunklen Modus.
Helle Primäraktionen sind wie im Mock schwarz. Buttonrollen werden aus Qt gelesen,
nicht aus deutschen/englischen Beschriftungen. Escape, Standardbutton, Checkboxen,
Dateiauswahl und Anwendungslogik bleiben nativ.

## Bauen und installieren

Vom Repository-Verzeichnis:

```sh
cmake -S kde-customizations/dialogs -B .cache/dialogs-build -G Ninja
cmake --build .cache/dialogs-build
ctest --test-dir .cache/dialogs-build --output-on-failure
python kde-customizations/dialogs/install.py --build .cache/dialogs-build
```

Der Installer sichert die betroffenen Dateien unter
`~/.local/state/ralleur-desktop-tweaks/dialogs-*`, speichert den bisherigen
Widgetstil separat und setzt KDEs Widgetstil auf `ralleur-dialogs`.
Qt findet das Benutzerplugin nach erneuter Anmeldung über `QT_PLUGIN_PATH`.
Der vorhandene Files/Dolphin-Starter findet es bereits beim nächsten neuen
Dolphin-Prozess. Laufende Anwendungen werden nicht beendet. Kein automatischer
Wechsel der systemweiten Farben; Hell/Dunkel folgt weiterhin der KDE-Palette.
Qt6-Widgets-Anwendungen mit eigenem Stil oder eigenen Stylesheets können den Stil
umgehen. Qt Quick, GTK, Electron-Webinhalte und Qt5 sind nicht erfasst.

Gefahrlose Vorschau ohne Dateioperationen, vor einer Installation:

```sh
QT_PLUGIN_PATH="$PWD/.cache/dialogs-build/plugins" QT_STYLE_OVERRIDE=ralleur-dialogs \
  .cache/dialogs-build/preview
# zusätzlich --light für die helle Variante
```

## Grenzen zum Mock

Die Dateikarte mit Metadaten, das Papierkorb-Badge und die genaue Anordnung der
Aktionen gehören zum jeweiligen Anwendungsdialog und werden von einem Widgetstil
nicht hinzugefügt. Warn-, Fehler- und Fragesymbole behalten ihre Bedeutung.
Fensterrahmen, Rundung der äußeren Fensterecken, Schatten und Hintergrundunschärfe
werden weiterhin von KWin/Fensterdekoration gesteuert. Der Stil erzeugt keinen
Bildschirm-Blur und entfernt keine Titelleisten. Die Vorschau ist eine echte
QMessageBox, kein bildgetreuer Nachbau des Mocks.

## Rückbau

```sh
python kde-customizations/dialogs/install.py --restore
```

Der Rückbau stellt die vorige Stilauswahl und Dateien wieder her. Zwischenzeitlich
manuell geänderte Installationsdateien werden nicht überschrieben. Danach Apps
neu öffnen beziehungsweise erneut anmelden. Backups bleiben erhalten.

## Kontextmenüs

Derselbe Stil erfasst auch native Qt6-`QMenu`-Menüs einschließlich Untermenüs.
Die Kontextmenü-Mocks dienen als Grundlage für 14-Pixel-Ecken, innere Abstände,
größere Zeilen, abgerundete Auswahlflächen und dezente Trennlinien. Aktionen,
Icons, Tastaturkürzel und Auswahlzustände kommen weiterhin aus der Anwendung.
Die Menügestaltung wird vor dem Anzeigen angewendet, damit Wayland-Popups ihre
Oberfläche behalten. Die native KDE-Plattformanbindung liefert die zur Palette
passenden Icons. GTK, Web-Kontextmenüs und Qt-Quick-Menüs sind nicht erfasst.

Eine harmlose Beispielansicht baut das Target `menu-preview`. Die vorhandenen
Installer- und Rückbau-Befehle gelten auch für diese Erweiterung.
