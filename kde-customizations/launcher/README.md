# Startmenü nach der Mock-Vorlage

## Dynamischer Windows-Neustart

Die untere Leiste enthält statt „Dateien“ den Button **„In Windows Neustarten“**
mit blauem Windows-Symbol. Bei jedem Öffnen wird die Erkennung aktualisiert:
Ein aktiver UEFI-Eintrag muss auf `EFI/Microsoft/Boot/bootmgfw.efi` zeigen,
seine FAT-Partition muss vorhanden sein und auf demselben Datenträger muss eine
NTFS- oder BitLocker-Partition existieren. Eine NTFS-Datenpartition allein reicht
nicht aus. Bei fehlendem Ziel oder Lesefehlern bleibt der Button verborgen.
Dies erkennt die lokale Windows-Bootkonfiguration; die Windows-Systemdateien
auf einer ungemounteten Partition werden dabei nicht gelesen. Legacy-BIOS-
Installationen werden nicht unterstützt. `launcher.showPowerMenu` gilt auch hier.

Beim Klick startet `pkexec` den Helfer `windows-boot.py --reboot` mit einer
Systemfreigabe. Er prüft das Ziel erneut, setzt ausschließlich UEFI `BootNext`
und fordert danach den Neustart an. Die dauerhafte Bootreihenfolge bleibt erhalten.
Schlägt der Neustart fehl, stellt der Helfer den vorherigen BootNext-Wert wieder
her beziehungsweise entfernt den neu gesetzten Wert. Fehler erscheinen als
Benachrichtigung, abgebrochene Freigaben lösen keinen Neustart aus.

Prüfung: `python3 -m unittest discover -s kde-customizations/launcher/tests -v`.
Fünf Tests decken Erkennung, fehlende Ziele, Reihenfolge und Fehlerbehandlung ab.
Live wurden die Erkennung und die vollständige Beschriftung im Startmenü geprüft;
ein echter Neustart wurde nicht ausgelöst. Ansicht: `evidence/windows-start-menu.png`.
Sicherung: `~/.local/state/ralleur-desktop/backups/20261102-161313-windows-restart`.
Rückbau mit `restore.py` wie unten beschrieben.

## Hermes-Einstellungen

Unter **flausen Einstellungen → Hermes** sind Cloud-Modelle (DeepSeek Flash,
ChatGPT) und lokale Modelle (LFM3, Qwen 3.8 27B) getrennt angeordnet. ChatGPT
verwendet GPT-6.1 Sol mit OpenAI API-Schlüssel oder eigener Codex-Abo-Anmeldung.
API-Schlüssel und Abo-Zugang werden ausdrücklich getrennt behandelt.
Qwen läuft mit 90.112 Tokens Kontext über einen eigenen lokalen CUDA-Dienst;
Profil, Installation und Messungen stehen in [hermes/qwen38/README.md](hermes/qwen38/README.md).
Gespeicherte Werte gelten ab **Neue Unterhaltung**. Die Bridge lädt dafür das
bestehende Profil erneut; laufende Gespräche werden nicht umgestellt.
Die Seite wird durch `../settings/install.py` installiert.

## Hermes aus der Suchleiste

Freien Text eingeben und Enter drücken oder auf „Hermes fragen“ klicken. Die
Suchfläche öffnet über 360 ms eine native Chatkarte innerhalb des bestehenden
Launchers. App-Treffer bleiben darunter per Klick erreichbar; die vorhandenen
`>`-Befehle und ihre Tastaturbedienung bleiben erhalten. Das Funkel-Symbol öffnet
die Unterhaltung auch ohne Eingabe. Im Chat sendet Enter, Shift+Enter fügt eine
Zeile ein. Escape beziehungsweise das Kreuz führt zum Startmenü zurück.
Die Chatkarte verwendet direkt `modules/bar/GlassSurface.qml`, also dieselbe
Tönung und Kontur wie Topbar und Dock, mit höherer Deckkraft für die Lesbarkeit
(65 % im dunklen, 75 % im hellen Schema). Der dunkle Startmenü-Hintergrund
blendet beim Öffnen der Karte vollständig aus, damit er das Glas nicht verdeckt.
Der vorhandene native KWin-Blur bleibt erhalten. Die Glasansicht wurde auf dem
Desktop geprüft: `evidence/hermes/chat-glass-detail.png`.

