# flausen Einstellungen

Eine gemeinsame native QtQuick-Oberfläche für den aktiven **KDE/KWin-Desktop mit
Caelestia-KDE**. Die Light-/Dark-Referenzen des Nutzers bestimmen Navigation,
Typografie, Farben, Karten, Schalter und Regler.

## Ein Fenster für alle Bereiche

Startmenü → **Einstellungen**, App-Suche → **flausen Einstellungen** oder
`flausen-settings`. `Strg+F` fokussiert die Suche. `Esc` führt zurück bzw. schließt
auf der Hauptseite. Das Fenster hat keine native Titelleiste. Oben rechts sitzen Minimieren,
Maximieren/Wiederherstellen und Schließen. Die freie Fläche daneben dient zum
Ziehen; ein Doppelklick maximiert das Fenster. Der äußere Rahmen folgt Dolphin:
12 px Rundung, feine Kontur aus KDEs Palette und derselbe native KWin-Schatten.
Maximierte Fenster haben gerade Ecken und keinen zusätzlichen Schatten.

- **Erscheinungsbild:** echte Hell-/Dunkel-/Automatik-Modi, sechs Akzentfarben,
  Wallpaper-Auswahl, Transparenz, reduzierte Bewegung und Textgröße.
- **Desktop, Netzwerk, Bluetooth, Ton, Mitteilungen und weitere Caelestia-Bereiche:**
  ein gemeinsames flausen-Designsystem für Überschriften, Beschreibungen, Karten,
  Listen, Schalter, Regler und Detailseiten. Bestehende Systemdienste und Aktionen
  werden weiterverwendet; die Gestaltung ist auf Nexus begrenzt.
- **Geräte, Konto, Sprache, Bedienungshilfen, Energie und Sicherheit:** Die
  installierten nativen QtQuick-KDE-Module werden **direkt im selben Fenster**
  geladen. Ein lokaler `Flausen.Settings`-Host verbindet ihre Backends, Seiten,
  Unterseiten und Speichervorgänge mit der flausen-Navigation. Gemeinsame Farben,
  Schrift, Eingabefelder, Karten und Bedienelemente werden auf die eingebetteten
  Formulare angewendet. Die fachliche Anordnung dieser Formulare bleibt erhalten.
- **Hermes:** eigene Kategorie für den Assistenten im Startmenü. Modellwahl
  zwischen DeepSeek Flash und dem vorhandenen lokalen LFM3, Denkmodus sowie
  Eingabe eines neuen DeepSeek-Schlüssels. Die Seite liest und aktualisiert das
  vorhandene private Hermes-Profil. Ein leer gelassenes Schlüsselfeld erhält den
  bestehenden Schlüssel. Gespeicherte Änderungen gelten ab **Neue Unterhaltung**
  im Hermes-Chat; laufende Gespräche bleiben beim bisherigen Modell.
- **Datum & Uhrzeit:** eigene flausen-Seite mit asynchroner Anbindung an
  `org.freedesktop.timedate1`. Zeitzone, NTP und manuelle Zeit werden über die
  reguläre Systemautorisierung gesetzt. Eingaben werden vor dem Aufruf geprüft.
- **System → Alle Systemeinstellungen:** durchsuchbarer Katalog der installierten
  QtQuick-Systemmodule. Weitere Caelestia-Optionen bleiben in der Seitenleiste
  unter **Weitere Einstellungen** zugänglich.

Es werden keine separaten KDE-Einstellungsfenster gestartet. KDE-Konfigurationsmodule
bleiben als native Implementierung erhalten; dies ist keine Neuentwicklung aller
Hardware- und Sicherheitsdienste. Zusätzliche Authentifizierungsdialoge,
Dateiauswahlen und fachliche Bestätigungen (z. B. bei Displayänderungen) sind
weiterhin möglich. Alte rein auf QWidgets basierende Fremdmodule sind kein Teil des
QtQuick-Katalogs; das zuvor verwendete Zeitmodul wurde daher durch eine eigene Seite
ersetzt. Fehlende oder fehlerhafte Module werden im Fenster mit einer Fehlermeldung
angezeigt, anstatt eine fremde Anwendung zu starten.

## Benutzerprofil

