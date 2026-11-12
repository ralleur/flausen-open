# Ralleur Desktop

Modulares Ricing für **die originale Caelestia Shell + Hyprland**, mit Light/Dark, eigenständigen SVG-Wallpapers, Topbar, Dock, Uhr, MPRIS und echten Systemmetriken. Die bestehende KDE-/Caelestia-KDE-Installation wird nicht ersetzt. Quellcode und Installationsdateien stehen vollständig in diesem Verzeichnis.

**Stand der Abnahme:** Implementiert und funktional in verschachteltem Hyprland geprüft. Beide Themes wurden als produktive QML-Komponenten in fünf Größen gerendert und mit den Mocks verglichen. Eine vollständige visuelle Freigabe auf einer physischen Hyprland-Session steht aus: der verschachtelte NVIDIA-/Screencopy-Pfad wurde im Test unzuverlässig. Details und ehrliche Testgrenzen: [IMPLEMENTATION.md](IMPLEMENTATION.md), [visueller Vergleich](docs/VISUAL_REVIEW.md).

## Installation

Benötigt werden Hyprland (getestet: 0.57.0), Quickshell (getestet: 0.3.2), Python ≥3.13, Qt 6 ≥6.9, eine native Terminal-, Browser- und Dateimanager-Anwendung sowie die Caelestia-Build-Abhängigkeiten. Auf CachyOS/Arch gehören dazu insbesondere `cmake`, `ninja`, `gcc`, `git`, `pkgconf`, `qt6-base`, `qt6-declarative`, `qt6-shadertools`, `qt6-svg`, `qt6-multimedia`, `libqalculate`, `pipewire`, `aubio`, `cava`, `lm_sensors`. Für die volle Standard-Shell: `fish`, `ddcutil`, `brightnessctl`, `networkmanager`, `power-profiles-daemon`, Material Symbols und die vom Upstream empfohlenen Hilfsprogramme. Für dieses Design: **Inter** (`inter-font`), Breeze-Icons, `qt6ct`; für Dolphin das KDE-Plattformtheme. Empfohlen: Kitty, Firefox oder Chromium, Dolphin oder Thunar, mpv. Es werden keine Systempakete automatisch installiert und keine Fontdateien mitgeliefert.

Für mpv als steuerbaren MPRIS-Player zusätzlich `mpv-mpris` installieren. Andere MPRIS-fähige Player werden automatisch erkannt. Ohne einen solchen Dienst zeigt die Karte den korrekten Empty State.

```bash
cd /home/USER/ralleurOS/ralleur-desktop
./bin/ralleur doctor
./bin/build-upstream
```

Der Builder lädt die in [upstream.lock.json](config/upstream.lock.json) festgeschriebenen originalen Caelestia-, CLI- und M3Shapes-Versionen. Er baut ohne Root in private Verzeichnisse und gibt den passenden Installationsbefehl aus. Bei Standard-XDG-Pfaden lautet er:

```bash
./bin/ralleur install \
  --upstream "$HOME/.cache/ralleur-desktop/upstream/shell" \
  --plugin-prefix "$HOME/.local/share/ralleur-caelestia-runtime/v2.5.0" \
  --dry-run

# Gleicher Befehl ohne --dry-run installiert mit vorheriger Sicherung.
./bin/ralleur install \
  --upstream "$HOME/.cache/ralleur-desktop/upstream/shell" \
  --plugin-prefix "$HOME/.local/share/ralleur-caelestia-runtime/v2.5.0"
```

In diesem Workspace liegt zusätzlich bereits der vollständig getestete Build vor. Er kann direkt verwendet werden:

```bash
./bin/ralleur install \
  --upstream /home/USER/ralleurOS/.cache/repro/shell \
  --plugin-prefix /home/USER/ralleurOS/.cache/runtime-repro
```

Das Release-Archiv enthält auch unveränderte Kopien der beiden Handoff-Referenz-PNGs als Vergleichsmaterial neben dem Quellverzeichnis; diese werden nicht installiert.

Danach **in einer eigenen Hyprland-Session**, beispielsweise von einer TTY nach regulärer Abmeldung:

```bash
Hyprland --config "$HOME/.config/ralleur-desktop/hyprland.lua"
```

