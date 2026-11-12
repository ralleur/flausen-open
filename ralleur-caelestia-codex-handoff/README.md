# Ralleur × Caelestia — Codex-Übergabepaket

**Ziel:** Ein funktionsfähiges, installierbares Linux-Desktop-Ricing, visuell orientiert an den zwei beigefügten Mocks und an der echten Ralleur-Markenidentität von https://ralleur.com.

## Inhalt

- `reference/desktop-light.png` – verbindliche visuelle Zielreferenz für den hellen Zustand.
- `reference/desktop-dark.png` – verbindliche visuelle Zielreferenz für den dunklen Zustand.
- `CODEX_TASK.md` – der eigentliche Arbeitsauftrag für Codex; **zuerst lesen**.
- `DESIGN_SPEC.md` – Zerlegung in sieben Module, Designanforderungen und responsive Verhalten.
- `ACCEPTANCE.md` – prüfbare Fertigstellungskriterien und Testmatrix.
- `DESIGN_TOKENS.reference.json` – unverbindliche Startwerte für Farben/Geometrie (aus der visuellen Richtung abgeleitet; keine extrahierten Original-Brand-Tokens).
- `SHA256SUMS` – Dateiprüfsummen der Originalreferenzen.

## Übergabe in eine Codex-Session

1. Das ZIP in die Codex-Session hochladen **oder** in das Zielrepo entpacken.
2. Codex sagen: `Lies CODEX_TASK.md und implementiere das Ralleur-Caelestia-Ricing aus diesem Paket. Nutze reference/desktop-light.png und reference/desktop-dark.png als visuelle Zieldefinition. Direkt implementieren, prüfen und korrigieren; keine vorgeschaltete PoC- oder Planungsrunde.`
3. Falls noch kein Repo existiert, im neu anzulegenden Repo arbeiten. Falls es ein CachyOS-Gaming-Spin-Repo ist, dieses Ricing als separates, optionales Theme/Profil integrieren und vorhandene Spiel-/Boot-Funktionalität unangetastet lassen.

## Ziel vs. Illustration

**Verbindlich:** Charakter, Farbwirkung, Layering, Geometrie, Proportionen, Dock, Statusleiste, Widgets, Fensterdesign und stimmige Light/Dark-Varianten. Diese Referenzen sind Designziele, **keine** fertig umsetzbaren Assets für Wallpaper oder UI.

**Nicht verbindlich:** Die dargestellte Browserwebsite, Demo-Werte in Terminal/Uhr/CPU-Anzeigen, die fiktive Beispiel-Musik, konkrete Dateinamen und die exakte Anzahl sichtbarer Fenster. Produktive Widgets müssen echte Daten anzeigen. Die Fensterlayouts sind eine repräsentative Beispielsituation, nicht die einzig zulässige Anordnung.

**Wichtig:** Das generierte Logo im Mock ist nicht die echte Ralleur-Marke. Echte Brand-Assets von ralleur.com bzw. dessen Originalquellen verwenden, nicht aus dem Mock abpausen. Keine Markenlogos, Fonts oder fremden App-Assets ungeprüft aus Screenshot-Pixeln reproduzieren.

## Upstream

- Caelestia Shell: https://github.com/caelestia-dots/shell
- Caelestia Dotfiles: https://github.com/caelestia-dots/caelestia
- Brand-Referenz: https://ralleur.com

Caelestia Shell ist auf Quickshell/QML und Hyprland ausgerichtet. Konfigurationsorte und APIs jeweils gegen die **tatsächlich installierte Version** prüfen. Nicht blind Vollbeispiel-Konfigurationen kopieren oder Upstream-Pfade überschreiben.
