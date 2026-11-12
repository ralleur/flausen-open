# App-spezifische Fensterregeln

Discord wird über `lab-discord.desktop` als Chromium-App gestartet. Eine eng
auf `chrome-discord.com__app-Default` beschränkte KWin-Regel merkt sich seine
zuletzt verwendete Fenstergröße (`sizerule=4`, Remember). Die Größe wird nur
beim Öffnen angewendet; das Fenster bleibt frei skalierbar. Andere Chromium-
Fenster und Discord-Clients werden nicht erfasst.

Spotify erhält dieselbe Merkregel, beschränkt auf
`chrome-open.spotify.com__-Default`. Beide Installer verwenden dieselbe
Implementierung und verwalten getrennte Größenwerte.

Voraussetzungen: KDE/KWin 6, Python 3, `kreadconfig6`, `kwriteconfig6`, `qdbus6`.
Kein Build nötig. Beim ersten Installieren die aktuelle Fenstergröße übergeben:

```sh
python3 kde-customizations/window-rules/install_discord_size.py --size 1325,936
python3 kde-customizations/window-rules/install_spotify_size.py --size 1027,801
```

Weitere Aufrufe können ohne `--size` erfolgen und erhalten den inzwischen von
KWin gemerkten Wert. Eine Sicherung der bisherigen `kwinrulesrc` liegt unter
`~/.local/state/flausen-window-rules/`. Der Installer erhält alle anderen Regeln.

Prüfung in der Sitzung: Die jeweilige App frei skalieren, schließen und wieder öffnen.
Die zuletzt verwendete Größe soll wiederhergestellt werden. Die Installation
schließt kein laufendes App-Fenster. Ein maximiertes Fenster wird durch
KWin separat behandelt; diese Regel speichert die normale Fenstergröße.

Rückbau: Gruppe `flausen-discord-size` beziehungsweise `flausen-spotify-size`
aus `~/.config/kwinrulesrc` entfernen und
deren Eintrag aus `[General] Order` löschen. Danach
`qdbus6 org.kde.KWin /KWin reconfigure` ausführen. Eine vollständige Sicherung
nur zurückspielen, wenn spätere Änderungen an anderen Regeln entfallen dürfen.
