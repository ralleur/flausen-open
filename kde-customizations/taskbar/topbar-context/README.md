# Kontextmenü und verschiebbare Taskbar

Rechtsklick auf die obere Taskbar öffnet vier Aktionen im Stil des neuen
Dock-App-Menüs: **Task manager**, **Taskbar settings**, **Unlock to move** bzw.
**Lock Taskbar** und **Auto Hide** mit Zustandshaken. Gemeinsame Schrift und
Rauchglas stammen aus `MenuStyle`/`MenuText` und dem vorhandenen Blur-Pool.
Zeilen, Icon-/Textspalten, Hover, Kontur und Innenrand entsprechen dem Dock-Menü.
Bei Standardmaßstab misst die Außenbreite rund 306 logische Pixel.

Nach dem Entsperren zieht die linke Maustaste die Taskbar an einen der vier
Bildschirmränder. Eine blaue Randmarkierung zeigt das Ziel. Erst beim Loslassen
in Randnähe wird die Position für diesen Monitor gespeichert; Loslassen in der
Mitte verwirft den Wechsel. Die Taskbar bleibt bis zum erneuten Sperren greifbar.
Im gesperrten Zustand bleiben Linksklicks bei den Widgets. Der Zustand wird mit
den bestehenden `SplitBarSettings` gespeichert.

Das untere App-Dock bleibt eigenständig. Bei einer Taskbar unten rückt das Dock
nach oben; seine Popouts bleiben horizontal und am Dock ausgerichtet. Taskbar-Glas
und Launcher-Ausschnitt folgen auch den seitlichen Positionen. Auto Hide schaltet
die vorhandenen Taskbar-Einstellungen `persistent` und `showOnHover`; das Dock
bleibt eigenständig sichtbar. Die manuelle Sichtbarkeit wird beim Umschalten
gelöst. Vollbild und Übersicht behalten ihre vorhandenen Regeln.

## Installation und Rückbau

Voraussetzung: bestehende Split-Taskbar einschließlich freigegebenem Rauchglas,
Dock-Kontextmenü, Settings und `flausen-task-manager`.

```sh
python3 kde-customizations/taskbar/topbar-context/install.py --dry-run
python3 kde-customizations/taskbar/topbar-context/install.py
systemctl --user restart caelestia-shell.service
```

Der Installer prüft jeden Patchabschnitt vor dem Schreiben, sichert betroffene
Dateien und kopiert die beiden gepflegten QML-Quellen. Wiederholte Installation
ist ohne Änderungen möglich. Unbekannte Quellstände werden abgewiesen.
Review-Patch: `../topbar-context.patch`. Sicherungspfad:
`../evidence/topbar-context-backup.txt`.

```sh
python3 kde-customizations/taskbar/topbar-context/install.py --restore BACKUP
systemctl --user restart caelestia-shell.service
```

Gespeicherte Benutzerpräferenzen werden beim Installieren/Rückbau nicht gelöscht.
Spätere Änderungen vor dem Wiederherstellen einer alten Dateisicherung vergleichen.

## Prüfung

```sh
python3 kde-customizations/taskbar/tests/topbar_context_live.py --screen HDMI-A-2
./bin/flausen check
```

Der Live-Test benötigt QtTest und eine ruhende KDE-Session. Er startet die Shell
neu und fügt vorübergehend einen lokalen Qt-Mausereignis-/IPC-Prüfzugang ein.
Rechtsklick, tatsächliche Klickflächen, Ziehen an alle vier Ränder, Sperren,
Auto Hide und beide App-Aktionen werden in der laufenden Shell geprüft.
Nur neu geöffnete Prüffenster werden geschlossen. Einstellungen und Quelldatei
werden anschließend wiederhergestellt; der Prüfzugang wird entfernt.
Kein systemweiter Eingabezugriff. Die natürliche Hover-Rückkehr über den
Compositor ist durch diese prozessinternen Mausereignisse nicht vollständig
abgedeckt. Kein neuer Frame-Zeit-Benchmark.

Belege: `../evidence/topbar-context-check.json`,
`../evidence/topbar-context-live.png` und `../evidence/topbar-context-comparison.png`.
