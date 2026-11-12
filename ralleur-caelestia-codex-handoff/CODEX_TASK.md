# Codex-Auftrag: Ralleur Desktop Rice auf Caelestia + Hyprland

## Ziel

Implementiere ein tatsächlich benutzbares, konsistentes Desktop-Ricing mit **Light und Dark Mode**. Die beiden PNGs unter `reference/` sind die **maßgebliche visuelle Zieldefinition**. Die Umsetzung soll bei üblicher Nutzung wie der Mock aussehen, nicht nur in einem statischen Screenshot.

- Light: `reference/desktop-light.png`
- Dark: `reference/desktop-dark.png`
- Echtes Brand-Design/Logo: https://ralleur.com
- Technische Basis: https://github.com/caelestia-dots/shell (Quickshell / QML / Qt, Hyprland)

**Arbeitsmodus:** Implementiere direkt → führe Checks aus → teste → korrigiere → dokumentiere. Kein separater PoC und keine obligatorische Planungs-/Review-Phase. Nicht nach jedem Teilschritt auf Freigabe warten. Wenn eine Entscheidung nicht vorgegeben ist, wähle die wartbarste, einfache Lösung und dokumentiere sie.

## Rahmenbedingungen / Bestandsschutz

- Inspiziere zuerst die vorhandenen Projektdateien, Distribution, Shell- und Compositor-Versionen, falls zugänglich. Keine Annahme, dass das Repo leer ist.
- Wenn keine existierende Projektstruktur vorhanden ist, lege eine **isolierte, versionierbare** Ricing-Struktur im Workspace an. Keine produktive Website verändern.
- Verwende möglichst die **originale Caelestia Shell** mit Hyprland. Keine komplette Neuentwicklung der Desktop-Umgebung. Vermeide unnötige Patches am Upstream; bevorzuge eigene modulare QML-Komponenten, separate Konfiguration und klar definierte Erweiterungspunkte.
- Falls nur KDE Plasma vorhanden ist, prüfe die Kompatibilität, aber ersetze eine laufende Session nicht stillschweigend. Berichte klar, welche Teile Hyprland voraussetzen und welche Alternativen es gibt.
- Prüfe die tatsächlich installierten Caelestia-Konfigurationspfade/-Schemas gegen die vorhandene Version, bevor du Dateien schreibst. Beispielorte können sein `~/.config/caelestia/` sowie eine Quickshell-Konfiguration. **Niemals blind unbekannte Konfigurationsschlüssel erfinden.**
- User-Konfiguration nur mit Sicherung/Backup, kontrollierter Installation und Rückweg verändern. Keine systemweiten Installationen, destruktiven Löschaktionen oder Root-Eingriffe ohne explizite Freigabe.
- Abhängigkeiten, Lizenzen und Wiederverwendbarkeit beachten (Caelestia Upstream unter GPL-3.0). Keine Fontdateien unberechtigt einbinden oder weitergeben.

## Lieferumfang: 7 Module

### 1. Wallpaper & Desktop Background
- Erstelle separate Wallpaper-Dateien **für Light und Dark**, angelehnt an den Mock: ruhige geometrische Architektur, feine Linien/Bögen, zurückhaltende kleine Rot-/Blau-/Gelb-/Grün-Akzente, landschaftlich-abstrakte Tiefe.
- Weil die Quellbilder UI enthalten, **nicht** einfach den kompletten Mock zum Wallpaper machen. Gestalte ein sauberes Wallpaper als eigenständiges Asset, idealerweise quelloffenes SVG (und geeignete Rasterexports).
- Zuordnung zu Themes und mehreren Displaygrößen ohne harte Verzerrung.

### 2. Desktop-Rahmen & Chroming
- Caelestia-Rahmen, organische Rundungen und abgerundete Bildschirmmaske passend zum Mock.
- Konsistente Abstände, Kanten, Flächen, Schatten und Blur. Visuell ruhig statt übertriebenem Glassmorphism.
- Das Verhältnis der Flächen und Zwischenräume bei 16:10 und Ultrawide prüfen.

### 3. Navigation / Leisten / Dock
- Schlanke obere Leiste: Workspaces, aktiver App-Name, Uhr/Datum und Systemstatus; optional zusammenhängend mit der Rahmenästhetik.
- Linkes vertikales Dock: Launcher, Home, angeheftete Apps, aktive Fenster/Indikatoren, unten Theme- und Settings-Aktion.
- Dock-Icons müssen reale Anwendungen starten bzw. fokussieren. Keine Attrappen. Unterstütze Tastatur-/Pointer-Interaktion und sinnvolle Tooltips.
- Bestehende Caelestia-APIs und Mechanismen für Workspaces, Launching und Statusdaten wiederverwenden, wo möglich.

