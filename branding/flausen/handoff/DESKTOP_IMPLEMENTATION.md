# Technische Integration: flausen. auf Caelestia/Hyprland

Das zuvor entwickelte Desktop-Rice bleibt in Aufbau und Verhalten bestehen. **Diese Übergabe ergänzt/ersetzt nur die Produktidentität.** Die beiden PNGs unter `reference/` zeigen die beabsichtigte UI-Komposition, sind **nicht** als Wallpaper zu verwenden.

## 7 klare Arbeitspakete

| Paket | Quelle / Layer | Konkrete Aufgabe |
|---|---|---|
| 01 Wallpapers | generierte SVG/Raster-Assets + Shell | Zwei fensterfreie Wallpaper passend zu hell/dunkel (keine UI im Bild), später flausen. Farbwelt integrieren |
| 02 Desktop-Rahmen | Caelestia / Hyprland | Rundungen, Kanten, Blurs, Spacing aus Mocks erhalten |
| 03 Navigation | Caelestia QML / Quickshell | linkes App-Dock, Topbar, Launcher; kleine flausen.-Marke nur bei Systemfunktionen |
| 04 Widgets | Quickshell + MPRIS + Telemetrie | Uhr, Player, CPU/RAM/Disk als echte Daten, Light/Dark Styling |
| 05 Fensterverhalten | Hyprland | responsive Workspaces, Floating/Tiling, Fullscreen-Games störungsfrei |
| 06 Apps | GTK/Qt/Browser/Terminal | konsistente UI-Farben und Icons, ohne fremde Apps zu forken |
| 07 Brand & OS Surfaces | Asset-/Token-Layer + Boot/Login/Installer/About | flausen.-Logo, Tokens und Claim einführen; ralleur nur als Parent-Credit |

## Umsetzungshinweise

- Caelestia und Hyprland sind unterschiedliche Schichten. Der Agent muss zuerst den tatsächlichen Stand prüfen; nicht stillschweigend KDE Plasma, Hyprland oder die Shell wechseln.
- Prüfe Caelestias **tatsächlich installierte** Konfigurations- und Token-Schemas, bevor du Overrides anlegst. Keine geratenen QML-Imports oder Shell-Keys.
- Bau ein kleines `flausen`-Theme-Modul/einen Token-Layer, aus dem QML, GTK, Qt und Bootstrap-Assets für Systemdialoge soweit möglich gespeist werden.
- Pfadlogos direkt via Qt SVG (wenn verfügbar), ansonsten validierte PNG-Fallbacks. Bei Vollbild-/HDR-Games darf kein Overlay erzwingen.
- Boot: Plymouth-Theme nur wenn Plymouth installiert/gewünscht; sonst systementsprechende Boot-Branding-Integration. Login: verwendeten Display Manager prüfen. Keine generische Annahme, dass SDDM installiert ist.
- Falls Login/Boot andere Rechte benötigen: zuerst im Repository implementieren und Anweisungen liefern; keine ungefragten systemweiten/rootseitigen Änderungen.
- Design-Tokens zur Quelle der Wahrheit machen. Nur die mitgelieferten SVG-Pfade als Logo-Ausgangsdateien verwenden, nicht die Logo-Pixel aus den Desktop-Mocks nachzeichnen.
- Ein Update der Caelestia Shell darf die eigenen Branddateien nicht überschreiben. Klare Install-, Uninstall- und Backup-Routinen.
- Die Shell soll auch für normale Nutzer intuitiv sein: technische Proton/Wine/Linux-Hinweise nicht unnötig im Vordergrund zeigen. Gaming bleibt First-Class.
- Desktop-Light/Dark muss das gesamte System umfassen; nicht bloß Wallpaper wechseln.

## Design-Trennung

1. **Parent Brand:** Ralleur (ralleur.com) mit seinem bestehenden, eigenen achtteiligen Kreislogo.
2. **Produktmarke:** flausen. (dieses neue Dreipunktlogo, freigegebenes Konzept).
3. **Technische Basis:** CachyOS/Arch, Caelestia, Hyprland, Qt/Quickshell – in Credits und Debug-Ausgaben transparent, aber **nicht** als visuelle Hauptmarke im Alltag.

Übernimm frühere, funktionale Anforderungen an OS, Gaming, USB-Lite/Full und Installation, soweit sie bereits im Repo dokumentiert sind. Das Branding-Briefing ist kein Anlass, diese Anforderungen neu zu erfinden.
