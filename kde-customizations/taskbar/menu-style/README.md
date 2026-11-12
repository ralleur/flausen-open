# Gemeinsame Menüschrift und Taskbar-Rauchglas

Das Startmenü bleibt die Referenz für die gemeinsame Schrift. Für das Material
der Taskbar wurde anschließend der mit dem Nutzer abgestimmte Kalender freigegeben:
Topbar, App-Dock, Startmenü und Dashboard verwenden nun dessen Rauchglas. Ihre erarbeiteten
Kartenmaße, Abstände, Einrückungen und Zeilenhöhen bleiben getrennt davon erhalten.

`services/MenuStyle.qml` hält die Werte; `components/MenuText.qml` erweitert
`StyledText` um die Systemschrift und gemeinsame Hauptfarbe. Das Startmenü bleibt
optisch die Referenz und bezieht seine bestehenden 16/15/13/12-Pixel-Rollen und
Materialfarben jetzt ebenfalls aus `MenuStyle`.

| Rolle | Gemeinsamer Wert |
| --- | --- |
| Familie | Qt-Systemschrift des Startmenüs, hier Noto Sans |
| Haupttext | 16 logische px / 12 pt bei Schriftmaßstab 1,15 |
| Neben-/Kleintext | ca. 13 / 12 px; Hierarchie der bestehenden Menüs bleibt |
| Legacy-Außenfläche dunkel | `#d911161d` (85,1 % Deckkraft), wie im Startmenü |
| Legacy-Außenfläche hell | `#e6f4f5f7`, wie im Startmenü |
| Taskbar/Overlays dunkel | `#b823292e`, 72,2 % Deckkraft, freigegebener Kalender |
| Taskbar/Overlays hell | `#e6e9ecef`, freigegebener Kalender |
| Außenkontur | dunkel `#38ffffff`, hell `#70969ca5` |
| Kartenfüllung | dunkel `#09ffffff`, hell `#0a000000` |
| Haupt-/Nebenfarbe | wie `StartHome.qml`, beide Themes aus derselben Definition |

Der Nutzer-Schriftmaßstab bleibt relativ zur Standardbasis 1,15 wirksam. Titel
behalten ihre Hierarchie. Im Update-Menü reservieren der Titelblock und die drei
Abschnittstitel den alten Platz: Die neue Schrift verschiebt keine Karten.
Rundungen und Icongrößen werden nicht global vereinheitlicht oder skaliert.

## Systemschrift auch für normale Caelestia-Texte

`MenuStyle.systemFontBindings` bindet die zentralen Rollen `body`, `label`,
`title` und `headline` an dieselbe Systemschrift wie `MenuText`. Damit verwenden
auch vollständige `Tokens.font`-Zuweisungen, etwa beim Now-Playing-Titel, die
gemeinsame Familie. Einzelne Widget-Korrekturen reichen dafür nicht aus: In
`shell.json` war für diese vier Rollen noch GoogleSansFlex gespeichert.
Die Systemfamilie gilt nun auch nach einem Neustart und folgt Änderungen der
Qt-Systemschrift. Separate Familienauswahl für diese Rollen wird dadurch ersetzt;
Größen, Gewicht, Nutzerskalierung sowie Icon- und Mono-Rollen bleiben eigenständig.

Installation über den unten beschriebenen gemeinsamen Installer. Für ein bereits
vollständig installiertes System genügt das Aktualisieren von
`services/MenuStyle.qml` aus dieser Quelle und ein Shell-Neustart. Vorherige Datei
und `shell.json` sichern; zum Rückbau beide aus der Sicherung wiederherstellen.

Live-Prüfung am 3. November 2026: Now Playing (ohne aktiven Player: „Nothing
playing“), Temperatur und Datum melden Noto Sans; sämtliche vier zentralen
Textrollen ebenfalls. Symboltexte behalten Material Symbols Rounded.
Beleg: [system-font-check.json](../evidence/system-font-check.json).

## Blur

Startmenü und schwebende Taskleisten-Popouts besitzen bereits eigene gerundete
Regionen im selben KWin-Blur-Effekt (`ContentWindow.qml`). Der unterschiedliche
Eindruck kam zusätzlich von den abweichenden Tönungs-/Deckkraftwerten. Die Popouts
verwenden jetzt dasselbe Material. Es wurde keine globale Blur-Einstellung geändert
und kein zusätzlicher Vollbild-Backdrop für die Popouts eingeschaltet.

## Installation

Auf diesem Rechner installiert. Benötigt die aktuellen Proportionsfassungen der
vier Popouts, einschließlich des gemeinsamen Netzwerk-/Bluetooth-Glasprofils:

