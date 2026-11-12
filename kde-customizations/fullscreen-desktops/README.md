# Vollbild auf einem der vier vorhandenen Desktops

Aktiver Standard: Ein normales Anwendungsfenster wechselt beim Start im Vollbild
oder beim späteren Wechsel ins Vollbild auf den nächsten freien Desktop rechts
vom aktuellen. Die Suche läuft von Desktop 4 zurück zu Desktop 1. Der aktuelle
Desktop selbst ist kein Ziel. Sind alle anderen Desktops belegt, nimmt die
Automatik den nächsten Desktop rechts, auf dem noch kein Vollbildfenster liegt.
Gibt es kein solches Ziel, bleibt das Fenster auf seinem Desktop.

Andere Anwendungsfenster, auch minimierte, gelten als Belegung. Desktopfenster,
Docks, auf allen Desktops angezeigte Fenster und zugehörige Dialoge des bewegten
Fensters blockieren das Ziel nicht. Die Automatik legt keine Desktops an und
löscht keine; die separate Vier-Desktop-Begrenzung bleibt aktiviert.

Das aktive Fenster nimmt den Fokus mit, ein Hintergrundfenster stiehlt ihn nicht.
Zugehörige Dialogfenster folgen. Beim Verlassen des Vollbilds werden die
ursprünglichen Desktopzuordnungen wiederhergestellt. Explizites manuelles
Verschieben eines Vollbildfensters wird beim Rückwechsel respektiert. Maximierte
Fenster bleiben auf ihrem Desktop.

Neue Anwendungsfenster und fremde Dialoge weichen von einem Vollbild-Desktop
auf den Ursprungsdesktop des Vollbildfensters aus. Liegt dort ebenfalls ein
Vollbildfenster oder ist der Ursprung unbekannt, sucht die Regel links mit
Umlauf nach einem Desktop ohne Vollbildfenster. Die eigenen Dialoge des
Vollbildfensters bleiben bei ihm. Sind alle vier Desktops im Vollbild belegt,
fehlt ein Ausweichziel. Beim Neuladen bleiben bereits laufende Vollbildfenster
an ihrem Platz und reservieren ihn weiter. Ihre vorherige Desktopzuordnung
ist nach einem Neuladen nicht mehr verfügbar.

## Installation

```sh
bash kde-customizations/fullscreen-desktops/install.sh
```

Der Installer sichert die vorherige Runtime und `kwinrc` unter
`~/.local/state/ralleur-desktop/backups/*-fullscreen-routing` und lädt nur dieses
KWin-Skript neu. Der Sicherungspfad steht in `backup-latest.txt`. Die technische
Plugin-ID `ralleur-fullscreen-desktops` bleibt für kompatible Updates erhalten.
Der bisher deaktivierte Plugin-Schlüssel ist wieder aktiviert, nun mit der
neuen Routing-Logik ohne dynamische Desktops.

## Prüfung

```sh
node kde-customizations/fullscreen-desktops/tests/routing.test.mjs
python3 kde-customizations/fullscreen-desktops/tests/live_check.py
```

Geprüft: 64 Kombinationen aus Startdesktop und Belegung mit der tatsächlichen
JavaScript-Implementierung; zusätzlich echte temporäre Waylandfenster für freie
Ziele, vollständige Belegung, Umlauf 4 → 1, Dialoge, Rückkehr, manuelles Verschieben,
Start im Vollbild und Schließen. Die Desktopzahl und alle vier IDs bleiben gleich.
Testfenster werden geschlossen; ursprünglicher Desktop und Fokus werden
wiederhergestellt. Ergebnis: `tests/live-result.json`. WoW selbst wurde nicht
für diesen Test gestartet oder umgeschaltet.

## Deaktivieren / Rückbau

```sh
kwriteconfig6 --file kwinrc --group Plugins --key ralleur-fullscreen-desktopsEnabled false
qdbus6 org.kde.KWin /Scripting unloadScript ralleur-fullscreen-desktops
```

Bestehende Fenster bleiben dabei auf ihren aktuellen Desktops. Die vier festen
Desktops bleiben erhalten. Für einen vollständigen Code-Rückbau kann das Paket
aus der Sicherung wiederhergestellt werden; die alte Version erzeugt zusätzliche
Desktops und sollte bei weiterhin aktiver Viererbegrenzung nicht aktiviert werden.
