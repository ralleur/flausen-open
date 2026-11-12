# Screenshot- und Zwischenablage-Popouts

Beide Taskleisten-Overlays nutzen die gemeinsame Systemschrift, Schriftrollen und
Glasfläche aus `MenuStyle` / `MenuText`. Mindestmaßstab 1,15, Zwischenablage-Inhalt
420 × 1,15 px, Screenshot-Inhalt 560 × 1,15 px,
Titel rund 27 px, Haupttext 16 px, Nebenzeilen rund 13 px. Karten haben das
gemeinsame Raster, feine Konturen und separate Icongrößen. Individuelle
Schriftaufschläge bleiben erhalten.

Der Screenshot-Popout verwendet eigene `MenuCapture*`-, `MenuScreenshotList`- und
`MenuRecordingList`-Bausteine. Die vorhandene Utility-Karte wird nicht verändert.
Aufnahme-Modus, Screenshot-Galerie, OCR, Bildsuche, Spectacle, Aufnahme-Steuerung,
Kürzel und KeyCaptureDialog bleiben angebunden. Dropdowns erhalten nur per
`sharedPopoverStyle` die gemeinsame Typografie und Fläche; andere Menüs behalten
ihr Erscheinungsbild. Die zuvor angepasste Desktop-Kontextdarstellung bleibt aktiv.
Die Zwischenablage behält Kopieren, Anheften, Bilder und die Rückmeldung.

Installation: `python kde-customizations/taskbar/capture-clipboard-style/install.py`.
Anschließend die Shell neu laden. Installer ist idempotent. Backup-Pfad in
`backup-latest.txt`; Rückbau durch Kopieren der gesicherten QML-Dateien an dieselben
Pfade und Entfernen der in `created.json` genannten Helfer.

Prüfung: natives GPU-Rendering mit erfundenen Text-/Bilddaten, separaten leeren
Aufnahmeordnern und einer No-op-Aufnahmelaufzeit. Normale Ansicht, Aufnahme-Modus,
sechs Screenshot-Dropdown-Aktionen, leerer Verlauf sowie größere Schrift wurden
geprüft; Textfamilie durchgehend Noto Sans. Es wurden keine Aufnahme, Kopier-,
Anheft-, Lösch- oder Kürzeländerungsaktionen ausgelöst. Die laufende Shell lädt
die Dateien ohne zugehörige QML-Fehler. Isolierte Bilder zeigen keinen
Compositor-Blur hinter echten Desktop-Fenstern.

Reproduzieren: `python preview.py --kind capture --out /tmp/capture.png`,
`--expanded`, `--record`, `--empty`, `--font-scale 1.6`; für den Verlauf
`--kind clipboard`. Beispielbilder und Messwerte liegen neben diesem Dokument.


## Screenshot-Rauchglas und Primäraktion (3. November 2026)

Auf Basis des gelieferten Capture-Mocks: rund 681 px Außenbreite, drei gleichmäßige
Galeriespalten und zwei sichtbare Reihen, ein zurückhaltender Screenshot-/Recording-
Schalter und die Kopfaktion an der ersten Titelzeile. Die gemeinsame Rauchglasfläche
`MenuStyle.taskbarSurface` und der vorhandene vorgewärmte Blur-Pool bleiben aktiv.
Systemschrift und getrennte Schriftrollen bleiben erhalten. Andere Menüs wurden
nicht auf das neue Layout oder den neuen Knopfstil umgestellt.

`MenuPrimarySurface.qml` im gemeinsamen `menu-style/` ist die neue Referenz für
Primäraktionen: vertikal `primaryTop` (#2588ff) nach `primaryBottom` (#0871ef),
feine Außenkontur `primaryEdge` und zurückhaltende innere Lichtkante. Beim Capture-
Splitbutton laufen Verlauf und Außenkontur durch; nur eine feine Linie trennt
Aufnahme und Dropdown. Hover, deaktivierter Zustand und beide Klickbereiche bleiben
getrennt bedienbar. Farben zentral ändern, keine Verlaufskopie je Menü anlegen.

Ein Klick kopiert ein Bild sofort in die Zwischenablage und wählt es für weitere
Aktionen aus, ein Doppelklick öffnet es zusätzlich. Die Auswahl erhält Kontur
und Haken; Texterkennung, Bildsuche und bestätigtes Löschen stehen unten.
Neueste/älteste zuerst ist umschaltbar. OCR und Bildsuche verwenden die bestehende
`ScreenshotAction` auf einer temporären Kopie des ganzen ausgewählten Bildes;
Originale bleiben erhalten, temporäre Kopien werden auch bei Fehlern aufgeräumt.
Bildsuche verwendet wie die bisherige Regionssuche den externen Uguu-/Lens-Weg.
Die Galerie lädt begrenzte Thumbnails (420 × 260); native Maße werden erst bei
Auswahl über `magick identify -ping` gelesen, damit OCR und Suche nicht nur auf
einem Thumbnail arbeiten. Der separate Kopierknopf entfällt; genau ein Bild ist auswählbar. Während einer
laufenden oder pausierten Bildschirmaufnahme bleiben Screenshot-Knopf und Galerie
im Screenshot-Modus verfügbar. Aufnahme-Status und -Steuerung erscheinen nur
im Recording-Modus.

Native Live-Prüfung: ca. 680,8 × 678,8 px, Noto Sans, freigegebene Rauchglasfarbe,
Galerieauswahl per Qt-Mausklick und korrekte Originalmaße. Messzugänge wurden wieder
entfernt, die Shell ist mit der produktiven Quelle neu gestartet. Zusätzlich native
Vorschauen für sechs Bilder, Auswahl, leere Galerie, Recording, Capture-Dropdown
und Schriftmaßstab 1,6. OCR und Bildsuche wurden mit isolierten Befehls-Stubs geprüft:
keine echte Zwischenablageänderung, kein Upload, kein Browseraufruf; Originaldatei
und temporäre Bereinigung geprüft. Keine neue Frame-Zeit-Messung dieses Schritts.

Reproduzieren (nach Installation):

```sh
python preview.py --kind capture --selected --out /tmp/capture-smoke.png
python preview.py --kind capture --action ocr --out /tmp/capture-ocr.png
python preview.py --kind capture --action search --out /tmp/capture-search.png
```

[Live-Ansicht](../evidence/capture-smoke-live.png),
[Mock und Live bei gleicher Breite](../evidence/capture-smoke-comparison.png),
[Prüfwerte](../evidence/capture-smoke-check.json),
[Änderung gegenüber dem Ausgangsstand](../capture-smoke.patch).
Rückbau dieses Schritts: QML-Dateien aus der in
`../evidence/capture-smoke-backup.txt` genannten Sicherung relativ zur Shell
zurückkopieren, deren `created.json` beachten und Shell neu starten.

Funktionsprüfung für direktes Kopieren und parallele Screenshots (isolierter
Recorder und `wl-copy`-Stub, keine Änderung der echten Zwischenablage):

```sh
python preview.py --kind capture --copy --out /tmp/capture-copy.png
python preview.py --kind capture --running --copy --out /tmp/capture-running-shot.png
python preview.py --kind capture --running --record --out /tmp/capture-running-record.png
python preview.py --kind capture --running --paused --out /tmp/capture-paused-shot.png
python preview.py --kind capture --running --paused --record --out /tmp/capture-paused-record.png
```
