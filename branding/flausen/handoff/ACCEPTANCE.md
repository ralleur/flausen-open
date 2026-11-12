# flausen. — Abnahmecheckliste

## Marke & Assets

- [ ] Hauptlogo `flausen.` (klein, inkl. gelbem Schluss-Punkt) auf hell/dunkel korrekt.
- [ ] Drei Kreise: gelb größer, korall + blau kleiner, originaler Farbcode und Reihenfolge.
- [ ] Kein Überschreiben des echten Ralleur-Parent-Logos oder der anderen Ralleur-Produkte.
- [ ] Symbole bei 24/32/64/128px und Lockup bei realistischen Größen geprüft.
- [ ] Pfad-SVG und PNG-Fallback in Boot-/Login-Umgebung validiert.
- [ ] Guter Kontrast in beiden Themes; Reduced Motion unterstützt.

## OS-Oberflächen

- [ ] Branding in Launcher, About/Settings, Login/Lock, Boot, Installer/USB sofern relevante Komponenten im Repo vorhanden.
- [ ] Systemmeldungen/Updates übernehmen passende Tonalität und konsistente UI-Tokens.
- [ ] Keine gefälschten Systemdaten, statischen Uhrzeit- oder Musikwerte in funktionalen Widgets.
- [ ] Fullscreen-/Gaming-Umgebungen ohne überlagernde Shell-Elemente.
- [ ] Keine unangemeldeten Änderungen an Root-/Boot-Konfiguration.
- [ ] Einfache Installation, Backup und Rollback sind vorhanden.

## Desktop

- [ ] Desktop-Light/Dark kompositorisch gegen `reference/desktop-light.png` und `reference/desktop-dark.png` geprüft.
- [ ] Desktop funktioniert auf 16:10 und Ultrawide; kleine Displays schalten Widgets sinnvoll weg.
- [ ] Hyprland/Caelestia-Versionen/Kompatibilität geprüft; KDE nicht implizit ersetzt.
- [ ] Unterschiede zwischen Design-Mock und tatsächlichem Verhalten sind dokumentiert.

## Qualität

- [ ] Logo-XML und Token-JSON syntaktisch gültig, Bildexports öffnen und sind nicht leer.
- [ ] Projektbezogene Shell-/Build-/Lint-/Startchecks durchgeführt.
- [ ] Implementierte vs. noch offene Bereiche klar benannt.
- [ ] Externe Assets/Lizenzen korrekt ausgewiesen, keine Font-Binaries beigefügt.
- [ ] Öffentliche Namens-/Markenfreigabe als eigener, noch offener Schritt behandelt.
