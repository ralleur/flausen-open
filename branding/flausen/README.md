# flausen. — verbindliche Produktidentität

Die Produktmarke heißt **flausen.**: immer klein und mit Punkt.
Die Positionierung lautet **„An everyday OS for work, creativity and play.“**
Gaming ist eine von mehreren Stärken des vielseitigen Alltags-Desktops. Die technische Produktkennung ist `flausen-os`. **ralleur** bleibt die
Muttermarke, im Produkt als „by ralleur“. Claim: „Your computer. Your playground.“

Die unveränderte Übergabe liegt unter `handoff/`; sie ersetzt ältere
OS-Namensvorgaben. Maßgeblich sind `handoff/BRAND_SPEC.md`,
`handoff/DESIGN_TOKENS.json` und die pfadbasierten Produktionslogos.
Repository-Ordner, Benutzername, Hostname, interne IPC-Namen, Upstream-Namen und
historische Lizenzangaben werden nicht pauschal umbenannt.

## Umgesetzt und installiert

- Markenassets einschließlich SVGs, PNG-Fallbacks, Referenzmocks und Credits im Repo.
- `generate.py` erzeugt aus den zentralen Tokens die JS-Bindings,
  `generated/identity.json` und zwei optionale Caelestia-Paletten. Die Kopie
  `kde-customizations/session-style/shared/FlausenBrand.js` ist generiert.
- Das vorhandene, geprüfte Caelestia-Feld `general.logo` lädt das originale
  Dreipunktsymbol. Keine Änderungen an den Shell-Upstream-Dateien.
- „Über flausen.“ ist als echte App im Startmenü installiert: Logo, Claim,
  Entwicklungsstatus, Parent-Credit, lokale Systemdetails und Credits. Keine
  erfundene Release-Version. Hell/Dunkel folgt der Systempalette.
- Der vorhandene Plasma-Sperrbildschirm verwendet die Produktmarke und die
  zentralen Farben beim nächsten Sperren; Authentifizierung bleibt nativ.
- Der Plasma-Login-Greeter ist mit denselben Brandassets neu gebaut und im
  Testmodus geprüft. **Noch nicht systemweit installiert.** Der reproduzierbare
  Quellpatch liegt in `kde-customizations/session-style/prepare.py`.

Der aktive Aufbau bleibt **KDE/KWin mit Caelestia**, kein Wechsel auf Hyprland.
Das frühere `ralleur-desktop/` bleibt als separater, inaktiver Hyprland-Aufbau
bestehen. Parent-Logos werden erhalten, insbesondere auch das eigenständige
ralleur-Screensaver-Projekt.

## Installation und Rückbau

Im Projektstamm:

```sh
python branding/flausen/generate.py
python branding/flausen/install.py
python kde-customizations/session-style/install-lock.py
```

`install.py` schreibt ausschließlich Benutzerdateien nach
`~/.local/share/flausen-os/branding`, App- und Icon-Einträge sowie das Logo-Feld
in `~/.config/caelestia/shell.json`. Vorheriger Zustand liegt unter
`~/.local/state/flausen-os/branding-<Zeitstempel>`. Andere Einstellungen werden
beim Rückbau erhalten; nachträgliche Änderungen an verwalteten Dateien oder
am Logo verhindern ein Überschreiben. Für Asset-Updates zuerst zurückbauen,
dann neu installieren. Quell- und Installationsverzeichnis bleiben getrennt.

```sh
python branding/flausen/install.py --restore
python kde-customizations/session-style/install-lock.py --restore
```

Der zweite Befehl stellt die Präsentation vor der ersten Session-Style-Installation
wieder her. Die genaue Darstellung unmittelbar vor diesem Branding-Schritt liegt
zusätzlich unter `~/.local/state/ralleur-desktop-tweaks/session-style-lock-20261102-113218-302853`.
Der vorhandene [Session-Style-Workflow](../../kde-customizations/session-style/README.md)
beschreibt den gesonderten Build, die Installation und den Rückbau des Login-Managers.
Der neu geprüfte Greeter liegt lokal unter `.cache/plasma-login-build/bin/plasma-login-greeter`.
Systemweite Installation ist hier nicht erfolgt.