```bash
python /home/USER/ralleurOS/kde-customizations/taskbar/menu-style/install.py
systemctl --user restart caelestia-shell.service
```

Der Installer sichert die vorherigen Dateien, ergänzt die zwei gemeinsamen
Bausteine und aktualisiert die bestehenden Quellen. Wiederholte Installation ist
wirkungslos. `../menu-style.patch` enthält die vollständige Änderung.
Die einzelnen Menü-Installer benötigen danach ebenfalls diese gemeinsame Basis,
da ihre aktuellen QML-Dateien `MenuStyle` und `MenuText` verwenden.

## Prüfung

Die laufende Shell meldet Noto Sans, 16 px Haupttext und 85,1 % Deckkraft wie beim
Startmenü. Der Update-Inhalt ist weiterhin 483 × 701,5 logische Pixel groß.
Es wurden keine neuen QML-Laufzeitfehler beobachtet.

Ein isolierter Vorher/Nachher-Vergleich verwendet dieselben Inhalte und dieselbe
Breite. Außenmaß des Update-Renderers: **520 × 740 px vorher und nachher**.
Kopfbereich, alle vier Karten, Trennlinie und Fußbereich behalten ihre Positionen
und Maße. Abschnittstitel behalten Höhe und Position; ihre Textbreite verändert
sich mit der neuen Schrift erwartungsgemäß. Numerische Ränder und Zeilenhöhen
wurden in den anderen Menüs nicht verändert.

Dunkles/helles Update-Menü, WLAN, Bluetooth und Passwortdialog mit größerer Schrift
wurden isoliert aus der Produktions-QML geprüft. Diese Layout-Vorschauen nutzen
Beispieldaten. Die Systemschrift wird offscreen als „Sans Serif“ gemeldet und auf
diesem Rechner laut Fontconfig ebenfalls auf Noto Sans aufgelöst. Der Live-Prozess
meldet ausdrücklich „Noto Sans“. Native Blur-Regionen und Startmenü wurden in der
laufenden Sitzung kontrolliert; die Layout-Vorschauen bilden keinen Compositor-Blur ab.

[Vorher/Nachher](../evidence/menu-style-comparison.png),
[Prüfwerte](../evidence/menu-style-check.json).

## Rückbau

Sicherung: `../evidence/menu-style-backup.txt`. Die dort vorhandenen QML-Dateien
relativ nach `~/.config/quickshell/caelestia/` zurückkopieren. Die beiden in
`created.json` genannten neuen Dateien entfernen, nachdem die bisherigen Quellen
wiederhergestellt sind. Shell neu starten. KWin-, Schriftmaßstab- und andere
Nutzer-Konfigurationen wurden bei dieser Anpassung nicht verändert.


## Freigegebener Rauchglas-Standard für die Taskbar

Nach Freigabe des Kalender-Feinabgleichs am 3. November 2026 auf die obere Leiste,
das separate App-Dock und sämtliche Taskbar-Popouts übertragen. `taskbarSurface`
ist der gemeinsame Materialwert; `calendarSurface` verweist zur Kompatibilität
darauf. `surface` und damit das Startmenü, Dashboard und Desktop-Kontextmenü
behalten ihre bisherigen Werte. Schriftrollen bleiben gemeinsam.

`TaskbarGlass.qml` enthält einmalig die acht zusätzlichen lokalen nativen
Blur-Durchgänge des Kalenders. Topbar und Dock verwenden ihre vorhandenen
Geometrien und Kapselradien, inklusive Ausschnitt hinter dem Startknopf und
mitwachsendem Dock bei Vergrößerung. Jedes geöffnete Popout verwendet denselben
Helfer mit seinem vorhandenen Radius. Die reinen Fenster-Vorschaubilder bleiben
rahmenlos. Die zusätzlichen Fenster sind durchklickbar, nehmen keinen Fokus und
reservieren keinen Bildschirmplatz. Verborgene Flächen haben keine aktive Blur-Region. Die optimierte Fassung
hält ihre Fenster unter den Anwendungen warm; im Vollbild sind sämtliche
sichtbaren Blur-Durchgänge abgeschaltet. Die globale KWin-Blur-Stärke
bleibt 1, Noise 0, Sättigung 100.

