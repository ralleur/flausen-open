# Dolphin: gemeinsame Ralleur-Kopfzeile

Kleine, benutzerlokale Erweiterung für **den vorhandenen Dolphin auf KDE/KWin**.
Sie ergänzt seine bestehende Werkzeugleiste um Minimieren, Maximieren/
Wiederherstellen und Schließen. Die separate Titelleiste samt App-Icon entfällt.
Darkly, KDE-Farben, Orte, Tabs und Dateifunktionen bleiben native Komponenten.

Die Seitenleiste verwendet Icons mit 16 logischen Pixeln, 8 Pixel linkem Einzug
und zusätzlichem vertikalem Abstand. Downloads, Dokumente, Bilder, Musik und
Videos haben eigene, farblich passende Liniensymbole. Nur deren Icon-Felder in
den vorhandenen Orte-Lesezeichen werden geändert. KDEs originales Places-Delegate bleibt erhalten;
Geräteaktionen, Drag-and-drop und Maus-Hit-Tests werden nicht ersetzt.
Die kleinen Menüindikatoren unter Zurück/Vorwärts sind ausgeblendet; die
Verlaufsmenüs bleiben erhalten. Die dunkle Dateifläche ist um zehn RGB-Stufen
aufgehellt (hier von `#080f10` auf `#12191a`), ohne die globale Palette zu ändern.
Palette-, Theme- und Stiländerungen werden im laufenden Fenster übernommen.
Dateifläche, Text, Auswahl, alternierende Zeilen, Pfadleiste und Tabs verwenden
jeweils die aktuelle Anwendungspalette. Die Aufhellung summiert sich bei
wiederholten Änderungen nicht. Der seitliche Einzug verwendet nur ein lokales
Stylesheet. Die zusätzlichen zwölf Pixel Zeilenhöhe kommen aus einer auf Places
begrenzten Größenberechnung im bestehenden Anwendungsstil, da KDEs Delegate
hier direkt den Anwendungsstil abfragt. Es gibt kein globales Stylesheet.

## Kontextmenü

Im Dolphin-Dateikontextmenü entfallen „Hier duplizieren“, „In neuen Ordner
verschieben“, „Stichwörter zuweisen“ und „Aktivitäten“. Die gemeinsamen Aktionen
werden nur aus diesem Menü entfernt; etwaige Tastenkürzel bleiben erhalten.

„Komprimieren“ heißt **zippen** und startet direkt Arks vorhandenen ZIP-Befehl
für die aktuelle Auswahl. **Shift** öffnet stattdessen das bisherige Untermenü
mit ZIP, tar.gz und dem Archivdialog. Die Umschalttaste kann auch im bereits
geöffneten Kontextmenü gedrückt und losgelassen werden. ZIP übernimmt die
native Dateibenennung, Kollisionsprüfung und Schreibbarkeitsprüfung. Bei einer
einzelnen vorhandenen Archivdatei gilt weiterhin Arks normale Eintragsauswahl.
Die Anpassung gilt nur für Dolphin, nicht für Portal-Dateidialoge.

Die Menüfläche nutzt jetzt `MenuStyle.smokeSurface`, dieselbe Rauchglas-Tönung
wie Startmenü und Taskbar: dunkel `#b823292e`, hell `#e6e9ecef`, mit feiner heller
Kontur und 14-Pixel-Rundung. CMake erzeugt `smokematerial.h` direkt aus der
gemeinsamen QML-Quelle; Änderungen daran lösen die Konfiguration erneut aus.
Schrift, Abstände, Icons und Aktionen bleiben erhalten. Das Desktop-Kontextmenü
behält bis zu einem eigenen Auftrag seine bisherigen Materialrollen.

