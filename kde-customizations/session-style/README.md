# Sperrbildschirm und Anmeldung

Grundlage sind die hellen und dunklen Sperrbildschirm-Mocks vom 1. November 2026:
zentrierte, abgerundete Karte, große Uhr, Datum, OS-Benutzerbild, Passwortfeld mit
Schloss und runder Pfeilbutton. Die Variante folgt der Qt/KDE-Anwendungspalette.
Die UI verwendet die vorhandene Ralleur-Marke. Datum und Uhrzeit sind live. Das Datum verwendet ausdrücklich `de_DE`,
beispielsweise „Sonntag, 1. November 2026“; die Uhrzeit folgt dem Gebietsschema.

Die native Benutzerauswahl, Anmeldung, Passwort-Synchronisierung, Fehleranzeige,
Tastaturumschaltung und Bildschirmtastatur bleiben erhalten. Es werden keine
PAM-Dateien, Benutzerkonten, Autologin- oder Sitzungsstart-Einstellungen geändert.
Die native Mediensteuerung sitzt auf breiten Sperrbildschirmen rechts oben;
bei weniger als 1100 logischen Pixeln wird sie ausgeblendet. Kurze Bildschirme
skalieren die Karte, damit die Sitzungsaktionen darunter erreichbar bleiben.

Sperrbildschirm und Anmeldung laden das zum jeweiligen Benutzer gehörende
Profilbild aus AccountsService (`org.freedesktop.Accounts.User.IconFile`),
wie die OS-Benutzereinstellungen. Ohne hinterlegtes Bild bleibt der native
Avatar bzw. das Benutzer-Symbol erhalten. Es wird kein Markenlogo erzwungen.
Benutzername, die Marke oben links und „Mit Enter fortfahren“ sind im Sperrbildschirm
visuell ausgeblendet. Benutzeridentität, Auswahl und Passwortverarbeitung
bleiben intern erhalten. Native Renderprüfung
in Hell und Dunkel: `.cache/lock-minimal-identity/`.

Die reduzierte Lockscreen-Karte erhält rundum 30 Pixel Innenabstand statt
fester Mindesthöhe. Die untere Aktionsgruppe wird anhand der sichtbaren
Buttons als Ganzes zentriert: Schlafen, Benutzer wechseln und Herunterfahren.
Herunterfahren verwendet KDEs native `SessionManagement.requestShutdown`
mit `ConfirmationMode.Skip`, ohne einen hinter dem Lockscreen liegenden
Bestätigungsdialog. Die tatsächliche Abschaltung wurde beim Prüfen nicht
ausgelöst. Render- und Layoutprüfungen: `.cache/lock-compact-actions/`.

## Installation im Benutzerkonto

```sh
python kde-customizations/session-style/install-lock.py
```

Das überschreibt ausschließlich die Präsentationsdateien des bereits aktiven
Benutzerpakets `~/.local/share/plasma/shells/caelestia.desktop`, mit gesichertem
Original unter `~/.local/state/ralleur-desktop-tweaks/session-style-lock-*`.
Die neue Oberfläche wird beim nächsten Sperren geladen. Die laufende Sitzung
wird durch die Installation nicht gesperrt oder beendet.

## Anmeldebildschirm

Installiert ist **Plasma Login Manager 6.8.2-1**, nicht SDDM. Seine Oberfläche
ist in das Greeter-Programm eingebaut. `prepare.py` aktualisiert die gemeinsame QML-Präsentation des passenden
Upstream-Tags und ergänzt einen rein visuellen Wallpaper-Lader. Dieser verwendet
das konfigurierte native Wallpaper im selben Szenengraphen, damit die Karte
denselben lokalen Blur wie beim Sperren erhält. Authentifizierungs-Backend und
Anmeldelogik bleiben unverändert. Der private Build wird separat installiert, die Paketdatei
`/usr/lib/plasma-login-greeter` bleibt erhalten.

Vom Repository-Verzeichnis aus lässt sich der Build reproduzieren:

```sh
git clone --branch v6.8.2 --depth 1 \
  https://invent.kde.org/plasma/plasma-login-manager.git .cache/plasma-login-src
python kde-customizations/session-style/prepare.py .cache/plasma-login-src
cmake -S .cache/plasma-login-src -B .cache/plasma-login-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DCMAKE_INSTALL_PREFIX=/usr
cmake --build .cache/plasma-login-build --target plasma-login-greeter -j 6
```

Die bereits vorbereitete, getestete Binärdatei kann mit Administratorrechten
installiert werden:

```sh
sudo python /home/USER/ralleurOS/kde-customizations/session-style/install-login.py \
  --binary /home/USER/ralleurOS/.cache/plasma-login-build/bin/plasma-login-greeter
```

Der Installer legt einen privaten Greeter unter `/usr/local/libexec/ralleur-login`
und einen systemd-Override unter
`/etc/systemd/user/plasma-login.service.d/ralleur-style.conf` an.
Er sichert vorherige Dateien unter `/var/lib/ralleur-login-style`.
Er startet weder Login Manager noch Sitzungen neu. Nach Neustart des Rechners
wird der neue Greeter verwendet. Nach einem Update von Plasma Login Manager
startet der Wrapper automatisch wieder den mitgelieferten System-Greeter, bis
für die neue Version ein passender Build geprüft wurde.