Widget-, Dock- und Tray-Kontextmenüs sowie bisher deckende Karten verwenden nun
die vorhandene leichte `cardFill`, damit die äußere Glasfläche sichtbar bleibt.
Screenshot-Dropdowns beziehen ebenfalls `taskbarSurface`. Da diese Untermenüs
im selben Shell-Fenster wie die Galerie liegen, verwischt ein begrenzter
`MultiEffect` zusätzlich deren QML-Hintergrund. Dabei wird nur das darunterliegende
Popout aufgenommen; das Untermenü selbst ist kein Teil der Quelle.

Installation, mit Sicherung und anschließendem Shell-Neustart:

```sh
python kde-customizations/taskbar/menu-style/taskbar_glass.py
systemctl --user restart caelestia-shell.service
```

Der gemeinsame Menü- und der Audio/Akku/Kalender-Installer rufen dieselbe
Konfigurationsroutine auf. Die anderen Quellen behalten ihre Kartenpositionen und
verwenden keine kopierten Materialwerte. Die Routine ist idempotent und ändert
keine Backend-/Lautstärke-/Verbindungs- oder Taskbar-Einstellungen.

[Übersicht](../evidence/taskbar-smoke-overview.png),
[Topbar](../evidence/taskbar-smoke-top.png),
[Dock](../evidence/taskbar-smoke-dock.png),
[Netzwerk](../evidence/taskbar-smoke-network.png),
[Audio](../evidence/taskbar-smoke-audio.png),
[Untermenü](../evidence/taskbar-smoke-dropdown.png).

Live geprüft: 39 benannte Popouts sowie vier dynamische Tray-Menüs laden,
die zusätzlichen Popout-Pässe verschwinden beim Schließen. Im temporären
Vollbildfenster sind Topbar-, Dock- und Popout-Pässe jeweils 0. Native Screenshots
zeigen die Glaswirkung über echten Fenstern; globale Blur-Werte sind unverändert.
Temporäre Prüf-IPC wurde entfernt. [Prüfwerte](../evidence/taskbar-smoke-check.json).
`./bin/flausen check` ist erfolgreich.

Rückbau: QML-Dateien aus dem in `../evidence/taskbar-smoke-backup.txt` angegebenen
Verzeichnis relativ nach `~/.config/quickshell/caelestia/` zurückkopieren,
`components/TaskbarGlass.qml` aus dessen `created.json` entfernen und die Shell
neu starten. Review-Patch: `../taskbar-smoke.patch`.


## Diagnose der ursprünglichen Performanceprobleme

Historische Diagnose vor der unten beschriebenen Optimierung: Die Funktions-
und Sichtprüfung oben hatte keine Animationsperformance nachgewiesen.
Nach der Nutzerrückmeldung wurde die aktuelle Acht-Fenster-Implementierung am
3. November 2026 auf 3840 × 2160 bei 119,88 Hz/HDR systematisch gemessen. Die
freigegebene Optik ist weiterhin installiert; die Optimierungsprototypen und die
Mess-IPC wurden vollständig zurückgebaut.

`TaskbarGlass` erzeugt für jede aktive Fläche acht echte `PanelWindow`-Instanzen.
Leiste und Dock halten dadurch 16 zusätzliche Fenster und Renderthreads vor;
ein Popout erhöht die Zahl auf 24. Beim Öffnen/Schließen werden dessen acht
Fenster neu erzeugt und zerstört. Ihre Fenstergrößen folgen gleichzeitig jedem
Animationsschritt. Beim Dock ändern sie sich mit der Vergrößerung.

A/B/A mit derselben Kalender-Animation, unveränderter Tönung und unveränderten
globalen Blur-Werten, jeweils zwölf Öffnen-/Schließen-Zyklen:

| Fall | Quickshell-CPU¹ | KWin-CPU¹ | 95. Perzentil der Qt-Frame-Abstände² |
| --- | --- | --- | --- |
| 8 zusätzliche Fenster, aktuelle Fassung | ca. 60–61 % | ca. 38–40 % | ca. 331–351 ms |
| Keine zusätzlichen Fenster | ca. 15 % | ca. 13 % | 9 ms |
| 2 zusätzliche Fenster | ca. 28 % | ca. 22 % | 58 ms |
| 8 wiederverwendete Fenster, feste Endgröße (Diagnoseprototyp) | ca. 15 % | ca. 28 % | 10 ms |

¹ Prozent eines CPU-Kerns, über `/proc` und monotone Laufzeit ermittelt.
² `frameSwapped` des Shell-Hauptfensters, Zeitstempel auf dem GUI-Thread mit
1-ms-Auflösung; keine DRM-Präsentationsmessung. Phasen mit laufender Kalender-
Animation sind ausgewertet. Ein 120-Hz-Bild benötigt ungefähr 8,3 ms.