KWindowEffects fordert nativen KWin-Blur für die gerundete Menüfläche an.
Zusätzlich verwendet Dolphin acht lokale, eingabefreie native Blur-Flächen pro
sichtbarem Menü, entsprechend den acht Durchgängen von `TaskbarGlass`. Der Pool
für Hauptmenü und erstes Untermenü wird vorgewärmt. Native Tooltip-Flächen
verwenden unter Wayland einen Positioner und liegen hinter dem eigentlichen
Menü; sie erhalten weder Fokus noch Schatten. Die Puffer bleiben mindestens
512 × 768 px groß und wachsen nur bei größerem Inhalt. Beim Schließen bleibt
ausschließlich eine außerhalb der Fläche liegende Blur-Region übrig. Die
Ressourcen überleben das Menü und werden mit dem Dolphin-Fenster freigegeben.
Weitere gleichzeitig sichtbare Untermenüs erhalten wiederverwendete Poolplätze.
Die globale Blur-Stärke wird dafür nicht geändert.
Der bestehende Dienst `ralleur-start-backdrop.service` erhält über seinen
lokalen Socket zusätzlich eine pro Dolphin-Prozess gebundene Kontext-Lease.
Er zeichnet auf allen Bildschirmen denselben dezenten Hintergrund-Blur wie
beim Startmenü. Die aktuellen Geometrien des Hauptmenüs und seiner Untermenüs
werden aus dieser Blur-Region ausgespart, damit Text und Icons scharf bleiben.
Die Fläche nimmt weder Maus- noch Tastatureingaben an. Schließen, Zerstören
oder eine getrennte Socket-Verbindung gibt den Effekt wieder frei; auch ein
Dienstneustart räumt die Blur-Stärke-Lease auf. Startmenü-Leases bleiben getrennt.
Benötigt werden die aktuelle Version von `../launcher/backdrop/helper/shell.qml`,
dessen Service-Datei und die kleine `ralleurGlassMenu`-Ausnahme im gemeinsamen
Dialogstil. Qt Network ist eine zusätzliche Build-Abhängigkeit.

`context_probe` ist ein explizit zu bauendes Testplugin für das System-Dolphin
(`cmake --build … --target context_probe`). Mit `RALLEUR_CONTEXT_PROBE_DIR`
und `QT_QPA_GENERIC_PLUGINS=ralleurdolphin,ralleurcontextprobe` öffnet es ein
Menü über einer Testdatei, prüft die direkte ZIP-Aktion, öffnet das Shift-Untermenü,
schreibt Screenshots/JSON und schließt sein eigenes Testfenster wieder.
Mit `RALLEUR_CONTEXT_PROBE_NATIVE_INPUT=1` schreibt die Probe stattdessen
`click.json` mit PID und relativen Fensterkoordinaten und wartet auf eine echte
Kontextmenü-Eingabe. Wayland-Fensterkoordinaten sind relativ zum Elternfenster;
für externe Eingabe/Screenshots die tatsächliche KWin-Geometrie berücksichtigen.
Die Rauchglas-Prüfung lief mit echtem Shift+F10 unter Wayland und zusätzlich
unter XWayland. Nachgewiesen: acht aktive Pässe im Hauptmenü, 16 mit Untermenü,
null nach Schließen; dieselben 16 gemappten Puffer mit je 512 × 768 px bleiben
erhalten. Alle sechs Komponententests und die Katalogprüfung bestehen. Dies ist
keine Frame-Zeit-Messung.
[Native Ansicht](evidence/context-menu-smoke.png),
[Prüfwerte](evidence/context-menu-smoke-check.json).

Bei dieser Installation wurde ausschließlich die Plugin-Bibliothek atomar
aktualisiert; eine bereits nachträglich geänderte Icon-Theme-Datei blieb erhalten.
Die Sicherung steht im Prüfprotokoll. Für den gezielten Rückbau
`plugin.before.so` zunächst in eine neue Datei neben der installierten Bibliothek
kopieren und diese atomar ersetzen; danach `installation.before.json` als
`~/.local/state/ralleur-desktop-tweaks/dolphin-header-installation.json`
wiederherstellen und Dolphin regulär neu starten. Der allgemeine Installer
verweigert weiterhin das Überschreiben der fremden Icon-Änderung.

