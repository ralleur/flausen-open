> Aktuelle Schrift- und Materialbasis: [gemeinsamer Menüstil](../menu-style/README.md).
> Haupttext jetzt wie im Startmenü 16 px / 12 pt; ältere Größenangaben unten
> dokumentieren den vorherigen Proportionsschritt. Karten und Abstände bleiben erhalten.

# Bluetooth-Overlay mit gemeinsamen Menü-Proportionen

Das Taskleisten-Overlay verwendet dieselbe Größenbasis wie Update-Hub und Netzwerk:
ca. 520 logische Pixel außen, 483 Pixel Inhalt bei Mindestmaßstab 1,15. Hauptschrift
13,524 pt, Titel 1,68-mal so groß; Nebenzeilen sind kleiner und kontrastreich.
Die Vorgaben stehen in [MENU_DESIGN.md](../../MENU_DESIGN.md).

Die Statuskarte kombiniert Bluetooth-Symbol, Adapterstatus und Schalter.
Geräte stehen in einer gemeinsamen Karte mit festen Spalten für Symbol, Namen,
Verbindungsstatus, Akku und Aktionen. Lange Namen werden gekürzt und vollständig
im Tooltip gezeigt. Verbundene Geräte haben einen Haken; Verbindungsaufbau und
Trennen zeigen den vorhandenen Fortschrittsindikator. Niedrige Akkustände bleiben
als Zahl und Warnfarbe erkennbar. Die Suche kann gestartet und beendet werden;
das Zahnrad öffnet die bestehende Bluetooth-Verwaltung.

Die bisherigen Aktionen bleiben angebunden: `adapter.enabled`,
`adapter.discovering`, `device.connected` und `device.forget()`. Geräte bleiben
nach verbunden/gepaart/Name sortiert, mit maximal fünf Einträgen wie zuvor.
Bei ausgeschaltetem oder fehlendem Adapter wird der Zustand ausdrücklich gezeigt.
Es gibt keine automatische Suche, Kopplung oder Verbindungsänderung beim Öffnen.

## Installation

Auf diesem Rechner bereits installiert:

```bash
python /home/USER/ralleurOS/kde-customizations/taskbar/bluetooth-popover/install.py
systemctl --user restart caelestia-shell.service
```

Voraussetzung ist das vorhandene gemeinsame Netzwerk-/Update-Glasprofil.
Der Installer sichert alle Änderungen, installiert `Bluetooth.qml`, ergänzt
`minScale: 1.15` in `Content.qml` und Bluetooth im Glasprofil der `ClipWrapper.qml`.
Wiederholte Installation verändert keine bereits passenden Dateien.

Der bekannte alte Bluetooth-Schriftaufschlag `+0.26`, der die verkleinerte alte
Fläche kompensierte, wird bei aktivierter Einzel-Schriftanpassung gezielt auf 0
migriert. Andere Werte, globale Schriftanpassungen und andere Menüs bleiben
unverändert. Die Migration steht mit Vorwert in der Sicherung. Spätere
Schriftvergrößerung bleibt wirksam; Zeilen wachsen mit ihrem Inhalt.

`../bluetooth-proportions.patch` enthält die QML-Änderungen. Die gezielte
Konfigurationsmigration übernimmt der Installer.

## Prüfung

Die tatsächliche Komponente wurde in der laufenden Shell mit dem nativen
Bluetooth-Modul zusätzlich unsichtbar instanziiert und ohne QML-Fehler geprüft.
Damit wurden keine Nutzerinteraktionen abgefangen. BlueZ-Adapterzustände und
Verbindungs-/Kopplungszustände wurden vor und nach der Arbeit lesend verglichen.
Es wurde kein Gerät verbunden, getrennt oder entfernt und die Suche nicht aktiviert.

Die Sichtprüfung verwendet dieselbe Produktions-QML mit einem isolierten
Bluetooth-API-Double: hell/dunkel, mehrere verbundene Geräte, niedriger Akku,
langer Gerätename, Verbindungsaufbau, ausgeschaltetes Bluetooth, fehlender Adapter,
laufende Suche sowie größere Schrift (1,6). Diese Bilder sind ausdrücklich
Layout-Vorschauen mit Beispieldaten, keine behaupteten Live-Geräte.
Der globale Theme-Modus wurde nicht umgeschaltet.

[Vorschau](../evidence/bluetooth-proportions-preview.png),
[Prüfdaten](../evidence/bluetooth-proportions-check.json).

Reproduzierbare Vorschau mit dem gemeinsamen Renderer:

```bash
python ../network-popover/proportions/render.py --kind bluetooth --out /tmp/bt-dark.png
python ../network-popover/proportions/render.py --kind bluetooth --light --out /tmp/bt-light.png
python ../network-popover/proportions/render.py --kind bluetooth --bluetooth-state off --out /tmp/bt-off.png
python ../network-popover/proportions/render.py --kind bluetooth --bluetooth-state missing --out /tmp/bt-missing.png
python ../network-popover/proportions/render.py --kind bluetooth --bluetooth-state searching --out /tmp/bt-search.png
python ../network-popover/proportions/render.py --kind bluetooth --font-scale 1.6 --out /tmp/bt-large.png
```

Der Renderer ersetzt ausschließlich in seiner temporären Kopie den Bluetooth-
Import durch das API-Double; die Layout-Datei bleibt sonst unverändert. Das Double
hat keine BlueZ-Verbindung und führt keine Aktionen aus. Die beiden verwendeten
Icon-Zuordnungen werden aus dem echten Icon-Helper übernommen. Offscreen-Warnings
zum Modifier-Key-Backend sind erwartet. Echte Kopplungsabläufe und Tastaturnavigation
wurden bei dieser Stiländerung nicht ausgeführt. Temporäre Prüf-IPC wurde entfernt.

## Rückbau

Die Sicherung steht in `../evidence/bluetooth-proportions-backup.txt`.
Die drei gesicherten QML-Dateien relativ nach `~/.config/quickshell/caelestia/`
zurückkopieren. Bei Bedarf nur `bar.previewFontScales.bluetooth` entsprechend
`migration.json` wiederherstellen; nicht die gesamte gesicherte `shell.json`
über zwischenzeitliche Einstellungen kopieren. Anschließend die Shell neu starten.
