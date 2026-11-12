# Taskbar-Wetter nach Rauchglas-Mock

Das schwebende Wetterfenster übernimmt den gelieferten Mock: Standort mit
Auswahl, Aktualisieren, großes Wettersymbol mit Temperatur und Beschreibung,
Hoch/Tief, drei Kennzahlen und eine Stundenkurve mit sieben Spalten. Material,
Schrift und Konturen stammen weiterhin aus `MenuStyle`/`MenuText`. Der bestehende
Taskbar-Blur-Pool bleibt unverändert; es gibt keine zusätzlichen nativen Fenster
und keine Änderung der globalen KWin-Stärke. Dashboard und Wetterwidget behalten
ihre bisherigen Komponenten und Ansichten.

`Weather.qml` ist die gepflegte Taskbar-Quelle. `WeatherHourly.qml` zeichnet die
Kurve, Punkte, Verlauf, Stunden, Symbole und gegebenenfalls Regenwahrscheinlichkeiten.
`WeatherSymbol.qml` enthält skalierbare Canvas-Vektorsymbole für Tag, Nacht,
Wolken, Regen, Schnee, Gewitter, Nebel und Wind. Die Symbolfarben sind semantische
Wetterfarben; Glas und Text verwenden ausschließlich den gemeinsamen Menüstil.

## Verhalten und Daten

Die Anzeige verwendet den vorhandenen Wetterservice; es gibt keinen zweiten
Wetterabruf. Vor die kommende Stundenprognose wird die aktuelle gemessene Temperatur
als „Now“ gesetzt. Navigation blättert drei Stunden vor/zurück und bleibt auf die
vorhandenen Daten begrenzt. Die Prognose lässt sich einklappen. Windstille wird
als 0 km/h angezeigt. Fehlende Daten haben einen ausdrücklichen Leerzustand.
Die Standortauswahl nutzt die bestehende Suche sowie deren Übernahme- und
Automatikfunktionen. Eine bloße Öffnung ändert keine gespeicherte Position.

Die Fußzeile liest den Beobachtungszeitpunkt aus dem bereits vorhandenen
Service-Cache über `StandardPaths.CacheLocation`; sie erfindet keine Abrufzeit.
Heute wird die Uhrzeit, bei älteren Daten auch das Datum gezeigt. Ist kein
Zeitpunkt bekannt oder fehlen Wetterdaten, erscheint „Weather data“.
Die vorhandenen Sonnenauf-/untergangszeiten desselben Caches bestimmen Tag und
Nacht für die Stundenicons des jeweiligen Tages. Der bisherige Service liefert
hier grundsätzlich Tagesicons. Die Korrektur erfolgt nur in dieser Ansicht.
Ein fehlender Cache verhindert die übrige Wetteranzeige nicht.

Normaler Maßstab: mindestens 1,15 wie die anderen Taskbar-Popouts, ca. 543 px
Außenbreite. Geometrie und Schriftmaßstab bleiben getrennt. Haupttext ist 16 px,
Nebenrollen ca. 13 px. Das Fenster wächst bei größerer Schrift; die Kennzahlen
teilen eine gleichmäßige Zeilenhöhe. Bei schmaler Breite stehen die Kennzahlen
untereinander und die Kurve zeigt fünf Stunden. Das vorhandene äußere Flickable
übernimmt zu hohe Inhalte. Es werden keine Schriftpräferenzen umgeschrieben.

## Installation

Voraussetzung ist die vorhandene KDE/Caelestia-Shell mit dem gemeinsamen Menü-
und Rauchglasstand. Dies ist kein vollständiger upstream Neuinstaller.

```sh
python kde-customizations/taskbar/weather-popover/install.py --dry-run
python kde-customizations/taskbar/weather-popover/install.py
systemctl --user restart caelestia-shell.service
```

Der Installer prüft den Integrationspatch vor Änderungen, sichert Dateien mit
Manifest und kopiert die drei Quellen. `integration.patch` ergänzt ausschließlich
den Mindestmaßstab des Wetter-Popouts in `Content.qml`. Wiederholung ändert nichts.
Es wird keine neue direkte Komponente unter `kde-customizations/` angelegt.

Letzte Sicherung: `../evidence/weather-popover-backup.txt`. Die vollständige
Sicherung vor der ersten Änderung steht in `../evidence/weather-popover-initial-backup.txt`.
Zum vollständigen Rückbau:

```sh
python kde-customizations/taskbar/weather-popover/install.py --restore "$(cat kde-customizations/taskbar/evidence/weather-popover-initial-backup.txt)"
systemctl --user restart caelestia-shell.service
```

## Prüfung am 4. November 2026

Native dunkle KDE/Wayland-Ansicht mit den echten Standort-/Wetterdaten geprüft.
Mock und Live-Ansicht wurden auf dieselbe äußere Breite gebracht. Zusätzlich:
Vor-/Zurücknavigation, Grenzen, Ein-/Ausklappen, Öffnen der Standortsuche ohne
Übernahme, 300 px Inhaltsbreite, Schriftmaßstab 1,7, fehlende Daten, konstante
Temperaturen und Regenwerte. Für die Sonderzustände wurden ausschließlich
vorübergehende Ansichts-Fixtures eingesetzt. Keine Standortpräferenz geändert.
Helles Theme und andere Bildschirm-DPI wurden nicht erneut visuell abgenommen.

Drei Öffnen-/Schließen-Gegenproben pro Blurvariante erfassen `frameSwapped`-Abstände,
keine DRM-Präsentationszeiten. Beide Varianten liegen etwa bei 8 ms Median.
Der bestehende Pool bleibt bei acht Durchgängen und 640 × 1024 px Pufferkapazität.
Die Messwerte enthalten auch inaktive Lücken zwischen Animationen; Maxima sind
deshalb keine reine Animationslatenz. Einzelne Messreihen sind kein allgemeiner
Performance-Nachweis. Aktuelle Werte: `../evidence/weather-smoke-performance.json`.

Temporäre QtTest-/IPC-Zugänge und die Testalias sind nach der Prüfung entfernt;
die produktive Shell wurde neu gestartet. Wiederholter Installationslauf und
`./bin/flausen check` erfolgreich. Keine neuen zugehörigen QML-Fehler im
abschließenden Produktionsstart beobachtet.

[Live-Ansicht](../evidence/weather-smoke-normal.png),
[Mockvergleich bei gleicher Breite](../evidence/weather-smoke-comparison.png),
[große Schrift](../evidence/weather-smoke-large.png),
[schmale Ansicht](../evidence/weather-smoke-narrow.png),
[Funktionsprüfung](../evidence/weather-smoke-check.json),
[Animations-Gegenprobe](../evidence/weather-smoke-performance.json).

Die native Prüfung ist wiederholbar (QtTest, Pillow und Spectacle erforderlich;
Testmonitor `HDMI-A-2`, Shell-Neustarts). Sie sichert die beiden instrumentierten
Dateien im Speicher und stellt sie auch nach fehlgeschlagenen Assertions wieder
her. Bei parallelen Quelländerungen stoppt sie statt fremde Änderungen zu überschreiben.

```sh
python kde-customizations/taskbar/weather-popover/live_check.py --mock "/Pfad/zum/Wetter-Mock.png"
```
