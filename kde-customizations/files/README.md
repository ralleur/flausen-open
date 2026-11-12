# Files

Der vorhandene Dolphin ist der einzige Dateimanager und heißt in App-Menü und
Fenstertiteln **Files**. Die Namensanpassung liegt in `../dolphin-header` und wird
mit dessen Erweiterung installiert. Ordnernamen bleiben im Fenstertitel erhalten.

`python3 kde-customizations/files/install.py` setzt die Ordnerzuordnung auf diesen
Starter, wählt KDE ausdrücklich als FileChooser-Portal und aktiviert die
Portal-Nutzung für GTK-Anwendungen. Der ChatGPT/Codex-Starter erhält die Variable
direkt; für andere bereits laufende Apps gilt sie nach einer neuen Anmeldung.
Vorherige Dateien werden unter `~/.local/state/ralleur-desktop-tweaks/files-*`
gesichert. Neu angelegte Dateien stehen dort in `created-files.txt`.

Die KDE-Dateidialoge verwenden dasselbe Ordnersymbolthema und dieselbe kompakte
Seitenleiste wie Files. Ein service-lokales Qt-Plugin verwendet die vorhandene
Files-Kopfzeile auch für `KFileWidget`-Dialoge: Fensterknöpfe in der Werkzeugleiste,
abgerundeter Rahmen, native Verschiebe-/Größenänderungsfunktionen und zunächst
1040 × 700 Pixel (auf kleinen Bildschirmen begrenzt). Die Speicher-/Öffnen-Logik
bleibt vollständig bei KDE. Der Installer lädt das KDE-Portal neu; einen offenen
Dateidialog danach erneut öffnen. Andere Portal-Dialoge sind nicht betroffen.

Dateidialoge sind KDE-Dialoge, keine eingebetteten Dolphin-Fenster. Apps mit einer
eigenen Dateiauswahl können die Desktop-Vorgaben umgehen. Das GTK-Portal bleibt
als Systemkomponente installiert; es ist kein weiterer Dateimanager.

## ZIP beim Öffnen entpacken

`python3 kde-customizations/files/install-zip.py` richtet ZIP-Dateien so ein,
dass Öffnen/Doppelklick direkt mit Ark in den Ordner der ZIP entpackt.
Es wird kein zusätzlicher Ordner mit dem Archivnamen angelegt; die im Archiv
enthaltenen Unterordner bleiben erhalten. Die ZIP-Datei bleibt bestehen.
Ark übernimmt Fortschritt, Passwortabfragen und Rückfragen bei Dateikonflikten.
Andere Archivtypen behalten ihre bisherige Zuordnung. Über „Öffnen mit → Ark“
lässt sich eine ZIP weiterhin ansehen.

Der separate Installer sichert vorhandene Zuordnungen und den Starter unter
`~/.local/state/ralleur-desktop-tweaks/zip-*`. Rückbau auf die normale
Archivansicht: `xdg-mime default org.kde.ark.desktop application/zip`.
