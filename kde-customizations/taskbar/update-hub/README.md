> Aktuelle Schrift- und Materialbasis: [gemeinsamer Menüstil](../menu-style/README.md).
> Haupttext jetzt wie im Startmenü 16 px / 12 pt; ältere Größenangaben unten
> dokumentieren den vorherigen Proportionsschritt. Karten und Abstände bleiben erhalten.

# Zentraler Update-Hub

Das Dropdown folgt den bereitgestellten hellen und dunklen Referenz-Mocks:
Titel mit Update-Anzahl, Gruppen **System**, **Spiele**, **Apps**, dezente Karten
mit Kontur und native App-Icons. Steam und Battle.net bündeln jeweils Launcher
und eingerückte Spiele-Zeile; WowUp und ArtCraft teilen eine App-Karte.
Haken und Pfeil nach oben bleiben die Statusanzeigen. Eine verfügbare
Caelestia-Aktualisierung erhält zusätzlich die kurze blaue Beschriftung.
Der Fußbereich zeigt den ältesten Prüfzeitpunkt der sichtbaren Quellen sowie
„Updates öffnen“. Der Knopf öffnet die bestehende Update-Verwaltung und startet
keine Installation. Versionen stehen im Tooltip und auf der Nexus-Seite.
Glas-Tönung und Kontur folgen dem hellen/dunklen Theme. Nur das Update-Popout
verwendet die neue Tönung und Rundung in `ClipWrapper.qml`.
Die Mindestskalierung entspricht dem Kalender (1,15). Quellen können einzeln
angezeigt werden; ihre Auswahl bleibt gespeichert. Die vorhandene
Caelestia-Versionsverwaltung bleibt erhalten und wird separat bezeichnet.

## Datenquellen

| Quelle | Installierter Stand | Vergleich / Anzeige |
| --- | --- | --- |
| Steam Client | Installierte Version aus dem Bootstrap-Protokoll | Valves Client-Manifest für denselben Kanal |
| Steam-Titel | Manifeste aller Bibliotheken | Update-Warteschlange, laufende Downloads mit Fortschritt, Build-ID und Update-Regel |
| Battle.net | Dateiversion von Battle.net.exe | Blizzards öffentlicher `bna/versions`-Feed, Region EU |
| Battle.net-Spiele | Aktive Produkte in `.build.info` | Blizzards Versions-Feed je Produkt und installierter Region |
| WowUp-App | Version der eingerichteten AppImage | Offizielles GitHub-Release der passenden WowUp-Ausgabe |
| WowUp-Addons | Nativer Addon-Speicher | Installierte und von WowUp zuletzt erfasste Zielversionen, bekannte Updates und Auto-Update-Status |
| ArtCraft-Suite | Installierte Flatpak-App-Versionen | Offizieller ArtCraft-Release-Feed; Launcher, PhotoCraft und LightCraft einzeln |

Blizzards Adapter erkennt auf diesem Rechner WoW Retail und Forever; weitere
Produkte mit derselben `.build.info`-Struktur werden dynamisch aufgenommen.
Unbekannte Formate und fehlende Serverdaten werden als Fehler / unbekannt
angezeigt. Ein Beta- oder abweichender Versionsstand wird nicht als Downgrade
angeboten. Der Steam-Clientvergleich verwendet die vom Bootstrapper protokollierte
**installierte** Version: ein bereits heruntergeladenes Manifest allein beweist
keine erfolgte Installation.

ArtCraft wurde aus Flatpak-Bundles mit deaktivierten Origins installiert.
Der Hub prüft deshalb `https://api.storyteller.ai/v1/craft_apps/release_info`,
den auch der Launcher verwendet, statt aus fehlenden Flatpak-Remote-Updates
„aktuell“ abzuleiten. Der Zeitpunkt des offiziellen Feeds wird ebenfalls gezeigt.

Steam-Spielstatus und WowUp-Addonstatus sind ausdrücklich lokale Daten. Der Hub
zeigt deren Zeitpunkt; er behauptet dafür keine eigene frische Online-Prüfung.
CurseForge-Authentifizierung und Steam-Sitzungen werden nicht übernommen.
App- und Spielupdates werden weiterhin von den jeweiligen Programmen installiert;
Update-Regeln bleiben dort konfigurierbar. Der Hub nennt die Einstellungswege und
öffnet die zuständige App. Die Quellen-Schalter steuern ausschließlich die Anzeige.

## Aktualisierung und Fehler

Online-Prüfung beim Start, auf Knopfdruck und alle 30 Minuten. Alle 20 Sekunden
werden zusätzlich lokale Manifeste und gespeicherte Addon-Daten neu eingelesen,
ohne weitere Netzabfragen. HTTP-Abfragen laufen parallel mit begrenzter Laufzeit.

Letzte erfolgreiche Publisher-Antworten liegen in
`~/.local/state/ralleur-update-hub/publisher-cache.json` (XDG_STATE_HOME gilt).
Bei Verbindungsfehlern bleibt der vorherige erfolgreiche Zeitpunkt erhalten;
der Hub zeigt **„Offline · letzter Stand“**. Diese Fehlerkennzeichnung bleibt
auch bei der nächsten rein lokalen Aktualisierung erhalten und verschwindet erst
nach erfolgreicher Online-Prüfung. Daten älter als 24 Stunden werden als veraltet
markiert. Noch nie erfolgreich geprüfte Quellen melden einen Fehler statt „aktuell“.

