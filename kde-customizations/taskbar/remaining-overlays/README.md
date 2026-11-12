# Audio, Akku und Kalender

Diese drei Taskleisten-Popouts verwenden `MenuStyle` und `MenuText` des Startmenüs:
Systemschrift, Haupttext 16 px, abgestufte Nebenzeilen, gemeinsame Glasfläche und
feine Kartenkonturen. `ClipWrapper` liefert das bestehende KWin-Material; globale
Blur-Einstellungen bleiben erhalten.

Audio und Akku verwenden 420 × 1,15 px Inhalt und das gemeinsame Kartenraster.
Der Kalender behält seine bestehende Breite von 497 × 1,15 px;
sein Rauchglas-Raster ist unten beschrieben. Schrift und Icon-Geometrie bleiben getrennt. Der
individuelle Akku-Schriftaufschlag bleibt erhalten.

Audio behält Gerätewahl, Eingangspegel, Mute, Wheel-Steuerung und App-Streams samt
Farben. Die drei lokalen `MenuAudio*`-Bausteine vermeiden Änderungen an Slidern
anderer Ansichten. Akku behält UPower und PowerProfiles einschließlich Warnungen;
ohne Akku zeigt die Karte Netzbetrieb. Die Kalendernavigation und Heute-Markierung
bleiben erhalten.

Installation: `python kde-customizations/taskbar/remaining-overlays/install.py`,
anschließend `systemctl --user restart caelestia-shell.service`. Der Installer ist
idempotent. Backup-Pfad: `../evidence/remaining-overlays-backup.txt`. Zum Rückbau die
gesicherten QML-Dateien an die gleichnamigen Stellen der Shell kopieren und die in
`created.json` genannten neuen Helfer entfernen.

Prüfung: Die drei echten Komponenten wurden in der laufenden Shell unsichtbar
instanziiert; alle laden mit 12 pt Haupttext bei Schriftmaßstab 1,15. Lautstärken
und Energieprofil vor/nach Prüfung sind identisch, siehe
[Prüfwerte](../evidence/remaining-overlays-check.json). Isolierte Vorschauen mit
Beispieldaten decken erweiterte Audioquellen, leere Streams, Akku/Netzbetrieb und
hellen Kalender ab. Zusätzlich wurden alle drei Beispielansichten nativ über Wayland mit GPU gerendert:
Noto Sans und die Heute-Markierung des Kalenders sind sichtbar. Die isolierte
Fläche bildet den KWin-Blur über echten Desktop-Fenstern nicht nach.

[Vorschau Audio](../evidence/remaining-audio-expanded-isolated.png),
[größere Schrift](../evidence/remaining-audio-large-isolated.png),
[Akku](../evidence/remaining-battery-isolated.png),
[Netzbetrieb](../evidence/remaining-battery-none-isolated.png),
[Kalender](../evidence/remaining-calendar-light-isolated.png).

Reproduzierbar über `../network-popover/proportions/render.py` mit
`--kind audio|battery|clock`, `--expanded`, `--audio-state empty`,
`--battery-state none`, `--light` und `--font-scale 1.6`.

Native GPU-Beispiele: [Audio](../evidence/remaining-audio-native-fixture.png),
[Akku](../evidence/remaining-battery-native-fixture.png),
[Kalender mit Heute-Markierung](../evidence/remaining-calendar-native-fixture.png).
Dafür beim Renderer `--native` ergänzen.

Auch Datum und Uhrzeit der Taskleiste (`Clock.qml`) verwenden nun die gemeinsame
Systemschrift. Ihre bisherige Schriftgröße, Formatierung und Abstände bleiben
erhalten. Native Prüfung: [Schriftnachweis](../evidence/clock-font-check.json).


## Kalender: erste Rauchglas-Referenz

Am 3. November 2026 nach dem November-Mock umgesetzt und live installiert.
Die Außenfläche bleibt im bestehenden `ClipWrapper`: gemeinsame `MenuStyle`-Farben,
Kontur und KWin-Blur, ohne zusätzliche Kalender-Kartenfüllung. Andere Menüs und die
globale Blur-Stärke wurden nicht verändert. Dies ist die erste Umsetzung zur
visuellen Abstimmung des künftigen Standards.

- Monat/Jahr links, „Today“, Zurück und Weiter kompakt rechts. Kopfaktionen stehen
  auf Höhe der ersten Titelzeile; große Schrift darf den Titel umbrechen lassen.
