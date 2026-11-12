# Implementierung und tatsächlicher Teststand

Stand: 1. November 2026. **Implementierung vorhanden; physische Desktop-Endabnahme teilweise offen.** Es gibt keine statische Website-Replik, keine fotografierten Mock-Widgets und keine erfundenen Laufzeitwerte.

## Ausgangslage und Schutz des Bestands

Der Workspace enthielt das Handoff mit beiden verbindlichen 1586×992-PNGs, noch keine Ricing-Implementierung und kein Git-Repository. Die Handoff-Dateien wurden zuerst gelesen; die Bildreferenzen wurden geöffnet. Für die neue Lösung wurde die getrennte, versionierbare Struktur `ralleur-desktop/` angelegt und der Workspace als Git-Repository initialisiert. Die Handoff-Dateien wurden nicht umgeschrieben; ihre vorhandenen Prüfsummen bestehen weiterhin.

Vorhandene Umgebung: CachyOS, KDE Plasma/`kwin_wayland`, Quickshell 0.3.2 und eine bereits laufende **Caelestia-KDE** v2.6.3. Diese ist ein anderer Fork mit anderem Plugin-ABI und wurde nicht als Hyprland-Upstream behandelt. Hyprland war nicht installiert. Alle zusätzlich benötigten Tests erfolgten mit heruntergeladenen, SHA-256-geprüften und nur unter `.cache/` entpackten Paketen bzw. selbst kompilierten privaten Bibliotheken. Kein Root-Eingriff, keine Paketinstallation ins System, keine Session-Umschaltung.

Produktive KDE-, Caelestia- und Hyprland-Konfigurationen waren keine Installationsziele. Die endgültige Installation verwendet eigene XDG-Konfigurations-, Daten- und Cache-Verzeichnisse. Kleine bestehende App-Präferenzen werden kopiert, nicht schreibbar durchgereicht. Testinstallationen lagen ausschließlich unter `.cache/` bzw. in temporären Testverzeichnissen. Der Installer sichert auch eine eventuell schon vorhandene Entrypoint-Datei vor Änderungen.

## Architektur und sieben Module

| Bereich | Umsetzung | Herkunft / Erweiterungspunkt |
|---|---|---|
| 1. Wallpaper | Eigene ruhige Architektur mit Terrassen, Berg-/Wasserschichten, Bögen und wenigen originalen Brand-Akzenten; je Light/Dark SVG und 2560×1600 PNG. `PreserveAspectCrop`, keine Verzerrung durch feste Display-Streckung. | Eigene Assets, erzeugt von `bin/generate.py` aus den Tokens; eigene Hintergrund-Layer. |
| 2. Rahmen / Chroming | Native Caelestia-Drawers und organischer Bildschirmrahmen; 6 px Rahmen, 22 px innere Rundung, eigene Karten mit 18 px Radius; ruhige Flächen und dünne Konturen. Hyprland-Gaps, Rundung, Schatten und kleiner Blur. | **Caelestia Standard**, über das geprüfte v2.5.0-Schema konfiguriert; keine QML-Core-Patches. |
| 3. Navigation | Topbar mit echten Workspaces, aktiver Fenstertitel, Systemuhr, PipeWire, Netzwerkzustand, UPower und Tray. Dock: Launcher, Home, Browser, Editor, Terminal, Dateien, Musik, Theme, Einstellungen, Session. App-Fokus über Caelestias `Hypr`-Service, Start über echte Programme. Tastaturfokus und Tooltips. | **Eigene Quickshell-Komponenten**; nativer Caelestia-Launcher, Nexus und Session-Menü bleiben erhalten. |
| 4. Widgets | Uhr/Datum minütlich; aktive originale `Players.active`-Auswahl; MPRIS-Transport und Seek; Linux-CPU/RAM alle 3 s, Disk alle 30 s, ein geteilter Prozess. Empty States ohne Fake-Cover oder Demo-Track. | Native Caelestia-Player-Auswahl / Quickshell MPRIS; eigene Karten und `metrics.py`. |
| 5. Fenster | Hyprland Lua 0.57 mit Tiling, 18 px Gaps/Rundung, nativen Move-/Resize-/Fullscreen-Aktionen; per Monitor zurückweichende eigene Layer. Repräsentatives Fensterlayout nur auf expliziten `demo`-Aufruf. | **Hyprland-Konfiguration**, getrennte `local.lua`; kein globales Browser-/Terminal-Floating. Legacy-Hyprlang zusätzlich erzeugt, ungetestet. |
| 6. Apps | Kitty, Konsole, GTK 3/4, qt6ct/Fusion, KDE-Farbschema, Firefox-Chrome/-Profil und Chromium-Profil. Dolphin gezielt mit KDE-Plattformtheme. Kitty-Farben per eigenem Socket live neu setzen. | **Native App-Theme-Systeme**, generierte Dateien im eigenen Session-Verzeichnis. |
| 7. Designsystem | `design/tokens.json` für Light/Dark, Brand-Farben, semantische Flächen, Abstände, Radien, Fokus, Hover, Typografie, Icongrößen und Breakpoints. Originales Ralleur-Symbol, keine Rekonstruktion aus Mock-Pixeln. | **Zentrale Tokens**; Theme-Manager erzeugt Caelestia-Palette und alle Theme-Verbraucher konsistent. |