Die Ausgangsfassung erzeugt und zerstört in zwölf Zyklen jeweils 96 Fenster;
zusätzlich wurden rund 1.600 Größenänderungsereignisse gezählt. Allein feste
Fenstergrößen reduzieren Aussetzer, beseitigen die teure Neuanlage aber nicht.
Der Wiederverwendungsversuch erzeugt nach Warmup keine neuen Fenster und keine
Größenänderungen mehr. Dieser Test verwendet absichtlich feste Kalenderkoordinaten
und ist kein auslieferbarer Ersatz.

Separater achtsekündiger Dock-Zeigerdurchlauf ohne neue Fenster: etwa 2.760–2.780
Größenänderungsereignisse, 95. Perzentil 37–39 ms; ohne Zusatzfenster etwa 10 ms.
Die GPU lag in den Kalender-Versuchen durchschnittlich bei rund 36–47 %, maximal
57 %. Damit ist eine pauschale GPU-Sättigung als Hauptursache nicht belegt; die
kontrollierten Varianten weisen vor allem auf Fenster-/Render-Ressourcen und
laufende Größenänderungen hin. 16 ruhende Helfer erhöhen zudem die Zahl der
Quickshell-Renderthreads von 7 auf 23 und in diesen Läufen den RSS um etwa 150 MiB.

**Optimierungsrichtung:** Helfer gezielt wiederverwenden, Puffer während
Animationen auf geeigneten stabilen Endmaßen halten und nur sichtbare
Blur-Ausschnitte animieren. Für das Dock ebenso Reserven für die Vergrößerung
vorsehen. Den Bedarf an acht getrennten Compositor-Oberflächen anschließend
weiter reduzieren. Eine reine Absenkung auf zwei Pässe ist laut Gegenprobe
keine hinreichende Lösung für die 120-Hz-Animationen.

[Messwerte und Methode](../evidence/taskbar-smoke-performance-check.json),
[Rohdaten inklusive Qt-Frame-Zeitstempeln](../evidence/taskbar-smoke-performance-raw.json).


## Performance-Optimierung: produktiver Stand

Auf Nutzerauftrag anschließend umgesetzt und installiert. Die freigegebenen
Farben, acht Blur-Durchgänge je sichtbarer Fläche, Radien, Schrift und
Karten-/Widget-Geometrien bleiben erhalten. Ein kontrollierter Vorher/Nachher-
Vergleich auf demselben nativen Hintergrund zeigt innerhalb des Kalenders eine
mittlere absolute Kanalabweichung von nur **0,04 auf der 0–255-Skala**.
[Direkter Bildvergleich: vorher links, optimiert rechts](../evidence/taskbar-optimized-visual-comparison.png).

### Ressourcen während Animationen wiederverwenden

- Ein fester Pool pro Bildschirm mit je acht nativen Flächen für Topbar, Dock,
  Popout und Untermenü: insgesamt 32. Er wird beim Shell-Start vorbereitet;
  wiederholtes Öffnen vermehrt ihn nicht.
- `TaskbarGlass` behält native Fenster und Puffer. Fensterkapazitäten wachsen nur
  in Größenstufen, wenn neuer Inhalt oder Einstellungen mehr Platz verlangen.
  Das Popout reserviert die unanimierten Inhaltsmaße, das Dock ausreichend Platz
  für die Vergrößerung. Während der geprüften Animationen gibt es **keine**
  Fensterneuanlage, Zerstörung oder Fenstergrößenänderung.
- Die sichtbare gerundete Blur-Region folgt weiterhin der tatsächlichen Animation.
  Eine gemeinsam berechnete Region und zwei einpixelige Randanker stabilisieren
  den Begrenzungsrahmen der KWin-Blur-Texturen. Ein minimaler Paint-Knoten erhält
  die kumulative Unschärfe; eine vollständige Glas-Karte muss nicht in acht
  zusätzlichen Qt-Szenen pro Frame neu gezeichnet werden.
- Ungenutzte Flächen haben nur eine außerhalb liegende leere Blur-Region und liegen
  in der Layer-Shell-Ebene **Bottom**, unter Anwendungsfenstern. Im Vollbild gilt
  das für alle vier Pools. Native Fenster bleiben dabei erhalten; die Rückkehr
  erzeugt keinen neuen Fensterpool. Maus-/Tastatur-Eingabe und reservierter
  Bildschirmplatz bleiben ausgeschlossen.
- `TaskbarGlassState` und `TaskbarDropdownGlass` vermitteln kurzlebige Menüobjekte
  an den dauerhaft vorgewärmten Untermenü-Pool des richtigen Bildschirms. Das
  Schließen/Zerstören eines alten Menüs kann keinen neueren Besitzer freigeben.

