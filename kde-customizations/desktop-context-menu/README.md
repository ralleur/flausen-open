# Desktop-Kontextmenü im Dolphin-Stil

Auf ausdrücklichen Nutzerwunsch übernimmt das Desktopmenü die Stilwerte aus
`../dolphin-header/contextmenu.cpp`: native System-Menüschrift (hier Noto Sans
10 pt), Außenradius 14 px, Innenrand 8 px, Zeilenradius 9 px und Hauptzeilen mit
10 px vertikalem Padding plus 1 px Rahmen. Glasflächen, Konturen und Hoverfarben
sind für hell/dunkel identisch zur Dolphin-Definition. System-Icons ersetzen
bei diesem Menü die Material-Glyphen. Die Kontextrollen liegen im gemeinsamen
`MenuStyle`; `Menu.dolphinContextStyle` ist nur im Desktopmenü aktiviert.

Die Aktion `OpenRightClickMenu` heißt nun „Menü anpassen“. Sie wird unabhängig
von der konfigurierten Reihenfolge zuletzt angeordnet und mit Trenner sowie
kleinerer, kursiver Schrift angezeigt. Ihre bisherige Aktion bleibt erhalten.
Der angepasste Default und die bestehende Konfiguration verwenden denselben Namen.

Das Desktopmenü zeichnet seine eigene Glasfläche; die alte Blob-Füllung ist für
dieses Menü deaktiviert. Eine unabhängige, auf 14 px gerundete KWin-Blurregion
folgt der Menüfläche. Die globale Blur-Stärke bleibt erhalten. Andere Kontextmenüs
und Popovers werden dadurch nicht umgestaltet.

Installation: `python kde-customizations/desktop-context-menu/install.py`,
anschließend die Caelestia-Shell neu laden. Der Patch wird vor Änderungen geprüft,
der Installer ist idempotent. Der letzte Sicherungspfad steht in
`backup-latest.txt`. Rückbau: die gesicherten Dateien an ihre gleichnamigen Stellen
unter `~/.config/quickshell/caelestia/` kopieren.

Prüfung: QML-Dateien erfolgreich geparst, Menü nativ in einer isolierten
Wayland-Instanz gerendert, letzte Aktion/Schriftgröße/Kursiv geprüft.
`python kde-customizations/desktop-context-menu/preview.py --out /tmp/desktop-menu.png`
führt ausschließlich die Darstellung aus, keine Menüaktionen. Die Vorschau hat
keine Desktop-Compositor-Unschärfe und keine Übersetzungseinrichtung der Hauptshell.
Beleg: [native Vorschau](preview-native.png), [Messwerte](preview-native.json).
