# Freiwilliges Tiling mit Krohnkite

Aktiv auf KDE/KWin 6.8.2 unter Wayland, Krohnkite 0.9.10.0.
Fenster bleiben standardmäßig floating. Keine automatische Aufnahme neuer Apps.

| Geste | Verhalten |
| --- | --- |
| Super+Shift+Linksziehen | Fenster ins Tiling aufnehmen; über einem gekachelten Fenster ablegen, um dort einzusortieren bzw. die Plätze zu tauschen |
| Super+Rechtsziehen | Floating-Fenster frei skalieren; im Tiling gemeinsame Trennlinie verschieben |
| Super+Linksziehen | Frei bewegen; gekacheltes Fenster aus dem Tiling lösen |

Beim Skalieren nahe der gewünschten Fensterkante greifen. Floating-Fenster liegen
über dem Tiling. Dialoge und die vorhandenen Ausnahmen bleiben frei bzw. ignoriert.
Die Leisten werden über KWin-Arbeitsflächen berücksichtigt; Fensterabstände: 8 px.

Der Quickshell-Desktop verwendet `WlrLayer.Background`. `WlrLayer.Bottom` liegt
in KWin auf derselben Ebene wie Krohnkites `keepBelow`-Fenster und kann diese
beim Aktivieren des Desktops verdecken. `python install_desktop_layer.py` korrigiert
die installierte `Background.qml` mit Sicherung unter `~/.local/state/ralleur-tiling/`.
Bei deaktiviertem Datei-Watching anschließend die Oberfläche mit
`systemctl --user restart caelestia-shell.service` neu laden; App-Fenster bleiben offen.

Standard ist das Quarter-Layout: vier gekachelte Fenster bilden vier Quadranten
(oben links, oben rechts, unten rechts, unten links). Bei einem Fenster wird die
ganze Arbeitsfläche genutzt, bei zwei je eine Hälfte, bei drei eine Hälfte und
zwei Viertel. Die Trennlinien bleiben skalierbar. Weitere Fenster über die vier
Plätze hinaus bleiben schwebend. Beim Schließen, Minimieren oder Herauslösen
eines Fensters verteilt Krohnkite den Platz neu.

## Umsetzung

`install.py` sichert das vorhandene Paket und die Konfiguration unter
`~/.local/state/ralleur-tiling/`. Es erzeugt eine eigene Inhaltsgeneration innerhalb
des bestehenden Krohnkite-Pakets und lädt sie über einen kleinen Einstieg. Das vermeidet
KWin-intern zwischengespeicherte QML-/JS-Dateien bei Aktivierung ohne Abmeldung.
Die ursprünglichen Quelldateien sind vollständig im Backup vorhanden.

`gesture.js` ergänzt ausschließlich den Move-Start-/Drop-Pfad. Ein kleines natives
QML-Modul liest KWin-Modifikatoren und registriert Super+Shift+Links als Move-Aktion:
KWin startet seine normale Super-Move-Aktion nicht, wenn Shift bereits beim
Mausdruck gehalten wird. Shift darf auch während eines Super-Drags hinzukommen.
Krohnkites eigener Dock-Drag-Pfad wird bei dieser Variante übersprungen. Die native
statische Rasterzuordnung wird beim Drop gelöst, bevor Krohnkite anordnet.

Zusätzlich verhindert das KWin-Skript `ralleur-tiling-guard` KDEs eigenes
Shift-Raster bereits während des Ziehens. Sein nativer Eingabefilter entfernt
Shift ausschließlich aus der internen Fensterbewegung; die tatsächliche
Tastaturbelegung bleibt unverändert und wird von Krohnkite weiter erkannt.
Das gilt auch für Titelleisten-Drags und nachträglich gedrücktes Shift.
Shift allein nimmt kein Fenster ins Tiling auf. Der Helfer ist nur wirksam,
solange Krohnkite in KWin aktiviert ist; seine Deaktivierung gibt das native
Raster wieder frei. Kanten-Snapping ohne Shift bleibt erhalten.

