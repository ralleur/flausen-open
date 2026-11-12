# Ralleur / Caelestia — Visuelle Spezifikation

## Referenzen

### Light Mode
![Light-Mode-Ziel](reference/desktop-light.png)

### Dark Mode
![Dark-Mode-Ziel](reference/desktop-dark.png)

Die PNG-Dateien sind die primären Referenzen für **Gesamtkomposition, Dimensionen, Hierarchie, Abstände und Atmosphäre**. Pixelidentität wird nicht verlangt, wo sie Laufzeitfunktionen, App-UI oder Responsivität verhindern würde.

## Sieben visuelle Zonen

| Nr. | Zone | Position im Mock | Erwartete visuelle Wirkung | Funktionalität |
| --- | --- | --- | --- | --- |
| 1 | Wallpaper | gesamter Desktop hinter Fenstern | ruhige geometrische Bühne mit seltenen Farbakzenten | Light-/Dark-Asset, mehrere Auflösungen |
| 2 | Rahmen | äußerer Bildschirmrand und Fensterkanten | feine Flächen, abgerundete Maske und konsistente Gaps | nicht klickblockierend |
| 3 | Navigation | ganz oben und links vertikal | schlank, präzise, integriert, nicht dominierend | Workspaces, App-Launch/Focus, Status |
| 4 | Widgets | drei kleine Karten rechts | kompakte Utility-Karten mit klarer Hierarchie | Uhr, Player, Metriken live |
| 5 | Fenster | Browser oben links, Terminal unten links, Dateimanager unten rechts | ausgewogene Kachelung, dezente Tiefe | normales Tiling/Fullscreen |
| 6 | Anwendungen | Inhalt der drei Fenster | kohärente Oberflächen mit leisen Farbakzenten | reale Apps / realer Inhalt |
| 7 | Designsystem | über alle Zonen | glaubwürdige, eigenständige Markenästhetik | Tokens + Themes |

## Formensprache

- **Layout:** visuell klar gegliederte, großzügige Fensterflächen; nicht alle Flächen gleich wichtig. Das vertikale Dock und die rechte Utility-Spalte wirken wie eine leicht abgesetzte Shell-Ebene.
- **Ecken:** moderne, großzügige, aber nicht karikaturhaft runde Fenster, Karten und Rahmen.
- **Farben:** Light mit warmen neutralen/hellgrauen Flächen und fast schwarzer Schrift; Dark mit Graphit, Nachtblau und zurückhaltenden warmen Akzenten. Kleine Farbsignale: Rot, Blau, Gelb, Grün, jeweils gezielt eingesetzt.
- **Typografie:** klare moderne Sans-Serif mit guter Lesbarkeit, z. B. Inter, und Monospace im Terminal. Originale Marken-Typografie bevorzugen, sofern verfügbar.
- **Effekte:** feine Schatten, wenig Blur, keine übertrieben glänzenden 3D-Karten oder dauernden Leuchtringe.
- **Kontrast:** auch im Light Mode hinreichend kontrastreich; dunkle Flächen nicht zu schwarz, sekundäre Informationen nicht zu blass.

## Relative Layout-Zielwerte (nur zur Orientierung)

Bei der 1586×992-Referenz:

- Topbar: sehr schmal, ca. 3–4 % der Bildhöhe.
- Linke Dockfläche: ca. 3–4 % der Bildbreite, nahe linkem Außenrand.
- Browserfenster: oberer linker Schwerpunkt, etwa 60 % der Breite und 50 % der Höhe.
- Terminal: links unten, etwa 35 % Breite.
- Dateimanager: unten mittig/rechts, etwa 45 % Breite.
- Widgets: ganz rechts mit ca. 15–17 % Bildbreite, untereinander in drei Karten.

Dies sind **ästhetische Relationen**, keine harten Pixelmaße. In der praktischen Shell sollen App-Fenster nicht durch dauerhaft reservierte Widgetbereiche auf kleinen Displays unbenutzbar werden.

## Interaktion und Breakpoints

- **Groß / Ultrawide:** linkes Dock und Topbar sichtbar; Widgets rechts als eigenständige Spalte; großzügige Tiling-Gaps.
- **Standard-Desktop / 16:10:** Widgets entweder sichtbar bei ausreichend Platz oder intelligent einklappbar; Tiling bleibt produktiv.
- **Kompakter Laptop:** Widgets hinter einem Sidebar-Toggle; App-Dock kompakter oder automatisch ausblendbar, Fenster nutzen verfügbare Breite.
- **Fullscreen:** Rahmen/Dock/Widgets müssen sich korrekt zurücknehmen, kein Overlay über Spielen/Videos und keine unnötigen Frametime-Kosten.
- **Theme Toggle:** umschalten ohne Anwendungsneustart, soweit möglich; aktive App mit nativer Theme-Begrenzung darf erst nach Neustart vollständig wechseln, das muss dokumentiert sein.

## Besonders wichtig: Grenzen der Mock-Illustration

1. Die gerenderte Website in den Browserfenstern ist **nicht** die echte Website. Die echte Seite ist die Markenquelle; keine Änderungen an der Produktivseite.
2. Die Schrift-/Icon-Details in KI-Mocks können falsch sein. Bevorzuge echte App-Icons, korrekte Systeminformationen und konsistente Symbolik.
3. Die Wallpaper-Art ist teilweise durch Fenster verdeckt; erschaffe ein separates, konsistentes Wallpaper in derselben Bildsprache.
4. Beispiel-Uhrzeiten, Musik und Systemdaten sind **keine Sollwerte**. Sie müssen dynamisch aus dem System kommen.
5. Die Screenshots zeigen teils macOS-artige Titelknöpfe. Nutze realistische, konsistente Linux-Fensterdekorationen, statt die App-Funktionalität für Pixelähnlichkeit zu beschädigen.

## Priorisierung für visuelle Vergleiche

1. Makrokomposition und Flächenaufteilung.
2. Light-/Dark-Neutralwerte und Akzentgewichtung.
3. Rundungen, Gaps, Schatten und geringe Transparenz.
4. Typografische Hierarchie sowie Icons.
5. Detailähnlichkeit einzelner Apps (so weit plattformseitig möglich).
