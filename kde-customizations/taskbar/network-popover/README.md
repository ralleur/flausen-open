> Aktuelle Schrift- und Materialbasis: [gemeinsamer Menüstil](../menu-style/README.md).
> Haupttext jetzt wie im Startmenü 16 px / 12 pt; ältere Größenangaben unten
> dokumentieren den vorherigen Proportionsschritt. Karten und Abstände bleiben erhalten.

# Netzwerk-Overlays: gemeinsame Menü-Proportionen

WLAN, Ethernet, VPN-/Tailscale-Liste, Verbindungsdetails und Passwortdialog folgen
jetzt [MENU_DESIGN.md](../../MENU_DESIGN.md). Die bestehenden NetworkManager-
und Tailscale-Backends bleiben erhalten.

- Gleiche Basis wie der Update-Hub: Mindestmaßstab 1,15, Inhalt 483 logische Pixel
  breit, außen ca. 520 Pixel. Hauptschrift 13,524 pt, Titel 1,68-mal so groß.
- Eigenständige Rollen für Haupttext, Nebenzeilen, Abschnittstitel und Icons.
  Signal-Icons haben eine feste Spalte; Schlösser und Status bleiben rechts.
- Mehr seitlicher Rand; kompaktere Zeilen mit ausreichenden Klickflächen.
  Einfache Zeilen wachsen bei größerer Schrift mit dem Inhalt.
- Schalter und Icons werden geometrisch skaliert. Ein Schriftaufschlag vergrößert
  nicht zusätzlich jedes Symbol.
- VPN/Tailscale und Verbindungsdetails bleiben aufklappbar. Bestehende Verbindungs-
  und Passwortaktionen wurden übernommen.
- Der Passwortdialog erhält einen kompakten Titel mit Schloss, ruhige Abstände,
  eine feine Fokus-/Fehlerkontur und begrenzte Maskierung bei langen Eingaben.
  Überschriften können bei größerer Schrift umbrechen.
- Glas und Kontur entsprechen dem Update-Menü in hell und dunkel; andere
  Popout-Typen behalten ihre bisherigen Materialwerte.

## Installation

Auf diesem Rechner bereits installiert:

```bash
python /home/USER/ralleurOS/kde-customizations/taskbar/network-popover/install-proportions.py
systemctl --user restart caelestia-shell.service
```

Der Installer sichert geänderte Dateien und ist wiederholbar. Er setzt die drei
Netzwerk-Popouts auf `minScale: 1.15`, installiert `Network.qml` und
`WirelessPassword.qml` und ergänzt den Netzwerkbereich im Glasprofil der
`ClipWrapper.qml`. Grundlage sind die bereits vorhandenen Netzwerk-/Tailscale-
Anpassungen und der aktuelle Update-Hub-Stil.

Der frühere Netzwerk-Schriftaufschlag `+0.27` kompensierte einen Flächenmaßstab
von 0,648: alter Inhalt 272,16 Pixel breit bei Schriftmaßstab 0,918. Er wird
gezielt auf 0 migriert, damit die neue Mindestgröße ihn nicht doppelt vergrößert.
Die tatsächliche Hauptschrift bleibt mit etwa 13,5 pt vergleichbar groß und
steht jetzt in einer passenden Fläche. Andere Schriftaufschläge und individuelle
Werte ungleich diesem alten Kompensationswert bleiben erhalten. Der Vorwert wird
in `migration.json` gesichert. Spätere Schriftanpassungen bleiben wirksam.

Der Patch `../network-proportions.patch` enthält die QML-Änderungen; die gezielte
Migration von `bar.previewFontScales.network` erfolgt durch den Installer.

## Prüfung und Grenzen

Die produktive Shell lädt WLAN und Ethernet mit dem neuen Maßstab und der neuen
Schriftbasis ohne QML-Laufzeitfehler. Die Sitzung war bei der Sichtprüfung bereits
gesperrt. Daher wurden dieselben Produktions-QML-Dateien zusätzlich mit isolierten
Daten und ohne NetworkManager-Zugriff gerendert. Diese Vorschauen zeigen ausdrücklich
Beispielnetze und reservierte IP-Adressen, keine behaupteten Live-Verbindungen.

