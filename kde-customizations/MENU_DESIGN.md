# Proportionsregeln für Desktop-Menüs und Popovers

Am 2. November 2026 anhand des Update-Popovers und der hellen/dunklen
Referenz-Mocks mit dem Nutzer abgestimmt. Diese Regeln sollen bei zukünftigen
Menüänderungen im Projekt wiederverwendet werden. Verbindliche Markenregeln in
[BRAND_SPEC.md](../branding/flausen/handoff/BRAND_SPEC.md) gelten weiterhin.

## Warum der Mock ruhiger wirkt

Die Größen der gelieferten Bilddateien täuschen. Vergleicht man ausschließlich
die Popover-Flächen bei gleicher Außenbreite, ist die alte Umsetzung deutlich
höher und ihre Schrift relativ zu den Icons größer. Sie kombiniert die Dichte
einer großen Textansicht mit den Icons und Außenrändern eines kompakten Menüs.
Das führt zu vielen ähnlich starken Elementen und einem unnötig langen Blickweg.

Bei einer normierten Breite von 514 Bildpixeln misst die vom Nutzer gelieferte
reale Ansicht 872 Pixel Höhe, die ausgeschnittene Referenz etwa 722 Pixel.
Die alte Ansicht ist damit etwa 21 % höher. Ihre App-Icons sind bereits ungefähr
so groß wie die Referenz-Icons; eine globale Verkleinerung würde sie zu klein
machen. Die Korrektur muss die einzelnen Größenverhältnisse verändern.

Die Referenz verbindet größere seitliche Freiflächen mit kleineren Texten und
kompakteren Zeilen. Sie hat **weniger ungenutzte vertikale Fläche und mehr
horizontale Ruhe**. Launcher und Spiele bleiben durch gemeinsame Karten verbunden,
während Abstand und Abschnittstitel verschiedene Gruppen klar trennen.
Die Kopfaktionen sitzen auf Höhe des Titels; die Unterzeile verschiebt sie nicht.

## Wiederverwendbare Ausgangswerte

Für ein Popover mit etwa 520 logischen Pixeln Außenbreite, einschließlich seiner
äußeren Innenränder. Werte beschreiben die **fertig gerenderte Oberfläche**,
nicht QML-Punktgrößen. `font.pointSize` und Pixelmaße nicht miteinander verwechseln.
Die Werte bei anderen Menübreiten und Bedienanforderungen proportional anpassen.

| Rolle | Ausgangspunkt | Beziehung |
| --- | --- | --- |
| Hauptbeschriftung | 16 px wie im Startmenü | Ruhiger Grundmaßstab, nicht jede Zeile als Überschrift |
| Titel | ca. 27 px | Etwa 1,6–1,7 × Haupttext |
| Sekundärzeile | 12–13 px | Etwa 0,78–0,82 × Haupttext |
| Abschnittstitel | 15–16 px | Leicht kleiner als Haupttext, zurückhaltende Farbe |
| App-Icon | 40–44 px sichtbare Form | Etwa 2,5–2,8 × Haupttext; nicht mit dem Text schrumpfen |
| Statussymbol | 18–23 px sichtbare Form | Klar lesbar, optisch leichter als das App-Icon |
| Äußerer Seitenrand bis Karte | 28–32 px | Größer als der Karten-Innenrand |
| Karten-Innenrand | 16–20 px | Eigene konsistente Icon- und Textspalten |
| Einfache App-Zeile | 52–56 px hoch | Icon mit ausreichend Freiraum; Klickfläche erhalten |
| Launcher mit Untertitel | 62–66 px hoch | Textblock und Icon vertikal als Einheit zentrieren |
| Eingerückte Kindzeile | Mindestens ca. 44 px hoch | Unterordnung durch Einrückung, nicht winzige Schrift |
| Abstand zwischen verwandten Karten | 12–14 px | Kleiner als der Abstand zu einem neuen Abschnitt |
| Wechsel zu einem neuen Abschnitt | ca. 20–24 px bis zum Titel | Nähe vermittelt Zugehörigkeit |
| Titel bis zugehörige Karte | ca. 8–12 px | Abschnittstitel nicht zwischen Gruppen schweben lassen |
| Primärknopf | 36–40 px hoch | Text kleiner als Zeilenlabel; Breite nach Inhalt und Sprache |

