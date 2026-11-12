# ralleur Sperrbildschirm und Bootanimation

Quelle: `/home/USER/Downloads/ralleur-screensaver-main`.

## Sperrbildschirm

Lokales Plasma-Wallpaper `com.ralleur.screensaver`, Version 2.1.
Acht direkt gezeichnete, geglättete Qt-Quick-Vektorformen auf schwarzem Hintergrund.
Das Logo setzt sich beim Start in einer zufälligen Ecke mit Randabstand zusammen,
damit die mittige Anmeldekarte den Auftakt nicht verdeckt. Auch bei einem
Größenwechsel fällt eine ungültige Position auf eine Ecke zurück.
Die Swift-Physik und alle sieben Aktionen sind nach JavaScript portiert:
Ankunft, Burst, Regen, Tauschen, Welle, Umzug und Schlange; dazwischen zufälliges
Atmen und kleine Bewegungen. Keine Videodatei, kein Decoder, keine Bildtexturen,
kein Canvas und keine Offscreen-Effekte. Die Darstellung erfolgt in nativer
Bildschirmauflösung einschließlich HiDPI. Updates maximal 60/s, mit 240-Hz-
Physik-Unterteilung; Animation pausiert bei unsichtbarem Wallpaper.

Es verwendet KDEs vorhandenen Sperrbildschirm mit dessen Authentifizierung.
Zeitlimit, Passwortpflicht und Energiespareinstellungen bleiben unverändert.
Die vorherige Videovariante liegt nur noch als Rückfallsicherung unter
`backup/video-media-v1`; sie wird nicht mehr geladen.

## Bootanimation

Plymouth-Script mit acht kleinen PNGs (zusammen weniger als 1 KB).
Keine Videodecodierung, Zusatzdienste, Mindestlaufzeit oder Quit-Animation.
Das Logo bewegt sich leicht; bei Passwort-/Wiederherstellungseingaben steht es
oberhalb des vorhandenen Dialogs still. Die bisherigen Password-, Question-
und Message-Callbacks des installierten `minimal-unlock`-Themes bleiben erhalten.
Kernelparameter, TPM-Entsperrung, sd-encrypt, Tastatur und Dienstabhängigkeiten
werden nicht verändert. Das neue Theme wird mit `mkinitcpio -P` eingebunden.

Eine exakt unveränderte Bootzeit kann vor einem Neustart nicht nachgewiesen
werden. Referenz siehe `backup/boot-before.txt`. Nach dem Neustart mit
`systemd-analyze` vergleichen; mehrere Starts helfen, normale Streuung von
einem reproduzierbaren Unterschied zu unterscheiden. Auch die echte
Entschlüsselungsabfrage muss im Bootkontext geprüft werden.

## Prüfungen

- QML-Lint und Laden des Wallpaper-Items mit Qt.
- Alle sieben Aktionen und lange Zufallssequenzen bei Full HD, 4K, Hochformat und Ultrawide auf endliche, stabile Positionen geprüft.
- Größenwechsel, Pausieren und nativen 4K-Render geprüft (`check-vector.qml`).
- Bootscript durch den nativen Plymouth-Parser geprüft.
- Installer prüft nach dem Build Theme, Passwortagent und systemd-cryptsetup
  in allen initramfs-Images; bei Fehlern stellt er die vorherigen Images wieder her.

## Sicherung und Rückkehr

Benutzereinstellungen: `backup/kscreenlockerrc`.
Root-Sicherung nach Installation: `/var/lib/ralleur-boot-backup`.

Sperrbildschirm zurücksetzen (als Benutzer):

```sh
cp /home/USER/ralleurOS/kde-customizations/screensaver-boot/backup/kscreenlockerrc /home/USER/.config/kscreenlockerrc
```

Boot-Theme zurücksetzen und für die aktuell installierten Kernel neu bauen:

```sh
sudo plymouth-set-default-theme minimal-unlock
sudo mkinitcpio -P
```

Die initramfs-Sicherung nicht nach späteren Kernelupdates blind zurückkopieren.