Reines Ausblenden über `visible: false` wurde ebenfalls gemessen und verworfen:
Qt baut dabei native Ressourcen ab; trotz bleibender QML-Objekte kehren Aussetzer
zurück (95. Perzentil ca. 169 ms). Das Absenken leerer Fenster auf Bottom benötigt
keine solche Neuanlage und bleibt in der Gegenprobe bei etwa 11 ms.

### Messung der endgültigen Fassung

Gleicher Rechner wie bei der Diagnose: 4K, 119,88 Hz, HDR, RTX 5080. Zwölf
Kalender-Öffnen-/Schließen-Zyklen, dazwischen ein Lauf ohne zusätzliche Flächen;
separat der identische achtsekündige Dock-Zeigerdurchlauf. Gemessen werden
Qt-`frameSwapped`-Callback-Abstände (keine DRM-Präsentationszeitstempel).

| Messung | Vorher | Optimiert |
| --- | --- | --- |
| Kalender: 95. Perzentil | ca. 331–351 ms | ca. 10–11 ms |
| Kalender: längste Pause im finalen Lauf | ca. 364–371 ms | ca. 19–24 ms |
| Kalender: Quickshell-CPU, Anteil eines Kerns | ca. 60–61 % | ca. 18–20 % |
| Kalender: KWin-CPU, Anteil eines Kerns | ca. 38–40 % | ca. 26–27 % |
| Dock: 95. Perzentil | ca. 37–39 ms | ca. 11–13 ms |
| Fenster erzeugt/zerstört oder resized während Animationen | zahlreiche | 0 |

Die medianen Frame-Abstände liegen bei 8 ms. Einzelne spätere Dock-Gegenproben
hatten auch ohne Zusatzflächen ca. 12 ms im 95. Perzentil; System-/Treiberlast
schwankt. Diese Messung ist kein allgemeines 120-fps-Versprechen. Das Warmhalten
bindet mehr Render-/RAM-Ressourcen als ein bedarfsweiser Aufbau; dafür entfallen
die wiederkehrenden Ressourcenwechsel. Der Pool bleibt begrenzt.

Live erneut geprüft: 39 Popout-Typen, vier Tray-Menüs, vier Untermenü-Wechsel,
konstanter 32er-Pool, echtes natives Vollbild inklusive Desktop-Rückkehr. Alle
aktiven Blur-Durchgänge werden im Vollbild null. Temporäre Testfenster, Fokus- und
Desktop-Wechsel sowie Mess-IPC wurden zurückgebaut. `./bin/flausen check` und
wiederholte Installation sind erfolgreich. Globale KWin-Blur-Werte sind unverändert.

[Finale Messwerte](../evidence/taskbar-optimized-performance-check.json),
[Rohdaten und Gegenproben](../evidence/taskbar-optimized-performance-raw.json),
[Funktionsprüfung](../evidence/taskbar-optimized-functional-check.json),
[Untermenü](../evidence/taskbar-optimized-dropdown.png).

Installation wie oben über `taskbar_glass.py`. Rückbau ausschließlich dieser
Optimierung: Dateien aus dem in `../evidence/taskbar-smoke-optimization-backup.txt`
benannten Verzeichnis wiederherstellen und die zwei dort in `created.json`
genannten neuen Komponenten entfernen. Shell danach neu starten.
Review-Patch: `../taskbar-smoke-optimization.patch`; der frühere reine
Materialschritt bleibt separat in `../taskbar-smoke.patch` dokumentiert.

## Dock-App-Kontextmenü nach Rauchglas-Mock

Das App-Kontextmenü des unteren Docks verwendet eine gemeinsame Außenfläche ohne
zusätzliche Innenkarte. Pin- und Fensteraktion teilen feste Icon-/Textspalten;
„Beenden“ steht unter einem Trenner mit rotem Power-Symbol. Hover und Tastaturfokus
heben die ganze abgerundete Zeile dezent blau hervor. Systemschrift und Schriftmaßstab
kommen aus `MenuStyle`/`MenuText`, Material und acht lokale Blur-Pässe aus dem
vorhandenen Popout-Pool. Andere Kontextmenüs und globale KWin-Werte bleiben erhalten.

Quelle: `../overlay/modules/bar/popouts/DockContext.qml`. Nur dieses Menü erhält
8 statt der allgemeinen Popout-Innenrandbasis; die Breite wächst mit langen Texten
und dem separaten Schriftmaßstab. Ohne laufendes Fenster entfällt „Beenden“ samt
Trenner. Die bestehende Battle.net-Framegen-Steuerung bleibt zusätzlich sichtbar;
deren Backend, Pin-, Start- und Beenden-Aktionen wurden übernommen.

