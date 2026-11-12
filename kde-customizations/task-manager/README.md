# flausen Task-Manager

Native QtQuick-Anwendung für KDE/KWin und Caelestia. Die Vorlage des Nutzers
bestimmt die Ressourcenkarten, horizontale Navigation, Prozesstabelle und
rechten Prozessinspektor. Farben, Karten und 12-px-Fensterrahmen stammen aus dem
Settings-Menü (`FlausenStyle`, `WindowControl`, `WindowFrame`); Schriftfamilie und
Schriftrollen aus `MenuStyle` und `MenuText`. Gemeinsame Quellen werden referenziert,
nicht kopiert. Kein globaler KWin-Blur-Eingriff.

## Funktionen

- Das gelieferte Logo wird unverändert als `icon.png` gepflegt und im Fensterkopf
  sowie über die eigene App-ID `flausen-task-manager` im Dock verwendet.
- **Hintergrund & System** ist standardmäßig zugeklappt. Der Abschnittsknopf
  öffnet/schließt die gefilterten Hintergrundprozesse und zeigt deren Anzahl.
- Auslesbare CPU-/GPU-Modelle, Laufwerksmodelle mit Kapazität sowie physische
  Netzwerkadapter stehen in den Ressourcenkarten und der Leistungsansicht.
  Vollständige, gekürzte Gerätenamen sind über den Tooltip zugänglich. Fehlende
  Hardwareangaben bleiben leer. RAM-Typ, konfigurierte Datenrate, Modulgröße und
  Modell kommen bevorzugt aus udevs zwischengespeicherten `memory_id`-Daten;
  optional dient `dmidecode` ohne Rechteerhöhung als Rückfall. Konfigurierte
  Datenrate hat Vorrang vor nomineller SPD-Geschwindigkeit und wird in MT/s
  angegeben; unbekannte Werte werden nicht geschätzt.
- Jedes physische Laufwerk hat eine eigene Karte, I/O-Raten und einen Verlauf.
  Erkennung über `/sys/block`, Messung über gerätespezifische Linux-Zähler.
  Partitionen, Loop, ZRAM und virtuelle Mapper/RAID-Volumes werden nicht zusätzlich
  gezählt; deren physische Laufwerke bleiben sichtbar. Geräte werden während des
  Betriebs neu erkannt. Neue/ausgetauschte Geräte beginnen ohne erfundene Rate.
- Alle vom DRM-Treiber erkannten GPUs haben separate Karten und Verläufe.
  Vulkan kennzeichnet integrierte/dedizierte GPUs anhand der Hardware-IDs, wenn
  verfügbar. NVIDIA-Messwerte werden über `nvidia-smi` je PCI-Gerät zugeordnet;
  AMD-Auslastung, Speicher, Temperatur und Takt über die lesbaren DRM-/hwmon-Dateien.
  Bei integrierter Grafik ist der gemeldete reservierte Grafikspeicher kein
  dedizierter VRAM. Fehlende Telemetrie bleibt leer.
- Die Leistungsansicht zeigt CPU-Kerne als vertikale Segmentbalken: ein Kästchen
  je physischem Kern, gemittelt über seine SMT-Threads. Die Balken verteilen sich
  rahmenlos über die gesamte innere Kartenbreite. Die Zuordnung kommt aus
  der Linux-CPU-Topologie; bei fehlender Topologie werden die bekannten logischen
  Threads einzeln und entsprechend beschriftet angezeigt. Tooltips nennen deren
  einzelne Lastwerte. Die frühere zusätzliche Thread-Kachel entfällt.
- Alle Verläufe nutzen denselben nativen `SparklineItem` und `CircularBuffer`
  wie der Netzwerkgraph im Taskleisten-Overlay. Eine gemeinsame lineare Animation
  verschiebt Messpunkte kontinuierlich zwischen den Abfragen. Serienpuffer und
  sanft angepasste automatische Skalen leben unabhängig von den aktualisierten
  Ansichtsdelegaten. Zusätzliche frühe Messwerte übernehmen die laufende Position;
  die gewählte Abfragerate und „reduzierte Bewegung“ werden berücksichtigt. Es
  werden keine Zwischenmesswerte erfunden.