Das Leisten-Icon berücksichtigt bekannte Updates aller sichtbaren Quellen,
einschließlich der Addons. Bei Fehlern erscheint ein Fehlersymbol. Die Abfragen
starten keine Launcher, installieren nichts und verändern keine nativen App-Dateien.
Die Anzeigepräferenzen liegen in `~/.config/Caelestia/caelestia-shell.conf` unter
`[RalleurUpdateHub]`. Lesende Diagnose:

```bash
quickshell ipc -p "$HOME/.config/quickshell/caelestia" call updateHub inspect
```

## Installation und Rückbau

Bereits installiert. Auf einer Shell mit den bisherigen Taskbar-Patches:

```bash
python /home/USER/ralleurOS/kde-customizations/taskbar/update-hub/install.py
systemctl --user restart caelestia-shell.service
```

Bei bereits vorhandenem Hub `--upgrade` verwenden. Vorherige Dateien werden nach
`~/.local/state/ralleur-taskbar-backups/<Zeitstempel>-update-hub/` gesichert;
`../evidence/update-hub-backup.txt` nennt den letzten Pfad. Zum Rückbau einer
Aktualisierung die dortigen Dateien relativ zum Shell-Verzeichnis wiederherstellen
und die Shell neu starten. Die zuletzt installierte Fassung ist außerdem vollständig
in `update-hub.patch` enthalten; `update-hub-status.patch` aktualisiert die erste
Hub-Fassung aus diesem Chat auf die tatsächlichen Versionsabfragen.

Zum vollständigen Entfernen des Hubs die fünf ursprünglichen QML-Dateien aus
`~/.local/state/ralleur-taskbar-backups/20261102T151528Z-update-hub/` wiederherstellen;
die ursprüngliche `modules/nexus/PageDictionary.qml` liegt in
`~/.local/state/ralleur-taskbar-backups/20261102T151726Z-update-hub/`.
Danach `services/UpdateHub.qml` und `services/update-hub-probe.py` entfernen und
die Shell neu starten. Der eigene Cache und gespeicherte Anzeigepräferenzen können
beim Rückbau erhalten bleiben.

## Prüfung

```bash
python -m unittest discover -s kde-customizations/taskbar/update-hub/tests -v
```

Zwölf Tests decken unter anderem echte Update-Vergleiche, keine Downgrades,
mehrere Steam-Bibliotheken, aktive Blizzard-Builds und regionale Unterschiede,
ArtCrafts Feed, WowUps getrennte App-/Addonstände sowie Offline-Cache und
Wiederherstellung der Verbindung ab. Alle sechs Quellen wurden zusätzlich auf
diesem Rechner abgefragt; das produktive QML lädt ohne neue Laufzeitfehler.
Dropdown und Detailseite wurden visuell kontrolliert. Es wurde kein Update installiert.

Primärquellen: [ArtCraft Launcher](https://github.com/storytold/craft-launcher),
[WowUp](https://github.com/WowUp/WowUp),
[Steam-Update-Einstellungen](https://help.steampowered.com/en/faqs/view/71AB-698D-57EB-178C).

## Referenz-Stil und Rückbau

`update-hub-style.patch` führt von der vorherigen kompakten Liste zum
Referenz-Stil. Das dunkle Popout wurde in der echten Sitzung visuell geprüft;
483 × 834,2 logische Pixel bei Schrift-/Flächenmaßstab 1,15. Die hellen Farben
sind an das Theme gebunden; das globale Theme wurde für diese Prüfung nicht
umgeschaltet. Backend und Update-Regeln wurden nicht verändert.

Zum Rückbau ausschließlich dieser Stiländerung die Dateien aus
`~/.local/state/ralleur-taskbar-backups/20261102T161752Z-update-hub/` relativ zum
Shell-Verzeichnis wiederherstellen und die Shell neu starten. Bei vollständigem
Entfernen des Hubs zusätzlich zu den oben genannten Dateien auch die ursprüngliche
`modules/bar/popouts/ClipWrapper.qml` aus dieser Sicherung wiederherstellen.

## Korrigierte Größenverhältnisse

Die letzte Anpassung übernimmt die Proportionsregeln aus
[MENU_DESIGN.md](../../MENU_DESIGN.md). Haupttext 20 % kleiner bei unverändert großen
App-Icons, mehr Seitenrand, kompaktere Karten und Kopfknöpfe auf Titelhöhe.
Live: Außenfläche 519,8 × 738,3 logische Pixel (Höhe/Breite 1,42), Referenz 1,40.
Der Schrift-/Flächenmaßstab bleibt 1,15. Backend und Statusabfragen bleiben erhalten.

Patch von der vorherigen Kartenansicht: `update-hub-proportions.patch`.
Rückbau: die vorherigen Dateien aus
`~/.local/state/ralleur-taskbar-backups/20261102T165707Z-update-hub/`
relativ zum Shell-Verzeichnis wiederherstellen und die Shell neu starten.
Die Regeln sind in der Projekt-`AGENTS.md` für zukünftige Menüaufträge verankert.
