#!/usr/bin/env bash
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
build_dir="${XDG_CACHE_HOME:-$HOME/.cache}/ralleur-desktop-scroll-build"
script_dir="${XDG_DATA_HOME:-$HOME/.local/share}/kwin/scripts/ralleur-desktop-scroll"
cmake -S "$source_dir" -B "$build_dir"
cmake --build "$build_dir" --parallel 4
# Unload before replacing the native library used by the compositor.
qdbus6 org.kde.KWin /Scripting unloadScript ralleur-desktop-scroll || true
mkdir -p "$script_dir/contents/ui/native"
cp "$source_dir/metadata.json" "$script_dir/"
cp "$source_dir/main.qml" "$script_dir/contents/ui/"
cp "$source_dir/native/qmldir" "$build_dir/libdesktopscroll.so" "$script_dir/contents/ui/native/"
kwriteconfig6 --file kwinrc --group Plugins --key ralleur-desktop-scrollEnabled true
qdbus6 org.kde.KWin /KWin reconfigure
