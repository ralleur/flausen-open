# Webapps

Spotify wird als eigenes Chromium-Fenster mit Startmenü-Eintrag und dem
Spotify-Icon aus dem vorhandenen Caelestia-Iconset (mit Theme-Fallback `spotify`) geöffnet. Das separate Profil unter
`$XDG_DATA_HOME/flausen-webapps/spotify` (Standard: `~/.local/share/…`) speichert
die Anmeldung. Es werden keine Zugangsdaten im Repository gespeichert.

Voraussetzungen: Chromium unter `/usr/bin/chromium`, KDE/KWin 6, Python 3 mit
`dbus-python` und `PyGObject`, `qdbus6` und für die Menüaktualisierung KDEs
`kbuildsycoca6`. Kein Build nötig.

Installation:

```sh
python3 kde-customizations/webapps/install.py
```

Der Installer sichert einen abweichenden vorhandenen Starter unter
`$XDG_STATE_HOME/flausen-webapps` (Standard: `~/.local/state/…`).
Er verändert keine anderen Webapps oder Browserprofile.

## Integrierte Kopfzeile

Die lokale Manifest-V3-Erweiterung in `spotify-header/` setzt Minimieren,
Maximieren/Wiederherstellen und Schließen rechts in Spotifys vorhandene schwarze
Kopfzeile. Die Knopfmaße und SVG-Geometrie entsprechen
[Dolphin und den gemeinsamen Fensterknöpfen](../window-controls/README.md):
30 px Bedienfläche, 6 px Abstand und 16 px Zeichenfeld. Die Suche und das
Profil behalten eigene Flächen; die native Liedtitelzeile entfällt.

Freie Kopfzeilenflächen dienen zum Ziehen, Doppelklick maximiert oder stellt
wieder her. Rechts unten gibt es eine unsichtbare 10-px-Fläche zum Skalieren.
Das ist eine Chromium-Integration, kein Qt-Plugin: Der native Dolphin-Schatten
und seine abgerundete Fensterkontur werden damit nicht nachgebildet.

Der Installer verlinkt die Erweiterungsquelle als `flausen-header` im separaten
Spotify-Profil und registriert **nur dort** den Native-Messaging-Host.
`--load-extension` lädt die Erweiterung beim nächsten vollständigen App-Start;
ein bereits laufender Chromium-Prozess dieses Profils muss vorher regulär
beendet werden. Anmeldung und Profil bleiben erhalten. Bei Änderungen am
Hintergrundskript dessen Dateinamen aktualisieren, weil Chromium den Service
Worker selbst bei einer geänderten Erweiterungsversion zwischenspeichern kann.

Die Erweiterung fordert ausschließlich `nativeMessaging` an und läuft nur auf
`https://open.spotify.com/`. Der lokale Host findet das konkrete App-Fenster
anhand eines kurzzeitig gesetzten zufälligen Titeltokens und der exakten
Spotify-Fensterklasse. Erst nach erfolgreicher Zuordnung und sichtbaren Knöpfen
wird dessen native Dekoration ausgeblendet. Beim normalen Verbindungsende,
Navigation zu einer anderen Domain oder Beenden des Hosts wird sie restauriert.
Pro Fenster verhindert eine Laufzeitsperre konkurrierende Hosts beim Neuladen.
Eine hart per SIGKILL beendete Bridge kann keine Aufräumaktion ausführen;
gegebenenfalls über `Alt+F3` die Titelleiste wieder einschalten oder Spotify
neu öffnen. Es gibt keine dauerhafte Regel zum Ausblenden von Titelleisten.

Minimieren, Maximieren und Schließen verwenden die
[Chromium-Fenster-API](https://developer.chrome.com/docs/extensions/reference/api/windows).
Die lokale Verbindung verwendet
[Native Messaging](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging);
Fensterzuordnung und Bewegung nutzen die
[KWin-Scripting-API](https://develop.kde.org/docs/plasma/kwin/api/).

Zum Wiederherstellen der zuletzt verwendeten Fenstergröße gibt es die
[Spotify-KWin-Regel](../window-rules/README.md). Diese separat mit der aktuellen
Fenstergröße installieren; danach merkt sich KWin Größenänderungen automatisch.

Prüfung: Der Installer validiert den Starter, sofern `desktop-file-validate`
vorhanden ist. `gtk-launch flausen-spotify` öffnet Spotify. Anmeldung und
Musikwiedergabe müssen mit einem Spotify-Konto in der Sitzung geprüft werden;
der Installer installiert keine zusätzlichen Codecs oder DRM-Module.

Automatische Prüfung der Profilisolation, Wiederinstallation, Konfliktbehandlung
und Nachrichtenrahmung:

```sh
python3 -m unittest discover -s kde-customizations/webapps/tests -v
```

Live geprüft mit Chromium 156 und KWin 6 unter Wayland: integrierte Knöpfe,
Minimieren, Maximieren/Wiederherstellen, Verschieben ohne Positionssprung,
Skalieren rechts unten und Ende der Bewegung nach Loslassen. Neuladen und
Navigation aus Spotify müssen zusätzlich den nativen Rahmen wiederherstellen
beziehungsweise die integrierte Kopfzeile erneut aktivieren.

Rückbau: `$XDG_DATA_HOME/applications/flausen-spotify.desktop` entfernen und
`kbuildsycoca6 --noincremental` ausführen. Das Spotify-Profil bleibt erhalten;
bei gewünschtem vollständigem Rückbau kann es nach Schließen der App separat
entfernt werden.

Nur die Kopfzeile zurückbauen: Spotify schließen, `--load-extension=…` aus dem
Starter entfernen und im Profil `flausen-header` sowie
`NativeMessagingHosts/org.flausen.spotify_header.json` entfernen. Danach
`kbuildsycoca6 --noincremental` ausführen. Die Anmeldung und die separate
KWin-Größenregel bleiben erhalten.