Die Karte zeigt echte Hermes-Werkzeugaufrufe mit aufklappbaren Details,
Antworten während der Ausgabe, Fehler und Abbrechen. Folgefragen verwenden
denselben Gesprächskontext. Beim Schließen des Menüs bleibt die Unterhaltung
bis zum Shell-Neustart erhalten; „Neue Unterhaltung“ setzt sie zurück. Schließen
beendet einen laufenden Auftrag nicht; dafür gibt es ausdrücklich „Abbrechen“.
Eine Unterbrechung macht bereits ausgeführte Aktionen nicht rückgängig.
Gemessene RAM- und Audiowerte sowie gelesene Konfigurationen erscheinen zusätzlich
direkt in den Aktionskarten. Der Hauptagent ist jetzt **DeepSeek Flash**
(`deepseek-flash`) über die offizielle DeepSeek-API. Die Oberfläche kennzeichnet
dies ausdrücklich als Cloud. LFM3 bleibt als lokales Modell installiert.

`hermes/bridge.py` bettet den unveränderten `AIAgent` aus dem offiziellen
[Hermes Agent](https://github.com/NousResearch/hermes-agent) ein. Geprüfter
Runtime-Commit: `c7da41dd522dc19cc08bbfcfa69d4b078224b45d`. Ein privater
JSON-Lines-Kanal verbindet die QML-Oberfläche mit dem Python-Prozess. Der
Prozess startet beim Öffnen der Chatkarte; das Modell wird erst nach einer
Anfrage aufgerufen. Es wird keine eigene HTTP-Schnittstelle geöffnet.

Für die lokale Alternative verwendet Ollama `lfm3:1.7b-hermes`: dieselben Q4_K_M-Gewichte wie
`lfm3:1.7b`, mit `num_gpu=0`, zwei CPU-Threads und 65.536 Tokens Kontext.
Die aktuelle Hermes-Version verlangt mindestens 64.000 Tokens; die vorherige
8K-Variante `lfm3:1.7b-cpu` bleibt unverändert verfügbar. Das Modell darf nach
einer Anfrage nach einer Minute aus dem Speicher entladen werden. Der
Bridge-Prozess läuft mit niedriger Priorität (`nice 10`).

Der Hauptagent nutzt `https://api.deepseek.com`, Modell `deepseek-flash`, mit
aktiviertem Denkmodus und erhaltenen Reasoning-Daten zwischen Werkzeugaufrufen.
Der Schlüssel liegt ausschließlich im privaten Laufzeitprofil in `.env`,
Dateirechte `0600`, unter `DEEPSEEK_API_KEY`; er gehört nicht ins Repository.
API-Fehlermeldungen werden auf Schlüsselzeichenfolgen bereinigt. Der normale
Dateileser schützt die private Credential-Datei. Der Schlüssel wird bei einer
erneuten Installation nicht überschrieben. Die lokale Alternative verwendet
weiterhin Ollama unter `127.0.0.1:11434/v1`.
Das eigene Profil liegt unter `~/.local/state/ralleur-hermes/profile`;
vorhandene Hermes-Profile werden nicht verändert. Automatische Memory-/Review-
Funktionen und Kontextkompression sind für diese Integration deaktiviert.
Lange Gespräche lassen sich über „Neue Unterhaltung“ zurücksetzen.
Hermes führt lokale Diagnoseprotokolle in seinem eigenen Profil.

Die explizit aktivierten Werkzeuge sind derzeit:

- `read_file`, `search_files`: native Hermes-Werkzeuge zum allgemeinen Lesen und
  Suchen, ohne vorgeschalteten Shell-Befehl. Schreibwerkzeuge sind nicht aktiviert.
- `system_status`: aktuellen RAM, CPU-Last und freien Platz im Home-Dateisystem lesen.
- `desktop_status`: Farbschema und Audiozustand über dieselbe Shell lesen.
- `autostart_status`: effektive Desktop-Autostarts aus den XDG-Verzeichnissen,
  aktivierte systemd-Benutzerdienste/Timer und KDE-Sitzungsskripte lesen.
  Benutzerdateien überschreiben gleichnamige Systemdateien; `Hidden`,
  Desktop-Zuordnung, fehlendes `TryExec` und Bedingungen werden ausgewiesen.
  Die Einträge werden dabei niemals ausgeführt. „Aktiviert“ beschreibt die
  Konfiguration und ist keine Behauptung über gerade laufende Prozesse.
- `inspect_system`: allgemeine Leseabfragen zu Hardware, Paketen,
  Benutzerdiensten, eigenen Prozessen, Datenträgern, Netzwerk und letzten Logs.
  Der Bereich ist vorgegeben; Modelltext wird nicht als Shell-Code ausgewertet.
- `system_command`: allgemeiner Ausführungsweg über Hermes' eigenen
  Terminal-Executor. Zuerst erscheinen Begründung und konkreter Befehl im Chat.
  Erst der Button „Einmal ausführen“ gibt genau diesen Vorschlag frei.
  Ablehnen, Abbrechen, abgelaufene oder nicht passende Freigaben führen zu
  keiner Ausführung. Es gibt keine dauerhafte oder pauschale Freigabe.
- `open_app`: eine der unterstützten, tatsächlich installierten Anwendungen über
  Caelestias vorhandene App-Startfunktion öffnen.
- `set_volume`: Lautstärke zwischen 0 und 100 Prozent setzen und anschließend
  über PipeWire prüfen.

Die allgemeine Ausführung ergänzt die festen Werkzeuge; weitere Systemfragen
benötigen dadurch nicht jeweils einen eigenen Spezialfall. Das Systemwissen im
Prompt ordnet die installierten Komponenten ihren Dateien zu: PowerDevil,
Bildschirmsperre, Tastenkürzel, Farbschema, KWin, Dock, Monitore, Audio,
Netzwerk und Benutzerdienste. Die Übersicht enthält keine aktuellen Messwerte;
der Agent muss diese weiterhin lesen. Dieses Muster orientiert sich an
[Omarchys System-Skill und Befehlsentdeckung](https://github.com/omacom/omarchy/blob/quattro/default/agents/skills/omarchy/SKILL.md).
Omarchy-Befehle und Hyprland-Konfigurationen werden nicht auf dieses KDE-System
übertragen. Direkte Dateischreib-, Browser-, Delegations- und Automationswerkzeuge
bleiben deaktiviert. Der Agent führt allgemeine Befehle nur nach einer sichtbaren
Einzelfreigabe aus.

### Prüfung des neuen Standards

Die vorherigen Prüfungen wiesen hauptsächlich funktionierende Aufrufe nach.
Die neue Prüfung vergleicht vollständige Modellantworten mit den tatsächlichen
Konfigurationswerten. LFM3 verwechselte trotz allgemeiner Lesewerkzeuge und
aktiviertem Denkmodus unter anderem Bildschirmabschaltung und Bildschirmsperre;
das zählt als fachlicher Fehler. Größere lokale Qwen-Modelle wurden zusätzlich
untersucht, aber nicht als neuer Standard aktiviert.

DeepSeek Flash bestand sieben Fragen mit echten Lesewerkzeugen: Standby-Zeit,
Bildschirmabschaltung, KDE-Farbschema, angeheftete Dock-Apps, Autostart,
Lautstärke und ausdrücklich nicht gesetzte Akku-Einstellungen. Die ersten
Antworten lagen in dieser Stichprobe zwischen etwa 2 und 9 Sekunden.
Zusätzlich sind Folgefragen im selben Chat, die sichtbare Cloud-Kennzeichnung,
Freigabe und Ausführung eines harmlosen Prüfbefehls, Abbrechen und Wiederöffnen
der Unterhaltung live geprüft. Das ist eine konkrete Regressionstest-Stichprobe
und keine Garantie für jede mögliche Systemaufgabe.

Protokolle: `evidence/hermes/evaluation/deepseek-conversations.json` und
`evidence/hermes/evaluation/cloud-ui-*.json`. Wiederholung mit dem eingerichteten
privaten Profil verbraucht API-Tokens:

```bash
~/.local/share/ralleur-hermes/venv/bin/python /home/USER/ralleurOS/kde-customizations/launcher/hermes/evaluate_conversations.py --model deepseek-flash --output /tmp/hermes-check.json
```

Quellen: `overlay/modules/launcher/HermesChat.qml`,
`overlay/modules/launcher/services/HermesDesktop.qml` und `hermes/`.
Installation auf der passenden, bereits angepassten Caelestia-Basis:

```bash
bash /home/USER/ralleurOS/kde-customizations/launcher/hermes/install.sh
python /home/USER/ralleurOS/kde-customizations/launcher/hermes/test_bridge.py
```

Die Installation sichert die betroffenen Dateien und schreibt ein mit
`restore.py` kompatibles Prüfsummenmanifest. Sie installiert Hermes mit dessen
eigenem Dependency-Lock über `uv`; ein normales `pip install` berücksichtigt
die upstream definierten Dependency-Overrides nicht.

Die ursprüngliche Sicherung für diese Erweiterung steht unter
`~/.local/state/ralleur-desktop/backups/20261101-210937-hermes-launcher`.
Gezielter Rückbau der Oberfläche:

```bash
python /home/USER/ralleurOS/kde-customizations/launcher/restore.py /home/USER/.local/state/ralleur-desktop/backups/20261101-210937-hermes-launcher --dry-run
# Ohne --dry-run werden ausschließlich die vier Launcher-Dateien zurückgesetzt.
systemctl --user restart caelestia-shell.service
```

Der Modell-Download und die isolierte Hermes-Runtime bleiben dabei erhalten.
Live-Prüfprotokolle und eine Detailansicht liegen unter `evidence/hermes/`.

Das laufende Caelestia-KDE-Startmenü verwendet jetzt eine abgerundete Glasfläche
mit eigenem KWin-Blur, Suche oben, Benutzerzeile, zwölf App-Kacheln, echten zuletzt
geöffneten Dateien und einer unteren Aktionsleiste. Unter der Topbar hält das Menü nun 24 logische Pixel Abstand zur linken Kante. Topbar und Dock wurden nicht verschoben.

- „Letzte Apps“ zeigt bis zu zwölf zuletzt gestartete oder fokussierte Apps,
  neueste zuerst und ohne Dopplungen. Geschlossene Apps bleiben im Verlauf,
  solange sie weiterhin installiert und im Launcher sichtbar sind. Unter
  „Alle Apps“ stehen die nativen Kategorien und Favoritensterne zur Verfügung.
- Benutzername und Avatar stammen vom lokalen Konto. Das Avatarbild verwendet
  Mipmapping für glatte Verkleinerung sowie eine echte runde Maske mit Kantenglättung. Klick öffnet die
  Kontoverwaltung. Es wird keine beispielhafte E-Mail-Adresse angezeigt.
- „Zuletzt geöffnet“ liest vorhandene lokale Dateien aus `recently-used.xbel`.
  Drei Einträge werden direkt gezeigt, „Mehr“ erweitert auf maximal zwölf.
  Fehlende Dateien und die eigenen Launcher-Prüfbilder werden ausgelassen.
  Dateien öffnen mit ihrer zugeordneten Anwendung. Bei leerem Verlauf erscheint
  ein entsprechender Hinweis.
- Suche, Befehlspräfix `>`, Zwischenablage, Wallpaper- und Fensterwechsel verwenden
  weiterhin Caelestias vorhandene Komponenten. Ctrl+K fokussiert die Suche.
  Der Pfeil im Suchfeld beziehungsweise Escape führt aus „Alle Apps“ zurück.
- Einstellungen, der bedingte Windows-Neustart, Sperren, Neustart und Ausschalten sind echte Aktionen.
  Neustart und Ausschalten beachten `launcher.showPowerMenu` und verwenden die
  vorhandenen Sitzungsbefehle.
- Die Fläche ist maximal 720 × 880 logische Pixel groß. Auf kleineren Displays
  wird sie begrenzt; der Startbereich scrollt, und unter 540 Pixel Inhaltsbreite
  wechselt das App-Raster auf vier Spalten. Die Suche und Aktionsleiste bleiben stehen.
  Die Tönung folgt dem hellen beziehungsweise dunklen Farbschema.

## Quellen und Anwendung

`overlay/modules/launcher/` enthält die vollständigen Launcher-Komponenten.
`mock-start-menu.patch` beschreibt Änderungen gegenüber dem vorherigen lokalen
Stand **nach** dem ursprünglichen Top-Left-Patch, inklusive der eigenständigen
Blur-Region in `modules/drawers/ContentWindow.qml`. Die abgeleiteten QML-Dateien
stehen wie Caelestia unter GPL-3.0. Python 3 wird zum Lesen der lokalen Daten benötigt.

Die Änderungen sind auf diesem Rechner bereits installiert. Nach einem
Caelestia-Update zunächst die neue Basis vergleichen. Für dieselbe alte Basis:

```bash
patch --dry-run -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/launcher/mock-start-menu.patch
# Vor Anwendung die vier betroffenen Dateien sichern.
patch -p0 -d "$HOME/.config/quickshell/caelestia" < /home/USER/ralleurOS/kde-customizations/launcher/mock-start-menu.patch
cp /home/USER/ralleurOS/kde-customizations/launcher/overlay/modules/launcher/{Content.qml,StartHome.qml,start-data.py,windows-boot.py,windows.svg} "$HOME/.config/quickshell/caelestia/modules/launcher/"
# Shared helper requires the existing minimal-polkit password-dialog setup.
cp /home/USER/ralleurOS/kde-customizations/launcher/backdrop/blur-strength.py "$HOME/.config/quickshell/minimal-polkit/blur-strength.py"
mkdir -p "$HOME/.config/systemd/user/caelestia-shell.service.d"
cp /home/USER/ralleurOS/kde-customizations/launcher/backdrop/launcher-blur.conf "$HOME/.config/systemd/user/caelestia-shell.service.d/"
bash /home/USER/ralleurOS/kde-customizations/launcher/backdrop/build-blur-settings.sh
mkdir -p "$HOME/.config/quickshell/ralleur-start-backdrop" "$HOME/.local/share/kwin/effects/ralleur-start-backdrop"
cp /home/USER/ralleurOS/kde-customizations/launcher/backdrop/helper/* "$HOME/.config/quickshell/ralleur-start-backdrop/"
cp /home/USER/ralleurOS/kde-customizations/launcher/backdrop/ralleur-start-backdrop.service "$HOME/.config/systemd/user/"
cp -r /home/USER/ralleurOS/kde-customizations/launcher/backdrop/effect/. "$HOME/.local/share/kwin/effects/ralleur-start-backdrop/"
kwriteconfig6 --file kwinrc --group Plugins --key ralleur-start-backdropEnabled true
qdbus6 org.kde.KWin /KWin reconfigure
systemctl --user daemon-reload
systemctl --user restart caelestia-shell.service
```

## Prüfung und Rückbau

Auf dem laufenden 3840×2160-Desktop visuell geprüft: Startseite mit zwölf Apps,
alle 61 Anwendungen, Suchtreffer „Files“, Befehlsmenü mit 16 Einträgen und echter
Blur. Die Startseite passt ohne Scrollen in den verfügbaren Bereich. Keine neuen
QML-Typ-, Referenz- oder Binding-Loop-Fehler im abschließenden Neustart.
Die temporäre IPC-Prüfsteuerung wurde entfernt. Destruktive Sitzungsaktionen
wurden nicht ausgelöst; kleinere Displays und das helle Schema wurden nicht live
visuell geprüft. Protokoll: [evidence/live-check.json](evidence/live-check.json),
[Startmenü](evidence/start-menu-detail.png).

Sicherung des vorherigen Standes:

```text
/home/USER/.local/state/ralleur-desktop/backups/20261101-192750-launcher-mock
```

Rückbau prüft die installierten Prüfsummen, um spätere Änderungen zu schützen:

```bash
python /home/USER/ralleurOS/kde-customizations/launcher/restore.py /home/USER/.local/state/ralleur-desktop/backups/20261101-192750-launcher-mock --dry-run
# Ohne --dry-run wird der vorherige Zustand wiederhergestellt.
systemctl --user restart caelestia-shell.service
```

---

# Launcher oben links

Die installierte Caelestia-Shell wurde am 2026-11-01 angepasst:

- Launcher unter der oberen Leiste links verankert.
- Öffnungsanimation klappt von oben nach unten auf.
- Mausregion und Ziehrichtung an die neue Position angepasst.
- Hintergrund und Blur nutzen die Anker `top` / `left`.

`top-left.patch` enthält die Änderungen relativ zu
`~/.config/quickshell/caelestia`. Vor erneutem Anwenden mit `patch --dry-run -p0`
prüfen. Danach `systemctl --user restart caelestia-shell.service`.

Live visuell geprüft: vollständig geöffneter Launcher oben links, Suchfeld und
Sitzungsschaltflächen sichtbar. Keine QML-Binding- oder Typfehler beim Neustart.
Originaldateien liegen unter
`~/.local/state/ralleur-desktop/backups/20261101-150732-launcher-top-left`.

## Korrigierte Aktionsübergabe

Die untere Leiste übergibt ihre Befehle als JavaScript-Arrays. Ein typisierter
`list<string>`-Funktionsparameter wandelte die verschachtelten Arrays des
Repeater-Modells in leere Listen um. `triggerSessionCommand` akzeptiert jetzt
`var` und kopiert die Argumente vor der Übergabe an SessionManager beziehungsweise
Quickshell. Leere Aktionen werden abgefangen. Dieselbe Korrektur gilt für die
Kontoverwaltung in der Benutzerzeile.

Die Klickstrecke aller fünf Buttons wurde geprüft. Dateien und Einstellungen
wurden tatsächlich gestartet; Sperren, Neustart und Ausschalten lieferten die
korrekten Befehle, deren Ausführung im Test abgefangen wurde. Die temporären
QtTest-/IPC-Hilfen und der Testabfang sind entfernt. Protokoll:
[evidence/footer-actions-check.json](evidence/footer-actions-check.json).

## Desktop-Effekt wie im Passwortfenster

Bei geöffnetem Startmenü erhält das Drawer-Fenster eine bildschirmfüllende
KWin-Blur-Region und dieselbe fast transparente schwarze Fläche (`#02000000`)
wie das bestehende `minimal-polkit`-Passwortfenster. Der übrige Desktop wird
leicht unscharf. Die Komponenten des Menüs bleiben scharf. Die Leisten innerhalb
derselben Shell-Fläche bleiben ebenfalls scharf; es wird kein Screenshot als
Ersatzhintergrund verwendet.

Der bestehende Blur-Helfer wurde auf gemeinsame Nutzer erweitert: Passwortdialog
und Startmenü nutzen `BlurStrength=1`, `NoiseStrength=0`, `Saturation=100`.
Erst beim Schließen der letzten Oberfläche stellt der Helfer alle ursprünglichen
Werte wieder her, einschließlich zuvor nicht gesetzter Schlüssel. Der Dateilock
koordiniert gleichzeitige Aufrufe. Die zusätzliche systemd-Drop-in-Datei entfernt
bei Stopp oder Absturz der Shell verbliebene Launcher-Nutzer. Das
Authentifizierungsverhalten des Passwortdialogs bleibt erhalten.

Vollständiger Helfer und Drop-in liegen unter `backdrop/`; `backdrop/backdrop.patch`
enthält ausschließlich die neue Drawer-Änderung gegenüber dem vorherigen lokalen
Startmenü. Der kumulative Hauptpatch enthält sie ebenfalls. Voraussetzung ist das
bereits vorhandene Passwortfenster unter `~/.config/quickshell/minimal-polkit`.

Geprüft: visuelle Unschärfe beim Öffnen, Wiederherstellung beim Schließen,
beide Schließreihenfolgen gemeinsam mit einem simulierten Passwortdialog-Nutzer
und Bereinigung beim Shell-Neustart. Es wurde kein Passwort angefordert oder
ausgelesen. [Prüfprotokoll](evidence/backdrop-check.json).

Sicherung vor dieser Ergänzung: `/home/USER/.local/state/ralleur-desktop/backups/20261101-194117-launcher-backdrop`.
Nur diese Ergänzung zurücknehmen: Startmenü und Passwortdialog schließen,
Caelestia-Shell stoppen, `ContentWindow.qml` aus dieser Sicherung nach
`~/.config/quickshell/caelestia/modules/drawers/ContentWindow.qml` und
`blur-strength.py` nach `~/.config/quickshell/minimal-polkit/blur-strength.py`
zurückkopieren. Anschließend ausschließlich
`~/.config/systemd/user/caelestia-shell.service.d/launcher-blur.conf` entfernen,
`systemctl --user daemon-reload` und `systemctl --user start caelestia-shell.service`
ausführen. Nachträgliche Änderungen vorher vergleichen. Der allgemeine
Launcher-Rückbau oben stellt die ursprünglichen Launcher-Dateien wieder her;
der gemeinsame Helfer und das Drop-in können danach mit diesen Schritten
separat entfernt werden.

## Weiches Ein- und Ausblenden des Hintergrunds

Der Bildschirm-Blur liegt jetzt auf einer eigenen transparenten, eingabefreien
Fläche unter dem Menü. Die Blur-Einstellungen werden vor ihrem Anzeigen
vorbereitet; der KWin-Effekt `ralleur-start-backdrop` blendet die Fläche samt
nativer Unschärfe über 240 ms mit InOutCubic ein und aus. Erst nach 360 ms werden
die temporären Blur-Einstellungen freigegeben. Damit wird der zuvor sichtbare
Konfigurationswechsel nicht mehr auf einen bereits bildschirmfüllenden Blur
angewendet. Menü und Leisten behalten ihre eigene Animation.

Die Hilfsfläche läuft als schlanker Quickshell-Prozess ohne weitere Shell-Module.
Sie startet und stoppt zusammen mit der Caelestia-Shell; ihre Freigabe ist nach
Monitor getrennt. Der Effekt wird ausschließlich auf die vom Dienst registrierte
Prozess-ID angewendet, da KWin Layer-Shell-Flächen anhand der Prozessklasse statt
ihrer Namespace-Bezeichnung meldet. Der Dienst aktualisiert diese ID bei jedem
Start. Andere Fenster und das Passwortfenster werden nicht animiert.

Unter `backdrop/helper/`, `backdrop/effect/` und `backdrop/ralleur-start-backdrop.service`
liegen die vollständigen neuen Dateien. `backdrop/fade.patch` ergänzt die
vorherige Hintergrund-Version; die anderen Patches wurden ebenfalls aktualisiert.

Die laufende KWin-Animation wurde beim Öffnen und Schließen abgefragt und ihr
Ende geprüft. Sechs schnelle Zustandswechsel endeten ohne sichtbare Fläche oder
verbliebenen Blur-Nutzer. Der gemeinsame Passwortdialog-Helfer wurde erneut auf
beide Schließreihenfolgen und Shell-Neustart geprüft. Temporäre Prüf-IPC und
Diagnoseausgaben wurden entfernt. Protokoll:
[evidence/backdrop-fade-check.json](evidence/backdrop-fade-check.json).

Sicherung vor dieser Erweiterung: `/home/USER/.local/state/ralleur-desktop/backups/20261101-194450-backdrop-fade`. Für den Rückbau zusätzlich zu den
oben genannten Hintergrund-Dateien den Dienst `ralleur-start-backdrop.service`
stoppen und entfernen, den Effekt mit
`qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect ralleur-start-backdrop`
entladen, dessen Ordner unter `~/.local/share/kwin/effects/` entfernen und die
KWin-Schlüssel `Plugins/ralleur-start-backdropEnabled` sowie die Gruppe
`Effect-ralleur-start-backdrop` entfernen. Die vorherige Drop-in-Datei enthielt nur
`[Service]` und den vorhandenen `ExecStopPost` zur Blur-Bereinigung; die neue
`[Unit]`-Abhängigkeit auf den Hilfsdienst dabei ebenfalls zurücknehmen.
Danach systemd neu einlesen und Caelestia starten. Spätere eigene Änderungen
vorher vergleichen.

## Blur beginnt mit dem Klick

Die Hintergrundfläche wird jetzt aus derselben Zustandsänderung wie das Menü
angesteuert. Eine bestehende lokale Socket-Verbindung ersetzt den jeweils neu
gestarteten IPC-Prozess. Die Oberfläche wartet nicht mehr auf den Abschluss der
Blur-Vorbereitung. Ein einzelner nativer KConfig-Helfer ersetzt die vielen
Unterprozesse beim Lesen, Schreiben und Neuladen der temporären Einstellungen.
Das Dateilock und das gemeinsame JSON-Format bleiben mit dem Python-Helfer des
Passwortdialogs kompatibel. Die Einstellungen werden wie bisher nach dem
Ausblenden zurückgesetzt. OutCubic macht die Unschärfe bereits zu Beginn des
240-ms-Verlaufs sichtbar; das weiche Ausblenden bleibt erhalten.

Quellcode: `backdrop/blur-settings.cpp`. Mit
`bash backdrop/build-blur-settings.sh` aus diesem Verzeichnis bauen; benötigt
C++-Compiler, pkg-config, Qt6Core/Qt6DBus und KF6ConfigCore mit Entwicklungsdateien.
Ziel ist `~/.local/libexec/ralleur/blur-settings`. Der Hintergrunddienst entfernt
vor seinem Start nur seinen eigenen eventuell verbliebenen Runtime-Socket.

Messung der letzten drei Öffnungen: Die Hintergrund-Anforderung wurde jeweils
im selben Millisekunden-Zeitstempel wie die Menüöffnung empfangen. KWin begann
seine sichtbare Animation nach 43–48 ms, während das Menü noch öffnet. Der
Native-/Python-Mischbetrieb stellte nach beiden Freigaben die vorherigen Werte
exakt wieder her. [Prüfprotokoll](evidence/immediate-blur-check.json).
Temporäre Messausgaben wurden entfernt. Beim vollständigen Rückbau zusätzlich
`~/.local/libexec/ralleur/blur-settings` entfernen.

## Linker Abstand und zuletzt verwendete Apps

`recent-apps-inset.patch` verschiebt ausschließlich den Launcher innerhalb der
bestehenden Panels um 24 logische Pixel nach rechts. Die verfügbare Breite wird
entsprechend reduziert; Blur-Region und Klickbereich folgen der Panel-Geometrie.
Andere Panels werden nicht verschoben. Unter „Letzte Apps“ zeigt das Raster jetzt
bis zu zwölf echte zuletzt gestartete oder fokussierte Anwendungen. Bei weniger
Einträgen bleiben die Kacheln linksbündig in ihrer normalen Spaltenbreite.

Die App-Historie erfasst Launcher-Starts sowie neue und aktivierte KWin-Fenster,
also auch Dock-Starts und normale Fensterwechsel. Gespeichert werden maximal 48
Desktop-IDs als JSON in QtCore Settings unter `[RalleurStartMenu]`, Schlüssel
`recentAppIdsJson`. Es werden keine Fenstertitel gespeichert und keine Favoriten
oder häufigen Apps als vermeintliche Historie ergänzt. Die Liste füllt sich ab
der ersten erfassten Verwendung. Unsichtbare beziehungsweise deinstallierte Apps
werden bei der Darstellung ausgelassen. Ein zeitlich entkoppelter ScriptModel
vermeidet Änderungen am Raster während der QML-Delegate-Erzeugung.

Live geprüft: linker Inhaltsbeginn bei x=50 (24 Pixel Außenabstand plus 26 Pixel
Innenabstand), vollständige Kontur, Chromium → Dolphin → ChatGPT als echte
Fensterwechsel, neue App jeweils vorne, keine Dopplungen sowie unveränderte
Reihenfolge nach Shell-Neustart. Temporäre Diagnose-IPC wurde entfernt.
[Prüfprotokoll](evidence/recent-apps-check.json),
[Ansicht](evidence/recent-apps-detail.png).

Sicherung vor dieser Änderung: `/home/USER/.local/state/ralleur-desktop/backups/20261101-204357-recent-apps-inset`. Sie enthält die vier betroffenen
Dateien relativ zum Shell-Verzeichnis. Zum gezielten Rückbau diese Dateien nach
Prüfung späterer Änderungen zurückkopieren und die Shell neu starten. Die
App-Historie bleibt als Benutzereinstellung erhalten. Der kumulative Hauptpatch
und das allgemeine Rückbau-Manifest enthalten die neuen Änderungen ebenfalls.


## Rauchglas mit vorgewärmtem Blur-Pool

Startmenü und Hermes-Fläche nutzen jetzt das freigegebene `MenuStyle.smokeSurface`
der Taskbar. Der lokale `TaskbarGlass`-Pool ersetzt die frühere bildschirmfüllende
Launcher-Backdrop-Anforderung und deren globale Blur-Lease. Er verwendet acht
stabile, wiederverwendete native Flächen; keine Fensterneuanlage/-zerstörung oder
Puffergrößenwechsel während der geprüften Animationen. Das bestehende 720 × 880-px-
Layout, Suche, Karten, Schriften, Footer und Hermes-Geometrie bleiben erhalten.

Installation über `../taskbar/menu-style/taskbar_glass.py`; gemeinsame Umsetzung,
Layoutnachweis, Performance-Gegenproben und Rückbau:
[Startmenü-/Dashboard-Rauchglas](../taskbar/menu-style/README.md#startmenü-und-dashboard-gemeinsames-rauchglas-ohne-layoutänderung).


## Wiederhergestellt: bildschirmfüllender Hintergrund-Blur

Auf Nutzerwunsch ist der Hintergrund-Blur des Startmenüs wieder aktiv. Der
lokale Rauchglas-Pool und das Menü-Layout bleiben erhalten. `ContentWindow`
meldet den Launcher über eine dauerhafte Socket-Verbindung als `launcher:`-Client
beim vorhandenen Dolphin-Backdrop an. Dieser zeichnet auf allen Bildschirmen
denselben Blur wie beim Dolphin-Kontextmenü. Das Startmenü liegt darüber und
bleibt scharf. Schließen oder Verbindungsabbruch gibt die Anforderung frei;
nach einem Helper-Neustart verbindet sich die Shell erneut und meldet ihren
aktuellen Zustand. Dolphin- und Launcher-Anforderungen können überlappen.
Die gemeinsame bisherige Blur-Lease bleibt aktiv, solange ein Client offen ist.

Installation: `backdrop/helper/shell.qml` nach
`~/.config/quickshell/ralleur-start-backdrop/shell.qml` kopieren und
`python3 ../taskbar/menu-style/taskbar_glass.py` ausführen; anschließend
`systemctl --user restart ralleur-start-backdrop.service caelestia-shell.service`.
Der Installer erhält die Anbindung bei späteren Rauchglas-Anpassungen.