Oben links werden Anzeigename und Profilbild des angemeldeten Kontos aus
AccountsService angezeigt. Das Bild wird geglättet und mit Mipmaps verkleinert. Ein Klick auf das Bild
öffnet über das Desktop-Portal die native KDE-Dateiauswahl mit der vorhandenen
Dolphin-Kopfzeile, Seitenleiste und Fenstergestaltung und
speichert die Auswahl als systemweites Profilbild. Ein Klick auf den Namen
öffnet das eingebettete KDE-Benutzerkonto. Abbrechen ändert nichts; Fehler beim
Speichern werden angezeigt. Änderungen am Profil werden im Kopf übernommen.

## Icon-Proportionen

Navigation verwendet zentrierte 32-px-Symbolfelder in 44-px-Zeilen;
Kategoriekarten 48-px-Felder mit optisch ca. 40 px großen Material-Symbolen.
Schrift und Kartenaußenmaße werden unabhängig davon beibehalten. `SettingsIcon`
zentriert die Glyphen und zeichnet sie geglättet; Katalogicons werden passend
zur Displayauflösung geladen. Pfeile bleiben als sekundäre Symbole kleiner.

## Navigation und Änderungen

Die bisherigen Caelestia-Seitenindizes und IPC-Ziele bleiben gültig. Neue Kategorien
werden hinten ergänzt. Die Suche öffnet eingebettete Systemmodule direkt, etwa
**Nachtlicht**, **Maus**, **Zeitzone** oder **Benutzerkonto**.

Eingebettete Module bieten **Übernehmen**, **Zurücksetzen** und – wenn vom Modul
unterstützt – **Standardwerte**. Bei ungespeicherten Änderungen fragt ein flausen-
Dialog vor Navigation oder Schließen nach: weiter bearbeiten, verwerfen oder
übernehmen. Auch das native Schließen des Fensters wird geschützt. Berechtigungen
und die tatsächliche Speicherung werden vom jeweiligen KDE-Modul ausgeführt.
Modulspezifische Werkzeugleisten-Aktionen und deren nachgeladene Unterseiten sind
ebenfalls eingebunden.

Die eigene Datumsseite verwendet explizite Übernehmen-Aktionen pro Abschnitt;
noch nicht übernommene Textfeldeingaben werden beim Verlassen verworfen.

## Theme

Die sechs `flausen-*`-Paletten besitzen jeweils Light und Dark. Auswahl und
Weitergabe an Anwendungen laufen über die originale Caelestia-CLI. „Automatisch“
verwendet den vorhandenen AutoScheme-Dienst; feste Zeiten bzw. Sonnenzeiten lassen
sich unter **Zeitplan & Farben** konfigurieren. Transparenz nutzt die bestehende
KWin-/Caelestia-Blur-Anbindung. Textgröße skaliert die neue Oberfläche und die Shell,
keine fremden Anwendungen. Reduzierte Bewegung steuert auch die eigenen Schalter.

Die lokale Farb-CLI hat eine Schreibsperre für gemeinsame Matugen-Zwischendateien.
Sie wird vor Benutzer-Hooks freigegeben. Dadurch kollidieren schnelle Farbwechsel
und automatische Wechsel nicht mehr beim Schreiben.

## Installation und Upgrade

Benötigt werden die hier vorhandenen Qt6-/KF6-Entwicklungspakete: CMake, C++20,
Qt Quick/QML/DBus, KF6 KCMUtilsQuick und CoreAddons. Der Installer baut das lokale
Modul ohne Root nach `.cache/flausen-settings-native` und installiert es in
`~/.local/lib/qt6/qml/Flausen/Settings/`. Der bestehende Caelestia-Importpfad enthält
diesen Ort bereits. Es werden keine Systempakete verändert.

```sh
python kde-customizations/settings/install.py
systemctl --user restart caelestia-shell.service
python kde-customizations/settings/install.py --check
```

Der Installer schützt abweichende lokale Änderungen. `baseline.json` enthält die
geprüften Ausgangsstände. Ein Installations-Ledger unter
`~/.local/state/flausen/settings-installed.json` ermöglicht spätere Upgrades,
solange installierte Dateien nicht zwischenzeitlich verändert wurden. Identische
Installationsläufe sind idempotent. Vor jedem geänderten Dateisatz werden Originale,
Berechtigungen und Hashes gesichert. Paket-Upgrades erfordern weiterhin einen
Abgleich der betroffenen Nexus- und KDE-APIs.