Diese Werte sind **keine Vorschrift, das Update-Menü-Verhältnis auf andere
Menüinhalte zu erzwingen**. Für sieben Statuszeilen liegt die Referenz bei einem
Höhen-/Breitenverhältnis von etwa 1,40; andere Inhalte benötigen andere Höhen.
Lange deutsche Texte, große Schrift-Einstellungen und kleinere Displays müssen
weiter funktionieren. Keine Übersetzung kürzen oder Text verkleinern, nur um eine
Bildabmessung exakt zu treffen.

## Ausrichtung und optische Korrekturen

- Titel und Abschnittstitel dürfen etwas weiter eingerückt sein als die Karten.
  Karten selbst teilen dieselbe linke und rechte Kante.
- Namen, Untertitel und Statussymbole verwenden feste gemeinsame Spalten.
  Die rechte Statusspalte springt nicht je nach Textlänge.
- Kopfknöpfe oben an der **Titelzeile** ausrichten. Ihre unsichtbare Bedienfläche
  kann größer sein als das gezeichnete Icon.
- Kindzeilen werden eingerückt. Der Controller ist ein erkennbares Icon, kein
  verkleinertes Satzzeichen. Der Haupttext behält eine ähnliche Schriftgröße.
- Trenner in Launcher-Karten beginnen am Ende der Icon-Spalte; Trenner in der
  App-Liste beginnen an der Textspalte. Die Linie organisiert den Inhalt, statt
  die gesamte Kartenbreite zu durchschneiden.
- Transparente Ränder in Icon-Dateien berücksichtigen. Gleiche Dateiabmessungen
  ergeben nicht automatisch gleich große sichtbare Logos. Keine Markenformen
  verzerren oder zur geometrischen Gleichheit unkenntlich beschneiden.
- Rundungen und feine Konturen ordnen sich dem Inhalt unter. Akzentfarbe für
  verfügbare Updates und die primäre Aktion reservieren. Zustände zusätzlich
  durch Haken/Pfeil/Fragezeichen kenntlich machen.
- Glas darf Lesbarkeit vor echten Fenstern nicht aufheben. Helle und dunkle
  Materialien an das Theme binden; nicht nur auf ruhigem Wallpaper beurteilen.

## Umsetzung und Prüfung

Das Update-Menü definiert separate typografische Rollen (`bodyPointSize`,
`titlePointSize`) und behält den Kalender-/Popover-Maßstab 1,15. Gegenüber der
vorherigen Fassung wurden Haupttexte um 20 % verkleinert, die App-Icons jedoch
beibehalten. Karten erhielten mehr Seitenrand und gezielt kürzere Zeilen.
Der Titel und die Kopfaktionen wurden neu aufeinander ausgerichtet.

Vor weiteren Änderungen:

1. Außenfläche der Referenz bestimmen und beide Flächen auf gleiche Breite bringen.
2. Text/Icon-Verhältnis, Ränder, Spalten und Abstandsgruppen vergleichen.
3. Den größten Unterschied zuerst korrigieren; nicht pauschal die ganze UI skalieren.
4. In der echten Shell prüfen: Lesbarkeit, lange Beschriftungen, Klickflächen,
   unbekannte Zustände und Platz auf dem Bildschirm. Details/Backend erhalten.
5. Ergebnis bei gleicher Breite erneut ansehen. Falls ein gewünschtes Verhältnis
   mit Nutzbarkeit kollidiert, die Nutzbarkeit erhalten und die Abweichung benennen.

