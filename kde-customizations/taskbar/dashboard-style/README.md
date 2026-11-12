# Dashboard am oberen Bildschirmrand

Das Dashboard verwendet die gemeinsame Startmenü-/Taskleistenbasis `MenuStyle`
und `MenuText`: Systemschrift, Haupt-/Nebenfarben, Kartenfüllungen, Außenfläche
und Kontur. Alle Dashboard-Reiter sind einbezogen. Schriftgrößen und Gewichte
bleiben als eigene Rollen erhalten; `MenuStyle.withSystemFamily()` übernimmt die
Systemfamilie auch bei expliziten Font-Zuweisungen. Keine eigene Materialpalette.

Kartenraster, Ränder, Rundungen, Uhr, Icons und Bedienfunktionen behalten ihre
geometrischen Werte. Die geänderten Schriftmetriken können Textbreiten verändern.
Das Dashboard zeichnet seine Glasfläche selbst; sein alter Blob-Hintergrund ist
abgeschaltet. Eine gerundete Region im bereits vorhandenen KWin-Effekt liefert
Blur, ohne globale Blur-Einstellungen zu ändern.

Installation (gemeinsame menu-style-Basis vorausgesetzt):

```bash
python /home/USER/ralleurOS/kde-customizations/taskbar/dashboard-style/install.py
systemctl --user restart caelestia-shell.service
```

Live geprüft: 931 × 570 logische Pixel, Noto Sans, alle fünf sichtbaren Reiter
laden ohne neue QML-Fehler. Die reale Ansicht wurde über geöffneten Fenstern
kontrolliert; Screenshot in `evidence/dashboard-dark.png`. Helles Theme wurde
nicht live umgeschaltet; die Farben stammen aus den gemeinsamen Theme-Rollen.
Temporäre Prüfzugänge sind wieder entfernt.

`backup-latest.txt` verweist auf die Sicherung vor dieser Änderung. Zum Rückbau
die dort gespeicherten QML-Dateien relativ ins Shell-Verzeichnis zurückkopieren
und die Shell neu starten. `dashboard-style.patch` enthält den vollständigen Diff.


## Freigegebenes Rauchglas und optimierter Pool

Das Dashboard verwendet inzwischen `MenuStyle.smokeSurface`, identisch mit
Taskbar und Startmenü. Die Materialquelle unter `overlay/services/MenuStyle.qml`
ist ein Symlink auf die zentrale Definition. Der Installer integriert deren
vorgewärmten nativen Blur-Pool und verhindert so Fensterneuanlagen und laufende
Puffergrößenwechsel während der Animationen. Die bestehende Geometrie und alle
fünf aktivierten Reiter bleiben erhalten; nur die Materialfüllung wurde geändert.

Erneut live geprüft: Hauptreiter vorher/nachher 931 × 570 px, übrige Reiter mit
identischen Außenmaßen, unveränderte Layout-/Schriftdeklarationen. Zehn
Öffnen-/Schließen-Zyklen liefern ca. 10 ms im 95. Perzentil der Qt-Frame-Abstände,
mit null Fensterneuanlagen/-zerstörungen und null Größenänderungen der Poolfenster.
Details, Ansichten und Rückbau des neuen Materialschritts:
[gemeinsames Rauchglas](../menu-style/README.md#startmenü-und-dashboard-gemeinsames-rauchglas-ohne-layoutänderung).