Sicherungen: `~/.local/state/flausen/settings-backups/<Zeitstempel>/`.
Die zusammengefasste Sicherung vor der zweiten Ausbaustufe liegt unter:
`~/.local/state/flausen/settings-backups/20261102-172000-793049/`.
Sie führt zur ersten flausen-Fassung mit externen KDE-Verknüpfungen zurück.

```sh
python kde-customizations/settings/install.py --restore "$HOME/.local/state/flausen/settings-backups/20261102-172000-793049"
systemctl --user restart caelestia-shell.service
update-desktop-database "$HOME/.local/share/applications"
```

Rollback prüft alle Hashes vor dem Schreiben und schützt spätere Änderungen.
Benutzerpräferenzen, die über die Oberfläche verändert wurden, sind kein Teil des
Datei-Rollbacks. Die ursprüngliche Sicherung vor der ersten flausen-Fassung bleibt
unter `20261102-165454-661680` erhalten.

## Korrekturen an nativen Formularen

Die gemeinsame Gestaltung erhält native Mindestmaße der Bedienelemente.
Info-Schaltflächen bleiben dadurch kompakt; FormEntry-Zeilen reservieren auch
Platz für ihre nachfolgenden Hilfsschaltflächen. Die Bildschirmseite hält so
sRGB-Regler, Zahlenfeld und Hilfe innerhalb der Karte. Private Textfelder von
ComboBoxen erhalten keinen zweiten Rahmen. Sichtbare Button-Beschriftungen
entfernen Tastatur-Mnemonics auch bei nachgeladenen Textobjekten; die ursprüngliche
Beschriftung und die nativen Aktionen bleiben erhalten.

Der Rückweg ausschließlich für diese Formularkorrekturen steht in
`evidence/display-fix-backup.txt`. Die Sicherung bewahrt den vorher vorhandenen
segmentierten Reglerstil.

## Grafikspeicher bei Hermes

Der horizontale Balken steht für 100 % des VRAMs der gewählten GPU. Blau und Gelb
verwenden die vorhandenen flausen-Blau-/Amber-Akzente (Hell und Dunkel). Grau zeigt
die gemessene aktuelle Belegung. NVIDIA wird über `nvidia-smi`, AMD über sysfs
abgefragt; Adapterkapazitäten werden nicht addiert. Die Anzeige aktualisiert sich
alle zehn Sekunden, solange die Seite sichtbar ist. Nicht verfügbare Werte werden
nicht als null ausgegeben.

Die **GPU-Vorschau** folgt der ausgewählten lokalen Modellkarte und ist dort
standardmäßig eingeschaltet. Bei DeepSeek wird nur die aktuelle Belegung gezeigt.
LFM3 bleibt eine ausdrücklich hypothetische Vorschau vollständiger GPU-Nutzung:
Dateigröße als Modellnäherung und konservatives FP16-KV-Budget für eine Sequenz.
Die tatsächlich eingerichtete CPU-Nutzung wird zusätzlich erklärt.

Für **Qwen 3.8 27B** liest der Helper das installierte `qwen38/profile.json` und
ruft `llama-fit-params` auf, ohne Modellgewichte zu laden oder den Server zu starten.
Die GPU-Schichten, Q4_0-KV und die gewählte Kontextgröße bestimmen die Schätzung.
CPU-Modellanteile werden nicht als VRAM gerechnet. Neben Modell und Kontext zeigt
die Vorschau **Laufzeit & Reserve**: geschätzte Compute-Puffer plus konservativ
978 MiB für MTP-Draft 3, 282 MiB CUDA-Kontext und 462 MiB Treiberreserve. Diese
Zuschläge sind Näherungswerte des eingerichteten RTX-5080-Profils, keine Messung
einzelner Allokationen. Bei 44 GPU-Schichten und 90.112 Tokens ergibt das rund
8,15 GiB Modell, 1,16 GiB Kontext und 2,36 GiB Laufzeit/Reserve.

Das Kontextbudget verändert nur die Vorschau. Eine gewählte Größe bleibt auch
nach der periodischen Aktualisierung erhalten. Nicht verfügbare Qwen-Schätzdaten
werden nicht durch LFM3-Werte ersetzt. Auf dem AMD-Adapter wird Qwens NVIDIA-
Vorschau deaktiviert.
Die Restmenge ist keine Zusicherung für ein bestimmtes Spiel oder dessen Bildrate.