Das schaltet keine laufende KDE-Session um. Es werden weder Displaymanager noch Login-Auswahl oder Autologin verändert. Wer bereits Hyprland nutzt, kann die erzeugte Lua-Datei kontrolliert in seine eigene Konfiguration einbinden; vorher selbst sichern. Nicht gleichzeitig zwei Caelestia-Shells auf demselben Display starten.

Mit dem privaten Hyprland-Runtime neben dem Plugin-Prefix kann der installierte Desktop auch über `ralleur-desktop desktop` gestartet werden. Innerhalb einer laufenden Sitzung öffnet sich eine eigene verschachtelte Hyprland-Sitzung mit getrennter D-Bus-Verbindung und Skalierung 1; aus einer TTY startet eine native Sitzung mit automatischer DPI-Wahl. Der vorhandene Compositor wird dabei nicht beendet. Der Laufzeitstatus liegt unter `~/.local/state/ralleur-desktop/desktop.log`.

## Bedienung

| Aktion | Shortcut / Befehl |
|---|---|
| Caelestia-Launcher | Super+Leertaste; Logo / Dock-Punkte |
| Workspace | Super+1…9; Topbar |
| Fenster auf Workspace verschieben | Super+Shift+1…9 |
| Terminal / Dateien / Browser | Super+Return / Super+E / Super+B |
| Light ↔ Dark | Super+Shift+T; Dock ◐; `ralleur-desktop theme toggle` |
| Widget-Spalte / kompakte Sidebar | Super+W; Topbar ◫ |
| Fullscreen / Floating | Super+F / Super+V |
| Verschieben / Skalieren | Super+linke / rechte Maustaste |
| Caelestia-Einstellungen | Dock ⚙; `ralleur-desktop ipc settings` |
| Session-Menü | Dock ⏻; `ralleur-desktop ipc session` |
| Bewusstes Mock-Beispiellayout | `ralleur-desktop demo` |

`demo` öffnet **echte Apps** auf einer neuen benannten Arbeitsfläche und ordnet nur diese neuen Fenster an. Vorhandene Fenster auf `ralleur-demo` werden nicht überschrieben. Bei schmalen Displays bleibt das normale Tiling aktiv. Außerhalb dieser bewusst gestarteten Demonstration gibt es keine starren App-Fensterregeln.

Ab 1500×650 **logischen** Pixeln wird rechts Platz für die Widgets reserviert. Darunter bleibt die Sidebar standardmäßig geschlossen; das explizite Öffnen legt sie vorübergehend über Fenster. Die Sichtbarkeit der großen Spalte und der kompakten Sidebar ist getrennt, damit ein Größenwechsel keine Sidebar unerwartet öffnet. Alle eigenen sichtbaren Oberflächen weichen Fullscreen-Fenstern auf dem jeweiligen Monitor.

## Themes und Apps

`design/tokens.json` ist die Farb-, Geometrie-, Typografie- und Effektquelle. `bin/generate.py` erzeugt daraus die nativen Theme-Dateien und Wallpaper. Änderungen danach mit `./bin/ralleur generate` und erneuter Installation übernehmen.

- Shell, Wallpaper, Caelestia-Palette und Kitty-Farben wechseln ohne Shell-Neustart. Kitty erhält nach dem Shell-Startup und beim Umschalten einen eigenen Farbsatz, auch wenn Shell-Startdateien OSC-Farben senden.
- GTK 3/4 verwenden native Einstellungen und CSS; Qt verwendet qt6ct/Fusion. Dolphin verwendet gezielt das native KDE-Plattformtheme und das erzeugte KColorScheme.
- Firefox erhält ein **eigenes** Profil mit `user.js`/`userChrome.css`; Chromium erhält ebenfalls ein eigenes Profil. Browser- und GTK-/Qt-Chrome können einen App-Neustart benötigen. Website-Inhalte werden nicht umgefärbt. Die echte ralleur.com ist derzeit dunkel gestaltet und unterscheidet sich inhaltlich deutlich vom Mock.
- Dock-Aktionen fokussieren vorhandene passende Fenster oder starten eine verfügbare App. Fehlt eine App, erscheint eine verständliche Meldung. Musik fällt auf mpv zurück. Launcher und native Einstellungsdialoge bleiben Caelestia-Komponenten.

