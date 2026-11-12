# Codex — flausen. Brand Integration (direkt implementieren)

## Auftrag

Du arbeitest an einem Gaming-OS-Projekt, dessen freigegebener Markenname ab jetzt **flausen.** lautet. Der Entwickler hat das ursprüngliche Konzept mit der dreifarbigen Punktmarke, dem klein geschriebenen Schriftzug und dem gelben Schlusspunkt als bevorzugte Identität ausgewählt. Diese Dateien sind keine bloße Inspiration: **verwende die mitgelieferten Assets und Design Tokens als verbindliche Ausgangsbasis.**

Wichtig: Die vorhandene Ralleur/Caelestia-Desktop-Vision soll funktional erhalten bleiben. Die **Desktop-Mocks** sind unter `reference/desktop-light.png` und `reference/desktop-dark.png`; das **Markendesign** unter `assets/logos/` und `preview/brand-board.png`. Der Code soll zu den Bildern hin konvergieren, nicht nur die PNGs anzeigen.

## Arbeitsweise

1. Das aktuelle Repository sowie die Boot-, Login-, Shell-, Installer- und About-Bestandteile **inspizieren**. Keine Annahme, dass es ein frisches Projekt ist.
2. Alle projektspezifischen alten Platzhalternamen **nur dort**, wo sie das neue Gaming-OS bezeichnen, auf **flausen.** umstellen. **Nicht** bestehende Namen anderer Produkte, Repo-URLs, Upstream-Paketnamen oder historische Lizenzangaben automatisiert umbenennen.
3. `BRAND_SPEC.md`, `DESIGN_TOKENS.json` und die gelieferten SVGs integrieren. Technisch immer `flausen-os` oder konventionskonforme Kennungen, sichtbare Darstellung `flausen.`.
4. Die sieben in `DESKTOP_IMPLEMENTATION.md` definierten Komponentenpakete umsetzen bzw. die vorhandene Implementierung vervollständigen. Falls schon umgesetzt: gezielt integrieren statt neu bauen.
5. Es gibt **keine vorgelagerte PoC- oder Planungsphase**: implementieren -> Tests ausführen -> UI prüfen -> korrigieren. Gestalterische Abweichungen nur begründet und dokumentiert, keine neue Namensrunde.
6. Light/Dark auf allen relevanten Systemoberflächen (Boot, Login, Desktop, Launcher, Widgets, About, Installer) konsistent integrieren. Keine starren Fake-Metriken / Fake-Buttons.
7. Soweit die Testumgebung es erlaubt, echte Screenshots von Light-/Dark-Desktop, Boot und Login aufnehmen und gegen die Referenzen vergleichen. Fehlende System-/GPU-Testumgebung ehrlich dokumentieren.
8. Abschluss mit Dateiliste, tatsächlichem Implementierungsstatus, ausgeführten Checks, den Abweichungen zum Mock und kurzen Install-/Rollback-Anweisungen.

## Liefer- und Qualitätskriterien

- SVGs müssen für ihren Anwendungsfall nutzbar sein, PNG-Fallbacks in passender Auflösung erzeugt werden.
- Farbwerte aus `DESIGN_TOKENS.json` als zentrale Quelle verwalten; keine uneinheitlichen Kopien in vielen Dateien.
- Launcher- und Shell-Icons müssen bedienbar sein, die OS-Marke darf in Spiele-Vollbild nicht stören.
- UEFI-/GRUB-/systemd-boot-/Plymouth-Bezug **nur nach Erkennung des tatsächlich eingesetzten Boot-Stacks**. Keine globale Boot-Konfiguration ohne Backup und Berechtigung.
- Login-Branding für realen DM passend (z. B. SDDM nur, falls installiert/gewollt).
- Bereits vorhandene Ralleur-Projektlogos bleiben unangetastet; nur das Gaming-OS wird flausen.
- Caelestia-/KDE-Upstream möglichst unangetastet und updatefähig halten; ggf. Overrides/Extensions.
- Installer und Updates sind einfach und verständlich; keine sichtbare Windows-/Linux-Kompatibilitätsschicht für Spiele, soweit das Projekt dies bereits fordert.
- Dateien nicht vorschnell löschen, bestehende Nutzerkonfiguration vorher sichern, Rollback ermöglichen.
- Keine Lizenz- oder Trademark-Verfügbarkeit behaupten; vor öffentlichem Release ist Name/Trademark/Domain noch zu prüfen.

## Prioritäten

**P0:** Name, Logo, Design Tokens, About/Systemdarstellung, Launcher-Branding, Theme-Integration.
**P1:** Boot/Lock/Login, Installer/ISO-/USB-Branding, Microinteractions.
**P2:** Sorgfältiger visueller Feinschliff und responsive, zugängliche Darstellung.

## Lies in dieser Reihenfolge

`README.md` -> `BRAND_SPEC.md` -> `DESIGN_TOKENS.json` -> `DESKTOP_IMPLEMENTATION.md` -> `ACCEPTANCE.md` -> `CODEX_TASK.md` -> visuelle Referenzen.

Wenn du bereits die vorherige Ralleur-Caelestia-Übergabe bearbeitest: **dieses Briefing überschreibt deren Brandbenennung und Logo-Platzhalter, aber nicht ihre funktionalen Desktop-Anforderungen**.
