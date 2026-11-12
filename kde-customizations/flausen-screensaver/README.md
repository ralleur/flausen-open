# flausen. — Kinetic Playground

Verspielter nativer KDE-Lockscreen-Hintergrund auf Schwarz, abgeleitet aus dem
neuen kinetischen Symbol `branding/flausen/kinetic/flausen-symbol.svg`.
Die drei SVG-Pfade (blauer Formkörper mit Aussparung, orangefarbener Keil,
Petrolstreifen) und ihre Farben werden unverändert übernommen. Gezeichnet wird
mit Qt Quick Shapes; Bewegungen sind reine Transformationen der Vektorformen.
Keine Videowiedergabe, keine hochskalierten Bilddateien, kein Canvas oder Blur.
Die bestehende Sperrbildschirmkarte und Authentifizierung bleiben erhalten.

## Bewegungen

- Zufällige Ecke als Startpunkt, außerhalb der zentralen Anmeldekarte.
- Ankunft mit federndem Einsammeln der drei Teile.
- Ruhiges Schweben, kleine Hüpfer, Wackler und gelegentliche Salti.
- Auseinanderwirbeln und elastisches Wiederzusammenfinden.
- Herunterfallen und Neuaufbau an einer anderen Stelle.
- Spielerischer Platztausch und anschließendes Sortieren zum Originalzeichen.
- Hüpfen und Salti als Welle.
- Gemeinsames Weiterhüpfen an einen neuen Platz.
- Schlangenlinie durch den Bildschirm, dann Rückkehr zum Logo.

Die Aktionen wechseln zufällig, vermeiden unmittelbare Wiederholungen und
wechseln zwischen Ausflügen und ruhigen Phasen. Positionsphysik mit Unterteilung
bis 240 Hz, Darstellung höchstens 60 Updates pro Sekunde. Unsichtbare Animation
pausiert. Das Paket enthält nur etwa 32 KB Code und Vektordaten; tatsächlicher
Energieverbrauch hängt von Grafiktreiber, Auflösung und Bildfrequenz ab.

## Installation und Rückbau

```sh
python kde-customizations/flausen-screensaver/install.py
python kde-customizations/flausen-screensaver/install.py --restore
```

Installation als eigenes Paket `com.flausen.kinetic.screensaver`. Der bisherige
ralleur-Saver bleibt installiert. Die vorherige Auswahl liegt unter
`~/.local/state/flausen-os/screensaver/installed.json`.
Die neue Animation lädt beim nächsten Sperren. Bootanimation, initramfs,
Passwortregeln und Desktop-Wallpaper-Rotation werden nicht geändert.

## Reproduktion und Prüfungen

`prepare.py` extrahiert die Originalpfade und berechnet Bézier-Grenzen und
Drehpunkte. `port_engine.py` überträgt die vorhandene achtteilige ralleur-Physik
auf drei beliebig geformte Teile. `check.qml` prüft alle Aktionen, lange
Zufallssequenzen, Full HD/4K/Hochformat/Ultrawide, Größenwechsel und Pausieren
und speichert einen 4K-Render. `qmllint` prüft die QML-Dateien.

Native Prüfung mit dem echten KScreenLocker ausschließlich im Testmodus:
`evidence/verification.json`, `evidence/lockscreen.png`.
Die Renderprüfung löst weder eine Bildschirmsperre noch einen Login oder
Herunterfahren aus. Eine echte Entsperrung wurde nicht automatisiert ausgelöst.

`preview.qml` erzeugt Vorschauframes in `.cache/flausen-saver-preview/`.
Die daraus erzeugte MP4 ist nur eine Vorschau; der installierte Saver läuft live
als Vektoranimation und lädt die MP4 nicht.
