#!/usr/bin/env bash
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
script_dir="${XDG_DATA_HOME:-$HOME/.local/share}/kwin/scripts/ralleur-fullscreen-desktops"
backup_dir="${XDG_STATE_HOME:-$HOME/.local/state}/ralleur-desktop/backups/$(date +%Y%m%d-%H%M%S)-fullscreen-routing"
mkdir -p "$backup_dir"
cp "$HOME/.config/kwinrc" "$backup_dir/kwinrc"
if [[ -d "$script_dir" ]]; then cp -a "$script_dir" "$backup_dir/package"; fi
mkdir -p "$script_dir/contents/code"
cp "$source_dir/metadata.json" "$script_dir/"
cp "$source_dir/main.js" "$script_dir/contents/code/"
kwriteconfig6 --file kwinrc --group Plugins --key ralleur-fullscreen-desktopsEnabled true
qdbus6 org.kde.KWin /Scripting unloadScript ralleur-fullscreen-desktops >/dev/null
# After unloading, KWin can reuse a script number that is still registered on D-Bus.
qdbus6 org.kde.KWin /Scripting start
[[ $(qdbus6 org.kde.KWin /Scripting isScriptLoaded ralleur-fullscreen-desktops) == true ]]
printf '%s\n' "$backup_dir" > "$source_dir/backup-latest.txt"
printf 'Fullscreen routing installed. Backup: %s\n' "$backup_dir"