Gezielte Installation auf die bestehende Rauchglas-Basis:

```sh
python kde-customizations/taskbar/menu-style/taskbar_glass.py --dock-context
systemctl --user restart caelestia-shell.service
```

Die Option sichert und installiert ausschließlich `DockContext.qml` und die
menüspezifischen Innenränder in `Content.qml`. Auch die vollständige
Rauchglas-Installation enthält diese Fassung. Wiederholte gezielte Installation
ändert nichts. Rückbau: die zwei Dateien aus dem in
`../evidence/dock-context-backup.txt` genannten Verzeichnis relativ in die
Shell-Konfiguration zurückkopieren, anschließend die Shell neu starten.
Review: `../dock-context.patch`.

Live geprüft: laufendes Chromium (drei Aktionen), geschlossenes Steam (zwei
Aktionen), Battle.net mit Framegen-Schalter sowie Hover der Fensteraktion.
Keine neuen QML-Fehler beim Laden dieser Varianten. Die Aktionen wurden zur
Sichtprüfung nicht ausgelöst. Der native Vergleich über einem Browserfenster
bringt Mock und echte Menüfläche auf dieselbe Außenbreite von 594 px; die echte
Fläche maß vor dem Ethernet-Abgleich rund 395 × 247 px. Hintergrund und Unschärfeeindruck hängen vom
Inhalt hinter dem Menü ab. Kein neuer Frame-Zeit-Benchmark für diese Layoutänderung.
`./bin/flausen check` ist erfolgreich.

[Mock/Live bei gleicher Breite](../evidence/dock-context-comparison.png),
[Live-Menü](../evidence/dock-context-live.png),
[geschlossene App](../evidence/dock-context-stopped.png),
[Battle.net](../evidence/dock-context-battlenet.png).


## Startmenü und Dashboard: gemeinsames Rauchglas ohne Layoutänderung

Auf ausdrücklichen Folgeauftrag auf Startmenü (einschließlich Hermes-Fläche) und
Dashboard übertragen. Die maßgebliche Farbe heißt nun `MenuStyle.smokeSurface`:
dunkel `#b823292e`, hell `#e6e9ecef`. `taskbarSurface` und `calendarSurface`
bleiben kompatible Verweise auf denselben Wert. Die Legacy-Rolle `surface` für
andere, nicht beauftragte Oberflächen bleibt erhalten. Das Dashboard-Overlay
referenziert die gemeinsame QML-Quelle per Symlink statt eine veraltete Kopie
über die aktuelle globale Definition zu installieren.

Startmenü und Dashboard erhalten jeweils einen weiteren vorgewärmten
`TaskbarGlass`-Pool mit acht Durchgängen. Das sind jetzt insgesamt **48 native
Hilfsflächen pro Bildschirm**, begrenzt auf sechs Rollen. Beide neuen Pools
verwenden dieselbe Wiederverwendung, stabilen Kapazitäten und Texturextents wie
die optimierte Taskbar; ungenutzte Flächen bleiben leer in Bottom. Breite/Höhe
für die Reservierung kommen aus den unanimierten Inhaltsmaßen. Die vorhandenen
Layout- und Animationsbindungen, Karten, Rundungen und Schriftrollen bleiben
unverändert.

Das Startmenü fordert keinen bildschirmfüllenden Backdrop mehr an und führt
beim Öffnen keine globalen Blur-Einstellungsprozesse mehr aus. Seine lokale,
gerundete native Region bleibt als Basis erhalten. Die alten verformten
Launcher-/Dashboard-BlurMask-Fallbacks sind deaktiviert, damit nur die bestehenden
gerundeten Flächen plus die warmen Pools wirken. Der separate Backdrop-Dienst
bleibt für seine anderen Desktop-/Dolphin-Kontext-Clients verfügbar. Globale
KWin-Werte bleiben bei Stärke 1, Noise 0, Sättigung 100.

**Layoutnachweis:** Alle 174 geprüften Layout-/Schriftdeklarationen der drei
betroffenen UI-Dateien sind erhalten; beim Dashboard-Radius wurde lediglich der
vorhandene Wert über eine gemeinsame Eigenschaft an den Blur weitergereicht.
Startmenü vorher/nachher 720 × 880 px; Dashboard-Hauptreiter 931 × 570 px.
Auch die Außenmaße aller vier weiteren aktivierten Reiter sind gleich. Im
Laufzeitbaum schwankten nur einzelne Breiten der ausgeblendeten Performance-Seite
mit Live-Inhalten, während der Media-Reiter ausgewählt war. Das ist keine Änderung
der Layoutdefinition.

