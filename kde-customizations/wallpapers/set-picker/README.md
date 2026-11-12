# Drei Wallpaper-Sets im Caelestia-Konfigurator

Die Seite „Hintergrund auswählen“ bietet unter der Vorschau eine umbrechende, per Tastatur
bedienbare Set-Auswahl:

- `ralleur set`: `~/Bilder/Wallpapers/ralleur-4k/png` (15 Bilder).
- `flausen dark`: `~/Bilder/Wallpapers/flausen-4k/dark/png` (24 Bilder).
- `flausen light`: `~/Bilder/Wallpapers/flausen-4k/light/png` (24 Bilder).

Die Auswahl schreibt den vorhandenen Schlüssel `paths.wallpaperDir` über
`GlobalConfig.save()`. Sie stellt Bildliste, Set-Vorschau, Ordneraktion und die
Quelle für Zufall/Diashow um. Das sichtbare Desktopbild wechselt erst beim
Auswählen eines Bildes oder durch die bestehenden Zufall-/Diashow-Aktionen.
Die Set-Auswahl selbst verändert Diashow-Intervall und -Modus nicht.
Die aktuelle Settings-Oberfläche steuert den automatischen Wechsel über
„Random: on/off“ und bietet das Intervall direkt darunter an; manuelle
Bildauswahl stoppt die Diashow. Quelle und Installation dieser Oberfläche:
[Settings](../../settings/README.md#wallpaper-wechsel-direkt-bei-der-auswahl). Individuelle Bilder lassen
sich weiterhin über „Durchsuchen“ öffnen; ein eigener Ordnerwert bleibt bis zur
expliziten Auswahl eines Sets erhalten.

`services/Wallpapers.qml` verwirft beim asynchronen Ordnerwechsel sofort noch
vorhandene Einträge aus dem alten Ordner. So kann Zufall nicht versehentlich
auf das vorherige Set zugreifen. Bei leerer Liste ist der Zufallsknopf deaktiviert.
Die bestehende Farbfilter-Timerreferenz und ein undefinierter boolescher Wert
wurden korrigiert; Transparenz wird über den Alpha-Wert geprüft.

## Installation und Rückbau

```sh
python3 kde-customizations/wallpapers/set-picker/install.py
systemctl --user restart caelestia-shell.service
```

Der Installer prüft `../set-picker.patch` vorab und sichert beide QML-Dateien
sowie die vorherige Konfiguration. Sicherungspfad: `evidence/backup.txt`.
Zum Rückbau ausschließlich die beiden gesicherten Dateien relativ zum
Shell-Verzeichnis `~/.config/quickshell/caelestia` zurückkopieren:

- `modules/nexus/pages/wallandstyle/WallpaperSelect.qml`
- `services/Wallpapers.qml`

Danach die Shell neu starten. Der zuletzt gewählte Wallpaper-Ordner kann bestehen
bleiben; wenn nötig nur `paths.wallpaperDir` aus der gesicherten `shell.json`
übernehmen, keine neueren anderen Einstellungen überschreiben.

## Prüfung

Bei Einführung der Set-Auswahl in der laufenden Shell alle drei Sets geladen, Bildlisten vollständig gegen die
Ordner verglichen (16/24/24), Vorschaupfade und gespeicherten Ordner geprüft.
Zufall und sequenzieller Wechsel blieben im jeweiligen Set. Auswahl über einen
Shell-Neustart geprüft. Danach ursprüngliches Set und ursprüngliches Desktopbild
wiederhergestellt. Keine QML-Fehler der betroffenen Komponenten im abschließenden
Lauf. Keine physischen Maus-/Tastatureingaben automatisiert; die UI-Aktionsfunktion
wurde für die Prüfung über einen temporären IPC-Zugang aufgerufen. Dieser Zugang
ist im endgültigen Code entfernt. Protokoll: `evidence/check.json`.