- Die Oberfläche folgt der KDE-Systemsprache (`plasma-localerc`), ersatzweise
  `LANGUAGE`/`LC_MESSAGES`/`LANG`. Englisch ist die Quellsprache und der Rückfall;
  Deutsch steht im gemeinsamen Katalog `locales/de.json`. Backend-Meldungen,
  Ressourcennamen, Tooltips und Dialoge verwenden denselben Katalog. Weitere
  Sprachen lassen sich über eigene JSON-Kataloge ergänzen. Änderungen der
  KDE-Sprache werden mit der nächsten Abfrage ohne Neustart übernommen;
  Navigation, Ressourcen-IDs und Graphzustände bleiben davon unabhängig.
  Zahlenformatierung ist nicht mehr fest auf Deutsch gesetzt.
- CPU-/GPU-Einzelverläufe sind die Standardanzeige.
- CPU- und GPU-Leistungskarten haben oben rechts einen dezenten Umschalter:
  Segmentbalken oder eigener Verlauf je Kern/Engine. Jede Karte schaltet unabhängig;
  die Wahl bleibt während der laufenden Anwendung und beim Seitenwechsel erhalten.
  Alle Einheiten sammeln ab Start bis zu 60 Messwerte, auch während die Balken
  sichtbar sind. Ein Umschalten beginnt deshalb keinen neuen Verlauf. Geometrie,
  Farbzuteilung und aktuelle Prozentwerte bleiben in beiden Ansichten gleich.
- GPUs verwenden ebenfalls Segmentbalken, jeweils für tatsächlich messbare
  Engines (Grafik, Speicher-I/O, Encoder, Decoder, JPEG, Optical Flow bzw. AMD VCN).
  Die Treiber liefern keine Auslastung je Shader-/CUDA-Kern; GPU-Kästchen sind
  ausdrücklich Engines und keine behaupteten Einzelkernmessungen. Nicht messbare
  Engines werden ausgelassen. NVIDIA-Abfrage fällt bei älteren Treibern auf die
  vorhandene Basis-Telemetrie zurück.
- Echte CPU-, RAM-, Datenträger- und Netzwerkmessung. 60 Messwerte pro Verlauf, einstellbares Intervall 0,5–5 s.
- Suche nach Name, Benutzer oder PID; Filter nach eigenen/anderen Prozessen;
  Sortierung nach Name, CPU, Speicher, Lesen, Schreiben oder PID.
- Verwandte Nachfahren mit gleichem Prozessnamen bilden aufklappbare Gruppen.
  Gruppenwerte summieren CPU, RSS und I/O. RSS kann gemeinsam genutzte Seiten
  mehrfach zählen. Erkannte eigene Anwendungen stehen vor Hintergrund/System.
- Inspektor für einen konkreten PID mit CPU/RAM-Verlauf, Benutzer, Threads,
  Nice-Wert, Startzeit, Pfad, offenen Dateien und Internet-Sockets.
- Beenden (SIGTERM), sofortiges Beenden (SIGKILL), Anhalten und Fortsetzen eigener
  Prozesse mit Dialog. PID und Startzeit werden vor jedem Eingriff erneut geprüft.
- XDG-Autostart-Einträge aktivieren/deaktivieren; systemweite Einträge erhalten
  eine vollständige Benutzer-Übersteuerung. `OnlyShowIn`, `NotShowIn` und andere
  Bedingungen bleiben erhalten und werden vom Sitzungsstarter ausgewertet.
- Eigene systemd-Benutzerdienste anzeigen, starten und stoppen.
- Startbreite 1410 logische Pixel; die Starthöhe wächst mit der Anzahl der
  Ressourcen-/Laufwerkskarten und bleibt durch den Bildschirm begrenzt. Mehrere
  Kartenreihen behalten lesbare Breiten. Auf ausreichend großen Bildschirmen passt
  die Leistungsansicht bei Standard-Schriftgröße vollständig hinein.
