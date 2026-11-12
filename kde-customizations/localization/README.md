# Deutsch und Englisch nach KDE-Systemeinstellung

Die Lokalisierung folgt `[Translations] LANGUAGE` in `plasma-localerc`.
Die Caelestia-Einstellung steht nach der Migration auf `system`; eine ausdrücklich
gewählte Shell-Sprache bleibt danach als individuelle Option verfügbar.
Änderungen der KDE-Sprache werden in der laufenden Shell beobachtet. Eigene
Desktop-Kontextmenüeinträge bleiben erhalten; Standardbeschriftungen werden auch
aus bereits geladenen Modellen neu übersetzt.

`messages-de.json` enthält die deutschen Übersetzungen zu englischen Quelltexten.
`english-strings.json` normalisiert die früher fest eingebauten deutschen Texte.
Der Installer ergänzt den vorhandenen Caelestia-Katalog, einschließlich seiner
Kontexte, statt die Upstream-Übersetzungen zu ersetzen. Derselbe Nachrichtenbestand
liefert den Qt-Katalog der Über-Seite und den gettext-Katalog für Dolphin, native
Settings und Session-Flächen. Hermes übernimmt die KDE-Sprache für Statusmeldungen
und als Vorgabe für neue Antworten; ausdrücklich gewünschte Antwortsprachen bleiben
möglich.

Regionale Formate und UI-Sprache sind unabhängig. Kalender und Zahlen verwenden
die KDE-Formateinstellung; der Kalender richtet Wochenbeginn und Wochenenden daran
aus. Ein deutsches Menü darf somit weiterhin amerikanische Datumsformate haben.

## Installation und Prüfung

Voraussetzungen: installierte Caelestia-KDE-Shell mit deutschem Upstream-Katalog,
Python 3, Qt-6-Werkzeuge `lupdate`, `lrelease`, `lconvert` und GNU `msgfmt`.
Nach Komponenteninstallationen, die QML oder Kataloge ändern, erneut ausführen:

```sh
python3 kde-customizations/localization/install.py --check
python3 kde-customizations/localization/install.py
systemctl --user restart caelestia-shell.service
quickshell ipc -p "$HOME/.config/quickshell/caelestia" call localization inspect
python3 -m unittest discover -s kde-customizations/localization/tests -v
./bin/flausen check
```

Der Installer verändert weder KDEs gewählte Sprache noch die Regionalformate.
Er entfernt ausschließlich die unveränderten Englisch-Overrides des früheren
Einweg-Installers. Die Dateimigration schützt Aktionskennungen, XDG-Kategorien,
Befehle und Vergleichswerte. Native Änderungen müssen zusätzlich mit den jeweiligen
Komponenten gebaut werden. Ein bereits gebautes Dolphin-Plugin kann gezielt mit
`--dolphin-build .cache/dolphin-header-build` aktualisiert werden; nur das durch den
Dolphin-Installationsbeleg identifizierte und unveränderte Plugin wird ersetzt.
Andere Dateien der Dolphin-Installation werden dabei nicht angefasst.

Alle Änderungen einschließlich entfernter Override-Dateien werden unter
`~/.local/state/flausen/language-backups/` gesichert. Rückbau:

```sh
python3 kde-customizations/localization/install.py --restore PFAD_ZUR_SICHERUNG
```

Spätere Änderungen sind beim Rückbau geschützt. Mehrere Migrationen in umgekehrter
Reihenfolge zurückbauen. Anwendungen übernehmen ihre Sitzungssprache regulär nach
Neustart bzw. erneuter Anmeldung. Die Über-Seite und Hermes lesen KDEs aktuelle
Sprachwahl selbst. Der systemweite Anmeldebildschirm braucht den neu gebauten
Greeter und dessen Administratorinstallation; `session-style/install-login.py`
installiert dafür einen eigenen Katalog außerhalb des Benutzerprofils.

## Verifikation

Die Tests laden den echten Caelestia-Translator und ändern `plasma-localerc` in
einem isolierten Profil: Deutsch → Englisch → Deutsch, mit jeweils unabhängig
gewählten Regionalformaten. Zusätzlich geprüft werden Nachrichtenplatzhalter,
der native gettext-Katalog, Fallbacks und die wiederholbare Dateimigration.
Ein anschließendes `--check` muss nach erfolgreicher Installation null Änderungen
melden. Die IPC-Abfrage zeigt tatsächliche System-, angeforderte und aktive
Shell-Sprache sowie das Formatgebiet. Builds, Installerprüfungen und eine neue
echte Anmeldung sind getrennte Nachweise.
