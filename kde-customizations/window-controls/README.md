# Einheitliche Fensterknöpfe

Fenster verwenden rechts **Strich, Viereck und X**.
Die Knöpfe haben 30 × 30 logische Pixel, 6 Pixel Zwischenraum und 5 Pixel
Abstand zum rechten Rand. Die Zeichen liegen in einem 16 × 16-Pixel-Feld
mit 1,2 Pixel Strichstärke. KWin und Dolphin verwenden dafür denselben
Renderer aus `controls.h`; GTK erhält geometrisch entsprechende SVG-Silhouetten.
Hover-Flächen sind abgerundete 28-Pixel-Rechtecke mit 12 % Deckkraft
(gedrückt 20 %), inaktive Zeichen verwenden 55 % Deckkraft. Auch beim Wiederherstellen
bleibt das Viereck erhalten; die Funktion und der Tooltip wechseln wie gewohnt.

- KWin: eigene, benutzerlokale Darkly-Dekoration mit geändertem Zeichenpfad für
  Minimieren und Maximieren. Rundungen, Schatten, Farben und Fensterlogik bleiben
  bei Darkly. Die Knopfleiste enthält nur die drei gewünschten Aktionen.
- Qt/Dolphin/Dateidialoge: kleines vererbendes Icon-Theme für `window-minimize`,
  `window-maximize`, `window-restore` und `window-close`, samt symbolischen Namen.
  Dolphins vorhandenes Ordner-Theme erbt dieses Overlay. KDE färbt SVGs weiterhin
  anhand der Palette ein.
- GTK3/4: ergänzende CSS-Regeln für native und Chromium-Titelknöpfe, einschließlich
  Hover, inaktivem und maximiertem Zustand. Die übrige Gestaltung bleibt erhalten.

KWin übernimmt die Dekoration im laufenden Betrieb. Bereits laufende Apps mit
selbst gezeichneter Kopfzeile und zwischengespeicherten Icons (insbesondere
Dolphin/GTK) benötigen ein erneutes Öffnen. Apps mit vollständig eigener
Fenstersteuerung können die Desktop-Vorgaben umgehen.

## Bauen und installieren

Basis: [Darkly v0.5.42](https://github.com/Bali10050/Darkly/tree/v0.5.42),
Revision `812546ed69ff7e55cf3cb0fe2b79379e85101bef`. Der Patch bleibt klein;
Upstream-Quellen und deren Lizenzen liegen im Build-Checkout. Erforderlich sind
Darklys Qt6/KF6-Bauabhängigkeiten einschließlich KDecoration3.

```sh
python kde-customizations/window-controls/prepare.py .cache/darkly-window-controls-src
cmake -S .cache/darkly-window-controls-src -B .cache/window-controls-build -G Ninja \
  -DBUILD_QT5=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build .cache/window-controls-build --target darklydecoration -j 4
python kde-customizations/window-controls/install.py --build .cache/window-controls-build
```

Die Bibliothek liegt unter `~/.local/lib/ralleur/window-controls/`. Jede Bibliotheksversion bekommt
einen Inhalts-Hash im Dateinamen, damit KWin eine neue Fassung sofort lädt. KWin erhält
einen relativen Plugin-Pfad, der auf diese private Bibliothek zeigt: KPluginMetaData
stellt jedem Plugin-Namen einen Namespace voran; der Pfad löst diesen Präfix auf.
Dadurch ist weder ein Systemeingriff noch ein KWin-Neustart nötig.
Das Paket erscheint als „Ralleur“, wenn es über einen passenden Qt-Plugin-Suchpfad
entdeckt wird. Die direkte Auswahl in `kwinrc` funktioniert ohne diesen Suchpfad.

Das Installationsmanifest sichert ursprüngliche Dateien und Einstellungen unter
`~/.local/state/ralleur-desktop-tweaks/window-controls.json`. Wiederholte Installation
bewahrt die ursprüngliche Rückbaubasis und bricht bei zwischenzeitlich geänderten
verwalteten Dateien ab. Bibliotheken werden atomar ersetzt.

## Rückbau

```sh
python kde-customizations/window-controls/install.py --restore
```

Der Rückbau stellt nur weiterhin unveränderte Dateien/Einstellungen wieder her.
Danach betroffene Apps erneut öffnen.

## Prüfung

Auf KWin 6.8.2 mit Qt 6.12 geprüft: Laden des privaten Plugins über
`supportInformation`, leere linke Knopfleiste und rechte Reihenfolge `IAX`,
sichtbare Symbole in Konsole, neu geöffnetem Dolphin und GTK3/GTK4-Proben.
GTK-Silhouetten verwenden gefüllte Pfade, da GTK symbolische SVG-Strokes
abweichend rendert. Die CSS-Selektoren übersteuern auch die spezifischen
Headerbar-Regeln der installierten Themes. Die Icon-Auflösung
von Dolphin zeigt auf das neue Overlay. Installation, erneute Installation und
Rückbau wurden mit isolierten Benutzerpfaden geprüft.

Änderungen am gemeinsamen Renderer erfordern zusätzlich einen Neubau und
eine Installation von `../dolphin-header`. Da beide Installer das vererbende
Icon-Theme berühren, zuerst Fensterknöpfe zurückbauen, dann Dolphin installieren,
anschließend Fensterknöpfe installieren. Laufende Apps werden dabei nicht beendet.

## PhotoCraft (Flatpak)

PhotoCraft 0.18 zeichnet unter KDE eigene Breeze-Pfeile in seiner Menüleiste.
Diese sind unabhängig von KWin und den GTK-Regeln. Die unterstützte Einstellung
`interface.systemTitleBar=true` in seinen Flatpak-Voreinstellungen deaktiviert
seine eigene Fenstersteuerung und verwendet unsere echte KWin-Dekoration.
Dadurch stimmen auch Knopfgröße, Abstände und Hover-Verhalten überein.
Quelle: [PhotoCraft-Titelleiste](https://github.com/storytold/photocraft/blob/v0.18.0/crates/ui-egui/src/panels/titlebar.rs),
[Systemtitelleisten-Einstellung](https://github.com/storytold/photocraft/blob/v0.18.0/apps/photocraft/src/main.rs).

PhotoCraft vorher regulär schließen (es schreibt seine Einstellungen beim Beenden):

```sh
python kde-customizations/window-controls/configure_photocraft.py
# Rückbau, ebenfalls bei geschlossenem PhotoCraft:
python kde-customizations/window-controls/configure_photocraft.py --restore
```

Nur dieser Einstellungswert wird geändert. Die vorige Belegung wird separat
unter `~/.local/state/ralleur-desktop-tweaks/photocraft-window-controls.json`
gesichert. Anschließend PhotoCraft über seinen normalen Starter öffnen.
Die neu geöffnete Flatpak-App wurde auf dem laufenden KWin visuell geprüft:
Systemtitelleiste mit Strich/Viereck/X, keine zusätzlichen Pfeilknöpfe im Menü.
