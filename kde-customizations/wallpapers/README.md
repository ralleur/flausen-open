# System-Wallpaper in 4K

Die drei aktiven Sets verwenden die finalen Motive der Überarbeitung als PNGs
mit 3840 × 2160 Pixeln. Flausen Light und Dark wurden aus den Entwürfen auf
4K hochskaliert. Die Dateinamen für Caelestia entsprechen denen der früheren
Exporte.

| Set | PNGs im Repo | Ordner für Caelestia | Motive |
| --- | --- | --- | --- |
| ralleur set | [png/](png/) | `~/Bilder/Wallpapers/ralleur-4k/png/` | 15 |
| flausen dark | [flausen/dark/png/](flausen/dark/png/) | `~/Bilder/Wallpapers/flausen-4k/dark/png/` | 24 |
| flausen light | [flausen/light/png/](flausen/light/png/) | `~/Bilder/Wallpapers/flausen-4k/light/png/` | 24 |

Zur Installation den jeweiligen PNG-Ordner an das Ziel kopieren. Bei einem
Upgrade den bisherigen PNG-Ordner zuvor beiseitelegen, damit ausgemusterte
Motive wie „Colour Current“ aus der Bildliste verschwinden.

## Ursprüngliche Vektorsammlung

`create_collection.py` erzeugt die früheren 16 Ralleur-Motive aus der
Logo-Geometrie und den acht Markenfarben. SVGs, Manifest und Übersicht in
`~/Bilder/Wallpapers/ralleur-4k/` dokumentieren diese frühere Sammlung.

Die ursprünglich eingerichtete Caelestia-Diashow rotierte alle 30 Minuten
zufällig zwischen den 16 PNGs. Der automatische Wechsel ist inzwischen aus;
er lässt sich im Wallpaper-Menü über „Random“ einschalten und konfigurieren. Der Slideshow-Wert in shell.json ist in Stunden angegeben (0.5).
Das bisherige Farbschema bleibt über den vorhandenen Wallpaper-Befehl bestehen.
Es werden keine neuen Timer oder Autostart-Dienste benötigt.

Anpassen: Caelestia > Wallpaper and Style > Slideshow and Order.
Der alte Generator benötigt Pillow und rsvg-convert und schreibt in den
ursprünglichen Sammlungsordner, inklusive `png/`.

Sicherung der ursprünglichen Konfiguration: `backup/shell.json`.
Ursprünglicher Hintergrundpfad: `backup/path.txt`.
Für einen gezielten Rückbau nur `background.slideshow*`,
`background.wallpaperEnabled` und `paths.wallpaperDir` aus der Sicherung
übernehmen; den Hintergrund mit `qs ipc -c caelestia call wallpaper set PFAD`
zurücksetzen. Neuere andere Einstellungen dabei behalten.

## flausen. — kinetic studies

Die eigenständige Sammlung umfasst jetzt 24 Kompositionen in jeweils Light und
Dark. Die ursprüngliche Vektorsammlung, Übersichten und Generator sind in
[flausen/README.md](flausen/README.md) dokumentiert.

## Set-Auswahl im Konfigurator

„Hintergrund auswählen“ bietet jetzt `ralleur set`, `flausen dark` und
`flausen light` direkt an. Die Auswahl gilt für Bildliste, Zufall und Diashow.
Installation, Rückbau und Prüfung: [set-picker/README.md](set-picker/README.md).