Belege und direkte Vergleichsansicht:
[Proportionsvergleich](taskbar/evidence/update-hub-proportions-comparison.png),
[Prüfwerte](taskbar/evidence/update-hub-proportions-check.json).

## Anwendung auf Netzwerk-Overlays

Die Regeln gelten inzwischen auch für WLAN und Ethernet einschließlich VPN,
Tailscale, Verbindungsdetails und Passwortdialog. Hauptschrift und Titel verwenden
dieselben Rollen wie das Update-Menü; Icons und Schalter haben eigene geometrische
Maße. Netzwerknamen erhalten eine feste Textspalte und Platz für Schlösser und
Status auf der rechten Seite. Überschriften können bei vergrößerter Schrift umbrechen.

Bei einer stark verkleinerten alten Fläche vorhandene Kompensationswerte beachten:
Im Netzwerkbereich wurde der bekannte alte Schriftaufschlag +0,27 beim Wechsel
auf Mindestmaßstab 1,15 gezielt migriert. Das ist keine allgemeine Regel, individuelle
Schriftpräferenzen zurückzusetzen. Vorherigen effektiven Schriftmaßstab messen,
Änderungen begründen und sichern; andere Werte erhalten.

Details und reproduzierbare isolierte Vorschauen:
[Netzwerk-Overlays](taskbar/network-popover/README.md).

## Anwendung auf Bluetooth

Auch das Bluetooth-Popout verwendet die gemeinsame Schriftbasis und das feste
Spaltenraster. Geräte-Icons bleiben geometrisch skaliert; Namen, Status, Akku
und Aktionen sind getrennte Rollen. Verbindungsaufbau und große Schrift dürfen
Zeilen mitwachsen lassen. Fehlender Adapter und ausgeschaltetes Bluetooth sind
explizite Zustände statt leerer Karten. Der bekannte alte Kompensationswert +0,26
wurde gezielt migriert; andere Schriftpräferenzen bleiben erhalten.

Implementierung und Vorschauen: [Bluetooth-Overlay](taskbar/bluetooth-popover/README.md).

## Gemeinsame Schrift- und Materialbasis: Startmenü als Referenz

Nach dem Proportionsabgleich wurde das Startmenü als Referenz für Schrift und
Material festgelegt. Die gemeinsame Definition liegt in
`taskbar/menu-style/MenuStyle.qml`, der Textbaustein in `MenuText.qml`.
Neue Menüanpassungen sollen diese Rollen verwenden und keine parallelen
Farb-/Schriftwerte kopieren.

- Systemschrift des Startmenüs (auf diesem Rechner Noto Sans), statt der
  bisherigen GoogleSansFlex-Beschriftungen in den Popouts.
- Haupttext 16 px, Nebenzeilen etwa 13 px, kleine Beschriftungen etwa 12 px.
  Die Umrechnung ergibt bei Standard-Schriftmaßstab 1,15 einen Haupttext von 12 pt.
  Der separate Nutzer-Schriftmaßstab bleibt wirksam.
- Außenfläche, Transparenz, Kontur, Haupt-/Nebenfarbe und Kartenfüllung stammen
  aus derselben Definition wie im Startmenü. Helle und dunkle Werte sind hinterlegt.
- Geometrie bleibt eine eigene Ebene: Kartenmaße, Innenränder, Einrückungen,
  Icongrößen und Zeilenhöhen beim Wechsel von Schrift/Material erhalten.
  Im Update-Menü reservieren Titelblock und Abschnittstitel ihren bisherigen Platz,
  damit kleinere Schrift keine Karten nach oben zieht.
- Startmenü und schwebende Taskleisten-Popouts verwenden bereits getrennte
  Regionen desselben KWin-Blur-Effekts. Material angleichen; keine neue globale
  Blur-Stärke einstellen oder einen zusätzlichen Vollbild-Blur pro Popout starten.