**Performance:** Je zehn Öffnen-/Schließen-Zyklen bei 4K/119,88 Hz/HDR,
zusätzliche Gegenprobe mit abgeschalteten Hilfsflächen. Mit acht Durchgängen
liegen Startmenü und Dashboard im 95. Perzentil der Qt-Frame-Abstände bei
ca. **10 ms** (ohne Zusatzflächen ca. 9 ms). Während der gemessenen Animationen
wurden keine Poolfenster angelegt, zerstört oder resized. Die Hauptansicht des
Dashboards zeigte einzelne längere Aussetzer bis ca. 100 ms auch ohne zusätzliche
Blur-Flächen; diese stammen daher nicht nachweislich aus dem neuen Pool.
Frame-Abstände sind `frameSwapped`-Callbacks, keine DRM-Präsentationsmessung.

Geprüft sind alle fünf Dashboard-Reiter, Startmenü, Suchansicht und eine rein
visuelle Hermes-Vorschau ohne Modell-/Nachrichtenaufruf. Geschlossen bleiben
Launcher-/Dashboard-Pässe null und die Poolgröße 48. Installationsroutinen sind
idempotent; Messzugänge wurden entfernt. `./bin/flausen check` ist erfolgreich.

[Neue Ansichten](../evidence/launcher-dashboard-smoke-overview.png),
[Layout, Messwerte und Prüfgrenzen](../evidence/panel-smoke-check.json),
[Frame-Rohdaten](../evidence/panel-smoke-performance-raw.json),
[Layoutdeklarationen](../evidence/panel-smoke-source-layout-check.json).

Installation weiterhin über `taskbar_glass.py`; auch `dashboard-style/install.py`
verwendet dieselbe Routine. Rückbau dieses Schritts: Dateien aus der Sicherung in
`../evidence/panel-smoke-backup.txt` relativ nach `~/.config/quickshell/caelestia/`
zurückkopieren und Shell neu starten. Review: `../launcher-dashboard-smoke.patch`.

### Größenabgleich mit Ethernet

Auf Nutzerrückmeldung folgt das Dock-App-Menü jetzt exakt der Ethernet-Basis:
`previewKey: "network"`, Mindestmaßstab 1,15 und Taskbar- statt Dock-Icon-Maßstab.
Damit gelten auch dieselben separaten Nutzer-Schriftkorrekturen wie bei Ethernet.
Hier beträgt die Hauptschrift 16 px statt zuvor rund 21 px. Die vorhandenen
Zeilen-, Icon- und Abstandswerte folgen dieser Größenbasis; die Außenfläche
ist jetzt 305,9 × 190,2 px statt 394,6 × 246,5 px. Rauchglas und Aktionen bleiben
erhalten. Native Sichtprüfung und wiederholte Installation erfolgreich, keine
neuen QML-Laufzeitfehler beobachtet; `./bin/flausen check` erfolgreich.

[Aktuelle Ansicht](../evidence/dock-context-ethernet-scale.png). Für den Rückbau
ausschließlich dieses Größenabgleichs `modules/bar/popouts/Content.qml` aus dem
in `../evidence/dock-context-scale-backup.txt` genannten Verzeichnis zurückkopieren
und die Shell neu starten. Die älteren Mock-Vergleiche dokumentieren den ersten
Layoutstand vor diesem Größenabgleich.


### Primäraktions-Referenz: Capture