### 4. Rechte Widget-Spalte
- Drei getrennte Oberflächen analog zu den Mocks: (a) große Uhr/Datum, (b) Medienkarte mit echter MPRIS-Steuerung, (c) CPU-/RAM-/Disk-Metriken mit echten Daten.
- Kein Hardcoding der Beispieldaten aus dem Bild: Zeit, Track, CPU %, RAM %, Speicherbelegung müssen dynamisch sein.
- Sinnvolle Leerstati bei keinem Player bzw. nicht verfügbaren Sensoren.
- Widget-Spalte auf großen Displays sichtbar; bei kleinen Displays ausgeblendet oder als per Shortcut/Geste öffnende Sidebar. Andere Fenster dürfen nicht unabsichtlich verdeckt werden.

### 5. Hyprland-Fensterverhalten
- Tiling-Abstände, Rundung, Schatten, Fokusakzente, Blur/Opacity, Fensterregeln soweit sinnvoll.
- Das Mock-Layout mit Browser oben und Terminal/Dateimanager unten als repräsentative Workspace-Anordnung, nicht als globale starre Regel für alle Apps.
- Fenster bleiben verschiebbar, skalierbar, fokussierbar und fullscreen-fähig. Volle Bildschirmnutzung für Spiele und Videos ohne permanente Overlays; insbesondere GPU-/Eingabelatenz im Blick behalten.
- Multi-Monitor- und DPI-Variation berücksichtigen.

### 6. App-Theming
- Passe eine Auswahl realer Apps an: Browser (z. B. Zen/Firefox), Terminal (z. B. Kitty), Dateimanager (z. B. Thunar/Nemo/Dolphin, je nach vorhandener Umgebung).
- Konsistente Light-/Dark-Tokens, Icons, Hintergrundfarben und Fensterdekorationen. Bestehende Theme-Systeme verwenden statt fremde Apps neu zu implementieren.
- Unterschiede bei CSD/SSD, GTK/Qt und Browser-Chrome nach Möglichkeit angleichen; nicht erfüllbare Unterschiede transparent dokumentieren.
- Mock-Browsertext ist nur eine Illustration: **ralleur.com nicht nachbauen und nicht verändern**.

### 7. Zentrales Ralleur-Designsystem
- Definiere eine einzige Quelle für Tokens: semantische Farben, Radien, Spacing, Transparenzen, Schatten, Typografie, Icongrößen, Fokus-/Hoverzustände und Breakpoints.
- Neutraler und heller Light Mode sowie dunkelgrafitfarbener Dark Mode; sparsame Farbakzente des **originalen** Ralleur-Brandings.
- Nutze vorhandene offizielle Ralleur-Assets, soweit legal und technisch zugänglich, statt aus generierten Mock-Pixeln ein neues Logo zu konstruieren.
- Stelle klare Light/Dark-Umschaltung bereit, idealerweise manuell und optional automatisch nach System/Zeit. Der Zustand soll über Leisten, Widgets, Wallpaper und App-Themes konsistent sein.

## Anforderungen an die Code-Struktur

- Klar getrennte Komponenten und Theme-Tokens statt einer einzigen großen QML-Datei.
- Dokumentiere, wo **Caelestia Standard**, **konfiguriertes Caelestia**, **eigene Quickshell-Erweiterung**, **Hyprland-Konfiguration** oder **App-spezifisches Theme** zum Einsatz kommt.
- Saubere Installation bzw. Verlinkung, Konfigurationsvalidierung soweit möglich und eine sichere Rückbau-Anleitung.
- Vermeide ressourcenintensive Daueranimationen und aufdringliche Effekte.

## Qualitätssicherung / Fertigstellung

- Sind alle sieben Module vorhanden und in README/Changelog erfasst?
- Funktionieren Light und Dark vollständig und ohne UI-Lücken?
- Sind Topbar, Dock, Buttons, Media Controls und Widgetdaten tatsächlich interaktiv bzw. korrekt?
- Können Spiele und Anwendungen Fullscreen verwenden, ohne von der Shell gestört zu werden?
- Ist das Layout auf 16:10 und einem Ultrawide-Display brauchbar? Für kleinere Displays einen sinnvollen adaptiven Modus bereitstellen.
- Führe verfügbare Build-/Syntax-/Startchecks aus. Falls kein echter Hyprland-Desktop oder Screenshot-Tooling verfügbar ist, melde genau diese Testlücke statt „visuell geprüft“ zu behaupten.
- Erstelle, wenn möglich, **echte** Screenshots der laufenden Umsetzung in Light und Dark und vergleiche sie mit den zwei Referenz-PNGs. Iteriere bei groben Abweichungen in Anordnung, Proportion, Kontrast und Farbwelt.
- Gib am Ende eine kurze Liste tatsächlich implementierter Bereiche, Start-/Installationsanleitung, bekannte Abweichungen, Testergebnisse und verbleibende Risiken aus.

## Was nicht gemeint ist

- Keine statische UI-Replik als Website oder Screenshot-Demo.
- Keine Manipulation der produktiven ralleur.com-Website.
- Keine täuschende Anzeige von Fake-Metriken, Fake-Musiksteuerung oder statischer Uhr.
- Keine unwartbare Komplettkopie des Caelestia-Upstreams, wenn separate Overrides/Erweiterungen genügen.