- Montag zuerst, unabhängig vom ersten Wochentag des Systemgebietsschemas.
  Monats- und Wochentagsnamen bleiben lokalisiert. Sechs stabile Kalenderzeilen
  zeigen auch die angrenzenden Monate; Wochenenden nutzen `MenuStyle.muted`.
- Ruhige 20-px-Datumszahlen, 16-px-Wochentage und ein kräftiger Titel von rund 33 px
  (1,65 × Datumszahl) bei Standard-Schriftmaßstab. Alle Rollen stammen aus derselben
  Systemschrift und skalieren mit der individuellen Schriftpräferenz.
- Der heutige Tag bekommt einen runden Marker in `MenuStyle.accent` mit weißer Zahl.
  `Time.date` hält ihn auch über Mitternacht aktuell. Mausrad, Mittelklick für heute
  und Rechtsklick auf das Uhr-Kontextmenü bleiben erhalten. Kopfknöpfe sind per
  Tastatur erreichbar und haben beschriftete 40-px-Bedienflächen.

[Vergleich bei gleicher Außenbreite](../evidence/calendar-smoke-comparison.png)
(Mock links, echte Shell rechts): Referenz ca. 608 × 446 px, Umsetzung ca.
608 × 451 px. Glas wurde im echten Popover über geöffneten Fenstern geprüft;
Wallpaper und Hintergrundinhalt beeinflussen seine wahrgenommene Farbe.
[Live-Ansicht](../evidence/calendar-smoke-live.png),
[GPU-Vorschau dunkel](../evidence/calendar-smoke-native.png),
[hell mit Schriftmaßstab 1,6](../evidence/calendar-smoke-large-light.png).

Die laufende Produktionskomponente wurde mit November/Dezember 2026, Januar 2027,
Februar 2028 sowie Monaten mit sechs Kalenderzeilen geprüft. 42 Zellen und Montag
als erste Spalte, Jahreswechsel über die echten Pfeilknöpfe und Rückkehr über
„Today“ sind bestätigt: [Prüfwerte](../evidence/calendar-smoke-check.json).
Temporäre Prüf-IPC wurde danach entfernt.


### Rauchglas-Korrektur: nur Kalender

Auf ausdrücklichen Wunsch ist die Kalenderfläche nun heller und rauchiger:
`MenuStyle.calendarSurface` verwendet dunkel `#d92b3034`, während die bisherige
Deckkraft von 85,1 % bestehen bleibt. Andere Menüs verwenden unverändert `surface`.
Die gemeinsame Schrift, das Raster und alle Kopfaktionen bleiben erhalten.

`CalendarGlass.qml` erzeugt ausschließlich für den geöffneten Kalender acht
zusätzliche lokale KWin-Blur-Durchgänge in dessen gerundeter Außenfläche. Die
Ebenen sind ohne Maus-/Tastatur-Eingabe und ohne reservierten Bildschirmplatz;
sie werden beim Schließen entfernt. Die Haupt-Shell liegt währenddessen darüber.
Alle Flächen folgen der Kalenderposition, Größe und dem zugehörigen Bildschirm.
Dies ist ein begrenzter Material-Prototyp, keine Änderung des globalen Blur-Werts.
Die globale `Effect-blur`-Konfiguration bleibt bei Stärke 1, Noise 0, Sättigung 100.

[A/B mit gleicher Rauchgrau-Tönung](../evidence/calendar-smoke-blur-comparison.png):
links nur der bisherige native Blur, rechts zusätzliche lokale Durchgänge.
Dahinterliegende Schrift wird sichtbar stärker zu breiten, weichen Formen zerlegt.
[Neue Live-Ansicht](../evidence/calendar-smoke-blur-on.png).
Isolierte GPU-Vorschauen zeigen die Tönung, aber keine gestapelten Compositor-Pässe.

Der bestehende Installer installiert den Helfer und ergänzt die Kalenderbedingung
im `ClipWrapper` sowie die temporäre Ebenenwahl in `ContentWindow`. Er ist weiterhin
idempotent. Rückbau dieses Materialschritts: die Dateien aus
`../evidence/calendar-glass-backup.txt` wiederherstellen und den neuen Helfer
`modules/bar/popouts/CalendarGlass.qml` entfernen; danach Shell neu starten.


### Feinabgleich nach direktem Mock-Vergleich