- Native Fensterbewegung und Größenänderung; oben rechts ausschließlich der
  Schließen-Knopf. Kein Minimieren-/Maximieren-Knopf und kein Maximieren per
  Titel-Doppelklick. X beendet die eigene Anwendung mitsamt Datenprozess;
  Strg+F sucht. Esc leert die Suche bzw. nutzt denselben Schließpfad.

Nicht verfügbare Prozesswerte bleiben `—`, insbesondere GPU/Netzwerk pro Prozess.
Fehlende Ressourcen- und Hardwareangaben werden ohne Hinweistext ausgeblendet.
CPU-Prozentwerte beziehen sich auf die gesamte CPU-Kapazität. Datenträgeraktivität
ist die auf 100 % begrenzte Busy-Zeit des jeweiligen Laufwerks, kein belegter
Speicherplatz. Netzwerk-Raten summieren die auslesbaren physischen Adapter;
Loopback und virtuelle VPN-Adapter werden nicht doppelt mitgerechnet. Ein Inspektor zeigt den einzelnen Prozess; die eingeklappte Gruppe
kann höhere Summen haben. Netzwerk- und Dateidetails unterliegen Linux-Zugriffsrechten.
Es gibt keine Rechteerhöhung und keine Änderung von Systemdiensten.

## Voraussetzungen und Installation

Aktueller Caelestia-KDE-Desktop unter `~/.config/quickshell/caelestia`, gemeinsame
Menüstil-Komponenten und Settings samt gebautem `Flausen.Settings`-Modul.
Systempakete: `quickshell`, QtQuick Controls/Layout, `python`, `python-psutil`,
`systemd`; optional `nvidia-utils`, `pciutils`, `vulkan-tools` und `dmidecode`. Material Symbols Rounded für die Navigation.
Kein eigener nativer Build erforderlich; das Settings-Modul wird wiederverwendet.
Die Anwendung hat einen eigenen Quickshell-Prozess und startet die Desktop-Shell
nicht neu.

```sh
python3 kde-customizations/task-manager/install.py --dry-run
python3 kde-customizations/task-manager/install.py
flausen-task-manager
```

Der Installer schützt lokal geänderte Dateien und sichert alle ersetzten Dateien
unter `~/.local/state/flausen/task-manager-backups/`. Wiederholte Installation ist
wirkungslos. App-Suche: **flausen Task-Manager**. Es werden keine vorhandenen
Tastenkürzel oder Menüeinträge ersetzt.

```sh
# Anwendung zuerst schließen; Pfad aus der Installerausgabe einsetzen.
python3 kde-customizations/task-manager/install.py --restore BACKUP
```

Der Rückbau schützt zwischenzeitliche lokale Änderungen. Er betrifft ausschließlich
Installationsdateien des Task-Managers; bewusst geänderte Autostart-Einstellungen
oder Dienstzustände sind normale Benutzereinstellungen und bleiben bestehen.

## Prüfung

```sh
python3 -m unittest discover -s kde-customizations/task-manager/tests -p 'test_*.py' -v
python3 kde-customizations/task-manager/tests/live_check.py
./bin/flausen check
```

Backend-Tests verwenden für Signaltests ausschließlich einen eigens erzeugten
`sleep`-Prozess. Die isolierte Live-Prüfung verwendet echte Systemdaten, prüft
Suche, Sortierung, Inspektor, alle vier Ansichten, Gerätenamen, zusätzliche
Laufwerkskarten (simulierte Geräte im isolierten Prüffenster), kleine Fensterbreite und erstellt
Screenshots unter `.cache/task-manager-evidence/`. Sie verändert keine Dienste,
Autostart-Einträge oder gespeicherten Theme-Einstellungen. QtTest ist nur für
diese Prüfung erforderlich. Die Produktionsanwendung enthält keine Test-IPC.
