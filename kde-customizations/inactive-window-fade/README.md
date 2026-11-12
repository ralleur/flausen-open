# Weicher Fokuswechsel

Die bestehende Caelestia-Fensterregel setzt inaktive normale Fenster und Dialoge
auf 95 % Deckkraft. Dieser ergänzende KWin-JavaScript-Effekt überblendet genau
die Wechsel zwischen 100 und 95 % in mindestens 250 ms mit `InOutCubic`. Langsamere
globale Animationen werden berücksichtigt, ebenso abgeschaltete Animationen.
Die schnellere Vorgabe dieser Sitzung würde 250 ms auf 62 ms verkürzen; deshalb
gilt für diesen einzelnen Effekt die Mindestdauer von 250 ms.
Bei schnellem erneutem Fokuswechsel wird vom berechneten Zwischenwert fortgesetzt.

Die Regel bleibt maßgeblich. Vorschau-/Polkit-Ausnahmen mit konstant 100 %,
versteckte Bridge-Fenster, Menüs und andere Deckkraftänderungen werden nicht
animiert. Voraussetzung: KDE Plasma 6/KWin mit der vorhandenen 95-%-Regel,
`python3`, `kwriteconfig6` und `qdbus6`. Kein Build erforderlich.

Installation und Aktivierung in der laufenden Sitzung:

```sh
python3 kde-customizations/inactive-window-fade/install.py
node --test kde-customizations/inactive-window-fade/tests/fade.test.cjs
./bin/flausen check
```

Der Installer sichert eine vorhandene Effektinstallation und `kwinrc` unter
`~/.local/state/flausen-inactive-window-fade/`. Er verändert keine Fensterregeln.
Live-Prüfung: zwischen zwei Fenstern wechseln, auch mehrfach schnell; aktiv
voll deckend, inaktiv unverändert leicht transparent. Dolphin-Vorschau bleibt
voll deckend. Optional protokolliert `Effect-flausen-inactive-window-fade/Debug`
in `kwinrc` die gestarteten Übergänge im KWin-Journal (Effekt danach neu laden).

Rückbau ohne Änderung anderer Einstellungen:

```sh
kwriteconfig6 --file kwinrc --group Plugins --key flausen-inactive-window-fadeEnabled false
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect flausen-inactive-window-fade
rm -r ~/.local/share/kwin/effects/flausen-inactive-window-fade
```

Eine vorherige Version kann aus dem Sicherungsordner `effect/` an denselben
Installationspfad zurückkopiert und erneut geladen werden.