Die dunkle Kalender-Tönung wurde anschließend von `#d92b3034` auf `#b823292e`
reduziert: 72,2 % statt 85,1 % Deckkraft und ein etwas dunkleres, weniger graues
Rauchblau. Dadurch kommen mehr Hintergrundfarben und Helligkeitsverläufe durch.
Die acht lokalen Blur-Durchgänge bleiben unverändert; Text hinter dem Kalender
bleibt weich. Helles Material, andere Menüs, Typografie und Geometrie sind unverändert.
[Live-Ansicht](../evidence/calendar-transparency-live.png),
[Werte](../evidence/calendar-transparency-check.json).
Die vorherige Materialfassung liegt im Backup aus
`../evidence/calendar-transparency-backup.txt`.


## Audio: vertikale Regler nach Referenz-Mock (3. November 2026)

Das Audio-Popout zeigt Ausgabe und Eingang nebeneinander: gleiche Kartenbreite,
Gerätewahl mit blauem Icon-Feld, runde Mute-Aktion, 24 vertikale Segmente und
Prozentwert. Ausgabe verwendet Grün, Eingang Korallrot; stummgeschaltete oder
fehlende Geräte erhalten keine farbige Füllung. Fehlende Geräte zeigen einen
Gedankenstrich statt eines gespeicherten Pegels. Gerätebezeichnungen nutzen die
gemeinsame Nebenzeilenschrift und zwei Zeilen; die ausgeklappte Gerätewahl bietet
bis zu drei Zeilen. Beide Listen setzen weiterhin die vorhandenen PipeWire-Dienste
ein. Namen und Auswahlzustände sind zusätzlich für Hilfstechnologien beschriftet.

Klick und Ziehen setzen den Pegel, Mausrad und Pfeiltasten ändern ihn in der
konfigurierten Schrittweite. Pos1/Ende setzen 0/100 Prozent. Die bestehende
Lautstärkefunktion hebt Mute beim Verstellen auf; der Ausgang spielt den bisherigen
Bestätigungston nach dem Loslassen. Die breite unsichtbare Trefferfläche bleibt
unabhängig von der gezeichneten Segmentbreite. Die Shell begrenzt das Popout bei
kleinen Bildschirmen über ihren vorhandenen scrollbaren Viewport.

„App volumes“ und „Now playing“ starten entsprechend dem Mock eingeklappt.
App-Streams behalten eigene Farben, Slider und Mute; die Wiedergabekarte zeigt
MPRIS-Titel, Interpret und verfügbare Zurück-/Play-/Weiter-Aktionen.
`MenuStyle`/`MenuText` und der bestehende vorgewärmte Glas-Pool bleiben die
Material- und Schriftquelle. Andere Menüs wurden für diesen Umbau nicht verändert.

[Mock-Vergleich bei gleicher Außenbreite](../evidence/audio-mock-comparison.png):
Referenz auf 520 × 694 px normiert, echte Shell etwa 520 × 698 px.
[Live-Ansicht](../evidence/audio-mock-live.png),
[aufgeklappt mit langen Namen](../evidence/audio-mock-expanded.png),
[große Schrift, hell, ohne Geräte](../evidence/audio-mock-large-empty.png),
[Prüfwerte](../evidence/audio-mock-check.json).
Die realen Pegel (33 % Ausgabe, 80 % Eingang) und Mute-Zustände blieben bei der
Live-Prüfung unverändert. Interaktionstests verwenden ausschließlich Beispieldaten.

Reproduzierbare native Bedienprüfung:

```sh
python kde-customizations/taskbar/network-popover/proportions/render.py \
  --kind audio --native --verify-audio --out /tmp/audio-controls.png
```

Sie prüft Klick, Drag, Mausrad, Tastatur einschließlich Grenzwerten, Mute,
Gerätewechsel und beide Klappbereiche. Die Ausgabe muss `AUDIO_INTERACTIONS_PASS`
enthalten; andernfalls endet der Renderer mit Fehler. Temporäre Live-Prüf-IPC
wurde nach der Sichtprüfung entfernt. Der Installer ist weiterhin idempotent;
`./bin/flausen check` meldet alle 22 Komponenten vollständig.

## Now Playing: quadratisches Cover und Transportleiste (3. November 2026)

`Media.qml` ersetzt ausschließlich den Taskleisten-Player. Das Dashboard behält
seinen bisherigen Aufbau. Die Vorlage wird mit großem quadratischem Cover,
zentrierten Metadaten, 32 Fortschrittssegmenten und fünf runden Knöpfen umgesetzt.
Die Quelle steht mit App-Icon im Kopf; mehrere MPRIS-Quellen bleiben auswählbar.
Titel können zwei Zeilen belegen. Unbekannte Dauer, fehlendes Cover und fehlende
Medien haben eigene Fallbacks; nicht unterstützte Aktionen sind deaktiviert.