Wenn Ollama oder Qwen bereits VRAM belegt oder der Modellstatus unbekannt ist, wird die aktuelle
Belegung in der Vorschau separat ausgewiesen und nicht nochmals addiert. Die
[Ollama-API](https://docs.ollama.com/api/ps) liefert nur den gesamten VRAM-Anteil
laufender Modelle, keine gemessene Aufteilung nach Gewichten/Kontext oder GPU.
Grundlage der Kontextabschätzung ist die
[KV-Tensor-Allokation in llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-kv-cache.cpp).
Tests prüfen unter anderem Hybrid-Layer, Kontextwachstum, getrennte GPUs und den
Offline-Fall. Der Live-Test prüft echte GPU-Kapazität und das Vorschauverhalten.
Der Dateirückweg dieser Erweiterung steht in `evidence/vram-backup.txt`.

## Hermes-Profil

Die Modellauswahl trennt **Cloud-Modelle** (DeepSeek Flash, ChatGPT) und
**Lokale Modelle** (LFM3, Qwen 3.8 27B).
Qwen verwendet einen eigenen lokalen llama.cpp-CUDA-Dienst mit 90.112 Tokens
Kontext, Q4_0-KV und MTP. Installation, Desktop-Anpassung und Messungen:
[Qwen-Laufzeit](../launcher/hermes/qwen38/README.md).

`helpers/hermes_settings.py` verwendet System-Python 3 mit PyYAML und empfängt
Anfragen ausschließlich über stdin. Antworten enthalten nur Konfigurationswerte,
einen Revisionshash und den Schlüsselstatus. Schlüssel erscheinen weder in
Prozessargumenten noch in Antworten. Geänderte Dateien werden atomar mit `0600`
geschrieben. Eine Profilsperre und der Revisionsvergleich verhindern, dass zwei
geöffnete Formulare unbemerkt Änderungen überschreiben. Andere Profilwerte und
Zugangsdaten bleiben erhalten. Die Seite führt keine Modellanfrage aus und lädt
keine Modelle herunter. Nicht übernommene Formulareingaben werden beim Schließen
des Einstellungsfensters verworfen.

Die zusammengefasste Dateisicherung für diese Erweiterung steht in
`evidence/hermes-backup.txt`.

Die Bridge liest beim expliziten Zurücksetzen der Unterhaltung das konfigurierte
Modell neu ein und meldet den neuen Cloud-/Lokalstatus an den Chat. Werkzeuge und
Freigaben für einzelne Shell-Befehle bleiben unverändert.

Die Zugangskarte für DeepSeek oder ChatGPT liegt jeweils direkt unter der
Cloud-Modellauswahl. Ein gemeinsamer, beschnittener Bereich animiert seine Höhe
über 220 ms; der Inhalt blendet über 140 ms ein bzw. aus. Bei lokalen Modellen
fällt die Höhe vollständig auf null, sodass die folgenden Abschnitte nach oben
rücken. Der Wechsel zwischen Cloud-Anbietern animiert auch unterschiedliche
Kartenhöhen. Deaktivierte Systemanimationen werden berücksichtigt. Ungespeicherte
Schlüssel bleiben beim Modellwechsel im Formular erhalten.

Der isolierte Live-Test prüft die Zwischenhöhe beim Einklappen, die vollständig
freigegebene Fläche und die Wiederherstellung der Ausgangsposition. Bildbelege:
`evidence/native/hermes-deepseek-access.png` und
`evidence/native/hermes-local-collapsed.png`.

## ChatGPT: API oder Codex-Abo

Die vierte Modelloption verwendet **GPT-6.1 Sol**. Unter der Cloud-Karte sind
zwei getrennte Zugänge wählbar:

- **API-Schlüssel:** `OPENAI_API_KEY` im privaten Hermes-`.env`, unabhängig vom
  DeepSeek-Schlüssel; eigene OpenAI-API-Abrechnung. Ziel `https://api.openai.com/v1`.
- **Codex-Abo:** eigener Gerätecode-Login über Hermes, mit Browser und sichtbarem
  Anmeldecode. Die bestehende Codex-CLI-/Desktop-Anmeldung wird weder importiert
  noch überschrieben. Ziel des nativen Hermes-Anbieters `openai-codex` ist
  `https://chatgpt.com/backend-api/codex`. Nutzungslimits und Modellzugang hängen
  vom Konto ab. Ein erschöpftes Abo fällt nicht auf die API zurück.

`helpers/openai_auth.py` läuft im bestehenden Hermes-venv. Seine JSON-Ereignisse
enthalten ausschließlich Anmeldecode/-URL, Ergebnis und Statusbooleans. Der
native Hermes-Code übernimmt Gerätecode-Anforderung, Polling, Tokenaustausch,
private Auth-Speicherung und spätere Erneuerung. Der Login verändert weder die
aktive Modellkonfiguration noch den aktiven Anbieter im Auth-Store. Erst
**Übernehmen** speichert die Auswahl; **Neue Unterhaltung** aktiviert sie.
Abbruch beendet den Login-Prozess. Statusabfragen erneuern keine Tokens.

Beide OpenAI-Wege verwenden Hermes' Responses-Transport (`codex_responses`) mit
den vorhandenen Desktop-Werkzeugen. Shell-Befehle benötigen weiterhin die
Bestätigung im Chat. Der Denkmodus wird über Hermes' Reasoning-Konfiguration
weitergegeben, ohne Chat-Completions-Parameter an die Responses-API zu schicken.

Prüfung: beide Auswahlwege in der echten QML-Oberfläche; Schlüsseltrennung,
verhinderte Speicherung ohne Anmeldung, Anbieter-/Endpunktwahl und Fehlerredaktion
in Tests. Der native Hermes-Auth-Store wurde mit gemocktem Netzwerk in einem
temporären Profil geprüft, einschließlich `0600` und unterdrückter Tokenausgabe.
Ohne eingegebenen API-Schlüssel bzw. abgeschlossene Abo-Anmeldung wurde keine
Live-Modellanfrage an OpenAI ausgeführt.

Belege: `evidence/native/hermes-chatgpt-api.png`,
`evidence/native/hermes-chatgpt-codex.png`, `evidence/gallery-check.json`,
`evidence/openai-auth-contract.json`. Tests: `tests/openai_auth_check.py`,
`tests/hermes_check.py` und `../launcher/hermes/test_bridge.py`.

Offizielle Grundlagen: [Codex-Anmeldung](https://learn.chatgpt.com/docs/auth),
[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol).

## Prüfung

- `tests/static_check.py`: QML-Parsing, vorhandene Systemmodule, zwölf Paletten via
  CLI-Preview. Ein vom Upstream übernommenes Plugin-QML kann der Qt-Formatter nicht
  serialisieren; dessen Syntax wird zusätzlich mit qmllint geprüft.
- `tests/live_check.py`: prüft zwölf Hauptbereiche, 13 eingebettete Geräte-/Systemmodule,
  Suche, Deep Links sowie den Schutz ungespeicherter Änderungen bei Navigation und
  nativem Schließen. Es startet eine separate, minimierte QtQuick-Testinstanz mit
  einer Kopie der Nexus-Dateien und einem eigenen Runtime-Verzeichnis; die laufende Shell wird nicht angehalten oder
  instrumentiert. Ein Mouse-Checkbox-Test verändert nur den Modul-Puffer und
  verwirft ihn anschließend. `--theme` prüft zusätzlich echte Farb-/Präferenzwechsel
  und setzt diese zurück; dafür eine ruhige Sitzung verwenden. `--gallery-only`
  öffnet ein separates Prüffenster und exportiert ausschließlich dessen QML-Inhalt.
- `tests/live_check.py --audit-only`: rendert 52 Ansichten (14 native Module und
  zwölf Hauptseiten bei zwei Formularbreiten) und prüft Kartenüberläufe, sichtbare
  Mnemonics und überbreite Hilfsschaltflächen. Der Funktionstest prüft zusätzlich
  die HDR-Beschriftung nach Austausch ihres Textobjekts, ohne HDR umzuschalten.
- `python tests/hermes_check.py`: private Schlüsselbehandlung, Modell- und
  Denkmodus-Speicherung, Erhalt anderer Profilwerte und Schutz veralteter Formulare
  in einem temporären Profil. Der Live-Test lädt zusätzlich die Hermes-Seite und
  prüft Modellwahl und Zurücksetzen ohne das echte Profil zu verändern.
- `tests/install_check.py`: Idempotenz, Dateischutz und vollständiger Rückweg in
  einem temporären HOME.

Nachweise liegen unter `evidence/`, native Seitenansichten unter `evidence/native/`.

Die adaptierten Caelestia-QML-Dateien und Erweiterungen stehen wie die Shell unter
GPL-3.0. Qt und KDE Frameworks werden dynamisch mit ihren vorhandenen Lizenzen
verwendet. Die Paletten basieren auf den installierten Caelestia-/Graphite-Paletten;
Drittanbieter-Lizenzen bleiben erhalten.

## Local endpoint in Hermes

Unter „Lokale Modelle“ steht als dritte Option „Local endpoint“ bereit. Sie bindet
einen Modellserver im eigenen Netzwerk über eine OpenAI-kompatible Chat-Completions-API
an. Basisadresse inklusive API-Pfad (z. B. `http://192.168.1.20:1234/v1`), exakte
Modellkennung und ein optionaler API-Schlüssel sind konfigurierbar. Das Modell muss
Tool-Aufrufe unterstützen, damit Hermes seine Desktop-Werkzeuge verwenden kann.

Adresse und Modellkennung liegen im privaten Hermes-Profil unter `local_endpoint`,
der Schlüssel separat in `.env` als `LOCAL_ENDPOINT_API_KEY`. Leere Schlüsseleingabe
behält den vorhandenen Schlüssel. Profiländerungen gelten ab einer neuen Unterhaltung.
Der Endpoint startet weder Ollama noch die lokale Qwen-Laufzeit. Es werden keine
Ollama-/llama.cpp-spezifischen Request-Optionen übertragen; den Denkmodus stellt
man am Server ein. Die lokale VRAM-Vorschau wird für diese Option ausgeblendet.

Prüfung: `python tests/hermes_check.py` und
`python ../launcher/hermes/test_bridge.py` prüfen Speicherung, ungültige Eingaben,
Schlüsselerhalt und Routing ohne eine echte Netzwerkverbindung.
`python tests/live_check.py --endpoint-only` lädt eine isolierte native
Einstellungsansicht, wählt die Karte, prüft die drei Felder und setzt den Entwurf
zurück. Das reale Profil bleibt unverändert.
Eine Verbindung zu einem konkreten Server ist erst nach dessen Konfiguration möglich.

Hermes ist im Einstellungs-Eintrag, Seitenkopf und Chat als **Experimental** mit
rotem Tag gekennzeichnet. Eine dauerhafte Warnung fordert den Betrieb lokaler
Agenten ausschließlich in Sandboxen und auf isolierten Testsystemen. Sie weist
explizit darauf hin, dass Hermes selbst keine Sandbox aktiviert. Diese
Kennzeichnung verändert weder Zugriffsrechte noch das aktive Modellprofil.
Die gemeinsamen Bausteine liegen unter `overlay/components/ExperimentalTag.qml`
und `AgentSafetyNotice.qml`; auch der Hermes-Installer installiert sie.


## Gemeinsamer Capture-Verlauf für blaue Controls

Blaue Schalter, aktive Audio-Geräte, segmentierte Regler und die entsprechenden
nativen KDE-Controls in eingebetteten Formularen nutzen `PrimaryControlFill` aus
`taskbar/menu-style`. Verlauf, Außenkontur und Lichtkante haben dieselbe zentrale
Quelle wie der Capture-Button. Vorhandene Geometrien, Fokusrahmen und Backend-
Signale bleiben erhalten. Native Ansichten für Bluetooth, Sound und Display wurden
geprüft. Installation des gemeinsamen Control-Standards vor dem Settings-Installer:
[Installation und Prüfwerte](../taskbar/menu-style/README.md#freigegeben-als-standard-für-blaue-controls).

## Wallpaper-Wechsel direkt bei der Auswahl

Die Set-Auswahl steht unter der Vorschau. „Random: on/off“ schaltet die
vorhandene Diashow dauerhaft ein bzw. aus. Einschalten aktiviert die zufällige
Reihenfolge und wählt sofort ein Bild aus dem gewählten Set; Ausschalten erhält
das aktuelle Bild. Das Wechselintervall wird hier in Minuten eingestellt
(1–1440), intern weiterhin in Stunden gespeichert. Eine manuelle Auswahl über
Vorschau, Bildliste oder Dateidialog stoppt den automatischen Wechsel.
Die separate Seite „Slideshow & Order“ verwendet dieselben Konfigurationswerte.

`python3 tests/wallpaper_check.py` prüft Schalter, Intervall, Speicherung und
manuelle Auswahl in einer isolierten Settings-Instanz. Hintergrund und
Diashow-Präferenzen werden anschließend wiederhergestellt. Bild und Prüfwerte:
`evidence/native/wallpaper-controls.png`, `evidence/wallpaper-controls-check.json`.