Der Test `context_menu` prüft Shift, die Weiterleitung an die ZIP-Aktion,
deaktivierte Ziele und die tatsächlich installierten KIO-/Ark-Menüplugins.
Mit `LC_ALL=de_DE.UTF-8 LANGUAGE=de RALLEUR_TEST_LANGUAGE=de` lässt er sich auf Deutsch prüfen.
`RALLEUR_TEST_ARCHIVE=1` aktiviert zusätzlich eine echte ZIP-Erstellung in
einem temporären Ordner; dabei öffnet Ark anschließend ein Dolphin-Fenster.

## Schnellvorschau mit Leertaste

Im Dateibereich öffnet **Leertaste** eine schwebende Vorschau der ersten
markierten Datei. Erneute Leertaste oder Escape beendet sie. Das Vorschaufenster
folgt bei geöffneter Vorschau der Auswahl im aktiven Dateibereich: Ein Klick auf
eine andere Datei ersetzt den Inhalt im selben Fenster und erhält Position und
Größe. Hintergrund-Tabs und inaktive Split-Ansichten ändern die Vorschau nicht.
Ohne Auswahl erscheint ein Hinweis; die nächste Auswahl zeigt wieder den Inhalt.
Beim Wechsel werden vorherige Medien und PDF-Dokumente sofort freigegeben.
Das Vorschaufenster zeigt nur den Inhalt, ohne Titelleiste, Dateinamenzeile oder Hinweisleiste.
Die Vorschaufläche bleibt auch ohne Fokus vollständig deckend. Die gezielte
KWin-Ausnahme in `preview-opacity.rules` hat Vorrang vor Caelestias allgemeiner
95-%-Deckkraft inaktiver Fenster. Sie berücksichtigt auch den von Dolphin beim
Dateiwechsel angehängten Anwendungstitel „ — Files“. Installation mit
`python kde-customizations/dolphin-header/install_preview_opacity.py`;
andere Fensterregeln bleiben erhalten, eine Sicherung wird ausgegeben.
Die Vorschau hat 16-Pixel-Rundungen, transparente Außenecken und eine feine
halbtransparente Verlaufskontur aus der aktuellen Textfarbe. Hintergrund und
Kontur folgen der Palette; die generische Dialog-Haut wird für diese eigene
Oberfläche ausgespart. Der Inhalt wird innerhalb der Rundungen
beschnitten; Bilder und Dokumente behalten ihre unveränderten Farben.
Die Vorschau lässt sich mit der linken Maustaste am Bild, an freien Flächen oder
am Rand verschieben. Bei Text/PDF bleibt die Fläche für Auswahl und Scrollen
verfügbar; dort dient der Rand zum Verschieben. Wiedergabeknöpfe und Schieberegler
bleiben bedienbar. Der eigentliche Fensterverschiebevorgang läuft nativ über
`QWindow::startSystemMove()` und KWin, auch unter Wayland.
Gedrückthalten der Taste schließt die Vorschau nicht wieder. Die bisherige
Leertasten-Zuweisung des Auswahlmodus wird nur im laufenden Dolphin entfernt;
der Auswahlmodus bleibt über das Menü verfügbar. Es wird keine globale
Tastenkombination geändert. Adresszeile, Such-/Filterfelder, Umbenennen und
Terminal behalten ihre normale Leertaste.

Die vorhandene Erweiterung verwendet Qt-Komponenten für Bilder, mehrseitige
PDFs, Text/Quellcode und Audio/Video (abhängig von den installierten Codecs).
Texte sind schreibgeschützt und auf 1 MiB begrenzt; große Bilder werden für die
Anzeige verkleinert. Ordner und unbekannte Dateitypen zeigen eine Information.
Entfernte Dateien werden nicht automatisch heruntergeladen. Die Vorschau startet
keine Dateihandler und verändert weder Datei noch Zwischenablage. Audio stoppt
beim Schließen sofort.

Die Auswahl wird getrennt je Tab/Split über Dolphins `selectionChanged`-Signal
übernommen. Vor dem Öffnen wird dessen vorhandener QObject-Slot
`emitSelectionChangedSignal()` aufgerufen, falls vorhanden, damit die native
300-ms-Verzögerung keine alte Auswahl liefert. Das bindet keine private
C++-Bibliothek, hängt aber wie die Fenstererkennung von Dolphins QObject-Namen ab.

