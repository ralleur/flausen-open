# Desktop-Benachrichtigungen im Rauchglas

Die schwebenden Caelestia-Benachrichtigungen folgen dem gelieferten Stapel-Mock.
Jede Meldung zeichnet eine eigene gerundete Glasfläche statt einer dunklen
Sammelfläche mit zusätzlicher Innenkarte. App/Zeit, Titel, Inhalt und Aktionen
haben getrennte Rollen. Gemeinsame Quellen bleiben `MenuStyle.smokeSurface`,
`MenuText`, `MenuPrimarySurface` und `TaskbarGlass`.

Die äußere Inhaltsbreite beträgt mindestens 460 px (428 px sichtbare Karte bei
normalen Rändern); größere vorhandene Breiten bleiben erhalten. Icons sind 48 px,
Titel 18 px, Haupttext 16 px und Metadaten 13 px. Der vorhandene separate
Schriftmaßstab wirkt weiter. App-Icons behalten ihre Farbe. Ohne App-Icon erscheint
ein Symbol auf einer dezenten blauen Kachel. Kritische Meldungen erhalten eine
Fehlerkontur. Die erste App-Aktion ist blau, weitere Aktionen sind zurückhaltend.
Fortschrittsmeldungen zeigen einen begrenzten Prozentwert, 32 Segmente sowie
Inhalt und Prozentzahl unter dem Balken. Fehlende Fortschrittshinweise erzeugen
keinen Balken.

Die neue Darstellung öffnet den Inhalt zunächst vollständig; die Zusatzaktionen
zum Einklappen und Kopieren erscheinen unter dem Icon beim Darüberfahren.
Die bisherigen Lebenszyklus-, Link-, App-Aktions-, Wisch- und Zeitlimitfunktionen
bleiben erhalten. Texte und Aktionszeilen können umbrechen. Lange Inhalte nutzen
das bestehende scrollbare Benachrichtigungsfeld. DND, Position, Zielmonitor,
Vollbildregeln und Ablaufpräferenzen werden nicht umgeschrieben. Das Archiv und
das Benachrichtigungs-Popout sind nicht Teil dieser Änderung.

## Blur und Ressourcen

Ein zusätzlicher gemeinsamer `TaskbarGlass`-Pool pro Monitor enthält acht
vorgewärmte Durchgänge für den ganzen Stapel. Die maximal sichtbaren Meldungen
haben ausschließlich leichte Region-Objekte. Ihre gerundeten Masken folgen den
tatsächlichen Karten, der Scrollposition und der Wischbewegung. Auch das bestehende
ContentWindow verwendet dieselben Einzelregionen statt einer Sammelmaske.
`TaskbarGlass.customShape` ist ein optionaler Maskeneingang; andere Aufrufer
behalten ihre bisherige Maske. Puffer wachsen nur bei Überschreiten der Kapazität,
nicht pro Animationsframe. Geschlossen bleiben acht Flächen mit leerer sichtbarer
Region bestehen. Die globale KWin-Blur-Stärke wird nicht verändert.

Ein zunächst getesteter Pool je Popup überschritt das Dateilimit des Prozesses.
Dieser Ansatz wurde vor Abschluss durch den einen gemeinsamen Stapel-Pool ersetzt.

## Installation und Rückbau

Voraussetzung ist die bereits angepasste KDE/Caelestia-Shell mit gemeinsamem
Menüstil und Rauchglas-Pool. Dies ist eine gezielte Erweiterung des bestehenden
Installationsstands, kein vollständiger Neuinstaller für upstream Caelestia.

```sh
python kde-customizations/taskbar/notification-style/install.py --dry-run
python kde-customizations/taskbar/notification-style/install.py
systemctl --user restart caelestia-shell.service
```

`Notification.qml` ist die gepflegte Quelle. `integration.patch` ergänzt Content,
Wrapper und ContentWindow sowie den optionalen Maskeneingang des gemeinsamen
Pools. Der Installer prüft alle Patchabschnitte vor Änderungen, erkennt bereits
installierte Abschnitte und sichert die geänderten Dateien mit Manifest.
Wiederholte Installation ist wirkungslos. Der gemeinsame Menü-Installer liefert
die aktualisierte `TaskbarGlass.qml` ebenfalls aus ihrer bestehenden Quelle.

Die letzte Sicherung steht in `../evidence/notification-style-backup.txt`, die
vollständige Sicherung vor der ersten Übertragung in
`../evidence/notification-style-initial-backup.txt`. Zum vollständigen Rückbau:

```sh
python kde-customizations/taskbar/notification-style/install.py --restore "$(cat kde-customizations/taskbar/evidence/notification-style-initial-backup.txt)"
systemctl --user restart caelestia-shell.service
```

## Prüfung am 4. November 2026

Native KDE/Wayland-Prüfung mit drei shellinternen Testmeldungen: Aktionen,
Schließen, Wegwischen, Zeitlimit-Pause beim Darüberfahren, langer deutscher Text
mit Link, Fortschrittswert und leere Ansicht. DND blieb aktiviert. Testmeldungen
wurden geschlossen, temporäre QtTest-/IPC-Messzugänge entfernt und die produktive
Shell neu gestartet. Wiederholte Installation und `./bin/flausen check` erfolgreich.
Keine neuen zugehörigen QML-Laufzeitfehler im abschließenden Start beobachtet.

Im finalen Stack messen die Karten 428 × 163, 428 × 111 und 428 × 129 px.
Ein vorhandener unterer Anschnitt durch den negativen Wrapper-Top-Offset wurde
korrigiert; das leere Feld bleibt 0 px hoch.

Drei Öffnen-/Schließen-Gegenproben pro Variante ergaben bei `frameSwapped` einen
Median von 8 ms mit und ohne Zusatzblur, p95 von 11 bzw. 12 ms. Die Maxima von
177 bzw. 415 ms schließen bewusst auch inaktive Lücken zwischen Animationen ein;
sie sind keine durchgehende Präsentationsmessung. Die Poolkapazität blieb in den
geprüften Zuständen bei 512 × 768 px und acht Durchgängen; geschlossen waren null
aktiv. Das ist eine begrenzte Gegenprobe, kein allgemeiner Performance-Nachweis.

Geprüft wurde der dunkle Live-Desktop mit normaler Schriftgröße. Helles Theme,
abweichende DPI und Vollbildpositionen wurden nicht erneut visuell abgenommen.
Für den Mockvergleich wurden beide Kartenstapel auf **428 px Außenbreite** gebracht;
der ruhige vorhandene Wallpaper-Ausschnitt zeigt weniger Farbvariation als der Mock.

[Live-Karten](../evidence/notification-smoke-cards.png),
[Mockvergleich bei gleicher Breite](../evidence/notification-smoke-comparison.png),
[Messwerte](../evidence/notification-style-check.json).

Reproduzierbare native Prüfung (temporäre QtTest-/IPC-Instrumentierung,
Shell-Neustart; benötigt QtTest, Pillow und Spectacle):

```sh
python kde-customizations/taskbar/notification-style/live_check.py
```

Der Test verwendet `HDMI-A-2` und stellt die produktive ContentWindow-Datei im
`finally`-Block wieder her. Währenddessen keine parallelen Shell-Quelländerungen.
