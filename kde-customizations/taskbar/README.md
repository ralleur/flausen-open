# Caelestia: Topbar und separates App-Dock

## Feste Abstände der Statussymbole

Netzwerk, Bluetooth, Audio und die übrigen Statussymbole behalten dauerhaft den
bisherigen größeren Hover-Abstand. Der Abstand hängt nicht mehr vom Mauszeiger
ab; die Animation dafür entfällt. Hover-Erkennung und Popouts bleiben erhalten.
Patch: `status-icons-spacing.patch`, nach den bisherigen Taskbar-Patches:

```sh
patch --batch --forward -p0 -d ~/.config/quickshell/caelestia -i "$PWD/kde-customizations/taskbar/status-icons-spacing.patch"
systemctl --user restart caelestia-shell.service
```

Rückbau mit demselben Patch und `patch -R -p0`, danach die Shell neu starten.

## Einheitliche sichtbare App-Icons

Das untere Dock gleicht transparente Bildränder automatisch aus. Quadratische
App-Symbole verwenden damit dieselbe sichtbare Kantenlänge wie die übrigen Icons;
Seitenverhältnis, Klickflächen und Abstände bleiben erhalten.
[Quelle, Installation und Rückbau](icon-normalization/README.md).
Patch: `dock-icon-normalization.patch`.

## Gemeinsame Schrift und freigegebenes Rauchglas

Die Systemschrift stammt weiterhin aus dem Startmenü. Die mit dem Nutzer
abgestimmte Rauchglas-Wirkung des Kalenders gilt jetzt für Topbar, App-Dock
und alle Taskbar-Popouts einschließlich Widget-, Dock-, Tray- und Untermenüs.
`MenuStyle.taskbarSurface` und `TaskbarGlass` pflegen Tönung und lokale Unschärfe
zentral; andere Desktop-Flächen behalten ihr Material. Die verfeinerten
Kartenpositionen und Abstaende bleiben erhalten. Werte, Installation und Rueckbau:
[menu-style/README.md](menu-style/README.md). Patches: `menu-style.patch`, `taskbar-smoke.patch`.