## Ordnerfarben

Beim ersten Installieren werden die vorhandenen unmittelbaren Home-Ordner samt
Icon und Dateisystem-Identität in `~/.config/ralleur-dolphin/folder-colors.json`
erfasst. Ihre Farben bleiben erhalten, auch nach einer Umbenennung. Ein später
angelegter Home-Ordner erhält Gelb wie Vorlagen. Unterordner erben die Farbe ihres
obersten Home-Ordners. Gewöhnliche Ordner außerhalb von Home sind Rot, unabhängig
von der globalen Akzentfarbe. Symbolische Links werden anhand ihres Ziels eingeordnet;
ihre Ziele werden über den Link nicht verändert. Besondere Anwendungs-/Geräteicons
bleiben erhalten.

Die Erweiterung gleicht Home und die gerade geöffneten lokalen Verzeichnisse
asynchron ab; neue Ordner in diesen Ansichten werden automatisch erfasst.
Tiefere Ebenen werden beim Öffnen angeglichen. Es gibt keinen rekursiven Scan
des gesamten Home-Verzeichnisses. Die Vererbung schreibt bei Bedarf KDEs normale
versteckte `.directory`-Datei mit `Desktop Entry/Icon=folder-FARBE`. Dadurch
bleiben native Inhaltsvorschauen erhalten. Bereits passende rote Standardordner
bekommen keine zusätzliche Datei. Nicht beschreibbare Verzeichnisse und
Versionsverwaltungs-Interna (`.git`, `.hg`, `.svn`) werden nicht verändert.

Die Originaldaten geänderter `.directory`-Dateien werden unter
`~/.local/state/ralleur-desktop-tweaks/folder-icon-changes/` gesichert.
Nachträgliche manuelle Änderungen werden bewahrt. Der Rückbau stellt nur noch
unveränderte, zur gespeicherten Verzeichnis-Identität passende Metadaten wieder her.

Die großen Ordner verwenden ein kleines, originales SVG-Overlay mit gerundeten
Ecken und dezenter Lichtkante. `dolphinrc` aktiviert dieses Icon-Theme nur für
Dolphin; alle anderen Symbole erben das bestehende KDE-Theme. Werkzeug- und
Aktionssymbole nutzen KDEs palettenabhängigen SVG-Renderer, damit sie auch bei
einem laufenden Hell/Dunkel-Wechsel lesbar bleiben. Ein expliziter Theme-Name
über `QIcon::setThemeName` wird vermieden, da er diesen Renderer umgehen kann.
Auch der MIME-Name
`inode-directory` ist enthalten, den Dolphin für gewöhnliche Verzeichnisse nutzt.
Ordner-Inhaltsvorschauen bleiben aktiv: Der vorhandene KIO-Vorschaudienst bekommt
über seinen eigenen `kioworkerrc`-Eintrag dasselbe Icon-Overlay. Er zeichnet die
Inhaltsbilder dadurch direkt auf den runden Ordner. Die native Dateiauswahl,
Vorschau-Erzeugung und Hover-Sequenz bleiben erhalten; es gibt keinen eigenen
Thumbnail-Renderer. Dieser gemeinsam genutzte KIO-Dienst verwendet die runde
Ordnerbasis auch für Ordner-Vorschauen anderer KDE-Anwendungen. Deren übrige
Oberflächen-Icons und die globale KDE-Theme-Einstellung werden nicht geändert.

## Technik und Startwege

Die zusätzliche Integration unter `../files` lädt dieselbe Kopfzeile gezielt
im KDE-Portal für Öffnen-/Speichern-Dialoge mit `KFileWidget`. Diese Dialoge
erhalten denselben Rahmen und dieselben Fensterknöpfe; ihre native KDE-Logik
bleibt erhalten. Ordnerfarben-Verwaltung und Leertasten-Vorschau bleiben auf
Dolphin beschränkt. Ohne den service-lokalen Portal-Eintrag betrifft die
Erweiterung weiterhin nur den Files/Dolphin-Starter.

