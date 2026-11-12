# Menügestaltung im Desktop-Projekt

Bei künftigen Änderungen an KDE-/Caelestia-Menüs und Popovers unter
`kde-customizations/` zuerst [MENU_DESIGN.md](kde-customizations/MENU_DESIGN.md)
lesen und dessen Proportionsregeln anwenden. Diese Regeln wurden mit dem Nutzer
am Update-Menü anhand seiner Referenz-Mocks abgestimmt.

- Referenz und Umsetzung vor einem Urteil auf dieselbe **äußere Breite** bringen.
- Schrift, Icons, Zeilenhöhe und Innenränder getrennt abstimmen; nicht alles
  gemeinsam skalieren. Große Schrift ersetzt keine klare Hierarchie.
- App-Icons optisch groß lassen, Beschriftungen ruhig halten; Titel ca. 1,65-mal
  Haupttext, Nebenzeilen ca. 0,8-mal Haupttext. Bedienflächen ausreichend groß halten.
- Ein konsistentes Raster für Karten, Textspalten und Statussymbole verwenden;
  zusammengehörige Elemente enger als verschiedene Gruppen setzen.
- Kopfaktionen an der Titelzeile ausrichten, nicht am gesamten Titel-/Untertitelblock.
- Reale Ansicht bei gleicher Breite visuell prüfen. Die Vorgaben sind ein
  Ausgangspunkt; Lesbarkeit, Inhalt und ausdrückliche Nutzerwünsche gehen vor.
- Andere Menüs nicht ohne Auftrag nachträglich umbauen.

Für Schrift und Material ist inzwischen das Startmenü die gemeinsame Referenz.
`MenuStyle` und `MenuText` aus `kde-customizations/taskbar/menu-style/` verwenden:
Systemschrift (aktuell Noto Sans), Haupttext 16 px, Neben-/Kleintext ca. 13/12 px.
Keine weiteren individuellen Schrift-/Glasprofile pro Menü einführen. Beim Angleichen
von Schrift oder Material die erarbeiteten Kartenpositionen und Geometrien erhalten;
KWin-Blur nicht pauschal global verändern.

# Repository-Organisation

Bei strukturellen Änderungen [docs/structure.md](docs/structure.md) und
[docs/development.md](docs/development.md) beachten. Der aktive Desktop bleibt
KDE/KWin mit Caelestia; `ralleur-desktop/` ist der separate frühere Hyprland-Aufbau.
Vorhandene Quellen einmal pflegen und referenzieren, statt sie in neue
Produktverzeichnisse zu kopieren. Neue direkte Komponenten unter
`kde-customizations/` in `installation/components.json` registrieren und
`./bin/flausen check` ausführen. Installation, Systemdefinition und Auslieferung
haben eigene Bereiche; deren dokumentierten Entwicklungsstand ehrlich erhalten.