Die originale Shell und ihre C++-Plugins sind auf Commit festgeschrieben. Die eigene Root-Datei verbindet die nativen Module mit `qml/Screen.qml`; die Upstream-Verzeichnisse werden im privaten Laufzeitverzeichnis verlinkt. Paketverwaltete Dateien bleiben unangetastet. `QML_IMPORT_PATH` **und** `QML2_IMPORT_PATH` zeigen gezielt auf denselben privaten Plugin-Prefix, damit global gesetzte KDE-Fork-Importpfade nicht zwei ABIs vermischen. Die originale CLI liegt ebenfalls privat und spricht denselben isolierten `caelestia`-Konfigurationsnamen an.

Einziger erforderlicher Quellpatch: Header-abhängige libcava-Signaturanpassung im privaten Build-Checkout, dokumentiert in [THIRD_PARTY.md](THIRD_PARTY.md). Weder Desktop-Module noch Style-Komponenten des Upstreams wurden kopiert oder überschrieben.

## Erfolgreich ausgeführte Prüfungen

**Reproduzierbarer Build:** `bin/build-upstream --workspace .cache/repro --prefix .cache/runtime-repro --jobs 6` wurde vollständig ausgeführt: frische festgeschriebene Checkouts, M3Shapes, alle Caelestia-Plugin-Module, Hilfsprogramme und Original-CLI im privaten venv. Danach wurde daraus eine neue isolierte Release-Testinstallation erstellt und die Shell erfolgreich gestartet. [Build-Nachweis](evidence/build.json).

**Syntax / Laden:** Python-Dateien erfolgreich mit `py_compile` geprüft; alle eigenen QML-Dateien durch `qmlformat` geparst/formatiert; die vollständige originale Shell plus Erweiterung meldete `Configuration Loaded`, ohne QML-Typ-/Property-/Binding-Fehler im finalen Start. Hyprland 0.57.0 meldet für die installierte Lua-Datei `config ok`. Der reine Verifier meldet zusätzlich seine fehlende IPC-Socket-Bindung außerhalb einer eigenen laufenden Instanz; das ist kein Lua-Parsefehler. Die verschachtelte Qt-Wayland-Umgebung kann Textinput-/Portal-Warnungen ausgeben.

**8 Kernprüfungen bestanden** ([Protokoll](evidence/core-tests.txt)):

- erzeugte Theme-Verbraucher und gültige SVGs;
- reale Linux-Metriken und Fehlerfall bei fehlendem Dateisystem;
- unveränderte Handoff-Prüfsummen;
- Installations-Dry-run und Ablehnung falscher Upstream-Revision;
- Installation, identischer No-op, Theme-Rundlauf und Wiederherstellung eines vorher vorhandenen Entrypoints;
- Schutz nachträglicher Änderungen und zusätzlicher Rettungssnapshot bei erzwungenem Rollback;
- Erhalt von `local.lua` beim Upgrade;
- Ablehnung eines Backup-Manifests mit fremden Installationszielen.

**7 Live-Funktionsprüfungen bestanden** in der laufenden Hyprland-Shell ([JSON](evidence/live-check.json)):

- CPU/RAM/Disk liegen im gültigen Bereich und kommen aus echten Daten;
- Workspace-Wechsel über die originale Hypr-API;
- Widget-Toggle hin und zurück;
- Light/Dark-Rundlauf ohne Shell-Neustart;
- Dock-Backend fokussiert vorhandenes Kitty über Workspace-Grenzen, ohne ein zusätzliches Fenster zu starten;
- Fullscreen-Zustand und Entfernen der eigenen sichtbaren Layer, danach Wiederherstellung;
- Pause/Play eines echten mpv-MPRIS-Players.

Für den MPRIS-Test wurde eine lokale FLAC-Testdatei tatsächlich in mpv mit MPRIS-Plugin dekodiert, lautlos über `--ao=null`. Die Testdatei und der Player sind keine Bestandteile des fertigen Desktops. Die ausgelieferten Widgets zeigen ihre echten Playerdaten oder den Empty State.

Zusätzlich ausgeführt: echte Chromium-, Kitty- und Dolphin-Fenster gestartet; das freiwillige Demo-Layout an deren tatsächlichen Fensteradressen angeordnet; der native Nexus-Einstellungsdialog geöffnet. Der anfängliche Dolphin-Palettenfehler wurde durch native KDE-Theme-Anbindung korrigiert. Bei Kitty wurde ein vom vorhandenen Shell-Startup überschriebener Farbsatz über den eigenen Socket korrigiert. Der ursprüngliche Fokusfehler an Workspace-Grenzen wurde über die verifizierte IPC-Fensteradresse behoben.