Ein Qt-Generic-Plugin hängt sich nur an `DolphinMainWindow` mit `mainToolBar`.
Die Fensterknöpfe rufen die normalen QWidget-Funktionen auf; Schließen umgeht
keine Rückfragen von Dolphin. Verschieben und Skalieren verwenden die nativen
QWindow-Funktionen. Dialoge behalten ihre normale Fensterdekoration. Rundungen
werden am echten Fenster gesetzt, der Schatten über KDEs KWindowShadow-API.
Der Alphakanal wird vor der nativen Fenstererzeugung vorbereitet. Für eine späte
Anbindung wird eine noch undurchsichtige Oberfläche neu erzeugt. Dadurch bleiben
die ausgesparten Ecken transparent und bilden keine schwarzen Rechtecke.

Das Plugin nutzt öffentliche Qt-/KDE-APIs, aber die Erkennung der Dolphin-
Hauptfenster hängt von deren Klassennamen und Toolbar-Namen ab. Bei größeren
Dolphin-/Qt-Updates erneut bauen und prüfen. Getestet wird hier Dolphin 26.08.2,
Qt 6.12.0, KDE Frameworks 6.31.0, KWin 6.8.2 und Darkly 0.5.42 unter Wayland.

Es gibt **keine globale Regel zum Entfernen der Titelleiste**. Ist das Plugin
nicht verfügbar oder kann Qt es nicht laden, bleibt Dolphin normal dekoriert.
Seine Injektionsvariablen werden nach dem Laden aus der Prozessumgebung entfernt,
damit gestartete andere Apps ihre normale Qt-Umgebung erhalten.

Die Installation verwaltet ausschließlich Benutzerdateien:

| Ort | Zweck |
|---|---|
| `~/.local/lib/ralleur/dolphin-header/plugins/generic/` | Qt-Plugin |
| `~/.local/bin/ralleur-dolphin` | Startskript für `/usr/bin/dolphin` |
| `~/.local/bin/dolphin` | Verweis auf das Startskript |
| `~/.local/share/applications/org.kde.dolphin.desktop` | vorhandener KDE-Launcher mit angepasstem Startbefehl |
| `~/.local/share/icons/ralleur-rounded-folders/` | kleines SVG-Overlay für Ordner |
| `~/.config/kioworkerrc` → `Icons/Theme` | dieselbe Ordnerbasis für den nativen KIO-Vorschaudienst |
| `~/.local/share/dbus-1/services/org.kde.dolphin.FileManager1.service` | Öffnen über FileManager1 |
| `~/.config/systemd/user/plasma-dolphin.service.d/ralleur-header.conf` | derselbe Startweg bei D-Bus-/systemd-Aktivierung |

XDG-Pfade werden für Konfiguration, Anwendungsdaten und Sicherungen berücksichtigt.
Die Bibliothek und Startskripte liegen bewusst benutzerlokal unter `~/.local`.
Die Installation verändert weder Systempakete noch Caelestia, Taskbar oder globale
Farben. Bereits laufende Dolphin-Fenster brauchen einen regulären Neustart.

## Bauen und installieren

Benötigt: CMake, Ninja, C++17-Compiler, Python 3, Qt 6 Widgets/DBus/Test/Concurrent,
PdfWidgets/MultimediaWidgets sowie KF6 WindowSystem, KIOFileWidgets, XmlGui und IconThemes.

```bash
python /home/USER/ralleurOS/kde-customizations/dolphin-header/generate_icons.py
cmake -S /home/USER/ralleurOS/kde-customizations/dolphin-header \
  -B /home/USER/ralleurOS/.cache/dolphin-header-build \
  -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build /home/USER/ralleurOS/.cache/dolphin-header-build -j 4
ctest --test-dir /home/USER/ralleurOS/.cache/dolphin-header-build --output-on-failure
python /home/USER/ralleurOS/kde-customizations/dolphin-header/install.py \
  --build /home/USER/ralleurOS/.cache/dolphin-header-build
```

Der Installer sichert vorherige Dateien und nennt das erzeugte Manifest. Eine
bereits vorhandene fremde `~/.local/bin/dolphin`-Datei wird nicht überschrieben.
Bibliotheken werden atomar ersetzt, damit ein laufender Prozess seine bisherige
Kopie weiter verwenden kann.