`MenuPrimarySurface.qml` kapselt den dezenten vertikalen Blauverlauf mit feiner
Kontur und Lichtkante; die vier `MenuStyle.primary*`-Farben sind die einzige Quelle.
Erstmals im Screenshot-Splitbutton angewendet. Geometrie, Klickbereiche, Hover und
Disabled liegen beim aufrufenden Control. Der gemeinsame Installer liefert den
Baustein mit. Die anschließende Freigabe für gemeinsame Controls steht unten.
[Capture-Prüfung und Mock-Vergleich](../capture-clipboard-style/README.md#screenshot-rauchglas-und-primäraktion-3-november-2026).


### Freigegeben als Standard für blaue Controls

Am 3. November 2026 hat der Nutzer den Capture-Stil ausdrücklich für alle blauen
Bedienflächen einschließlich Settings freigegeben. `PrimaryControlFill.qml` legt
das gemeinsame `MenuPrimarySurface` unter die vorhandenen Labels und StateLayer.
Die Hauptfläche, feine Kontur und innere Lichtkante stammen weiterhin ausschließlich
aus den vier `MenuStyle.primary*`-Werten. `MenuStyle.isBlueControl` erkennt deckende
blaue Füllungen; alternative Akzentfarben, transparente Auswahl-Tönungen und graue
Zustände behalten ihren semantischen Farbwert. Die Kontur lässt Fokusrahmen Platz
und übernimmt auch separate Eckradien. Die Dekoration empfängt keine Eingabe.

Abgedeckt sind `ButtonBase` (Text-/Icon-/IconText-Buttons), `ToggleButton`,
`StyledSwitch`, Radio-Auswahlpunkte und beide Hälften von `SplitButton`; außerdem
WLAN-/Bluetooth-Schalter, Energieprofil-Auswahl, Update-Aktion, Kalenderdatum,
Galerie-Haken und die gefüllten Hermes-Aktionen. Die Settings verwenden denselben
Baustein für `FlausenSwitch`, aktive Audio-Geräte, native KDE-Schalter, Checkboxen
und Radio-Auswahlpunkte in `KcmSkin`. Gemeinsame blaue `SegmentedTrack`-Segmente
übernehmen ihn für Shell-, OSD-, Settings- und eingebettete KDE-Regler. Farbmuster,
Schrift, reine Linien und Diagrammdaten sind weiterhin semantische Darstellungen.

Die upstream Shell-Controls werden mit geprüften, idempotenten Textankern in
`primary_controls.py` erweitert; es gibt keine zweite Kopie ihrer Implementierung.
Eigene Controls werden in ihren vorhandenen Quellen gepflegt. Die Installations-
und Rauchglasroutine `taskbar_glass.configure` bindet dieselbe Erweiterung ein.
Geometrie, StateLayer, native Eingabe und bestehender Blur-Pool bleiben erhalten.

Installation dieser Änderung:

```sh
python kde-customizations/taskbar/menu-style/primary_controls.py
python kde-customizations/sliders/install.py
python kde-customizations/settings/install.py
systemctl --user restart caelestia-shell.service
```

Die drei Routinen sichern vor Änderungen; wiederholte Anwendung ist idempotent.
Der Slider-Installer referenziert auch die zentralen Materialdateien direkt, damit
der gemeinsame Regler seine Abhängigkeiten erhält. Keine Materialkopie in Settings.

Prüfung: neun QML-Tests für Farb-/Disabled-Zustände, Fokusgeometrie, Eckradien,
Maus-Durchleitung sowie Slider-Maus/Tastatur/Endpunkte. Native Settings-Galerien
für Appearance, Sound, Bluetooth und Display mit eingebettetem KDE-Modul. Statische
Prüfung von 130 QML-Dateien und zwölf Paletten. Live-Prüfung von WLAN, Bluetooth und
Energieprofil mit sichtbarer Verlaufskomponente; dabei keine Systemschalter betätigt.
Temporäre Messzugänge wurden entfernt und die produktive Shell neu gestartet.
Keine neuen zugehörigen QML-Fehler beobachtet, Katalogprüfung erfolgreich.
Dies ist keine neue Frame-Zeit-Messung.

[Beispiele](../evidence/primary-controls-overview.png),
[Live-Bluetooth](../evidence/primary-bluetooth.png),
[Live-Energieprofil](../evidence/primary-battery.png),
[Prüfwerte und Sicherungen](../evidence/primary-controls-check.json),
[gesamte installierte Änderung](../primary-controls.patch).

Rückbau: Sicherungen aus `primary-controls-check.json` in umgekehrter Reihenfolge
anwenden. Settings über `settings/install.py --restore <Sicherung>` zurücknehmen;
für Slider und Primary-Controls gesicherte Shell-relative Dateien zurückkopieren
und `created.json` beachten. Auch den Slider-Installationsledger aus dessen vorherigem
Stand wiederherstellen bzw. vor erneutem Installieren abgleichen. Anschließend Shell
neu starten. Benutzerpräferenzen wurden in diesem Schritt nicht geändert.


Das Startmenü aktiviert auf ausdrücklichen Wunsch wieder den gemeinsamen
bildschirmfüllenden Dolphin-Backdrop. Sein lokaler Rauchglas-Pool bleibt
unverändert. Der Installer erhält die Socket-Anbindung; die aktuelle
Helper-Version und Installation stehen im
[Launcher-README](../../launcher/README.md#Wiederhergestellt-bildschirmfüllender-hintergrund-blur).