## Überprüfung

```sh
cmake -S kde-customizations/session-style -B .cache/session-style-build -G Ninja
cmake --build .cache/session-style-build
python kde-customizations/session-style/tests/install_test.py
```

`tests/probe.cpp` ist ein ausschließlich für den Testmodus verwendetes Qt-Plugin.
Es rendert den echten KScreenLocker mit `--testing` und den echten angepassten
Login-Greeter mit `--test`. Die Passwortprobe sendet nur an das Mock-Backend des
Login-Greeters einen absichtlich ungültigen Testwert und prüft Fehleranzeige und
erneute Bedienbarkeit. Das Plugin wird nicht installiert.

Native Prüfungen wurden in Hell und Dunkel mit dem Offscreen-Renderer durchgeführt.
Eine erfolgreiche echte Anmeldung sowie Fingerabdruck, Smartcard, mehrere
Monitore und die Bildschirmtastatur wurden nicht interaktiv durchlaufen.
Der Anmeldebildschirm rendert sein konfiguriertes natives Wallpaper zusätzlich
in der eigenen Oberfläche als Quelle für den lokalen Blur. Bei einem Ladefehler
bleibt der vorhandene separate Wallpaper-Dienst als Hintergrund verfügbar. Der Sperrbildschirm verwendet eine gleichmäßig getönte, transparente Karte
mit lokalem Live-Blur des Wallpapers hinter ihrer abgerundeten Kontur.
Bei Software-Rendering bleibt die transparente Tönung als Fallback erhalten.
Sperren und Anmeldung verwenden nun dieselbe aktuelle Kartendatei einschließlich
Transparenz, Live-Blur, deutschem Datum und reserviertem unteren Bedienbereich.
Die Systemstatus-Anordnung bleibt überwiegend nativ.

## Rückbau

```sh
python kde-customizations/session-style/install-lock.py --restore
sudo python kde-customizations/session-style/install-login.py --restore
```

Beide Installer verweigern das Überschreiben nachträglich manuell geänderter
Installationsdateien. Die Backups bleiben erhalten. Für den systemweiten Greeter
wird der Rückbau nach dem nächsten Neustart verwendet.

## Herkunft

Die Dateien unter `lock/` basieren auf dem installierten KDE-Plasma-Sperrbildschirm
(Plasma Workspace 6.8.2, [Upstream](https://invent.kde.org/plasma/plasma-workspace/-/tree/v6.8.2/desktoppackage/contents/lockscreen)).
`shared/RalleurSessionScreen.qml` erhält die Schnittstelle des nativen
`SessionManagementScreen.qml` und ersetzt dessen visuelle Anordnung.
Die ursprünglichen SPDX-Vermerke und Lizenzen sind in den Dateien erhalten.
Eigene Installer, Testprobe, Feldhintergrund und Build-Helfer: MIT.

Abschließender Lauf gegen die tatsächlich installierte Binärdatei:

```sh
python kde-customizations/session-style/tests/live_check.py \
  --login /usr/local/libexec/ralleur-login/plasma-login-greeter \
  --probe .cache/session-style-build/plugins \
  --out .cache/session-final-evidence
```

Das [Prüfprotokoll](evidence/verification.json) enthält den SHA-256-Hash der
installierten Datei, vier erfolgreiche Renderprüfungen und die beiden
Anmeldefehler-/Wiederholungsprüfungen nach Ende der nativen Fehleranimation.

Die [Benutzerbild-Prüfung](evidence/user-avatar.json) bestätigt für beide
Bildschirme in Hell und Dunkel die AccountsService-Bildadresse und den
erfolgreichen Ladezustand des tatsächlichen Bildes. Reproduzierbar mit
`tests/live_check.py` und den zusätzlichen Argumenten
`--avatar-user ralleur --avatar-source file:///var/lib/AccountsService/icons/ralleur`.

Die unteren Sitzungsaktionen stehen in einem begrenzten, bei Bedarf scrollbar
werdenden Bereich über der nativen Fußzeile. Die Karte reserviert diesen Platz
bei ihrer Positionierung und Skalierung. Das
[Layoutprotokoll](evidence/layout-and-german-date.json) prüft Aktionen und Fußzeile
bei 1280×800, 800×600, 640×480 und 360×640 im nativen Greeter-Testmodus.

Der aktualisierte Greeter wurde in Hell und Dunkel einschließlich falscher
Testanmeldung und Wiederholbarkeit geprüft; der lokale Blur wurde zusätzlich mit
dem GPU-Renderer kontrolliert.

## Lokalisierung

Eigene Session-Texte verwenden den gemeinsamen flausen-gettext-Katalog. Datums- und Zeitformate folgen der Systemregion. Nach einem Greeter-Neubau installiert `install-login.py` den Katalog für den systemweiten Anmeldeprozess mit. Dafür werden zusätzlich Qt-Linguist-Werkzeuge und `msgfmt` benötigt. Die Benutzersitzung erhält ihren Katalog über [localization/install.py](../localization/README.md).