Die Rauchglas-Flächen verwenden inzwischen einen vorgewärmten, begrenzten
Fensterpool und stabile Render-Puffer. So bleibt die freigegebene Optik erhalten,
während Fensteraufbau und Größenwechsel aus den Animationen verschwinden.
[Optimierung und Messwerte](menu-style/README.md#performance-optimierung-produktiver-stand).


## Dock-App-Kontextmenü

Das Kontextmenü des unteren Docks folgt dem Rauchglas-Mock mit Iconspalten,
blauen Hover-Zeilen und abgesetzter Beenden-Aktion.
[Quelle, gezielte Installation und Live-Vergleich](menu-style/README.md#dock-app-kontextmenü-nach-rauchglas-mock).

## Taskbar-Kontextmenü und Bildschirmrand

Die obere Taskbar hat ein Kontextmenü im Stil des Dock-Menüs: Task Manager,
Taskbar-Einstellungen, Entsperren/Sperren zum Ziehen und Auto Hide mit Zustand.
Im entsperrten Zustand lässt sie sich an alle vier Bildschirmränder ziehen.
Das separate App-Dock bleibt erhalten. Quelle, Installation, Rückbau und
Live-Prüfung: [topbar-context/README.md](topbar-context/README.md).

## Audio, Akku und Kalender

Die restlichen drei Overlays verwenden ebenfalls die gemeinsamen Schrift- und
Materialrollen. Audio behält Quellenwahl und App-Lautstärken, Akku die Energieprofile
und der Kalender seine breitere Geometrie und Navigation. Umsetzung und Prüfgrenzen:
[remaining-overlays/README.md](remaining-overlays/README.md).

## Bluetooth mit den gemeinsamen Menü-Proportionen

Das Bluetooth-Popout nutzt jetzt dieselbe Größenbasis wie Update-Hub und Netzwerk:
ruhige Schrift, feste Icon-/Statusspalten, Akkuanzeige und kompakte Gerätezeilen.
Power, Suche, Verbinden/Trennen und Entfernen bleiben angebunden.
Installation, Schriftmigration, Rückbau und Prüfgrenzen:
[bluetooth-popover/README.md](bluetooth-popover/README.md).
Patch: `bluetooth-proportions.patch`.


## Netzwerk-Overlays mit den gemeinsamen Proportionsregeln

WLAN, Ethernet, VPN/Tailscale, Verbindungsdetails und Passwortdialog verwenden
jetzt die Schrift-, Spalten- und Abstandsregeln des verfeinerten Update-Menüs.
Installation, gezielte Migration des alten Schriftaufschlags, Rückbau und
Prüfgrenzen: [network-popover/README.md](network-popover/README.md).
Patch: `network-proportions.patch` (nach den bisherigen Netzwerk-/Tailscale-Patches).


## Tailscale automatisch im VPN-Bereich

Die VPN-Liste führt jetzt NetworkManager-Profile und automatisch erkanntes
Tailscale zusammen. Tailscale läuft über einen eigenen Dienst und war deshalb
in der reinen NetworkManager-Profilliste unsichtbar. Der Adapter
`network-popover/tailscale-vpn.py` fragt den tatsächlichen `BackendState` alle
zehn Sekunden ab; installiertes Tailscale bleibt auch getrennt oder bei
Anmeldebedarf sichtbar. Ohne installiertes Binary entsteht kein Eintrag.
Die Ausgabe enthält ausschließlich den zusammengefassten Status.

Der Eintrag nutzt eine eigene Verbindungs-ID, damit Namensgleichheit mit einem
NetworkManager-Profil keine falsche Aktion auslöst. Klicks verwenden `tailscale up`
oder `tailscale down`, erhalten die vorhandenen Einstellungen und zeigen Fehler
an. Erkennung und Shell-Start ändern keine Verbindung. Dieselbe Liste wird in
den Netzwerkeinstellungen genutzt. Der VPN-Header zeigt den aktiven Anbieter.

Installation zusätzlich zur aktuellen `network-popover/Network.qml`:
`tailscale-vpn.patch` in `~/.config/quickshell/caelestia` mit `patch -p0` anwenden,
`network-popover/tailscale-vpn.py` nach `scripts/tailscale-vpn.py` unter diesem
Verzeichnis kopieren und `caelestia-shell.service` neu starten.
Sicherung: [Backup-Verzeichnis](evidence/tailscale-vpn-backup.txt).
Zum Rückbau die drei dort gesicherten Dateien an ihren ursprünglichen Ort
zurückkopieren, `scripts/tailscale-vpn.py` entfernen und die Shell neu starten.

Geprüft: fünf Adaptertests (Installation, Dienstfehler, Authentifizierungsstatus,
aktive Verbindung ohne Peer-Verkehr und Aktionsfehler) sowie die laufende Shell
mit Tailscale „Verbunden“. [Screenshot](evidence/tailscale-vpn.png),
[Prüfdaten](evidence/tailscale-vpn-check.json).
Die bestehende Tailscale-Verbindung wurde bei der Prüfung nicht umgeschaltet.
Tests: `python3 -m unittest discover -s network-popover/tests -v`.

## Netzwerkfenster nach den hellen und dunklen WLAN-Mocks

`network-popover/Network.qml` ist die installierte Komponente;
`network-popover.patch` enthält die Änderung gegenüber dem gesicherten Stand.
Gruppenflächen, Umrandungen, Textabstufungen und Überschrift entsprechen dem
überarbeiteten Update-Hub. Wi-Fi erhält eine Statuskarte mit blauem Schalter;
Netzwerke stehen in einer gemeinsamen Liste mit Signalstärke, Schlössern rechts,
Trennlinien und Verbindungssymbol. Scan-Button und aufklappbarer VPN-Bereich sind
separat. Die gemeinsame Glasfläche bleibt die Außenfläche. Zeilen wachsen mit
der getrennt einstellbaren Textskalierung mit.

Die vorhandenen NetworkManager-, Passwort-, Ethernet- und VPN-Aktionen bleiben
angebunden. Das Zahnrad öffnet die bestehende Netzwerk-Einstellungsseite. Der
WLAN-Schalter wartet auf die Backend-Antwort und zeigt Fehler im Popover an.
Angezeigt werden echte Netzwerke, keine Beispieldaten aus den Mocks.

Installation: `network-popover/Network.qml` nach
`~/.config/quickshell/caelestia/modules/bar/popouts/Network.qml` kopieren und
`systemctl --user restart caelestia-shell.service` ausführen.
Zum Rückbau `Network.qml` aus dem
[Backup-Verzeichnis](evidence/network-popover-backup.txt) zurückkopieren und
neu starten.

Live geprüft: [dunkel](evidence/network-popover-dark.png),
[hell](evidence/network-popover-light.png),
[VPN geöffnet](evidence/network-popover-vpn.png), Ethernet und Scan-Anforderung.
[Prüfdaten](evidence/network-popover-check.json).
Das ursprüngliche dunkle Theme ist wiederhergestellt; temporäre Test-IPC entfernt.
Es wurde keine Netzwerkverbindung umgeschaltet.

## Rechtes Randmenü: Output, Input und Helligkeit

Das OSD zeigt Output-Lautstärke, Input-/Mikrofon-Lautstärke und Helligkeit
untereinander. `osd.enableMicrophone=true` in `~/.config/caelestia/shell.json`
aktiviert den vorhandenen Input-Regler. Er bleibt auch neben dem Session-Menü
sichtbar. Ziehen und Mausrad verwenden weiterhin den nativen Audio-Service.

`osd-input-colours.patch` ergänzt `FilledSlider.fillColor` (Standard bleibt
`Colours.palette.m3secondary`) und setzt nur im OSD die exakten Werte aus
`settings/overlay/modules/nexus/pages/WallpaperAndStyle.qml`:
Output Grün `#53C67B`, Input Korallrot `#F16F5C`, Helligkeit Gold `#EFB34F`.
Die Farben bleiben beim Wechsel der aktiven Akzentfarbe gleich.

```bash
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/taskbar/osd-input-colours.patch
```

Zum Aktivieren den Shell-Dienst stoppen, im bestehenden `shell.json` ausschließlich
`osd.enableMicrophone` auf `true` setzen und `caelestia-shell.service` wieder starten.
Live geprüft: Shell geladen, drei Regler in richtiger Reihenfolge und Farbe;
[Detail-Screenshot](evidence/osd-input-colours.png).
Die vorherigen QML-Dateien und die Konfiguration liegen im
[Backup-Verzeichnis](evidence/osd-input-colours-backup.txt).
Zum Rückbau die beiden gesicherten QML-Dateien wiederherstellen und bei
angehaltener Shell nur den vorherigen Wert von `osd.enableMicrophone` übernehmen
(vorher nicht gesetzt), anschließend den Dienst starten.

### Segmentierte Glasleiste nach Mock

`osd-glass/Content.qml` und `osd-glass/SegmentedSlider.qml` ersetzen die
gefüllten Regler durch 22 abgerundete Segmente, feste Symbolkreise und
permanente Prozentanzeigen. Output bleibt grün, Mikrofon korallrot und
Helligkeit gold. Die Glasfläche ist 84 Pixel breit, hat eine feine helle
Kontur und verwendet die vorhandene Blur-Maske. Die Höhe passt sich dem
Bildschirm an. Audio-Maximalwert, Aktivierung der einzelnen Regler,
Ziehen, Tastatur und Mausrad verwenden weiterhin die vorhandenen Services.
Stummgeschaltete Audiokanäle zeigen inaktive Segmente und ihr Stumm-Symbol.
Ein Klick auf das Lautsprecher- bzw. Mikrofon-Symbol schaltet den jeweiligen
Standardkanal stumm und beim nächsten Klick wieder ein; der Pegel bleibt erhalten.
Die Symboltasten sind auch per Tab und Leertaste bedienbar.

`osd-glass.patch` nimmt ausschließlich die OSD-Fläche aus der gemeinsamen
undurchsichtigen Blob-Fläche heraus und deaktiviert ihre Verformung.
Installation auf der bereits angepassten Caelestia-Shell:

```bash
/home/USER/ralleurOS/kde-customizations/taskbar/osd-glass/install.sh
```

Der Installer sichert die vorherigen Dateien und startet den Shell-Dienst neu.
Live geladen und per Screenshot geprüft: [Detail](evidence/osd-glass.png).
Das Backup der ersten Aktivierung steht in [osd-glass-backup.txt](evidence/osd-glass-backup.txt).
Zum Rückbau den Dienst stoppen, `modules/osd/Content.qml` und
`modules/drawers/ContentWindow.qml` aus diesem Backup wiederherstellen,
die hinzugefügte `modules/osd/SegmentedSlider.qml` entfernen und den Dienst starten.

## Gleichbleibende Transparenz mit geschlossenem Startmenü

Der Launcher setzte den globalen KWin-Blur vorübergehend auf Stärke 1 und
stellte beim Schließen den deutlich stärkeren Standard wieder her. Dadurch
wirkte die Topbar im geschlossenen Zustand undurchsichtig, obwohl ihre
QML-Tönung unverändert blieb. Der dezente Wert ist jetzt dauerhaft in
`~/.config/kwinrc` unter `[Effect-blur]` gesetzt:

```ini
BlurStrength=1
NoiseStrength=0
Saturation=100
```

Nach Änderung `qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.reconfigureEffect blur`
ausführen. Dafür ist kein Shell-Neustart nötig. Nur bei geschlossenem
Launcher/Passwortdialog ändern, damit keine temporäre Sicherung den Wert
später zurücksetzt. Die Launcher-Helper sichern und restaurieren nun dieselben
Werte; der Effekt bleibt nach dem Schließen gleich. Da KWin diese Einstellungen
global verwendet, erhalten auch Dock und andere native Blur-Flächen den dezenten
Blur. Die Tönung und Geometrie der Leisten wurden nicht verändert.

Live geprüft: identische Werte bei geöffnetem und anschließend geschlossenem
Startmenü, temporäre Sicherung danach freigegeben; Topbar-Screenshots kontrolliert.
[Prüfprotokoll](evidence/persistent-glass-check.json),
[offen](evidence/persistent-glass-open.png),
[geschlossen](evidence/persistent-glass-after-close.png).
Die vorherige `kwinrc` ist im Verzeichnis aus
[evidence/persistent-glass-backup.txt](evidence/persistent-glass-backup.txt)
gesichert. Zum Rückbau bei geschlossenem Launcher/Passwortdialog nur
`BlurStrength` und `Saturation` unter `[Effect-blur]` löschen (vorher nicht
gesetzt), `NoiseStrength=0` beibehalten und den Blur-Effekt neu laden.

## Glas ohne Körnung

Die sichtbare Pixelstruktur stammte aus KWin: Ohne explizite Einstellung legt
der Blur-Effekt zusätzlich eine Rauschtextur über transparente Flächen.
`[Effect-blur] NoiseStrength=0` in `~/.config/kwinrc` schaltet sie dauerhaft ab.
Transparente Tönung, Blur-Regionen und Blur-Stärke bleiben unverändert.
Die Einstellung betrifft alle Flächen mit KWin-Blur, auch das untere Dock.

```bash
kwriteconfig6 --file kwinrc --group Effect-blur --key NoiseStrength --type int 0
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.reconfigureEffect blur
```

Bei geöffnetem Launcher/Passwortdialog zuerst dessen Schließen und die Freigabe
der temporären Blur-Einstellungen abwarten. Der vorhandene Helper sichert und
restauriert danach auch den expliziten Wert 0 korrekt.
Das Öffnen und Schließen des Launchers wurde geprüft. Der Screenshotvergleich
zeigt in einer gleichmäßigen Innenfläche keine Rauschstruktur mehr:
[Prüfung](evidence/noise-free-blur-check.json),
[vorher](evidence/noise-free-blur-before.png),
[nachher](evidence/noise-free-blur-after.png).
Sicherung und vorheriger Einzelwert: siehe
[Backup-Pfad](evidence/noise-free-blur-backup.txt).
Zum Rückbau nur `NoiseStrength` wieder löschen (vorher nicht gesetzt) und den
Blur-Effekt mit obigem D-Bus-Aufruf neu laden.

Lokale Anpassung der **laufenden Caelestia-KDE-Shell unter KDE/KWin**. Die linke
Zone mit Launcher und Arbeitsflächen und die rechte Zone mit Tray, Uhr und
Status bleiben in ihrer Reihenfolge erhalten und stehen nun oben. Die mittlere
Zone mit dem nativen App-Dock steht alleine unten in der Bildschirmmitte.

Die Einstellungen für angeheftete Apps, laufende Fenster und Plugin-Widgets
werden weiter aus Caelestia gelesen. Änderungen im vorhandenen Komponenten-Editor
wirken weiterhin auf die jeweilige Zone. Das untere Dock wächst mit seinem Inhalt
und begrenzt sich auf die verfügbare Monitorbreite; die native Scrollfunktion bleibt.
Es hat 12 logische Pixel Abstand zur Unterkante. Die zusätzliche äußere Box ist
entfernt; nur die native Dock-Fläche bleibt. Die Farben werden beibehalten. Es gibt keine zweite Shell oder Plasma-Leiste.

## Ralleur-Logo

Das Logo oben links nutzt die native Einstellung `general.logo` in
`~/.config/caelestia/shell.json`. Sie verweist auf
`~/.local/share/ralleur/branding/ralleur-symbol.svg`, eine unveränderte Kopie
der vom Benutzer bereitgestellten Datei `~/Downloads/ralleur-symbol.svg`.
Eine weitere Kopie liegt unter `assets/ralleur-symbol.svg` in diesem Ordner.
In `~/.config/Caelestia/caelestia-shell.conf` bleibt unter `[Launcher]`
`recolourCustomLogo=false`, damit die Originalfarben erhalten bleiben.
Die Änderung wird von der laufenden Shell übernommen.

Der vorherige Konfigurationsstand ist unter
`~/.local/state/ralleur-taskbar-backups/20261101T153521Z-symbol/shell.json` gesichert.
Zum Rückbau nur `general.logo` auf den vorherigen Badge-Pfad
`~/.local/share/ralleur/branding/ralleur-badge-dark.svg` setzen. Mit leerem Wert
wird stattdessen das Distributionslogo verwendet.

### Runder Logo-Button

`logo-button.patch` vergrößert ausschließlich den Launcher in
`modules/bar/components/OsIcon.qml`: ein kreisförmiger Button mit dezenter
Hintergrundfläche und Kontur. Sein Durchmesser folgt der vorhandenen Leistenhöhe
minus 6 Pixel; das Logo nutzt 82 Prozent davon einschließlich seiner SVG-Ränder.
Die feste Topbar-Höhe bleibt unverändert (aktuell 45 Pixel, Button 39 Pixel).
Links- und Rechtsklick behalten die vorhandenen Aktionen.

Der Zusatzpatch wird nach dem Taskbar-Patch angewendet:

```bash
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/taskbar/logo-button.patch
systemctl --user restart caelestia-shell.service
```

Sicherung der vorherigen Komponente:
`~/.local/state/ralleur-taskbar-backups/20261101T154404Z-logo-button/OsIcon.qml`.
Zum Rückbau diese Datei an ihren ursprünglichen Ort kopieren und die Shell neu
starten. Die laufende Shell wurde nach dem Neustart per Screenshot geprüft;
[evidence/logo-button-check.json](evidence/logo-button-check.json) bestätigt die
unveränderte Leistenhöhe und Dock-Geometrie.

Der zusätzliche Patch `logo-button-edge.patch` setzt den linken Rand der
Glasfläche bündig an den Logo-Button. Die rechte Kante sowie Leistenhöhe und
Inhaltspositionen bleiben erhalten. Er wird nach den vorhandenen Anpassungen
mit `patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/taskbar/logo-button-edge.patch`
angewendet; danach die Shell neu starten. Die vorherige `ContentWindow.qml`
liegt unter `~/.local/state/ralleur-taskbar-backups/20261101T154523Z-logo-button-edge/`.
Die neue Kante wurde per Screenshot geprüft; die Topbar bleibt 45 Pixel hoch.

Der nachfolgende Patch `symmetric-bar-edges.patch` setzt den Logo-Button und
die Glasfläche gemeinsam auf `SplitBarSettings.edgeGap` (12 Pixel) vom linken
Bildschirmrand. Rechts bleibt derselbe Abstand erhalten. Dafür wird nur der
linke Innenabstand der oberen Leiste angepasst; die Höhe bleibt 45 Pixel.
Anwendung nach `logo-button-edge.patch` analog mit `patch --forward -p0`;
anschließend die Shell neu starten. Sicherungen der beiden betroffenen Dateien:
`~/.local/state/ralleur-taskbar-backups/20261101T164918Z-symmetric-bar-edges/`.

## Getrennte Maßstäbe

Unter **Paneele → Taskleiste → Skalierung** stehen jetzt **Topbar-Maßstab** und
**Dock-Maßstab**, jeweils von 0,6 bis 1,6 und mit eigenem Reset auf 1,0. Beide
Änderungen wirken sofort. Auch die Einstellungssuche findet die neuen Regler.

Die Topbar verwendet weiter `bar.scale` in `~/.config/caelestia/shell.json`.
Der Dock-Maßstab wird separat in `~/.config/Caelestia/caelestia-shell.conf` unter
`[RalleurTaskbar]` als `dockScale` gespeichert. Beim ersten Laden wird einmalig
der bisher gemeinsame Maßstab übernommen. Danach verändern die Regler nur die
jeweilige Leiste. Beim Dock skalieren Höhe, Icons und Abstände zusammen. Wenn
„Mit Balkengröße skalieren“ aktiviert ist, verwenden auch Dock-Vorschauen den
Dock-Maßstab. Der separat gespeicherte Dock-Wert bleibt beim Rückbau erhalten.

## Umsetzung

Die installierte Version hat nur eine gemeinsame `bar.position`. Der Patch
verwendet ihre vorhandenen Bar-/Dock-Delegates zweimal mit getrennten Zonen.
`bar.position=top` aktiviert die Aufteilung. Andere Positionen verwenden die
bisherige gemeinsame Leiste; nach einem Wechsel die Shell neu starten.
Die persistente Anzeige der aktuellen Konfiguration bleibt aktiv. Die zweite
Fläche teilt die Sichtbarkeit der Hauptleiste; ein unabhängig ausblendbares Dock
ist nicht Teil dieser Änderung.

Die eigene Eingaberegion umfasst unten nur die Dock-Kapsel. Freie Flächen links
und rechts bleiben für Desktop und Fenster erreichbar. Dock-Vorschauen und
Kontextmenüs werden oberhalb des Docks angeordnet, Status-Popouts unter der Topbar.
KWin reserviert Platz an beiden Kanten für maximierte Fenster. Vollbild blendet
beide Leisten aus. Minimierungsanimationen erhalten die tatsächliche untere
Dock-Geometrie.

`split-taskbar.patch` enthält die Änderungen an elf bestehenden QML-Dateien.
`overlay/modules/bar/SplitDock.qml` ergänzt die untere Fläche sowie einen lesenden
IPC-Endpunkt zur Diagnose. `SplitBarSettings.qml` speichert den eigenen Dock-Maßstab. Die Originaldateien gehören zu Caelestia (GPL-3.0);
diese abgeleiteten QML-Anpassungen stehen ebenfalls unter GPL-3.0.

Getestete lokale Basis: Caelestia-KDE-Checkout
`c0cfd04d5b9da3fbf7b5f47016822888468e9829`. Der Installer prüft zusätzlich die
SHA-256-Werte der tatsächlich installierten Originaldateien; lokale Anpassungen
und andere Upstream-Versionen werden nicht blind überschrieben. Upstream verfolgt
Mehrfachleisten separat in [Issue #850](https://github.com/ladybug-me/caelestia-kde/issues/850).
Ein Caelestia-Update kann diesen lokalen Patch ersetzen; danach gegen die neue
Version prüfen und bei Bedarf anpassen.

## Installation

Benötigt werden die vorhandene Caelestia-KDE-Shell, Python und `patch`.

```bash
python /home/USER/ralleurOS/kde-customizations/taskbar/install.py --dry-run
python /home/USER/ralleurOS/kde-customizations/taskbar/install.py
systemctl --user restart caelestia-shell.service
```

Vor der ersten Änderung werden die betroffenen Quelldateien und `shell.json`
nach `~/.local/state/ralleur-taskbar-backups/<Zeitstempel>/` gesichert. Der Installer
nennt das Rückbau-Manifest. XDG_CONFIG_HOME und XDG_STATE_HOME werden berücksichtigt.
Eine wiederholte Installation über bereits gepatchte Dateien wird abgewiesen.

Aktuelles Manifest auf diesem Rechner:

```text
/home/USER/.local/state/ralleur-taskbar-backups/20261101T135851.232446Z/manifest.json
```

## Prüfung

Die echte 3840×2160-KWin-Sitzung wurde mit einem eigenen temporären Qt-Fenster
geprüft: Maximieren ergibt bei Topbar 0,6 und Dock 1,6 `x=10, y=44, Breite=3820, Höhe=2040`; die beiden Leisten
bleiben frei. In Vollbild ist die Topbar 0 Pixel hoch und das Dock unsichtbar;
nach Verlassen von Vollbild erscheinen beide wieder. Der Test beendet sein
eigenes Fenster anschließend. Ergebnisse: [live-check.json](evidence/live-check.json).

```bash
python /home/USER/ralleurOS/kde-customizations/taskbar/tests/live_check.py \
  --screen HDMI-A-2 \
  --out /home/USER/ralleurOS/kde-customizations/taskbar/evidence/live-check.json
```

Der Live-Test benötigt python-dbus, PyGObject, Qt QML, qdbus6 und die laufende
Caelestia-Shell. Er öffnet kurz ein eigenes Fenster, maximiert es und setzt es in
Vollbild. Daher gezielt während einer freien Arbeitspause ausführen.

Die beiden tatsächlichen Einstellungsfelder wurden im laufenden Nexus geprüft:
Topbar auf 1,2 ändert die Dock-Höhe nicht; Dock auf 1,4 ändert die Topbar-Höhe
nicht. Ein anschließender Shell-Neustart erhält beide unterschiedlichen Werte.
Beide Reset-Knöpfe setzen nur ihren jeweiligen Maßstab zurück. Danach wurden die
vor dem Test gewählten Werte wiederhergestellt. Ergebnisse:
[scaling-check.json](evidence/scaling-check.json). Die Teststeuerung wurde danach
vollständig entfernt; der produktive IPC-Endpunkt bleibt lesend.

Die reale Dock-Hover-Routing-Diagnose meldete `dockhover`, `open=true`,
`position=bottom` mit einer Vorschau oberhalb der unteren Leiste. Die Leisten
wurden außerdem per Screenshot kontrolliert. Vollständige Klick-/Drag-and-drop-
Abläufe und weitere Monitorgrößen wurden in diesem Schritt nicht automatisiert
geprüft; dafür werden die vorhandenen nativen Caelestia-Komponenten weitergenutzt.

Installation, Versionsschutz und Rückbau wurden zusätzlich in isolierten
XDG-Verzeichnissen ausgeführt. Rückbau verweigert später bearbeitete Quellen,
stellt die ursprünglichen Quellen und die Position wieder her und erhält
zwischenzeitlich geänderte App-Präferenzen:
[installer-check.json](evidence/installer-check.json).

Lesende Diagnose auf diesem Monitor:

```bash
quickshell ipc -p "$HOME/.config/quickshell/caelestia" \
  call ralleurTaskbar-HDMI-A-2 inspect
```

## Überlagerte KDE-Leiste entfernt

Das zusätzliche Plasma-Panel 21 (unten, automatisch ausgeblendet, mit
`org.kde.plasma.icontasks` und `org.kde.plasma.showdesktop`) wurde über die native
Plasma-Scripting-API entfernt. Die laufende Shell meldet jetzt **0 KDE-Panels**
und weiterhin **1 Desktop**; auch die gespeicherte aktive Plasma-Konfiguration
enthält kein Panel mehr. Caelestia bleibt aktiv. Dafür war kein Shell-Neustart nötig.

Sicherung der vorherigen Plasma-Konfiguration und panelbezogenes Rückbauskript:

```text
/home/USER/.local/state/ralleur-taskbar-backups/20261101T141119.343594Z-kde-panel/
```

`restore-panel.js` in diesem Verzeichnis stellt ausschließlich das entfernte Panel
wieder her und verweigert den Import, wenn bereits ein KDE-Panel vorhanden ist.
Es lässt sich bei Bedarf über `org.kde.PlasmaShell.evaluateScript` ausführen.
Der QML-Patch-Rückbau im folgenden Abschnitt ist davon unabhängig.
Protokoll: [kde-panel-removal.json](evidence/kde-panel-removal.json).
Die verwendete API ist in der [KDE-Scripting-Dokumentation](https://develop.kde.org/docs/plasma/scripting/api/) beschrieben.

## Bildschirmrahmen entfernt

Caelestias Display-Bezels sind über die nativen Einstellungen deaktiviert:
`border.thickness=0` und `border.rounding=0` in `~/.config/caelestia/shell.json`.
Die laufende Shell hat die Änderung ohne Neustart übernommen; äußere Rahmen
und maskierte Bildschirm-Ecken sind entfernt. Topbar und Dock bleiben aktiv.
Der vorherige Konfigurationsstand ist unter
`~/.local/state/ralleur-taskbar-backups/20261101T142132.194443Z-display-bezels/`
gesichert. Protokoll: [display-bezels.json](evidence/display-bezels.json).

## Rückbau

```bash
python /home/USER/ralleurOS/kde-customizations/taskbar/install.py \
  --restore /home/USER/.local/state/ralleur-taskbar-backups/20261101T135851.232446Z/manifest.json \
  --dry-run
# Gleicher Befehl ohne --dry-run stellt die Dateien wieder her.
systemctl --user restart caelestia-shell.service
```

Der Rückbau prüft alle verwalteten Dateien vorab. Nachträgliche Änderungen führen
zum Abbruch. Aus der aktuellen `shell.json` wird nur die verwaltete Bar-Position
zurückgesetzt; andere Einstellungen bleiben erhalten.

## Glaseffekt passend zum Sperrbildschirm

`overlay/modules/bar/GlassSurface.qml` verwendet dieselbe gleichmäßige Tönung
wie die Sperrbildschirm-Karte: Anthrazit mit rund 45 Prozent Deckkraft oder
Offwhite mit rund 55 Prozent Deckkraft, abhängig vom aktiven Farbschema.
Die vorhandenen abgerundeten `BackgroundEffect.blurRegion`-Regionen der Topbar
und des Docks liefern den Live-Blur durch KWin. Der KWin-Blur-Effekt ist geladen.
Leistenmaße und die getrennten Maßstäbe bleiben erhalten.

`glass-match.patch` dokumentiert die Änderung gegenüber der vorherigen lokalen
Glasfläche. Die Sicherung vor dieser Änderung steht unter dem Pfad in
[evidence/glass-match-backup.txt](evidence/glass-match-backup.txt). Zum Rückbau
die dortige `GlassSurface.qml` nach
`~/.config/quickshell/caelestia/modules/bar/GlassSurface.qml` kopieren und
`systemctl --user restart caelestia-shell.service` ausführen.
Die aktive Geometrie ist in [evidence/glass-match.json](evidence/glass-match.json)
festgehalten; beide Leisten wurden nach dem Shell-Neustart visuell geprüft.

Die Deckkraft wurde anschließend für die Leisten gegenüber der Karte reduziert,
damit die Glaswirkung über Desktop-Fenstern deutlicher sichtbar ist.
Die Sicherung vor dieser Nachjustierung steht in
[evidence/glass-more-transparent-backup.txt](evidence/glass-more-transparent-backup.txt).

## Derselbe Wallpaper-Blur wie im Sperrbildschirm

Die Leisten verwenden jetzt dieselbe Materialtechnik wie die Sperrbildschirm-Karte:
lokales Sampling des aktuellen Wallpapers, `FastBlur` mit Radius 48 und eine
abgerundete Maske, darüber die gleichmäßige helle beziehungsweise dunkle Tönung.
Die Glasschicht bildet das Wallpaper ab, statt vom Inhalt dunkler Anwendungsfenster
abhängig zu sein. Der vorhandene KWin-Blur bleibt als Fallback erhalten.

`wallpaper-glass.patch` enthält die Änderungen an fünf Dateien; die vollständigen
vorherigen Dateien liegen unter dem Pfad aus
[evidence/wallpaper-glass-backup.txt](evidence/wallpaper-glass-backup.txt).
Für den Rückbau diese fünf Dateien relativ zum Shell-Verzeichnis wiederherstellen
und die Shell neu starten. Der Patch ergänzt `glassBackdrop` an `Bar`, reicht
das vorhandene Wallpaper zum Dock durch und hält dessen Loader bei sichtbaren
Leisten aktiv. Größe, Position und Skalierung bleiben unverändert.

Das [Prüfprotokoll](evidence/wallpaper-glass.json) bestätigt die geladene Quelle
und native Geometrie. Das Produktionsmaterial wurde zusätzlich mit dem GPU-Renderer
gegen ein kontrastreiches Wallpaper geprüft.

### Kontext außerhalb der schmalen Leisten

`blur-context.patch` erweitert das Sampling auf bis zu 64 zusätzliche logische
Pixel pro Seite. Der Ausschnitt wird an den Bildschirmrändern begrenzt. Erst
nach dem Blur wird auf die sichtbare Leistenfläche zurückgeschnitten und die
runde Maske angewendet. Dadurch beeinflusst auch Bildinhalt knapp außerhalb
der dünnen Leiste ihre Unschärfe. Der zusätzliche Ausschnitt folgt der Skalierung.

Der GPU-Vergleich mit einem Farbstreifen knapp unterhalb der Topbar bestätigt
den Unterschied: [evidence/blur-context-check.json](evidence/blur-context-check.json).
Die vorherige `GlassSurface.qml` liegt am Pfad aus
[evidence/blur-context-backup.txt](evidence/blur-context-backup.txt).

## Korrektur: echte Hintergrundtransparenz

Die zusätzliche Wallpaper-Textur ist wieder entfernt: Sie verdeckte den realen
Fensterinhalt hinter den Leisten. `GlassSurface.qml` zeichnet jetzt ausschließlich
eine Tönung mit 25 Prozent Deckkraft im dunklen und 35 Prozent im hellen Modus.
Die bestehenden runden KWin-Blur-Regionen bearbeiten den tatsächlich dahinter
liegenden Inhalt. Der Wallpaper-Sampling-Pfad und die dafür zusätzlich aktivierte
Quelle sind aus den Leisten entfernt.

`real-backdrop.patch` ersetzt die vorherigen Wallpaper-Blur-Änderungen. Die
Sicherung liegt unter dem Pfad in
[evidence/real-backdrop-backup.txt](evidence/real-backdrop-backup.txt). Ein Test
mit einer blauen Fläche und dünnen weißen Linien unter dem laufenden Dock
bestätigt sowohl das Durchscheinen von Blau als auch die Unschärfe der Linien:
[evidence/real-backdrop-check.json](evidence/real-backdrop-check.json).

## Rechte Dock-Sektion für laufende Apps

`dock-sections.patch` ergänzt im unteren Dock eine feine senkrechte Trennlinie
zwischen angepinnten Apps links und laufenden, nicht angepinnten Apps rechts.
Linie und Zusatzabstand erscheinen nur, wenn beide Gruppen vorhanden sind.
Die Reihenfolge bleibt innerhalb jeder Gruppe erhalten; Drag-and-drop kann Apps
innerhalb ihrer Gruppe umordnen. Anheften und Lösen erfolgen weiter über das
vorhandene Kontextmenü. Fenstergruppierung und Arbeitsplatzfilter bleiben aktiv.
Scrollen, Hover-Vorschau und Minimierungsziele berücksichtigen den Zusatzabstand.

Nach den vorhandenen Taskbar-Anpassungen anwenden:

```bash
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/taskbar/dock-sections.patch
cp /home/USER/ralleurOS/kde-customizations/taskbar/overlay/modules/bar/SplitDock.qml "$HOME/.config/quickshell/caelestia/modules/bar/SplitDock.qml"
systemctl --user restart caelestia-shell.service
```

Die SplitDock-Diagnose enthält zusätzlich `dock.sections` mit Gruppenzugehörigkeit,
Fensterzahl und Icon-Positionen. Der Öffnen-/Schließen-Test mit einem temporären,
nicht angepinnten Qt-Fenster bestätigt die rechte Position, das Erscheinen und
Verschwinden der Linie sowie die ursprüngliche Dock-Breite nach dem Schließen:
[evidence/dock-sections-check.json](evidence/dock-sections-check.json).
Die sichtbare Linie wurde im
[Screenshot](evidence/dock-sections.png) geprüft. Drag-and-drop und Kontextmenüs
wurden nicht automatisiert durchgeklickt.

Die vorherigen Dateien `Dock.qml` und `SplitDock.qml` sind unter dem Pfad in
[evidence/dock-sections-backup.txt](evidence/dock-sections-backup.txt) gesichert.
Zum Rückbau beide Dateien nach `modules/bar/components/Dock.qml` bzw.
`modules/bar/SplitDock.qml` im Shell-Verzeichnis kopieren und die Shell neu starten.

## Anpinnen per Ziehen, letzte Apps und Größenänderung

`dock-interactions.patch` erweitert die vorherige rechte Dock-Sektion:

- Ein Symbol rechts über die Trennlinie nach links ziehen und loslassen: Die App
  wird an der gewählten Position angepinnt. Dies funktioniert auch mit einer
  bereits geschlossenen App aus dem Verlauf. Ein abgebrochener Drag pinnt nichts an;
  das reine Ziehen über die Linie ohne Loslassen verändert keine Favoriten.
- Die drei zuletzt verwendeten, nicht angepinnten Apps bleiben nach dem Schließen
  als startbare Symbole rechts sichtbar. Weitere noch laufende Apps bleiben ebenfalls
  sichtbar. Laufende Apps tragen weiter ihre Fensterindikatoren; geschlossene
  Verlaufseinträge starten die App beim Anklicken erneut. Anpinnen entfernt die App
  aus dem Verlauf. Der Verlauf speichert nur Desktop-IDs, keine Fenster oder Prozesse.
- Die Trennlinie nach oben ziehen vergrößert das Dock, nach unten verkleinert es.
  Eine breitere unsichtbare Grifffläche erleichtert das Treffen der feinen Linie.
  Der Größenbereich entspricht den vorhandenen Einstellungen (0,6 bis 1,6).
  Die Änderung erscheint sofort und wird beim Loslassen gespeichert; Abbrechen
  stellt die vorherige Größe wieder her. Der Topbar-Maßstab bleibt unabhängig.

Der Verlauf steht als `recentDockApps` neben `dockScale` unter `[RalleurTaskbar]`
in `~/.config/Caelestia/caelestia-shell.conf`. Eine kurze Initialisierungsphase
verhindert, dass das vorübergehend unvollständige Fenster-/App-Verzeichnis beim
Shell-Start die gespeicherte Historie verdrängt.

Nach `dock-sections.patch` anwenden:

```bash
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/taskbar/dock-interactions.patch
systemctl --user restart caelestia-shell.service
```

Prüfung in der realen KWin-Sitzung: Vier eigene, startbare Test-Apps nacheinander
geöffnet und geschlossen; genau die letzten drei blieben sichtbar. Ein geschlossenes
Testsymbol wurde per nativer Mausgeste rechts aufgenommen und an zweiter Stelle
links angepinnt. Native Ziehgesten an der Linie haben das Dock vergrößert und
verkleinert. Anheftung, Verlauf und Maßstab wurden nach Shell-Neustarts erneut
gelesen. Während der Prüfung neu geöffnete Nutzer-Apps werden regulär in den
Verlauf aufgenommen. Test-Anheftung und Test-Desktop-Einträge wurden anschließend
entfernt und der vorherige Maßstab 1,6 wiederhergestellt. Protokoll:
[evidence/dock-interactions-check.json](evidence/dock-interactions-check.json).

Sicherungen beider QML-Dateien und der vorherigen Konfiguration liegen im Verzeichnis
aus [evidence/dock-interactions-backup.txt](evidence/dock-interactions-backup.txt).
Zum Rückbau ausschließlich die beiden QML-Dateien relativ zum Shell-Verzeichnis
wiederherstellen und die Shell neu starten. Die Einstellungen müssen hierfür
nicht zurückgesetzt werden.

## Beidseitiges Anheften und ausgeblendete Apps

`dock-bidirectional-pin.patch` korrigiert die App-Auflösung und ergänzt das
Lösen per Drag-and-drop. Nach `dock-interactions.patch` anwenden und die Shell
neu starten.

- Rechts nach links ziehen und loslassen pinnt die App an der Ablageposition an.
- Links nach rechts ziehen und loslassen löst sie. Auch eine geschlossene App
  bleibt danach als startbares Symbol im rechten Verlauf erhalten.
- Die Trennlinie mit einer kleinen rechten Ablagefläche bleibt bei leerem
  rechten Bereich sichtbar. Damit sind Lösen und Größenänderung auch möglich,
  wenn gerade alle angezeigten Apps angepinnt sind. Der Größen-Griff liegt nun
  unabhängig von den App-Delegates im scrollbaren Inhalt.

Satty hat `NoDisplay=true` in seiner Desktop-Datei und fehlt deshalb in
`DesktopEntries.applications`. Das bisherige Modell hatte den Pin gespeichert,
aber das Symbol beim Wiederaufbau übergangen. Explizite Favoriten und Verlauf
werden jetzt über `DesktopEntries.byId` aufgelöst, das auch solche Apps findet.
Bestehende Muster-Favoriten behalten ihre bisherige Suche im App-Verzeichnis.

Die Ablagefunktion wurde in der laufenden Shell gezielt für Satty und Shelly
geprüft: Lösen, Anheften an der ursprünglichen Position, Entfernung aus dem
Verlauf und genau ein Symbol pro App. Außerdem wurde ein geschlossener
Konsole-Launcher gelöst, im Verlauf wiedergefunden und an seiner ursprünglichen
Position angeheftet. Der temporäre IPC-Testzugriff auf die native Ablagefunktion
ist anschließend entfernt worden; die endgültige Diagnose bleibt lesend.
Ein erster Versuch mit Betriebssystem-Mausbewegungen wurde durch gleichzeitige
Zeigerbewegungen unterbrochen; das Prüfprotokoll dokumentiert deshalb ausdrücklich
die gezielte Prüfung der Ablagefunktion, keine vollständige Maus-Automatisierung:
[evidence/dock-bidirectional-pin-check.json](evidence/dock-bidirectional-pin-check.json).

Sicherung der vorherigen `Dock.qml`:
[evidence/dock-bidirectional-pin-backup.txt](evidence/dock-bidirectional-pin-backup.txt).
Zum Rückbau diese Datei nach `modules/bar/components/Dock.qml` im
Shell-Verzeichnis kopieren und die Shell neu starten. Die App-Präferenzen
bleiben dabei erhalten.


## Battle.net: Framegen im Dock-Kontextmenü

Der Schalter **Framegen** erscheint ausschließlich bei `lab-battlenet`.
Er speichert die NVIDIA-Smooth-Motion-Einstellung für zukünftige Starts.
Der Battle.net-Starter liest sie und übergibt
`NVPRESENT_ENABLE_SMOOTH_MOTION=1` nur an Battle.net und seine Kindprozesse.
Ausschalten entfernt die gespeicherte Option und auch einen gegebenenfalls
geerbten Wert aus der Startumgebung. Andere Apps erhalten keine Änderung.

Bei laufendem Battle.net oder WoW ist der Schalter ausgegraut; der Hinweis
fordert zum vollständigen Schließen auf. Die Prüfung berücksichtigt auch
Prozesse ohne sichtbares Fenster, aktualisiert sich im offenen Menü alle
750 ms und wird beim Speichern erneut im Backend durchgeführt.
Die Einstellung liegt unter
`~/.local/state/linux-gaming-lab/battlenet-framegen.json` (bzw. XDG_STATE_HOME).
Ohne Datei ist Framegen aus. Der aktuelle Ausgangszustand bleibt aus.

`battlenet-framegen.patch` ergänzt das bestehende Dock-Kontextmenü.
`linux-gaming-lab-framegen.patch` enthält die Ergänzungen für den vorhandenen
Starter in `/home/USER/Projekte/linux-gaming-lab`, einschließlich Helper
`bin/battlenet-framegen` (ausführbar setzen) und gezielter Tests.
Beide Änderungen sind bereits installiert. Bei erneuter Installation die
Patches im jeweiligen Wurzelverzeichnis mit `patch --forward -p0` anwenden
und anschließend `caelestia-shell.service` als Benutzerdienst neu starten.

Prüfung: zehn Backend-Tests bestanden; der echte Dock-Menübaustein wurde
in der laufenden Shell auf Ein/Aus, Wiederöffnen und Sperren/Entsperren geprüft.
Für die Prozessprüfung wurde ein kontrollierter Testprozess verwendet,
kein echtes Battle.net oder WoW gestartet. Die Screenshots des normalen und
ausgegrauten Schalters wurden visuell geprüft. Temporäre IPC-Testfunktionen
sind entfernt. Details: [Prüfprotokoll](evidence/battlenet-framegen-check.json).
Sicherung der vorherigen Dateien:
[Backup-Pfad](evidence/battlenet-framegen-backup.txt).
Zum Rückbau `DockContext.qml` und `gaming.py` aus dieser Sicherung am ursprünglichen
Ort wiederherstellen und die Shell neu starten. Die zusätzlichen Helper können
anschließend entfernt werden; die gespeicherte Option hat ohne Startintegration
keine Wirkung.

## Neues Fenster per Shift-Klick

`dock-shift-click.patch` verbindet Shift + Linksklick auf ein App-Symbol mit
der vorhandenen Funktion zum erneuten Starten über den Desktop-Eintrag.
Damit lässt sich beispielsweise ein weiteres Chromium-Fenster öffnen.
Ob eine App zusätzliche Fenster unterstützt, bestimmt die App selbst.
Ein normaler Linksklick aktiviert weiterhin bestehende Fenster.

Der Patch ist installiert; die Shell wurde neu gestartet und das geladene Dock
per IPC geprüft. Anwendung nach den bisherigen Dock-Patches mit
`patch --forward -p0` im Shell-Verzeichnis, anschließend
`systemctl --user restart caelestia-shell.service`.
Sicherung der vorherigen `modules/bar/components/Dock.qml`:
[evidence/dock-shift-click-backup.txt](evidence/dock-shift-click-backup.txt).
Zum Rückbau diese Datei wiederherstellen und die Shell neu starten.
Prüfumfang und Einschränkungen:
[evidence/dock-shift-click-check.json](evidence/dock-shift-click-check.json).


## Vorschau nur für geöffnete Apps

`dock-open-preview.patch` verhindert im unteren Dock die Hover-Vorschau für
angeheftete und zuletzt verwendete Apps ohne zugeordnetes Fenster. Beide
Hover-Auslöser prüfen die Fensteranzahl. Beim Schließen des letzten Fensters
wird eine bereits offene Vorschau geschlossen; bestehende Vorschauen erhalten
das aktualisierte Fenstermodell. Minimierte Fenster zählen weiterhin als offen.

Der Patch ist installiert und die Shell wurde neu gestartet. Er wird nach den
bisherigen Dock-Patches mit `patch --forward -p0` im Shell-Verzeichnis angewendet.
Zum Rückbau die `Dock.qml` aus der unter
[evidence/dock-open-preview-backup.txt](evidence/dock-open-preview-backup.txt)
angegebenen Sicherung nach `modules/bar/components/Dock.qml` zurückkopieren und
`systemctl --user restart caelestia-shell.service` ausführen.

Die aus der installierten Komponente extrahierten QML-Handler wurden isoliert
für offene/geschlossene Apps, beide Hover-Auslöser, Schließen des letzten
Fensters, entfernte Apps und den Erhalt des Kontextmenüs geprüft. Die laufende
Shell meldet den geladenen Dock-Baustein per IPC. Ein physischer Hover-Test wurde
nicht durchgeführt; die Sitzung hatte bei der Prüfung ein Vollbildfenster.
Prüfprotokoll: [evidence/dock-open-preview-check.json](evidence/dock-open-preview-check.json).

## Beschriftung zum Beenden von Apps

`dock-quit-label.patch` ändert im Dock-Kontextmenü die Beschriftung von
„Aufgabe beenden“ zu „App beenden“. Die vorhandene Aktion bleibt erhalten.
Der Patch ist installiert. Bei erneuter Installation nach den bisherigen
Dock-Patches mit `patch --forward -p0` im Shell-Verzeichnis anwenden und
`systemctl --user restart caelestia-shell.service` ausführen.
Zum Rückbau die `DockContext.qml` aus der in
[evidence/dock-quit-label-backup.txt](evidence/dock-quit-label-backup.txt)
angegebenen Sicherung nach `modules/bar/popouts/DockContext.qml` zurückkopieren
und die Shell neu starten.

## Audio-Balken bis zur Dock-Oberkante

`visualiser-dock-height.patch` begrenzt die maximale Ausschlaghöhe der
Hintergrundvisualisierung bei geteilter Taskbar auf die Oberkante des unteren
Docks. Die Balken bleiben am bisherigen unteren Rand verankert und behalten
ihre volle Audio-Dynamik sowie abgerundete Spitzen. Die Höhe folgt dem
Dock-Maßstab einschließlich `SplitBarSettings.edgeGap`. Dazu erhält das native
`VisualiserBars`-Element eine passende Höhe; sein maximaler Ausschlag beträgt
40 Prozent seiner Elementhöhe.

Der Patch ist installiert und die Shell wurde neu gestartet. Anwendung nach
den bisherigen Patches mit `patch --forward -p0` im Shell-Verzeichnis, danach
`systemctl --user restart caelestia-shell.service`. Die laufende Shell lädt
fehlerfrei; Dock-Geometrie per IPC und sichtbare Balken per Screenshot geprüft.
Aktuell: Dock-Höhe 64 Pixel plus 12 Pixel Rand, Oberkante bei y=2084 auf dem
2160 Pixel hohen Monitor.

Sicherung: [evidence/visualiser-dock-height-backup.txt](evidence/visualiser-dock-height-backup.txt).
Zum Rückbau die gesicherte `Visualiser.qml` nach
`~/.config/quickshell/caelestia/modules/background/Visualiser.qml` kopieren
und die Shell neu starten.

### Korrektur: unabhängig von der oberen Taskbar (3. November 2026)

`visualiser-dock-independent.patch` folgt auf die bisherigen Visualiser-Patches.
Die frühere Höhenbegrenzung galt nur bei `bar.position === "top"`; an den anderen
Rändern konnte der Ausschlag auf Bildschirmhöhe anwachsen. Die obere Taskbar
bestimmt jetzt weder Höhe noch Randabstände der Visualisierung. Der maximale
Ausschlag entspricht exakt der tatsächlichen Höhe des unteren Docks. Die
Balkenunterkante folgt dessen tatsächlicher Unterkante, sodass auch bei einem
höher platzierten Dock beide Oberkanten übereinstimmen. Der frühere Zusatz des
unteren Bildschirmabstands zur **Balkenhöhe** entfällt. Audio-Dynamik und Farben
bleiben erhalten.

Installation auf die bestehende Fassung, nach Sicherung von
`modules/background/Visualiser.qml`:

```sh
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < kde-customizations/taskbar/visualiser-dock-independent.patch
systemctl --user restart caelestia-shell.service
```

Installiert und anhand der tatsächlichen QML-Geometrie geprüft: alle vier
Taskbar-Ränder, obere Maßstäbe 0,6/1,5, untere Maßstäbe 0,4/1,6/3,2
(16/64/128 px maximaler Ausschlag). Die Einstellungen wurden wiederhergestellt
und der temporäre Prüfzugang entfernt. `qmlformat` und Komponentencheck erfolgreich.
[Prüfwerte](evidence/visualiser-dock-independent-check.json),
[Sicherung](evidence/visualiser-dock-independent-backup.txt).
Zum Rückbau ausschließlich `Visualiser.qml` aus dieser Sicherung nach
`~/.config/quickshell/caelestia/modules/background/Visualiser.qml` zurückkopieren
und die Shell neu starten.

### Equalizer über die gesamte Bildschirmbreite

`visualiser-full-width.patch` folgt auf `visualiser-dock-independent.patch`.
Beide Hälften verwenden jetzt jeweils 50 % der Fläche, auch bei einer einzelnen
Audio-App. Die vorherige Größenformel ließ dort eine Lücke in der Mitte.
Seitliche Zusatzränder entfallen. Die Höhe bleibt an das untere Dock gebunden;
App-Aufteilung und Audio-Farben bleiben erhalten. Der Größenfaktor für die
frühere seitliche Ausdehnung bestimmt die Breite jetzt nicht mehr.

```sh
patch --forward -p0 -d "$HOME/.config/quickshell/caelestia" < kde-customizations/taskbar/visualiser-full-width.patch
systemctl --user restart caelestia-shell.service
```

Installiert, QML-Syntax und Komponentencheck erfolgreich. Live mit einer
Audio-App geprüft: durchgehende Balkenreihe über die Bildschirmbreite, ohne
zusätzliche Mittellücke. [Live-Ausschnitt](evidence/visualiser-full-width-live.png).
Sicherung: [visualiser-full-width-backup.txt](evidence/visualiser-full-width-backup.txt).
Rückbau: `Visualiser.qml` aus dieser Sicherung nach
`~/.config/quickshell/caelestia/modules/background/Visualiser.qml` zurückkopieren
und die Shell neu starten.

### Equalizer bündig am unteren Bildschirmrand

`visualiser-bottom-edge.patch` folgt auf `visualiser-full-width.patch`.
Die Balken beginnen mit `anchors.bottomMargin: 0` direkt am Bildschirmrand.
Ihre maximale Ausschlaghöhe bleibt an die tatsächliche Höhe des unteren Docks
gekoppelt; dessen Randabstand wird nicht mehr auf den Equalizer übertragen.

```sh
patch --batch --forward -p0 -d "$HOME/.config/quickshell/caelestia" -i "$PWD/kde-customizations/taskbar/visualiser-bottom-edge.patch"
systemctl --user restart caelestia-shell.service
```

Installiert, QML-Syntax und Komponentencheck erfolgreich. Die laufende Shell
zeigt bei aktiver Audio-App Balken bis zur unteren Kante:
[Live-Ausschnitt](evidence/visualiser-bottom-edge-live.png).
Sicherung: [visualiser-bottom-edge-backup.txt](evidence/visualiser-bottom-edge-backup.txt).
Rückbau: die dort gesicherte `Visualiser.qml` nach
`~/.config/quickshell/caelestia/modules/background/Visualiser.qml` zurückkopieren
und die Shell neu starten.

## flausen.-Formen für virtuelle Desktops

Die Desktop-Anzeige verwendet jetzt die vier Konzeptformen statt zufälliger
Caelestia-Shapes und Punkte. Jeder Desktop behält seine Form beim Umschalten;
aktive Markierung, Fensteranzeigen und bestehende Bedienung bleiben erhalten.
Installation, Sicherung, Rückbau und Prüfgrenzen:
[flausen-workspaces/README.md](flausen-workspaces/README.md).

## Capture-Kürzel direkt im Dropdown

Das [Capture-Menü](capture-menu/README.md) zeigt neben jeder Aktion das globale
Tastenkürzel und einen Stift zum Ersetzen oder Entfernen. Der Mausweg zum
Capture-Popout hat mehr Spielraum und 650 ms Schließverzögerung.
Der zugehörige Patch ist `capture-menu.patch`.

## Screenshot-Galerie

Die [Screenshot-Galerie](screenshot-gallery/README.md) ersetzt die Dateiliste durch
kleine Bildvorschauen. Einzelklick kopiert das Bild mit kurzer Bestätigung,
Doppelklick öffnet es. Patch: `screenshot-gallery.patch` (nach `capture-menu.patch`).

## Zwischenablage in der Topbar

Eine Büroklammer direkt rechts neben der Screenshot-Control öffnet den
Zwischenablageverlauf im gleichen Button-Stil.
Patch, Installation und Rückbau: [clipboard-control/README.md](clipboard-control/README.md).

## Saubere Kontur am Startknopf

`launcher-glass-cutout.patch` spart die Glasfläche einschließlich ihrer Kontur
hinter dem runden, halbtransparenten Startknopf aus. Eine invertierte runde
Deckkraftmaske folgt dem tatsächlich geladenen Logo-Widget und dessen Geometrie;
die zusätzliche Leistenlinie scheint dadurch nicht mehr unten durch den Button.
Die Maske berücksichtigt auch nachträgliche Layout- und Größenänderungen.

Der Patch ist installiert. Nach den bisherigen Taskbar-Patches mit
`patch --forward -p0` im Shell-Verzeichnis anwenden und
`systemctl --user restart caelestia-shell.service` ausführen.
Live geprüft: Shell aktiv, Button 39 × 39 Pixel bei x=12/y=12; Kontur anhand
eines Screenshots kontrolliert. Vorher/Nachher-Ausschnitte liegen unter
`evidence/launcher-glass-cutout-before.png` und
`evidence/launcher-glass-cutout-after.png`.

Zum Rückbau die drei QML-Dateien aus der Sicherung unter
[evidence/launcher-glass-cutout-backup.txt](evidence/launcher-glass-cutout-backup.txt)
relativ zum Shell-Verzeichnis wiederherstellen und die Shell neu starten.

## Größerer Kalender und vollständiges Datum

`calendar-clock.patch` setzt die Mindestskalierung des Kalender-Popouts auf
1,15, unabhängig von einer klein skalierten Topbar. Breite, Abstände und Schrift
wachsen gemeinsam. Die horizontale Uhr zeigt beispielsweise
`Mo. 2. Nov  16:03`: deutsches Tagesdatum, Monat ohne abschließenden Punkt,
zwei Leerzeichen und eine kompakte 24-Stunden-Uhr. Die vorhandenen Schalter
für Datum und Sekunden gelten weiter.

Der Patch ist installiert. Nach den bisherigen Taskbar-Patches im
Shell-Verzeichnis mit `patch --forward -p0` anwenden und anschließend
`systemctl --user restart caelestia-shell.service` ausführen.

Live geprüft: Datum einschließlich beider Leerzeichen, Kalender 571,55 × 318
Pixel bei Topbar-Maßstab 0,72 und Kalender-/Schriftmaßstab 1,15.
Die geöffnete Ansicht wurde visuell geprüft:
[evidence/calendar-clock-after.png](evidence/calendar-clock-after.png).
Der temporäre IPC-Prüfzugriff wurde anschließend entfernt.

Sicherung der beiden vorherigen QML-Dateien:
[evidence/calendar-clock-backup.txt](evidence/calendar-clock-backup.txt).
Zum Rückbau diese Dateien relativ zum Shell-Verzeichnis wiederherstellen
und die Shell neu starten.

## Zentraler Update-Hub

Das Update-Menü verwendet jetzt die Kalender-Mindestskalierung von 1,15 und
bündelt Steam, Steam-Spiele, Battle.net, Battle.net-Spiele, WowUp und ArtCraft.
Die Quellen-Auswahl wird gespeichert; Update-Regeln werden über die verlinkten
nativen Programme eingestellt. Details zu Status, Installation und Rückbau:
[update-hub/README.md](update-hub/README.md). Patch: `update-hub.patch`.

Der Hub vergleicht inzwischen installierte App-/Blizzard-Spielversionen direkt mit
den offiziellen Publisher-Feeds. Steam-Downloadstatus und WowUp-Addonstatus
werden mit ausgewiesenem lokalen Prüfstand angezeigt. Bei Netzfehlern bleibt
der letzte erfolgreiche Stand als offline gekennzeichnet. Zusatzpatch von der
ersten Hub-Fassung: `update-hub-status.patch`.


## Mouseover-Fenster im Stil des Startmenüs

`hover-start-style.patch` vereinheitlicht die gemeinsame Fläche aller schwebenden
Taskleisten-Popouts und Dock-Vorschauen: 24 Pixel Rundung, ein Pixel Kontur sowie
exakt dieselbe helle/dunkle Glas-Tönung wie im Startmenü. Eine eigene abgerundete
KWin-Blur-Region folgt der animierten Popup-Geometrie. Deckende Wurzel-Hintergründe
der geladenen Popouts werden in der geteilten Topbar-Konfiguration transparent;
innere Karten, Bedienelemente und Vorschau-Inhalte bleiben erhalten.

Die Änderung ist bereits installiert. Auf derselben zuvor angepassten Basis:

```bash
patch --dry-run -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/taskbar/hover-start-style.patch
patch -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/taskbar/hover-start-style.patch
systemctl --user restart caelestia-shell.service
```

Live geöffnet und auf Geometrie, Tönung, Kontur und transparente Wurzelflächen
geprüft: Kalender, Zwischenablage, Netzwerk, Bluetooth, Audio, Bildschirmaufnahme,
Update-Hub und eine echte Dock-Fenstervorschau. Kalender, Zwischenablage und Dock
wurden zusätzlich per Screenshot kontrolliert. Das helle Farbschema wurde nicht
live geprüft. Temporäre Prüf-IPC ist entfernt. Vorhandene Warnungen über fehlende
Skalierungseigenschaften von ScreenCapture sind unabhängig von der Glasänderung.

[Prüfprotokoll](evidence/hover-start-style-check.json),
[Kalender](evidence/hover-start-style-clock.png),
[Zwischenablage](evidence/hover-start-style-clipboard.png),
[Dock-Vorschau](evidence/hover-start-style-dockhover.png).

Die drei vorherigen QML-Dateien liegen relativ zum Shell-Verzeichnis in der
[Sicherung](evidence/hover-start-style-backup.txt). Zum Rückbau nach Vergleich mit
späteren Änderungen diese drei Dateien zurückkopieren und die Shell neu starten.

## Orange Audio-Balken

`visualiser-orange.patch` setzt beide Verlaufsfarben der Hintergrund-Balken auf
`#E56D2F`, das Orange des Ralleur-Symbols. Die bisherige Deckkraft von 70 Prozent
und die Begrenzung auf die Dock-Oberkante bleiben erhalten. Der Patch folgt auf
`visualiser-dock-height.patch`; anschließend die Shell neu starten.
Die Änderung ist installiert. Sicherung für den Rückbau:
[evidence/visualiser-orange-backup.txt](evidence/visualiser-orange-backup.txt).
Zum Rückbau die gesicherte `Visualiser.qml` an ihren ursprünglichen Ort
kopieren und `caelestia-shell.service` neu starten.

## Bis zu fünf getrennte Audio-Apps

Die Hintergrundvisualisierung teilt sich bei zwei bis fünf aktiven Audio-Apps
in gleich breite Bereiche auf. Jede App wird unabhängig analysiert und bekommt
eine freie Akzentfarbe: Orange `#E56D2F`, Blau `#2563C9`, Petrol `#278F8B`,
Gelb `#E4AD22`, Rot `#DF493F` aus der Ralleur-Palette. Aktive Apps behalten ihre
Reihenfolge und Farbe, wenn andere dazukommen oder wegfallen. Freie Farben werden
an nachrückende Apps vergeben. Die Zuordnung besteht innerhalb des laufenden
Helpers; ein Shell-Neustart beginnt eine neue Auswahl.

Chromium und World of Warcraft werden bei der ersten Auswahl bevorzugt; weitere
Apps folgen nach Namen. Ab der sechsten App bleiben die fünf bisherigen Apps
sichtbar. Sobald eine davon endet oder pausiert wird, kann eine wartende App
nachrücken. Mehrere Streams derselben App werden zusammengefasst. Die Erkennung
folgt dem vom Audioserver gemeldeten Pausenzustand; ein offener, stiller Stream
kann weiterhin einen Bereich belegen. Stummgeschaltete Apps bleiben zugeordnet
und liefern Nullwerte.

Bei weniger als zwei Audio-Apps wird das vorhandene Gesamtsignal wieder
beidseitig orange dargestellt. Änderungen werden ungefähr innerhalb einer
Sekunde erkannt. Die Begrenzung auf die Dock-Oberkante bleibt erhalten.

Der Helper verwendet die vorhandenen Programme `pactl` und `parec` sowie
Python 3 und `libcava.so`. `parec --monitor-stream` liest jeden ausgewählten
App-Stream separat vom Monitor seines tatsächlichen Ausgabegeräts.
Audio-Routing und Lautstärken werden nicht verändert; es werden keine
Audiodateien gespeichert. Ein gemeinsamer Helper bedient alle sichtbaren
Visualisierungen und endet, wenn sie entladen werden. App-Spektren werden
mit 32 Frequenzbändern und bis zu 30 Aktualisierungen pro Sekunde geliefert.
Die automatische Empfindlichkeit folgt Cava; die Balkenhöhe ist deshalb kein
absoluter Lautstärkepegel.

Installation nach `visualiser-orange.patch`: `app-visualiser.patch` und danach
`five-app-visualiser.patch` mit `patch --forward -p0` im Shell-Verzeichnis anwenden.
Die aktuelle `overlay/AppVisualiser.qml` nach `services/AppVisualiser.qml` und
`overlay/scripts/app-visualiser.py` nach `scripts/app-visualiser.py` kopieren;
anschließend `caelestia-shell.service` neu starten. Bereits installiert.
Lesende Live-Diagnose einschließlich App-Farben:

```bash
quickshell ipc -p "$HOME/.config/quickshell/caelestia" call ralleurAppVisualiser inspect
```

`tests/app_visualiser_check.py --live-ui` prüft fünf unterschiedliche
Frequenzsignale auf einem temporären, unhörbaren Null-Ausgang. Geprüft werden
unterschiedliche Frequenzspitzen, Verstummen eines Signals bei vier weiter
aktiven Signalen, stabile Farben nach Wegfall einer App, Warten/Nachrücken der
sechsten App, Zusammenfassung gleicher App-Namen sowie Auswahl bei einer App.
Mit `--live-ui` werden zusätzlich fünf verschiedenfarbige Bereiche in der
laufenden Shell per IPC bestätigt und ein Screenshot nach
`/tmp/ralleur-five-app-visualiser.png` aufgenommen. Der Test entfernt seine
Streams und seinen Null-Ausgang anschließend.
Prüfergebnis: [evidence/five-app-visualiser-check.json](evidence/five-app-visualiser-check.json).

Sicherung der vorherigen Zwei-App-Version:
[evidence/five-app-visualiser-backup.txt](evidence/five-app-visualiser-backup.txt).
Zum Rückbau die drei gesicherten Dateien unter ihren relativen Pfaden im
Shell-Verzeichnis wiederherstellen und die Shell neu starten.
Die ursprüngliche Sicherung vor der App-Trennung steht weiterhin unter
[evidence/app-visualiser-backup.txt](evidence/app-visualiser-backup.txt).

## Farbige Desktop-Formen und Begrenzung auf vier

Die vier flausen.-Desktopformen tragen jetzt Blau, Orange, Petrol und Braun.
Der aktive Hintergrundindikator erhält die Originalfarben. Ein KWin-Skript
begrenzt die Zahl der Desktops dauerhaft auf vier; die frühere Vollbild-Automatik
für zusätzliche Desktops ist dafür deaktiviert. Installation und Rückbau:
[flausen-workspaces/README.md](flausen-workspaces/README.md#maximal-vier-desktops).

Die Vollbild-Automatik ist inzwischen mit festem Desktop-Pool wieder aktiv:
nächster freier Desktop rechts, bei vollständiger Belegung direkt der nächste
rechts; Umlauf 4 → 1. Die Begrenzung auf vier bleibt aktiv.
Details: [Vollbild-Routing](../fullscreen-desktops/README.md).

## App-Lautstärkeregler in den Balkenfarben

`audio-app-colors.patch` ergänzt eine überschreibbare `sliderColour` an
`SliderRow` und verbindet `AppStreamRow` mit der gemeinsamen Farbzuordnung in
`AppVisualiser.colorForApp()`. Damit verwenden die App-Regler im Audio-Popout
und in den App-Lautstärkeeinstellungen dieselbe Akzentfarbe wie ihr Bereich
am unteren Bildschirmrand. Bei einer einzelnen analysierten App wird Orange
verwendet; Apps ohne zugeordneten Bereich erhalten neutrales Grau.
`flausen-app-visualiser` wird als interner Monitor aus der App-Liste ausgefiltert.

Installation nach den Visualisierungs-Patches: `audio-app-colors.patch` mit
`patch --forward -p0` im Shell-Verzeichnis anwenden und die aktuelle
`overlay/AppVisualiser.qml` nach `services/AppVisualiser.qml` kopieren; danach
`caelestia-shell.service` neu starten. Bereits installiert.

Fünf echte `AppStreamRow`-Instanzen wurden mit fünf unabhängigen, unhörbaren
Teststreams geprüft: Alle Regler entsprechen den fünf zugewiesenen Farben;
der interne Monitor fehlt in der App-Liste. Die temporäre Prüf-IPC wurde
anschließend entfernt.
[Prüfprotokoll](evidence/audio-app-colors-check.json),
[Sicherung](evidence/audio-app-colors-backup.txt).
Zum Rückbau die vier gesicherten Dateien an ihren relativen Pfaden im
Shell-Verzeichnis wiederherstellen und die Shell neu starten.


## Frei schwebende Fenster-Vorschauen

`frameless-window-previews.patch` entfernt bei den Vorschauen der unteren
Taskleiste die gemeinsame Glasfläche, deren Kontur und die zugehörige
rechteckige Hintergrundunschärfe. Die einzelnen Fenster erscheinen ohne
äußere Innenränder und ohne zusätzliche Namens-/Titelzeile. Vorschaugrößen,
Fensteraktivierung, Schließen-Schaltfläche und Mediensteuerung bleiben erhalten.
Die Rundung der eigentlichen Fenster-Vorschau bleibt bestehen.

Der Patch ist installiert; nach den bisherigen Menü-/Material-Patches mit
`patch --forward -p0` im Shell-Verzeichnis anwenden und
`systemctl --user restart caelestia-shell.service` ausführen. Die vollständige
Komponente liegt in [window-previews/DockHover.qml](window-previews/DockHover.qml).
Sicherung der drei geänderten Dateien:
[evidence/frameless-window-previews-backup.txt](evidence/frameless-window-previews-backup.txt).
Die laufende Shell wurde mit zwei Chromium-Fenstern visuell geprüft:
kein gemeinsamer Rahmen, keine Beschriftungszeile und kein Blur-Rechteck
zwischen bzw. hinter den Fenstern. Temporäre Prüfsteuerung danach entfernt.

Screenshot und Zwischenablage verwenden ebenfalls den gemeinsamen Menüstil.
[Umsetzung und native Vorschauen](capture-clipboard-style/README.md).


## Dock: Einfügevorschau und Vergrößerung

`dock-motion.patch` folgt auf die bisherigen Dock-Patches. Die Änderung ist
installiert. Favoriten und temporäre Apps verwenden beim Ziehen eine gemeinsame
Einfügevorschau. Die Nachbarn weichen animiert aus; erst beim Loslassen wird die
vorgeführte Position gespeichert. Währenddessen bleibt die Modellkennung stabil.
Ein Drop außerhalb der Leiste verwirft die Vorschau, Abbrechen ändert keine
Favoriten. Fenster ohne auflösbaren Desktop-Starter bleiben temporär.

Die Vergrößerung folgt dem Zeiger mit einem weichen Kosinusverlauf über die
Nachbaricons. Die Glasfläche wächst seitlich mit; das Layout der ruhenden Leiste
und die Fenster-Arbeitsfläche behalten ihre Maße. Der Eingabebereich wächst nur
bei aktivem Zoom nach oben. Ziehen, Größenänderung und reduzierte Bewegung
unterdrücken den Zoom. Globale KWin-Blur-Einstellungen werden nicht verändert.

Unter **Desktop & Dock → Dock** stehen **Magnification** (standardmäßig an)
und **Magnification strength** (0,15–0,90; Standard 0,55). Gespeichert wird im
bestehenden `[RalleurTaskbar]`-Profil; beide Regler haben einen Standardwert-Reset.

Installation auf derselben Basis: `patch --forward -p0` im Shell-Verzeichnis mit
`dock-motion.patch`, anschließend `systemctl --user restart caelestia-shell.service`.
Die mitgelieferten Overlay-Dateien und die Dock-Seite der Einstellungen sind
synchronisiert. Sicherung: [dock-motion-backup.txt](evidence/dock-motion-backup.txt).

Live geprüft: Kate aus der rechten Sektion an eine konkrete Favoritenposition
ziehen, wieder nach rechts lösen, Reihenfolge der anderen Favoriten erhalten,
Zoom aktivieren, vergrößerten oberen Iconbereich erreichen und Dock verlassen.
[Testprotokoll](evidence/dock-motion-check.json),
[Hover](evidence/dock-motion-hover.png), [Ziehen](evidence/dock-motion-drag.png).
`tests/dock_motion_live.py` reproduziert den Test auf diesem Desktop; wegen der
echten Mausbewegungen nur in einer unbenutzten Sitzung ausführen.

Dies bildet noch nicht das vollständige macOS-Dock nach: Der bestehende Klick
auf die aktive App minimiert weiterhin, mehrere Fenster werden zyklisch aktiviert.
Dateidrops auf Apps, Ordnerstapel und Papierkorb sind separate Funktionslücken.


### Korrektur der abgelegten Iconposition

`dock-drop-position.patch` korrigiert die erste Fassung von `dock-motion.patch`;
die kumulative Fassung enthält die Korrektur bereits. Nach einem Drag wird
`delegateItem.x` wieder an den aktuellen Sektionsabstand gebunden. Eine feste
Zuweisung behielt zuvor den Abstand des alten Abschnitts auch nach einem Wechsel
über den Trenner und verschob dadurch das Icon auf seinem neuen Platz.

Beim Loslassen wird die zuletzt dargestellte Einfügevorschau übernommen, ohne
den Mauspunkt erneut durch das bewegte Icon umzurechnen. Während die Favoriten
aktualisiert werden, bleibt das Modell vor Zwischenaktualisierungen geschützt;
der Neuaufbau folgt nach der Rückkehr des Icons in seinen Delegate. Die bestehende
Ausweich- und Zoomanimation bleibt erhalten.

Live geprüft: Anheften rechts → links, Umordnen links und Lösen links → rechts,
mit Griffpunkten bei 30 bzw. 70 Prozent der Iconbreite. Nicht nur die gespeicherte
Reihenfolge, sondern auch die tatsächlichen Iconmittelpunkte wurden mit dem
Sektionsraster verglichen; alle Abweichungen lagen unter 0,75 logischen Pixeln.
[Testprotokoll](evidence/dock-drop-position-check.json),
[Reproduktion](tests/dock_drop_position_live.py),
[Sicherung](evidence/dock-drop-position-backup.txt).


### Erweiterter Größenbereich des Docks

`dock-size-range.patch` folgt auf `dock-drop-position.patch`. Die Dock-Skalierung
reicht nun von **0,4 bis 3,2**, gegenüber zuvor 0,6 bis 1,6. Beide Grenzen stehen
zentral in `SplitBarSettings` und gelten für den Trenner, die Dock-Skalierung in
den Einstellungen und das Wiederherstellen der gespeicherten Größe. Die
Einstellungs-Overlays sind entsprechend aktualisiert.

Unter 1,0 wird das untere Dock linear verkleinert; die frühere Quadratwurzel
machte kleine Werte optisch deutlich größer. Der Trenner folgt beim Ziehen der
Mausposition: seine Mitte verschiebt sich um die halbe Dock-Höhenänderung.
Dadurch kann die minimale Größe in einem Zug erreicht werden. Die Topbar und
andere Skalierungsregler behalten ihren bisherigen Bereich und ihr Verhalten.

Bei der aktuellen Grundhöhe von 40 px ergeben sich **16 bis 128 px Dock-Höhe**.
Beide Endpunkte wurden in der laufenden Shell geladen und anhand der realen
Geometrie geprüft; die ursprüngliche Größe 1,6 wurde anschließend wiederhergestellt.
[Testprotokoll](evidence/dock-size-range-check.json),
[Live-Prüfung](tests/dock_size_range_live.py),
[Sicherung](evidence/dock-size-range-backup.txt).

## Dock ohne Icon-Hinterlegung und begrenzte Startanzeige

`dock-icon-feedback.patch` folgt auf `dock-icon-normalization.patch` und die
bisherigen Dock-Patches. Das untere Dock zeichnet keine Flächen mehr hinter
aktiven, dringlichen oder überfahrenen Icons. Vergrößerung, Fensterindikatoren,
Badges, Klickflächen und Vorschauen bleiben erhalten.

Fenster werden zusätzlich über den `StartupWMClass`-Wert des Desktop-Eintrags
zugeordnet. Das verbindet etwa `flausen-spotify` mit
`chrome-open.spotify.com__-Default`. Startanzeigen verwenden die stabile
Desktop-ID auch bei separaten Fenster-Icons und enden beim erkannten Fenster;
fehlgeschlagene Starts laufen nach 15 Sekunden aus (Prüfintervall 500 ms).

Installation auf der vorhandenen Basis:

```sh
patch --dry-run -p0 -d "$HOME/.config/quickshell/caelestia" < kde-customizations/taskbar/dock-icon-feedback.patch
patch -p0 -d "$HOME/.config/quickshell/caelestia" < kde-customizations/taskbar/dock-icon-feedback.patch
systemctl --user restart caelestia-shell.service
python3 kde-customizations/taskbar/tests/dock_launch_feedback.py
```

Der Test führt die installierten Startstatus-Funktionen in der QML-Engine aus:
abweichende Fensterklasse, separate Fenster-ID, unabhängige Starts und Timeout.
Rückbau: den Patch mit `patch -R -p0` im Shell-Verzeichnis zurücknehmen und den
Dienst neu starten. Andere laufende Änderungen vorher vergleichen.

Installiert und visuell geprüft: [Dock](evidence/dock-icon-feedback.png),
[Prüfprotokoll](evidence/dock-icon-feedback-check.json). Nach dem Neuladen wurde
das vorhandene Spotify-Fenster am angehefteten Starter ohne Doppel-Icon erkannt.
Der vollständige Webapp-Neustart konnte in der automatisierten Live-Prüfung
nicht verlässlich bestätigt werden; Abschluss und Timeout sind in der echten
QML-Engine geprüft.

## Desktop-Benachrichtigungen

Einzelne Rauchglaskarten mit App-/Zeitzeile, hervorgehobenem Titel, Aktionen und
segmentiertem Fortschritt nach dem Benachrichtigungs-Mock. Gemeinsame Material-
und Schriftrollen sowie ein stabiler Blur-Pool für den Stapel.
[Quelle, Installation, Rückbau und Live-Prüfung](notification-style/README.md).

## Wetter-Popover im Rauchglas

Taskbar-Wetter nach dem Standort-/Stundenprognose-Mock: große Wetteranzeige,
drei Kennzahlen, sieben Stunden mit Kurve und Tag-/Nachtsymbolen.
[Quelle, Installation, Rückbau und Live-Prüfung](weather-popover/README.md).