Kontrolliert wurden dunkel/hell, langer Netzwerkname, Ethernet, aufgeklappte
VPN-/Tailscale- und IP-Details, Passwortdialog, Fehler mit 64 maskierten Zeichen
und vergrößerte Schrift. Die aktive Verbindungsliste vor und nach der Arbeit ist
unverändert. Die eigentlichen Verbindungs- und Authentifizierungsfunktionen sind
unverändert; es wurde keine Verbindung umgeschaltet oder getrennt.

[Vorschau](../evidence/network-proportions-preview.png),
[Prüfdaten](../evidence/network-proportions-check.json).
Der Renderer läuft ohne Display-Zugriff mit vereinfachten Backend-Fixtures;
Fokus, echte Verbindungsvorgänge und systemweite Tastenkürzel werden damit nicht
getestet. Das globale Theme wurde nicht umgeschaltet.

Vorschauen reproduzieren:

```bash
python proportions/render.py --out /tmp/network-dark.png
python proportions/render.py --light --expanded --out /tmp/network-light.png
python proportions/render.py --kind ethernet --expanded --out /tmp/ethernet.png
python proportions/render.py --kind wirelesspassword --password-error --out /tmp/password.png
python proportions/render.py --kind wirelesspassword --font-scale 1.6 --out /tmp/password-large.png
```

Benötigt die vorhandene lokale Quickshell-/Caelestia-Installation, Python und Pillow.
Das einzige erwartete Renderer-Warning betrifft den fehlenden Modifier-Key-Backend
auf der Offscreen-Plattform. Temporäre Vorschau-IPC und Testdateien in der
produktiven Shell wurden entfernt.

## Rückbau

Das Sicherungsverzeichnis steht in
`../evidence/network-proportions-backup.txt`. Darin die vier Dateien unter
`modules/bar/popouts/` relativ zum Shell-Verzeichnis wiederherstellen. Falls der
alte Schriftaufschlag ebenfalls zurückgesetzt werden soll, nur
`bar.previewFontScales.network` entsprechend `migration.json` auf den Vorwert setzen;
die gesamte gesicherte `shell.json` nicht über zwischenzeitliche Einstellungen
kopieren. Anschließend die Shell neu starten.

## Live-Datenverkehr im Netzwerkmenü

Der Live-Graph mit Download, Upload und Gesamtverbrauch sitzt als letzte Karte
unter den Verbindungsdetails, sowohl bei Ethernet als auch WLAN. Er verwendet
weiterhin `Caelestia.Services.NetworkUsage`, dieselben Verlaufspuffer und den
Dashboard-Messintervall. Die Werte beziehen sich wie zuvor auf den gemeinsamen
Netzwerk-Sampler, nicht ausschließlich auf das im Menü dargestellte Gerät.
Die bisherige Netzwerkkarte im Dashboard entfällt; dessen Leerzustand wurde angepasst.
Schrift und Kartenmaterial stammen aus `MenuStyle` / `MenuText`.

Installation: `python kde-customizations/taskbar/network-popover/install-traffic.py`
und `systemctl --user restart caelestia-shell.service`. Den Installer nach den
älteren Proportions-Installern ausführen. Er sichert beide geänderten Dateien;
der Sicherungspfad steht in `../evidence/network-traffic-backup.txt`.

Geprüft: echte Shell mit steigender Anzahl von Verlaufspunkten und wechselnden
Datenraten; Screenshot bei 520 px Außenbreite. Die isolierte Vorschau kann beim
Beenden des nativen Netzwerkdienstes hängen; ein erfolgreich gespeichertes Bild
wird mit dieser Einschränkung gemeldet. Der produktive Dienst lädt ohne QML-Fehler.