`MenuStyle`/`MenuText`, die gemeinsame blaue `MenuPrimarySurface` und der vorhandene
Glas-Pool bleiben die Quellen für Schrift und Material. Der Mindestmaßstab ist
1,15. Das Popout misst regulär etwa 469 px Breite; lange Titel und große Schrift
lassen die Höhe wachsen, der bestehende Shell-Viewport begrenzt kleine Displays.
Die Quellenfilter, manuelle Quellenauswahl und Lautstärke per Mausrad bleiben
vorhanden. Der Fortschritt lässt sich anklicken/ziehen; Pfeiltasten ändern ihn
um fünf Sekunden, Pos1/Ende springen an die Grenzen. Wiederholung wechselt zwischen
aus, Titel und Playlist. Die laufende Position wird nur bei sichtbarer Wiedergabe
aktualisiert, ohne den bisherigen Beat-Tracker für diese Ansicht zu laden.

Installation erfolgt mit dem oben genannten Installer. Sicherung vor dem Umbau:
[Backup-Pfad](../evidence/now-playing-backup.txt). Für den vollständigen Rückbau
`modules/bar/popouts/Media.qml` und `Content.qml` aus dieser Sicherung an dieselben
Stellen der Shell kopieren und die Shell neu starten.

[Vergleich mit gleicher Außenbreite](../evidence/now-playing-comparison.png),
[echte Shell mit Chromium](../evidence/now-playing-live.png),
[native MEUTE-Beispielansicht](../evidence/now-playing-native-fixture.png),
[große Schrift und langer Titel, hell](../evidence/now-playing-large-light.png),
[ohne Medien](../evidence/now-playing-empty.png),
[Prüfwerte](../evidence/now-playing-check.json).
Die isolierte Ansicht bildet das Compositor-Glas nicht nach. Das MEUTE-Cover für
den Vergleich ist ein Ausschnitt der vom Nutzer bereitgestellten Vorlage und
kein im Produkt hinterlegtes Cover. Live wurden Quelle, Metadaten, Fortschritt
und Glas geprüft; die Interaktionstests verwenden ausschließlich Ersatzdienste.

Reproduzierbare native Bedienprüfung (installierte Shell-Abhängigkeiten nötig):

```sh
python kde-customizations/taskbar/remaining-overlays/tests/render_media.py --out /tmp/media.png
python kde-customizations/taskbar/remaining-overlays/tests/render_media.py --out /tmp/media-large.png --long --light --font-scale 1.6
python kde-customizations/taskbar/remaining-overlays/tests/render_media.py --out /tmp/media-empty.png --empty
```

Alle Aufrufe müssen `MEDIA_CONTROLS_PASS` ausgeben. Optional lädt `--art /pfad/cover.png`
ein lokales Beispielcover. Geprüft werden Seek-Klick, Pos1/Ende, externe
Positionsänderungen, Play/Pause, Titelsprung, Shuffle, die drei Wiederholungsmodi,
Öffnen der Quellenwahl, Mausrad-Lautstärke und deaktiviertes Seeking.

### Cover-Korrektur bei doppelten Chromium-Quellen

Chromium kann denselben Tab zusätzlich zur Plasma-Browserintegration melden.
Sein eigener Eintrag enthält teils nur „Titel • Interpret“ und das Browser-Logo;
die Browserintegration liefert dagegen das Albumcover. `Media.artworkUrl` ergänzt
bei solchen unvollständigen Metadaten das Bild aus dem reicheren Eintrag, wenn
App und normalisierter Titel (gegebenenfalls mit Interpret) übereinstimmen.
Transport, Fortschritt und ausgewählte Quelle bleiben am ursprünglichen Player.
Fremde Titel oder andere Apps liefern kein Ersatzcover.

Die native Fixture-Prüfung deckt diese Zuordnung und die Ablehnung abweichender
Titel/Apps ab (`MEDIA_ARTWORK_MATCH_PASS`). Nach der Installation wurde das echte
Cover auch beim nächsten MEUTE-Titel angezeigt:
[Live-Nachweis](../evidence/now-playing-cover-fixed-live.png),
[Prüfwerte](../evidence/now-playing-cover-fix-check.json).