## Status der sieben Desktop-Pakete

| Paket | Stand dieses Namensauftrags |
|---|---|
| Wallpapers | Vorhandene Wallpaper erhalten; Mock-PNGs nur Referenz |
| Desktop-Rahmen | Bestehender KDE-/Caelestia-Aufbau erhalten |
| Navigation | Produktlogo live eingebunden; vorhandene Aktionen erhalten |
| Widgets | Bestehende reale Datenquellen erhalten |
| Fensterverhalten | Bestehende KWin-/Tiling-/Fullscreen-Regeln erhalten |
| Apps | Neue About-App; keine globale Umfärbung fremder Apps |
| OS-Oberflächen | Lock aktiv; Login gebaut/geprüft; Boot/Installer noch offen |

Die zwei generierten Caelestia-Paletten unter `generated/schemes/flausen/default/`
sind **nicht aktiviert oder visuell systemweit abgenommen**. Das aktuell gewählte
Desktop-Farbschema bleibt erhalten. Boot-Motive unter `handoff/assets/flausen-boot-*`
sind weiterhin statische Designkonzepte. Plymouth ist installiert; es wurde kein
neues Boot-Theme aktiviert, kein initramfs gebaut und keine Bootkonfiguration
geändert. Installer-/ISO-Branding, `/etc/os-release` und Release-Versionierung
sind noch keine Umsetzung dieser Benutzerintegration.

## Tatsächliche Prüfungen

- Mitgelieferte Asset-Prüfung: 12 SVGs, 16 PNGs und JSON/Dokumente gültig.
- Vier Installer-Tests: Rückbau, Erhalt anderer Einstellungen, Schutz manueller
  Änderungen sowie Rückabwicklung bei Schreibfehlern bestanden.
- Zwei bestehende Session-Installer-Tests bestanden.
- About-QML ohne qmllint-Warnungen, native Renderprüfung Hell/Dunkel.
- Plasma-Login-Manager-Build erfolgreich (vorhandene Upstream-C++-Warnungen).
- Vier native Lock-/Login-Renderprüfungen ohne Ladefehler; beide Login-Fehler-
  und Wiederholungsprüfungen gegen das Mock-Backend bestanden.
- Aktive Topbar auf einem echten Desktop-Screenshot kontrolliert: Symbol mit
  drei Originalfarben sichtbar. Der Screenshot mit privaten App-Inhalten wird
  nicht als Projektartefakt aufbewahrt.

Screenshots und maschinenlesbares Ergebnis: `evidence/about-{light,dark}.png`
und `evidence/session/verification.json`. Das sind native UI-Testaufnahmen,
keine Nachweise einer echten Anmeldung oder eines Bootvorgangs. Der Desktop
wurde für diesen Namensauftrag nicht erneut über alle Displayformate hinweg
gegen die vollständigen Mocks abgenommen. Echtes Booten/Entschlüsseln,
Login-Authentifizierung, HDR/Gaming und systemweite Theme-Umschaltung sind
hier nicht neu getestet.

Für eine öffentliche Veröffentlichung bleibt die im Handoff geforderte
Namens-, Marken- und Domainprüfung offen; es wird keine Freigabe behauptet.

## Neues kinetisches Symbol am Startknopf

Der Startknopf verwendet inzwischen ausschließlich den orangefarbenen Keil aus
dem neuen Website-Logo anstelle des Dreipunktzeichens. Installation, gezielter Rückbau und Nachweis:
[kinetic/README.md](kinetic/README.md). Die übrigen OS-Markenflächen sind davon
unabhängig.

Die Über-Seite verwendet den gemeinsamen [Sprachinstaller](../../kde-customizations/localization/README.md). Diesen nach der Branding-Installation ausführen; der Starter liest danach KDEs aktuelle Sprache, unabhängig von der Sprache älterer Sitzungsprozesse.
