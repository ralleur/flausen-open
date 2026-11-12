# Einheitliche sichtbare Dock-Icons

`DockIcon.qml` verwendet nur im unteren App-Dock eine normalisierte Darstellung.
`normalize.cpp` rendert Theme-, SVG-, Raster- und extrahierte Fenstericons mit Qt,
ermittelt die sichtbare Kontur ab Alpha 32/255 und bringt deren längste Kante auf
504 von 512 Pixeln. Das Seitenverhältnis bleibt erhalten; transparente Ränder
werden ausgeglichen. Schwache Schatten bestimmen die Größe nicht. Das Original
wird unverändert und proportional gezeichnet, mit einem Rand für Kantenglättung.
Breite oder flache Logos behalten ihre Form. Die verbleibende kleine Schattenzone
kann am Bildrand enden.

Klickflächen, App-Abstände, Zoom und Statusanzeigen bleiben auf dem bestehenden
Raster. Topbar und andere Menüs verwenden weiterhin ihre bisherige Darstellung.
Bei einem Lesefehler bleibt das ursprüngliche Icon sichtbar.
Die Icon-Textur wird mit festen 512 × 512 Pixeln geladen und beim Ändern der
Dock-Größe mit linearer Filterung und Mipmaps dargestellt. Die sichtbare
Bildgröße bleibt von der festen Laderesolution getrennt. So löst das Ziehen am Trenner
keine asynchronen Bild-Neuladungen und keine leeren Zwischenframes mehr aus;
das gilt auch für Originalicons während der Normalisierung.
Die erzeugten PNGs liegen unter `~/.cache/flausen/dock-icons-v1/`; ihr Inhalt
bestimmt den Cache-Schlüssel. Es laufen keine dauerhaften Hilfsprozesse.

Voraussetzungen: g++, pkg-config, Qt6Gui/Qt6Core-Entwicklungspakete, SVG-Imageplugin
und die installierte Caelestia-Basis einschließlich `dock-size-range.patch`.

```sh
python3 kde-customizations/taskbar/icon-normalization/install.py --dry-run
python3 kde-customizations/taskbar/icon-normalization/install.py
systemctl --user restart caelestia-shell.service
```

Der Installer baut zuerst und prüft den Patch vor Schreibzugriffen. Er sichert
alle drei Ziele unter `~/.local/state/ralleur-taskbar-backups/dock-icons-*/`.
Rückbau mit dem ausgegebenen Manifest (überschreibt die drei betroffenen Ziele):

```sh
python3 kde-customizations/taskbar/icon-normalization/install.py --restore /PFAD/manifest.json
systemctl --user restart caelestia-shell.service
```

Bei bereits installierter Icon-Normalisierung genügt für dieses Update eine
Sicherung von `~/.config/quickshell/caelestia/components/images/DockIcon.qml`,
das Kopieren der hier gepflegten `DockIcon.qml` an diese Stelle und ein Neustart
von `caelestia-shell.service`. Der ursprüngliche Installer setzt eine noch
ungepatchte Dock-Basis voraus.

Regression ohne Änderungen an der laufenden Desktop-Shell:

```sh
python3 kde-customizations/taskbar/tests/dock_icon_resize.py
```

Der Test lädt die echte QML-Komponente in einer separaten Quickshell-Instanz und
prüft 480 Größenänderungen mit normalisierten und Originalicons: kein Verlassen
von `Image.Ready`, feste Laderesolution, aktivierte Mipmaps und korrekte sichtbare Skalierung.

Live-Prüfung über `ralleurTaskbar-<Monitor>.inspect`: `iconSource` zeigt die
Originalquelle, `normalizedIconSource` die verwendete Cachedatei. Vergleich bei
gleicher Dock-Breite unter `../evidence/dock-icons-before.png` und
`../evidence/dock-icons-after.png`; Messwerte in `dock-icon-normalization-check.json`.
