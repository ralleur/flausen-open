# Qwen 3.8 27B in Hermes

Dritte Auswahl in **Einstellungen → Hermes**, neben DeepSeek Flash und LFM3.
Das bestehende Standardmodell wird bei der Installation nicht geändert.
Nach Auswahl und **Übernehmen** in Hermes eine neue Unterhaltung beginnen.

Vorbild: [mberatsanli/qwen38-27b-local](https://github.com/mberatsanli/qwen38-27b-local),
insbesondere Q4_0-KV, Flash Attention, MTP mit drei Draft-Tokens, eine Sequenz
und `-fit off`. Die feste Kontextgröße wird dadurch nicht still verkleinert.

## Lokales Profil

- `unsloth/Qwen3.8-27B-GGUF`, `UD-Q3_K_XL`, 13.146.393.504 Bytes.
- llama.cpp **b12052**, Commit `84d9ce0fa`, Linux x64 / CUDA 13.4.
- **90.112 Tokens** Gesamtkontext; Hermes verwendet bis zu 8.192 Ausgabetokens.
  Eingabe, bisherige Unterhaltung, Denken und Antwort teilen sich den Kontext.
- **44 GPU-Schichten**; weitere Modellanteile und deren Zustand liegen im RAM.
  Der laufende Desktop belegte vor dem Laden etwa 3 GiB VRAM. Die reine
  GPU-Konfiguration des Vorbilds passt unter diesen Bedingungen nicht.
- `-ctk q4_0 -ctv q4_0 -fa on`, MTP-Draft 3, `-np 1`, `--jinja`.
- Nur `127.0.0.1:18038`, Modellalias `qwen3.8:27b-hermes`.
- Start beim ersten Qwen-Aufruf, keine Aktivierung beim Booten.
- Nach **120 Sekunden ohne Anfragen** entlädt llama.cpp das Modell. Die nächste
  Anfrage lädt es wieder. Beim Wechsel zu einem anderen Modell in einer neuen
  Hermes-Unterhaltung wird der Dienst gestoppt.

Der Denkmodus-Schalter sendet Qwen-kompatible Template-Parameter: `medium`
beziehungsweise `none` plus `enable_thinking`. Es werden keine Ollama-Optionen
an llama.cpp geschickt. Die bestehenden Desktop-Werkzeuge und die ausdrückliche
Bestätigung von Shell-Befehlen bleiben erhalten.
Qwen erhält wegen der langsameren GPU/RAM-Ausführung ein Laufzeitbudget von
20 Minuten; andere Modelle behalten ihr bisheriges Budget. Abbrechen im Chat
bleibt jederzeit möglich.

## Laufzeit installieren

```bash
python kde-customizations/launcher/hermes/qwen38/install.py
```

Der Installer benötigt kein root, prüft SHA-256 für Modell und beide offiziellen
CUDA-Archive und verändert kein Hermes-Profil. Ziel:
`~/.local/share/ralleur-hermes/qwen38/` und `../models/`.
Die Bridge und die Einstellungsoberfläche werden durch die Desktop-Integration
bereitgestellt. Der Runtime-Installer allein ergänzt keine UI.

Die lokal abgestimmten Werte stehen in `qwen38/profile.json`. Folgeinstallationen
erhalten diese Datei. Änderungen werden mit
`systemctl --user restart ralleur-hermes-qwen.service` übernommen.
Kontextänderungen auch im Modellpreset in `settings/helpers/hermes_settings.py`
und in den UI-Angaben nachführen; bei einer bereits gespeicherten Qwen-Auswahl
danach das Profil erneut übernehmen.

```bash
systemctl --user stop ralleur-hermes-qwen.service
journalctl --user -u ralleur-hermes-qwen.service
python kde-customizations/launcher/hermes/qwen38/check_runtime.py \
  --output /tmp/qwen38-runtime.json
```

Der Laufzeittest verarbeitet tatsächlich 89.000 Eingabetokens und erzeugt eine
kurze Ausgabe, prüft die unverkleinerte Kontextgröße und zeichnet die gesamte
GPU-Belegung auf. Das prüft Speicher und Ausführung, keine Langkontextqualität.
Er erwartet einen bereits gestarteten Dienst.

## Prüfung am 2. November 2026

Die echte Hermes-Unterhaltung zur Autostart-Frage rief `autostart_status` auf
und gab die unabhängig geprüften Programme WowUp und VNC Desktop Sharing
korrekt wieder. Insgesamt 36 Sekunden einschließlich Modellanfragen und
Werkzeugverarbeitung; die abschließende Ausgabe lief mit rund 9,3 Tokens/s.
Diese Messung ist kein allgemeiner Geschwindigkeitsbenchmark.

Der echte Langkontexttest verarbeitete 89.000 Eingabetokens bei unverändertem
90.112-Token-Fenster ohne Kürzung. Dauer: 144,56 Sekunden, davon 143,67 Sekunden
für die Eingabe; mindestens 837 MiB GPU-Speicher blieben frei, einschließlich
des laufenden Desktops. Der Denkmodus lieferte bei einer Rechenprobe sowohl
`reasoning_content` als auch das richtige Ergebnis im Antwortfeld.

Belege unter `settings/evidence/`: `qwen38-hermes.json`, `qwen38-runtime.json`,
`qwen38-thinking.json`, `qwen38-lifecycle.json` und `native/hermes-qwen.png`.
Die UI-Prüfung wählte Qwen aus und setzte die Auswahl zurück, ohne die aktive
Modellkonfiguration zu ändern. Der echte Modellwechsel zurück zu DeepSeek
stoppte den Qwen-Dienst und gab rund 11,5 GiB VRAM wieder frei.

Die GPU-Vorschau folgt dem ausgewählten lokalen Modell. Für Qwen berücksichtigt
sie die eingerichteten GPU-Schichten, den Kontext und Laufzeit samt Reserve;
CPU-Anteile werden nicht als VRAM gezählt. Die aktuelle Gesamtbelegung wird
unabhängig davon live gemessen. Das Kontextbudget verändert nur die Vorschau.