Der ältere Haupttext von ca. 13,5 pt beschreibt den vorherigen Proportionsschritt;
aktuell gilt die gemeinsame Startmenü-Basis. Details und Nachweis der unveränderten
Kartenpositionen: [gemeinsamer Menüstil](taskbar/menu-style/README.md).

## Anwendung auf Audio, Akku und Kalender

Audio und Akku nutzen dieselben Schriftrollen und das Kartenraster bei Mindestmaßstab
1,15. Lautstärke- und Energieprofil-Bedienflächen behalten ihre Funktionen; Icons
werden unabhängig von der Schrift skaliert. Der Kalender behält seine breitere
Fläche, sein Datumsraster und die Monatsnavigation. Dafür eigene gemeinsame
Menübausteine verwenden, statt globale Slider anderer Ansichten umzubauen.
Details: [restliche Overlays](taskbar/remaining-overlays/README.md).

## Desktop-Kontextmenü: Dolphin als ausdrückliche Referenz

Für das Desktop-Kontextmenü wurde anschließend ausdrücklich das native
Dolphin-Kontextmenü als 1:1-Stilreferenz gewählt. Seine Kontextrollen stehen
eben den Popover-Rollen in `MenuStyle`: native System-Menüschrift, Radius 14 px,
8 px Innenrand, Zeilenradius 9 px und identische helle/dunkle Glas- und Hoverfarben.
`Menu.dolphinContextStyle` schaltet dies ausschließlich beim Desktopmenü ein.
Andere Menüs behalten ihre bisherigen Rollen. „Menü anpassen“ steht unabhängig
von der gespeicherten Reihenfolge zuletzt, kleiner und kursiv.

## Screenshot und Zwischenablage

Auch Screenshot- und Zwischenablage-Popouts nutzen die gemeinsamen Schrift- und
Materialrollen, den Maßstab 1,15 und das Kartenraster. Die Screenshot-Utility-Karte
bleibt eigenständig; nur die Taskleisten-Version und ihre Galerie-/Dropdowntexte
werden angepasst. Große Schrift darf die Titelhöhe vergrößern; Kopfaktionen und
Badge bleiben an der ersten Titelzeile ausgerichtet. Details und native
Beispieldaten-Prüfung: [Screenshot/Zwischenablage](taskbar/capture-clipboard-style/README.md).


## Erste Rauchglas-Referenz: Kalender

