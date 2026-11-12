# Visueller Vergleich mit den verbindlichen Mocks

Die ursprünglichen Bilder sind weiterhin unverändert unter `../../ralleur-caelestia-codex-handoff/reference/desktop-light.png` und `desktop-dark.png` vorhanden. Priorität der Gegenprüfung: Komposition, Neutralwerte, Proportionen/Abstände, Rundung, Typografie, anschließend App-Details.

## Aktueller Vergleich

| Referenz | Aktuelle eigene Komponenten |
|---|---|
| [Light-Mock](../../ralleur-caelestia-codex-handoff/reference/desktop-light.png) | [Light 1586×992](../evidence/components-light-1586x992.png) |
| [Dark-Mock](../../ralleur-caelestia-codex-handoff/reference/desktop-dark.png) | [Dark 1586×992](../evidence/components-dark-1586x992.png) |

**Die aktuellen Bilder sind echte Qt-/Quickshell-Renderbilder der produktiven Komponenten mit laufenden Daten, keine vollständigen Compositor-Screenshots.** Sie enthalten keine erfundenen Browser-/Terminal-/Dateimanager-Fenster. Für reale Fenster gibt es den expliziten `demo`-Aufruf. Die Renderbilder werden nicht als Nachweis eines bestandenen Fullscreen-/Multi-Monitor-Tests ausgegeben.

## Maße bei 1586×992

| Zone | Mock ungefähr | Implementierung in logischen Pixeln |
|---|---|---|
| Topbar | y≈9, h≈31 | x=10, y=10, h=32; Uhr auf der Bildschirmmitte |
| Dock | x≈11, y≈61, w≈52 | x=10, y=62, w=52, h=900 |
| Uhrkarte | x≈1312, y≈66, w≈247, h≈165 | x=1312, y=66, w=248, h=166 |
| Medienkarte | x≈1312, y≈249, h≈150 | x=1312, y=250, h=150 |
| Metriken | x≈1312, y≈417, h≈100 | x=1312, y=418, h=104 |
| Demo-Browser | x≈106, y≈66, w≈992, h≈516 | tatsächlicher Test: x=106, y=66, w=991, h=516 |
| Demo-Terminal | x≈106, y≈596, w≈578, h≈350 | tatsächlicher Test: x=106, y=595, w=577, h=347 |
| Demo-Dateien | x≈702, y≈596, w≈750, h≈350 | tatsächlicher Test: x=703, y=595, w=749, h=347 |

Anfangs wurden Dock/Widgets durch zusätzliche Exclusive Zones verschoben. Das ist korrigiert: sichtbare Flächen ignorieren fremde Ausschlusszonen; getrennte transparente Zonen reservieren den notwendigen Tiling-Platz. Kleine Displays reservieren keine dauerhafte rechte Spalte.

## Light und Dark

Light verwendet warme graue Flächen (`#E9E7E2`, `#F7F5F1`), fast schwarze Schrift und ausreichend sichtbare Konturen. Dark verwendet Graphit/Nachtblau (`#11161D`, `#191E24`), helle Schrift und sparsame Blau-/Rot-/Gelb-/Grün-Signale. Keine weißen Flächen wurden als vollständiger Dark-Dateimanager akzeptiert: der tatsächliche Dolphin-KDE-Palettenfehler wurde behoben.

Der geometrische Original-Ralleur-Marker ersetzt das abweichende Mock-Logo. Seine acht Farben stammen vom echten Brand-Asset. Uhrzeit, Datum, Player und Metriken müssen deshalb vom Mock abweichen. Die Terminalausgabe wird nicht auf den fiktiven Host-/Paketstand des Mocks gefälscht.

Die Wallpaper sind eine eigenständige, deutlich flachere Vektorinterpretation: Wasser-/Bergschichten, Terrasse, Säule, dünne Bögen und große zurückhaltende Farbkreise. Fotografie, Bäume, Materialtexturen und die fotorealistische Dämmerung des Mocks werden nicht pixelidentisch erreicht. Gegenüber der Referenz sind die Karten etwas flacher; native Linux-App-Titelzeilen, Icons und Schatten bleiben systemabhängig. Die reale Website zeigt inzwischen „The Living Atlas“, nicht das illustrative „Ideas take shape“ aus den Mocks.

## Andere Größen

| Größe | Light | Dark | Beobachtung |
|---|---|---|---|
| 1280×800 | [Bild](../evidence/components-light-1280x800.png) | [Bild](../evidence/components-dark-1280x800.png) | rechte Widgets standardmäßig geschlossen, Dock und Topbar frei |
| 1920×1080 | [Bild](../evidence/components-light-1920x1080.png) | [Bild](../evidence/components-dark-1920x1080.png) | getrennte rechte Karten, keine Überschneidung der Shell-Flächen |
| 2560×1600 | [Bild](../evidence/components-light-2560x1600.png) | [Bild](../evidence/components-dark-2560x1600.png) | 16:10; keine unnötig riesigen Karten, mehr Arbeitsfläche |
| 3440×1440 | [Bild](../evidence/components-light-3440x1440.png) | [Bild](../evidence/components-dark-3440x1440.png) | Ultrawide; Kartenbreite begrenzt, Wallpaper proportional beschnitten |

Diese Prüfung bewertet die eigene QML-Geometrie. Sie bestätigt weder physisches HiDPI noch einen echten zweiten Monitor. Der zusätzliche virtuelle Monitor scheiterte im Test an GBM-Buffer-Allokation. Keine entsprechende Abnahme wurde als bestanden markiert.

## Echte Aufnahmen und offene Endabnahme

- [Frühe native Dark-Shell](../evidence/hyprland-dark-initial-1586x992.png): Rahmen, Layer und reale Metriken; vor späteren Icon-/Uhr-Detailkorrekturen.
- [Früher nativer Kitty-Fullscreen](../evidence/hyprland-fullscreen-kitty-initial.png): keine sichtbaren Ralleur-Leisten oder Karten im Bild.
- [Native Dolphin-Dark-Prüfung](../evidence/hyprland-dolphin-dark-theme-check.png): App-Palette korrigiert; keine finale Kompositionsaufnahme.

Weitere Screencopy-Aufnahmen wurden im verschachtelten NVIDIA-/Aquamarine-Pfad unzuverlässig. Ein finaler vollständiger nativer Light-Screenshot mit allen Apps fehlt. Vor einer vollständigen Freigabe sind beide nativen Themes, App-Neustarts, Media-Seek/Playlist, Keyboard-Bedienung, echte Multi-Monitor-/HiDPI-Szenarien und ein Spiel-/Video-Fullscreen auf der Zielsession zu prüfen. Details: [IMPLEMENTATION.md](../IMPLEMENTATION.md).