Eigene Startbefehle werden als Argumentlisten in `~/.config/ralleur-desktop/apps.json` hinterlegt, z. B. `{"browser": ["firefox", "--new-window", "https://ralleur.com"]}`. Eigene Monitor-/Tastaturregeln gehören in `local.lua`; beide Dateien werden bei einer erneuten Installation erhalten. Zusätzliche Fensterklassen für Dock-Fokus stehen getrennt in `qml/AppCatalog.qml`. Deutsche Tastatur ist vorbelegt; mit `hl.config({ input = { kb_layout = "us" } })` in `local.lua` ändern.

Native Caelestia-Präferenzen außerhalb der designrelevanten Bereiche werden beim Upgrade übernommen. Bar, Border, Background, Appearance und die Ralleur-Start-/Fullscreen-Vorgaben werden aus dem Design neu erzeugt. Für Ralleur-Farben und Wallpaper den Ralleur-Schalter bzw. die Tokens verwenden; die allgemeinen Upstream-Paletten-/Wallpaper-Seiten in Nexus sind kein zweites synchronisiertes Ralleur-Theme-System.

## Isolation, Sicherung und Rückbau

| Ort | Inhalt |
|---|---|
| `~/.local/share/ralleur-desktop` | installierte Kopie dieser Erweiterung |
| `~/.config/ralleur-desktop` | eigene Session-Konfiguration, `local.lua`, App-Zuordnung |
| `~/.local/state/ralleur-desktop` | Theme-Zustand, App-Daten/-Caches, Profile, Laufzeitverknüpfungen |
| `~/.local/state/ralleur-desktop-backups/<Zeitstempel>` | Zustand aller verwalteten Ziele vor jeder Installation |
| `~/.local/bin/ralleur-desktop` | einziger globaler Benutzer-Entrypoint |

XDG-Variablen werden berücksichtigt. Für Tests lassen sich `RALLEUR_CONFIG`, `RALLEUR_DATA`, `RALLEUR_STATE` und `--bin-dir` setzen. App-Einstellungen werden innerhalb der eigenen Session geschrieben; es gibt keine schreibbaren Durchreich-Symlinks in produktive App-Konfigurationen. Kleine vorhandene App-Präferenzen werden einmal kopiert, danach in der isolierten Session erhalten. Upstream-Quellcode und Plugin-Prefix bleiben separat.

```bash
# Zuerst die Ralleur-Hyprland-Session regulär verlassen.
ralleur-desktop rollback
```

Bei nachträglich geänderten verwalteten Dateien verweigert der Rückbau das Überschreiben. `rollback --force` sichert diesen aktuellen Zustand zusätzlich als `before-rollback`, bevor der frühere Zustand wiederhergestellt wird. Eine schon vor Installation bestehende Entrypoint-Datei wird restauriert. Backups und App-Daten bleiben erhalten. Vollständige Anleitung: [docs/ROLLBACK.md](docs/ROLLBACK.md).

## Überprüfung und Entwicklung

```bash
RALLEUR_TEST_UPSTREAM="$HOME/.cache/ralleur-desktop/upstream/shell" \
  python -m unittest discover -s tests -v

# Produktionskomponenten mit echten Daten rendern; benötigt Pillow.
python tests/render_matrix.py --out evidence

# In einer bewusst gestarteten Testsitzung mit Kitty und echtem MPRIS-Player:
python tests/live_check.py \
  --shell "$HOME/.config/ralleur-desktop/session/quickshell/caelestia/shell.qml" \
  --cli "$HOME/.local/share/ralleur-desktop/bin/ralleur" --out evidence
```

`live_check.py` wechselt Test-Workspaces, Themes und Fullscreen und steuert den aktiven Player. Dafür eine separate Testsitzung verwenden. `--skip-capture` prüft weiterhin Zustände und entfernte Layer, protokolliert den Screenshot aber ausdrücklich als nicht ausgeführt. Die Vorschau `./bin/ralleur preview` zeigt nur die echten Ralleur-QML-Komponenten; sie ersetzt keine Caelestia-/Hyprland-Session und enthält keine nachgebauten App-Fenster.

Upstream-Lizenz GPL-3.0, eigener Code GPL-3.0; Markenassets separat, siehe [THIRD_PARTY.md](THIRD_PARTY.md). Die ursprünglichen Handoff-Dateien und Referenz-PNGs bleiben unverändert.