Der Kalender ist seit dem 3. November 2026 die erste Umsetzung des gelieferten
Rauchglas-Mocks zur Abstimmung des künftigen Standards. Eine einzelne gemeinsame
Glasfläche, ein linksbündiger Titel, kompakte Kopfaktionen, großzügige gleichmäßige
Spalten und sparsame Akzentfarbe bestimmen diese Referenz. Das Datum erhält den
blauen Kreis; Wochenenden und angrenzende Monate treten zurück. Die gemeinsame
Schrift- und Materialquelle bleibt `MenuStyle`/`MenuText`; kein eigenes Glasprofil
und keine globale Blur-Änderung. Die Kalender-Titelrelation von etwa 1,65 bezieht
sich auf die größeren Datumszahlen. Andere Menüs erst nach ausdrücklichem Auftrag
übertragen. Details und Vergleich bei gleicher Breite:
[Kalender-Referenz](taskbar/remaining-overlays/README.md#kalender-erste-rauchglas-referenz).


Nach dem ersten Kalender-Abgleich wurde ausdrücklich nur dort ein rauchigeres
Material mit stärkerer lokaler Unschärfe beauftragt. Dafür ist `calendarSurface`
in `MenuStyle` der vorläufige Materialwert; `CalendarGlass` begrenzt zusätzliche
native Blur-Durchgänge auf den Kalender. Die übrigen Menüs und die globale
KWin-Blur-Konfiguration behalten ihre bisherigen Werte. Diese Ausnahme ersetzt
noch keine gemeinsame Materialfreigabe für andere Menüs.


## Freigabe und Übertragung auf die gesamte Taskbar

Der Nutzer hat den transparenten Kalender-Feinabgleich ausdrücklich freigegeben
und die Übertragung auf Taskbar und alle Taskbar-Overlays beauftragt. Seitdem gilt
dort `MenuStyle.taskbarSurface`: dunkel `#b823292e` (72,2 %), hell `#e6e9ecef`.
`TaskbarGlass` enthält die acht lokalen nativen Blur-Durchgänge einmalig; es ersetzt
die bisherige Kalender-Sonderimplementierung. Layout, Typografie, Karten und Radien
bleiben unabhängig vom Material. Keine globale Blur-Stärke ändern. Für neue
Taskbar-Popouts diese gemeinsame Quelle verwenden. Andere Desktop-Flächen behalten
ihre bisherigen Materialrollen, bis sie ausdrücklich beauftragt werden.
[Umsetzung, Installation und Live-Prüfung](taskbar/menu-style/README.md#freigegebener-rauchglas-standard-für-die-taskbar).


## Rauchglas animieren, ohne Render-Ressourcen neu anzulegen

Die anschließende Performanceprüfung hat gezeigt, dass acht neu erzeugte und
laufend vergrößerte Hilfsfenster pro Fläche die Animationen stark bremsen.
Die produktive Taskbar verwendet deshalb `TaskbarGlass` mit einem begrenzten,
vorgewärmten Pool und stabilen Puffergrößen. Nur der sichtbare Blur-Ausschnitt
folgt der Animation. Ungenutzte Flächen bleiben mit leerer sichtbarer Region
unter den Anwendungen; auch im Vollbild liegen sie dort. Nicht pro Menü neue
Blur-Fenster aufbauen oder während der Animation native Puffergrößen nachführen.
Kurzlebige Untermenüs über `TaskbarDropdownGlass`/`TaskbarGlassState` an den
bestehenden Pool anbinden. Die globale KWin-Stärke bleibt unverändert.
Sichtprüfung und Funktionsprüfung ersetzen keine Frame-Zeit-Gegenprobe.
[Messung und Bildvergleich](taskbar/menu-style/README.md#performance-optimierung-produktiver-stand).


## Übertragung auf Startmenü und Dashboard

Auf ausdrücklichen Auftrag gelten Material und optimierter Pool nun auch dort.
`MenuStyle.smokeSurface` ist die gemeinsame Definition für Taskbar, Startmenü und
Dashboard; bestehende Rollen verweisen darauf. Keine weitere Materialkopie
anlegen. Das Dashboard-Overlay referenziert die zentrale Definition per Symlink.
Die vorhandenen Layout-, Schrift-, Karten- und Animationswerte bleiben erhalten.
Beide Panels haben lokale, vorgewärmte `TaskbarGlass`-Pools; der alte
bildschirmfüllende Launcher-Blur und seine globale Einstellungs-Lease werden
nicht mehr beim Öffnen aktiviert. Andere Backdrop-Clients bleiben eigenständig.
Layout-/Fontdeklarationen und Außenmaße wurden vorher/nachher kontrolliert,
Animationen zusätzlich mit einer Gegenprobe ohne Hilfsflächen gemessen.
[Prüfung und aktuelle Installation](taskbar/menu-style/README.md#startmenü-und-dashboard-gemeinsames-rauchglas-ohne-layoutänderung).


## Capture: Referenz für dezente Primäraktionen

Das Screenshot-Overlay wurde auf ausdrücklichen Auftrag am Capture-/Galerie-Mock
abgeglichen. Der neue Primärknopf nutzt die zentrale `MenuPrimarySurface` aus
`taskbar/menu-style/`: einen sanften vertikalen Blauverlauf, feine Außenkontur und
innere Lichtkante. Split-Aktionen haben eine gemeinsame Außenfläche und eine
zurückhaltende Trennlinie. `MenuStyle.primaryTop`, `primaryBottom`, `primaryEdge`
und `primaryLight` sind die gemeinsame Quelle; Hover und Disabled bleiben eigene
Zustände. Andere Menüs erst auf Auftrag übertragen. Rauchglas bleibt unverändert
an `MenuStyle.taskbarSurface` und den bestehenden Pool gebunden.
[Umsetzung und Vergleich](taskbar/capture-clipboard-style/README.md#screenshot-rauchglas-und-primäraktion-3-november-2026).


## Freigabe: Capture-Verlauf als gemeinsamer Control-Standard

Der Nutzer hat die Übertragung anschließend ausdrücklich auf alle blauen Controls
inklusive Settings beauftragt. Für deckende blaue Bedienflächen jetzt
`PrimaryControlFill` bzw. direkt `MenuPrimarySurface` verwenden. Keine lokalen
Verlaufskopien und keine Änderung von Geometrie oder Typografie dafür einführen.
Aus-, Disabled-, Hover- und Fokuszustände erhalten; andere Akzentfarben bleiben
an die gewählte Palette gebunden. Auch eigene Popover-Schalter und eingebettete
KDE-Controls in den Settings verwenden dieselbe Quelle.
[Abdeckung, Installation und Prüfung](taskbar/menu-style/README.md#freigegeben-als-standard-für-blaue-controls).


## Dolphin-Kontextmenü: gemeinsames Rauchglas

Auf ausdrücklichen Auftrag nutzt jetzt auch das native Dolphin-Kontextmenü
`MenuStyle.smokeSurface`. Die Qt-Widgets-Brücke wird beim Build aus dieser
gemeinsamen Quelle erzeugt. Acht lokale native Blur-Durchgänge ergänzen die
gerundete Menüfläche; vorgewärmte, eingabefreie Tooltip-Flächen behalten ihre
Puffer über das Schließen hinaus. Schrift, Geometrie und native Aktionen bleiben
erhalten. Der bestehende Hintergrund-Backdrop bleibt eigenständig; keine neue
globale Blur-Stärke. Das Desktop-Kontextmenü wird nicht mit umgebaut.
[Umsetzung und Wayland-Prüfung](dolphin-header/README.md#kontextmenü).


## Desktop-Benachrichtigungen: einzelne Rauchglaskarten

Auf ausdrücklichen Auftrag folgen die schwebenden Meldungen dem Stapel-Mock.
Jede Karte nutzt `MenuStyle.smokeSurface` und die gemeinsame Systemschrift;
Metadaten, Titel, Inhalt und Aktionen sind getrennte Rollen. Die Sammelfläche
entfällt. Ein gemeinsamer stabiler Blur-Pool pro Monitor verarbeitet die einzelnen
Kartenregionen; keine zusätzlichen Pools je Meldung und keine globale Blur-Änderung.
Archiv und Benachrichtigungs-Popout behalten ihre bisherige Gestaltung.
[Umsetzung und Vergleich bei gleicher Breite](taskbar/notification-style/README.md).


## Wetter-Popover: Rauchglas mit Stundenkurve

Das Taskbar-Wetter folgt auf Auftrag dem gelieferten Wetter-Mock. Standort und
Aktualisieren bilden eine Kopfzeile; Wetteranzeige, Kennzahlen und Stundenkurve
sind klar getrennt. Material und Schrift bleiben bei `MenuStyle`/`MenuText`,
der vorhandene stabile Taskbar-Blur-Pool bleibt erhalten. Sieben gleichmäßige
Stundenspalten teilen sich die Positionen für Temperaturpunkte, Zeiten und Symbole.
Schmale Ansichten zeigen fünf Spalten und gestapelte Kennzahlen. Dashboard nicht
mit umgestalten. [Quelle und Breitenvergleich](taskbar/weather-popover/README.md).