## Prüfung

Die Qt-Tests prüfen echte Knopfklicks und Fensterzustände, Schließen mit einer
ablehnenden Rückfrage, mehrere Fenster, unveränderte Dialoge, Toolbar-Umbau und
Mouse-Move/Click mit KDEs wirklichem Places-Delegate. Die Tests verwenden eigene
temporäre XDG-Verzeichnisse. Zusätzlich werden echte transparente Eckpixel nach
später Anbindung, Größenänderung und Maximieren/Wiederherstellen sowie das
Alphapuffer-Format beim Plugin-Start geprüft.
Die Farbtests prüfen Vererbung, neue Home-Ordner, Umbenennen, Link-Ziele,
native KDE-Metadaten und neu angelegte Ordner im laufenden Dateiwächter.
Die Rückbauprüfung erhält eigene Bookmark-Änderungen und manuell bearbeitete
Ordner-Metadaten.
Die Tastaturtests prüfen Vorschau-Toggle, Tastenwiederholung, Escape, leere und
gewechselte Auswahl, getrennte Split-Ansichten, Bild/PDF/Text, unberührte
Zwischenablage und normale Leerzeichen in Eingabefeldern.

`preview_probe` ist ein ausschließlich für eine explizite Live-Prüfung gebautes
Qt-Testplugin (`cmake --build … --target preview_probe`). Es wird niemals
installiert oder vom normalen Wrapper geladen. Mit separaten XDG-Verzeichnissen,
`QT_QPA_GENERIC_PLUGINS=ralleurdolphin,ralleurpreviewprobe` und explizitem
`RALLEUR_PREVIEW_PROBE_DIR` prüft es dieselben Tastendrücke gegen das echte
System-Dolphin und schreibt Ergebnis und Vorschaubild in das angegebene Verzeichnis.
Mit `RALLEUR_THEME_PROBE=1` wechselt dieselbe laufende Testinstanz zusätzlich
zwischen zwei dunklen Farbpaletten und einer hellen Palette. Die Farbrollen
der echten Datei-, Pfad- und Tableiste werden geprüft und Screenshots erzeugt.
Die Prüfung verwendet separate XDG-Dateien und verändert nicht das Desktop-Theme.

`tests/live_check.py` prüft ein bewusst ausgewähltes Testfenster auf dem laufenden
KWin. Es maximiert, restauriert, minimiert und restauriert dieses Fenster. Für den
Minimierungszustand wird **KWin** abgefragt: Qt meldet ihn unter Wayland nicht
zuverlässig über `QWidget::isMinimized()` zurück. Die Prüfung verändert keine
Dateien im geöffneten Ordner. Sie benötigt die konkrete KWin-Fenster-UUID.

## Rückbau

Alle Dolphin-Fenster zuerst regulär schließen. Dann das beim Installieren
ausgegebene Manifest verwenden:

```bash
python /home/USER/ralleurOS/kde-customizations/dolphin-header/install.py \
  --restore /absoluter/pfad/zum/manifest.json
```

Der Rückbau verweigert das Überschreiben nachträglich bearbeiteter verwalteter
Dateien. Native Dolphin-Einstellungen werden als Referenz mitgesichert, aber
nicht pauschal zurückgesetzt; die bisherigen Layout-Anpassungen bleiben erhalten.
Die gezielt gesetzten Icon-Theme-, KIO- und Ordner-Vorschau-Einstellungen werden bei
unverändertem Wert auf den gesicherten Ausgangswert zurückgesetzt.

Ein einzelner Start ohne die Erweiterung ist mit
`RALLEUR_DOLPHIN_HEADER=0 /home/USER/.local/bin/ralleur-dolphin` möglich,
nachdem bestehende Dolphin-Prozesse regulär beendet wurden. Ein direkter Start
von `/usr/bin/dolphin` verwendet ebenfalls das unveränderte Systemprogramm.

Eigener Code: MIT. Die Systemkomponenten und vorhandenen Icon-Themes behalten
ihre jeweiligen Lizenzen.