`python install_guard.py` installiert oder aktualisiert den Konflikt-Helfer
separat, ohne Krohnkite neu zu laden oder aufgenommene Fenster zurückzusetzen.
Neue Versionen verwenden eigene Dateipfade für die native Bibliothek.

Das Modul wird gegen die installierten KWin-Header gebaut. Nach KWin-Updates kann
ein Neubau nötig sein. Ein Krohnkite-Update kann den lokalen Einstieg ersetzen;
die Anpassung dann gegen den neuen Code prüfen und erneut anwenden.

Installation: `python install.py` aus diesem Verzeichnis. Ein bereits geändertes
Paket wird nicht ungeprüft erneut gepatcht. Für einen erneuten Build zunächst den
gesicherten Originalstand wiederherstellen. Nicht die geladene native Bibliothek
innerhalb derselben Sitzung überschreiben.

Rückbau: `python restore.py`. Stellt das ursprüngliche Krohnkite-Paket und nur die
von dieser Einrichtung geänderten KWin-Schlüssel wieder her. Andere zwischenzeitlich
geänderte Desktop-Einstellungen bleiben erhalten. Ursprünglich war Krohnkite aus.

## Prüfung

### Flüssige gemeinsame Größenänderung unter Wayland

`resize_patch.py`/`resize.js` verwenden KWin-Resize-Schritte statt verzögerter
Buffer-Rückmeldungen als Grundlage für Layoutänderungen. Während der Geste
werden nachträgliche Größenkorrekturen auf derselben Tiling-Fläche unterdrückt,
auch bereits eingeplante Timer. Beim Loslassen wird die zuletzt angeforderte
KWin-Geometrie verwendet; beim Abbrechen mit Escape die wiederhergestellte
Geometrie. Floating-Fenster bleiben im vorhandenen Resize-Pfad.

`python stage_resize.py --node /pfad/zu/node` prüft den echten gepatchten
Krohnkite-Code isoliert, baut den Eingabehelfer und stellt eine neue Generation
für die **nächste Anmeldung** bereit. Es lädt KWin nicht neu und verwendet
keinen Live-Probe-Helfer. Vorheriger Einstieg und Generation bleiben gesichert.
Der Test `tests/resize.test.cjs` prüft verspätete Buffer, Loslassen, Escape,
Korrektur-Timer, vertikale Trennlinien, Größenlimits und Floating.

Der native Live-Probe-Helfer konnte bei einer ausgeblendeten Drop-Vorschau einen
ungültigen QVariant über D-Bus zurückgeben und damit KWin zum Abbruch bringen.
`probe.cpp` lässt diesen fehlenden Wert nun aus. Diese Korrektur wurde nicht
erneut in der laufenden Sitzung getestet; für diesen Fix nur isolierte Tests nutzen.

`python tests/live_check.py` erzeugt bis zu vier temporäre Wayland-Fenster auf einer
temporären Arbeitsfläche und sendet echte Maus-/Tastaturgesten über KWin-EIS.
Es prüft: Floating als Ausgangszustand, Aufnahme eines und zweier Fenster,
unverändertes unbeteiligtes Floating-Fenster, Platztausch, gemeinsame Skalierung,
dritte Unterteilung, vier Quadranten, Herauslösen und Nachrücken nach Schließen.
Ein temporärer nativer Probe-Helfer prüft zusätzlich während des Ziehens den
echten KWin-Outline-Zustand. Geprüft sind Shift allein an der Titelleiste,
Super+Shift von Anfang an und erst während des Drags gedrücktes Shift.
Die letzte Prüfung bestand mit 69 Shift-Drag-Messpunkten ohne natives Raster.
Fenster und Testarbeitsfläche werden anschließend entfernt. Während der Prüfung
wird die Arbeitsfläche kurz gewechselt. Ergebnis: `tests/live-result.json`.

Diese Gestenprüfung ist auf dem vorhandenen 3840×2160-Monitor ausgelegt. Andere
Monitorgrößen und mehrere Ausgänge sind damit nicht separat abgenommen.
