#!/usr/bin/env bash
set -euo pipefail
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
shell_dir="${1:-$HOME/.config/quickshell/caelestia}"
backup_dir="$HOME/.local/state/ralleur/backups/osd-glass-$(date +%Y%m%d-%H%M%S)"
# Check the shared drawer patch before touching the running shell.
if patch --dry-run --forward -p0 -d "$shell_dir" < "$source_dir/../osd-glass.patch" >/dev/null 2>&1; then
    apply_patch=true
elif patch --dry-run --reverse -p0 -d "$shell_dir" < "$source_dir/../osd-glass.patch" >/dev/null 2>&1; then
    apply_patch=false
else
    echo 'OSD drawer patch does not match this shell version.' >&2
    exit 1
fi
mkdir -p "$backup_dir/modules/osd" "$backup_dir/modules/drawers"
cp -a "$shell_dir/modules/osd/." "$backup_dir/modules/osd/"
cp -a "$shell_dir/modules/drawers/ContentWindow.qml" "$backup_dir/modules/drawers/"
systemctl --user stop caelestia-shell.service
trap 'systemctl --user start caelestia-shell.service' EXIT
if "$apply_patch"; then
    patch --forward -p0 -d "$shell_dir" < "$source_dir/../osd-glass.patch"
fi
install -m644 "$source_dir/Content.qml" "$source_dir/SegmentedSlider.qml" "$shell_dir/modules/osd/"
echo "Backup: $backup_dir"
