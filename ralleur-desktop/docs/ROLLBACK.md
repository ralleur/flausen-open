# Sicherung und Rollback

Es gibt keine Root-Schritte, keine Paketinstallation und keine automatische Session-Umschaltung. Der Installer verwaltet ausschließlich seine eigene Datenkopie, die eigene Konfiguration und den expliziten Entrypoint `ralleur-desktop`.

Vor dem ersten Schreibzugriff werden alle drei Ziele einschließlich vorhandener Dateien und Symlinks in einem privaten Backup-Verzeichnis gesichert. `manifest.json` hält auch fest, welche Ziele zuvor gar nicht existierten. Eine Dateisperre serialisiert Installation, Theme-Schreiben und Rollback. Schlägt die Installation fehl, werden die vorherigen Ziele aus diesem Snapshot wiederhergestellt. Identische Installation ohne lokale Änderungen ist ein No-op. `--dry-run` zeigt die Ziele an; außer einem eigenen Zustands-/Lock-Verzeichnis entstehen keine installierten Dateien.

1. Die Ralleur-Session regulär verlassen. Vorhandenes KDE über die bisherige Anmeldung weiterverwenden.
2. `~/.local/bin/ralleur-desktop rollback` ausführen. Der Befehl wählt das letzte in `installation.json` verzeichnete Backup.
3. Bei eigenen Änderungen zunächst die Meldung lesen. Mit `rollback --force` werden diese Dateien unter `<Backup>/before-rollback/` gesichert, dann die früheren Ziele wiederhergestellt.
4. Für ein bestimmtes Backup: `/Pfad/zum/entpackten/ralleur-desktop/bin/ralleur rollback --backup /absoluter/Pfad/zum/Backup`. Derselbe XDG-Kontext bzw. dieselben `RALLEUR_*`-Pfade wie bei Installation müssen gesetzt sein.

Der Rückbau kann seinen eigenen installierten Befehl entfernen; der laufende Prozess hat den Code bereits geladen. Eine zuvor vorhandene Datei oder ein Symlink am Entrypoint wird wiederhergestellt. Ein vor dem Upgrade vorhandener Ralleur-Zustand wird einschließlich seines früheren Theme-Modus restauriert. Der erste Rückbau entfernt die neu angelegten Installationsziele. Die eigene Zustandsablage, Browserprofile, Cache und Backups werden bewusst behalten; sie können später nach Sichtprüfung gelöscht werden. Der separat gebaute Plugin-Prefix und die Upstream-Checkouts werden nicht gelöscht oder verändert.

Normale produktive Dateien wie `~/.config/caelestia/shell.json`, `~/.config/quickshell/caelestia`, `~/.config/kdeglobals` und `~/.config/hypr` sind keine Installationsziele. Falls die Ralleur-Datei manuell in eine vorhandene Hyprland-Konfiguration eingebunden wurde, diese eigene `dofile`-/`source`-Zeile vor dem nächsten Start entfernen bzw. das selbst erstellte Backup restaurieren. Der Installer bearbeitet diese Fremddatei nicht.

Automatisiert geprüft: bestehender Entrypoint wird restauriert; ursprüngliche Caelestia-Datei bleibt bytegleich; Theme-Wechsel verursacht keinen falschen Drift; identische Installation ist idempotent; lokale Änderungen werden geschützt und bei `--force` zusätzlich gerettet; `local.lua` bleibt bei einem Upgrade erhalten. Tests laufen ausschließlich in temporären Zielverzeichnissen.