**10 QML-Komponentenbilder:** Light und Dark jeweils in 1280×800, 1586×992, 1920×1080, 2560×1600 und 3440×1440. Alle PNGs vollständig dekodiert und auf exakte Abmessungen geprüft. Die Bilder enthalten laufende Uhr und reale Metriken. Bei 1280×800 bleiben Widgets geschlossen; bei großen Formaten ist die rechte Spalte sichtbar. Fehlende externe Tray-Icons fallen auf einen neutralen, weiterhin anklickbaren Indikator mit echtem Tooltip zurück. [Render-Matrix](evidence/render-matrix.json).

## Visuelle Prüfung und Grenzen

Beide Referenz-PNGs und die aktuellen Light-/Dark-Komponentenbilder wurden direkt angesehen. Anordnung, Abstände und Proportionen wurden iteriert; besonders eine zunächst doppelte Layer-Reservierung wurde korrigiert. Bei 1586×992 stimmen Dock und Kartenpositionen bis auf ungefähr 1–4 px mit der Vorgabe überein. Der [visuelle Prüfbericht](docs/VISUAL_REVIEW.md) enthält Maße, Bildverweise und Abweichungen.

Frühe **echte Hyprland-Screenshots** konnten erstellt werden: [Dark-Shell](evidence/hyprland-dark-initial-1586x992.png), [Kitty Fullscreen](evidence/hyprland-fullscreen-kitty-initial.png), [native Dolphin-Dark-Palette](evidence/hyprland-dolphin-dark-theme-check.png). Diese sind als Zwischenstände bezeichnet, nicht als finale vollständige Endabnahme.

Spätere Screencopy-Versuche im verschachtelten NVIDIA-/Aquamarine-Pfad hingen bzw. lieferten keine zuverlässigen neuen Frames; ein zusätzlicher virtueller Output konnte keine GBM-Buffer anlegen. Der letzte Live-Test verwendet daher explizit `--skip-capture`: **aktuelle Fullscreen-Aufnahme nicht ausgeführt**, obwohl die Zustands-/Layer-Prüfung besteht. Ein vollständiger finaler Light-Desktop-Screenshot mit allen echten Apps liegt nicht vor. Die zehn Software-Renderbilder ersetzen diese Prüfung nicht.

## Nicht ausgeführt / verbleibende Abweichungen

| Punkt | Status und Konsequenz |
|---|---|
| Physische Hyprland-Session, Spiele/Video, GPU-Latenz/Frametimes | **Nicht ausgeführt.** Fullscreen-Zustände und Layer sind geprüft; es gibt keine Zusage für konkrete Spiele oder NVIDIA-Treiber. |
| Physisches HiDPI und stabiler Multi-Monitor-Betrieb | **Nicht ausgeführt.** Logische Breakpoints/mehrere Größen gerendert; Code ist per Screen aufgebaut. Virtueller Zweitmonitor scheiterte am Test-Grafikpfad. |
| Finale vollständige native Light-/Dark-Aufnahmen | **Teilweise offen.** Frühe Dark-Aufnahmen vorhanden; aktueller Vergleich beruht zusätzlich auf gekennzeichneten QML-Renderbildern. |
| Firefox, Thunar/GTK 3/4 und Konsole | Themes erzeugt, nicht als echte GUI-Apps geprüft; im Test waren Chromium, Kitty und Dolphin verfügbar. App-Neustart kann erforderlich sein. |
| Alle Dock-Rollen, Home, Tray-Kontextmenüs, Audio-Mute, Batterie-Laptop | Backend/API vorhanden; Browser/Terminal/Dateien und Terminal-Fokus getestet. Übrige Aktionen nicht vollständig per Pointer/Tastatur durchgespielt. |
| MPRIS Seek, Next/Previous mit Playlist und mehrere gleichzeitige Player | Implementiert mit Capability-Checks; Pause/Play und Empty State geprüft, übrige Interaktionen nicht vollständig getestet. |
| Keyboard- und Screenreader-Endabnahme | Starker Fokus, Tooltips, Accessible-Namen und Shortcuts implementiert; kein vollständiger manueller Accessibility-/Keyboard-Trap-Test. |
| Native Caelestia-Palette-/Wallpaper-Seiten | Die Ralleur-Tokens und der Ralleur-Theme-Schalter sind maßgeblich. Die allgemeinen Upstream-Seiten bleiben zugänglich, sind aber kein zweites Ralleur-Designsystem; dort ausgewählte fremde Paletten/Wallpaper werden nicht als konsistent mit diesem Rice zugesichert. |
| Wallpaper / App-Chrome | Bewusst eigenständige vektorhafte Architektur statt fotorealistischer Mock-Landschaft. Linux-CSD/SSD und reale App-Inhalte unterscheiden sich. Die echte ralleur.com wird weder kopiert noch verändert. |
| Legacy-Hyprland-Konfiguration | Erzeugt, nicht gestartet oder end-to-end geprüft. Ziel und verifizierte Installation ist Lua/Hyprland 0.57. |

Installation und Rückbau: [README](README.md), [Rollback-Anleitung](docs/ROLLBACK.md). Backups und Profile bleiben zur Wiederherstellung erhalten. Die produktive KDE-Session wurde nicht ersetzt.
