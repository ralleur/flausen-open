# Super + Mausrad

KWin-Skript mit einem lokalen nativen QML-Modul für KDE Wayland.

- Super + Mausrad hoch: vorheriger Desktop.
- Super + Mausrad runter: nächster Desktop.
- Am Ende der Liste geht es am anderen Ende weiter.
- Fenster bleiben auf ihrem Desktop.

`./install.sh` baut das Modul gegen die installierten KWin-Header und installiert
es unter `~/.local/share/kwin/scripts/ralleur-desktop-scroll`. Es wird sofort und
bei der nächsten Anmeldung geladen. Nach einem KWin-Update bei Bedarf neu bauen;
die native KWin-API garantiert keine Binärkompatibilität.

Die QActions gehören zum QML-Objekt und werden beim Entladen mit entfernt.
Keine Hintergrundprozesse oder Eingabegeräteberechtigungen erforderlich.

Am 2026-11-01 zusätzlich in der laufenden Sitzung eingerichtet:
`~/.config/caelestia/keybinds.json`: `launcher` auf `Meta+Space` gesetzt;
KGlobalAccel entsprechend aktualisiert; in `kwinrc` unter
`[ModifierOnlyShortcuts]` den Wert `Meta` geleert. Super allein löst damit keine
Launcher-Aktion mehr aus. Caelestia wurde neu gestartet, um auch die gespeicherte
Belegung im laufenden Modell zu übernehmen.

Live geprüft mit XTest-Eingaben über Xwayland: Super + Rad runter wechselt von
Desktop 1 auf 2, Super + Rad hoch wieder zurück. Der Ausgangsdesktop wurde
wiederhergestellt.

Deaktivieren:

```sh
kwriteconfig6 --file kwinrc --group Plugins --key ralleur-desktop-scrollEnabled false
qdbus6 org.kde.KWin /Scripting unloadScript ralleur-desktop-scroll
```
