# flausen. — kinetic studies / Light & Dark

Caelestia verwendet die finalen 4K-PNGs aus [light/png/](light/png/) und
[dark/png/](dark/png/). Die folgenden Angaben beschreiben die frühere
Vektorsammlung und ihre generierten Exporte. Für eine erneute Generierung
`--output` mit einem separaten Zielordner verwenden.

24 eigenständige Kompositionen mit je einer Light- und einer Dark-Variante:
48 Hintergründe insgesamt. Die ursprünglichen 16 Motive erhalten passende
Gegenstücke; acht neue Kompositionen ergänzen die Serie.

Neu: Tidal Balance, Soft Collision, Thread Atlas, Diagonal Silence, Folded
Horizon, Suspended Duet, Quiet Assembly und Kinetic Score. Die Serie umfasst
schwebende Assemblagen, Papierüberlagerungen, gedrehte Landschaften, Konturen
und gebrochene Strömungen. Die Varianten behalten ihre Komposition und erhalten
gezielt angepasste Flächen, Konturen, Fäden und Papiertiefen.

## Ordner und Archive

`~/Bilder/Wallpapers/flausen-4k/` enthält:

- `light/svg/` und `light/png/`: 24 helle Originale und 4K-Exporte.
- `dark/svg/` und `dark/png/`: 24 dunkle Originale und 4K-Exporte.
- `light/collection-preview.jpg`, `dark/collection-preview.jpg`: eigene Übersichten.
- `collection-preview.jpg`: Gesamtübersicht aller 48 Varianten.
- `collection.json`: Titel, Familienzuordnung, Modus und Dateipfade ab Sammlungswurzel.
- `light/collection.json`, `dark/collection.json`: jeweilige Teilmenge, ebenfalls mit
  Pfaden ab der Sammlungswurzel.
- `verification.json`: Renderprüfung und SHA-256-Prüfsummen.
- `flausen-light-4k.zip`, `flausen-dark-4k.zip`: eigenständig verwendbare Teilarchive.
- `flausen-wallpapers-4k.zip`: vollständiges Set.

Die ursprüngliche Sammlung wurde vor der Umstellung als eigener Nachbarordner
bewahrt; der genaue Pfad steht in `previous-collection.txt`.

## Formen und Herstellung

Die vier Originalpfade liegen als unveränderter Snapshot in `geometry.json`
(Quelle: `website/src/geometry.json`). Nur Position, Drehung, einheitlicher Maßstab
und Materialdarstellung ändern sich. Blau #2563C9, Orange #E56D2F, Petrol #278F8B
und Braun #8F5B40 bilden die Grundpalette. Ruhige neutrale und abgetönte Flächen
ergänzen sie. Keine Schriftzüge in den Motiven.

Generieren mit Python, Pillow und librsvg (`rsvg-convert`):

```sh
python3 kde-customizations/wallpapers/flausen/create_collection.py
# Alternativ:
python3 kde-customizations/wallpapers/flausen/create_collection.py --output /ziel/flausen-4k
```

Alle SVGs bestehen aus nativer Vektorgeometrie, ohne eingebettete Bitmaps,
Filter, Schriften, externe Assets oder Skripte. Jeder PNG-Export wird auf
3840 × 2160 und volle Deckkraft geprüft. Light-Flächen haben eine relative
Luminanz über 0,65, Dark-Flächen unter 0,08. Die unveränderten Hauptformen
behalten ihre Markenfarben; helle Papierformen sind als bewusste Akzente möglich.

Prüfung: 48 SVGs geparst und gerendert; 48 PNGs geprüft, alle unterschiedlich;
24 vollständige Motivpaare; drei Archive auf Integrität und enthaltene
Manifestpfade kontrolliert. Beide Übersichten und ausgewählte große Exporte
visuell geprüft. Der Generator ändert keine Desktop-Einstellungen.

Als Wallpaper-Ordner können in Caelestia `flausen-4k/light/png` oder
`flausen-4k/dark/png` gewählt werden. Die Aufteilung richtet keine automatische
Umschaltung mit dem OS-Farbschema ein.
