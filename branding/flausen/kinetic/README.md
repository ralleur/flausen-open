# Kinetisches Symbol am Startknopf

Am Startknopf steht ausschließlich der orangefarbene Keil (#E56D2F) aus der
Website-Komposition. Sein SVG-Pfad ist unverändert aus
`website/src/geometry.json` (`orange-wedge`) übernommen. Ein quadratischer
Ausschnitt (260 × 260 SVG-Einheiten) mit proportionaler Skalierung erhält
Form und Seitenverhältnis. Der zusätzliche Innenabstand hält auch die obere
Keilspitze vom runden Buttonrand fern.
Die kompakte Symbolvorlage enthält eine abweichende Keilzeichnung und wird
für diesen Startknopf deshalb nicht verwendet. Das vollständige kompakte Logo
bleibt in `flausen-symbol.svg` erhalten.

Installiert über den unterstützten Schlüssel `general.logo` in
`~/.config/caelestia/shell.json`. Die aktive Symbolgröße beträgt ungefähr 32px;
`recolourCustomLogo=false` erhält das originale Orange. Die vorhandene runde
Schaltfläche und ihre Aktionen bleiben erhalten. Keine QML-Änderung erforderlich.

```sh
python3 branding/flausen/kinetic/start-button.py
systemctl --user restart caelestia-shell.service
```

Rückbau ausschließlich dieser Logo-Änderung:

```sh
python3 branding/flausen/kinetic/start-button.py --restore
systemctl --user restart caelestia-shell.service
```

Das Skript sichert die vorherige Konfiguration unter
`~/.local/state/flausen-os/kinetic-start-button/`. Beim Rückbau wird nur der
vorherige Logo-Wert eingesetzt; andere aktuelle Einstellungen bleiben erhalten.
Ein zwischenzeitlich geänderter Logo-Wert verhindert den Rückbau. Vor dem älteren
Branding-Gesamtrückbau zuerst diese Änderung zurückbauen.

Live geprüft: Shell läuft nach Neustart; Screenshot zeigt den einzelnen orangefarbenen Keil.
Vorher/Nachher-Ausschnitte: `../evidence/kinetic-start-button/`.
