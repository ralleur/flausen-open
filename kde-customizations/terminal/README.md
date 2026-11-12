# Terminal

Ersetzt die Caelestia-Wortmarke in der Fish-Begrüßung durch den gelieferten
flausen.-ASCII-Startscreen mit kurzer Mobile-Animation. Der bisherige
Fastfetch-Aufruf und seine Konfiguration mit Kernel, Uptime, Shell, Speicher,
Paketen, Benutzer, Hostname und Distribution bleiben erhalten.
Die Begrüßung verwendet derzeit `--static`, damit der Prompt ohne eine
vorgeschaltete Animation verfügbar ist. Eine dauerhafte Animation darf nicht
als Hintergrundprozess in denselben Textbereich wie Shell und Befehle schreiben.
Der manuelle Aufruf ohne `--static` zeigt die Infos bereits im ersten
Animationsbild unter dem Banner und läuft 3,2 Sekunden im Vordergrund.
Bei zu geringer Fensterhöhe bleibt die Ausgabe statisch, damit keine
Systeminfos durch Cursorbewegungen überschrieben werden.

`flausen.py` stammt aus dem vom Nutzer gelieferten Ordner `flausen-terminal`
und wurde für die gleichzeitige Fastfetch-Ausgabe erweitert;
`terminal.png` ist das unveränderte gelieferte Graphit-Terminal mit blauem Cursor.
Die Desktop-Einträge von Konsole und Foot erhalten dieses Symbol. Befehle,
Desktop-IDs, Übersetzungen und zusätzliche Starteraktionen bleiben erhalten.

Voraussetzungen: Python 3, Fish; optional Fastfetch, Konsole/Foot und die
KDE-Werkzeuge zum Aktualisieren des App-Caches. Das Symbol wird direkt über
seinen absoluten Dateipfad geladen. Kein Build nötig.

```sh
python3 kde-customizations/terminal/install.py
fish --no-execute kde-customizations/terminal/fish_greeting.fish
./bin/flausen check
```

Die Änderung greift in neuen Fish-Sitzungen. Das Skript passt sich der
Terminalbreite an und deaktiviert die Animation bei zu geringer Höhe.
`REDUCE_MOTION=1` oder `FLAUSEN_MOTION=off` deaktivieren die Bewegung ebenfalls.
Fastfetch wird auch ohne Python weiterhin ausgeführt.

Der Installer sichert nur die geänderten Benutzerdateien unter
`~/.local/state/flausen-terminal/<Zeitstempel>`. Rückbau mit dem ausgegebenen Pfad:

```sh
python3 kde-customizations/terminal/install.py --restore /pfad/zur/sicherung
```

Rückbau überschreibt keine inzwischen manuell geänderten Dateien.
