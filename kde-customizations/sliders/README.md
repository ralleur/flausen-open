# Gemeinsame segmentierte Schieberegler

Nach der Nutzerreferenz „Dunkle Einstellungen mit segmentierten Schiebereglern“:
schmale, leicht gerundete Segmente, aktiver Bereich in der System-Akzentfarbe, grauer Rest und eine
helle Kontur um die aktuelle Position. Bei 0 % bleibt alles grau. Hellmodus
verwendet eine dunkle Positionskontur. Geräte-/App-Farben bleiben erhalten.

`SegmentedTrack.qml` zeichnet beide Orientierungen und RTL; `SegmentedHandle.qml`
erhält die native Eingabegeometrie. Das Raster ist rein visuell, Werte und Schritte
kommen weiter vom jeweiligen Backend. Die gemeinsamen Shell-Regler, Nexus-Regler,
eingebetteten QtQuick-KDE-Module, Textgröße und das OSD verwenden diese Komponenten.
Die Settings-Regler behalten mindestens 32 px Bedienhöhe. Der vorhandene Qt6-Stil
`ralleur-dialogs` zeichnet auch QSlider segmentiert; seine ursprüngliche Geometrie,
Hit-Tests, Invertierung, Schritte und Tickmarks bleiben erhalten.

Installation vom Repository aus, in dieser Reihenfolge:

```sh
python kde-customizations/sliders/install.py
python kde-customizations/settings/install.py
cmake -S kde-customizations/dialogs -B .cache/dialogs-build -G Ninja
cmake --build .cache/dialogs-build
ctest --test-dir .cache/dialogs-build --output-on-failure
python kde-customizations/dialogs/install.py --build .cache/dialogs-build
systemctl --user restart caelestia-shell.service
```

Neue native Qt6-Prozesse laden den aktualisierten Stil; für die Weitergabe des
Pluginpfads an alle Anwendungen kann eine neue Anmeldung nötig sein. GTK,
Browserinhalte, Qt5 und Anwendungen mit eigenem Stil sind nicht erfasst.

Der Slider-Installer sichert Originale mit Manifest unter
`~/.local/state/flausen/sliders/<Zeitstempel>/`, führt ein Hash-Ledger und schützt
spätere lokale Änderungen. Settings- und Dialog-Installer haben eigene gesicherte
Rückwege. Bei erneuter Anwendung älterer OSD-Patches anschließend diesen Installer
ausführen, damit die gemeinsame Darstellung erhalten bleibt.

Prüfung:

```sh
python kde-customizations/sliders/tests/run.py
python kde-customizations/settings/tests/static_check.py
python kde-customizations/settings/tests/live_check.py --gallery-only --capture appearance --capture audio
```

Die QML-Tests prüfen Maus, Tastatur, Endpunkte, einen von 0–1 abweichenden Bereich,
Vertikalregler und deaktivierte Eingabe. Der CTest `sliders` prüft native horizontale,
vertikale und invertierte Regler. Screenshots der gemeinsamen Komponente liegen in
`evidence/`, echte Settings-Ansichten in `../settings/evidence/native/`.


Blaue aktive Segmente verwenden seit der ausdrücklichen Capture-Stilfreigabe
`PrimaryControlFill` aus dem gemeinsamen Menü-Stil. Andere Geräte-/App-Akzente
bleiben erhalten. Der Installer referenziert die zentralen Materialdateien direkt.
Der Teststarter stellt die echten Materialkomponenten mit einer minimalen
Hell-/Dunkel-Theme-Fixture bereit; neun QML-Prüfungen decken auch Farbzustände,
Fokusgeometrie und Maus-Durchleitung ab.
[Gemeinsamer Control-Standard](../taskbar/menu-style/README.md#freigegeben-als-standard-für-blaue-controls).
