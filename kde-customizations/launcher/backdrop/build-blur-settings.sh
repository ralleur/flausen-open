#!/bin/bash
set -euo pipefail
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
output="${1:-$HOME/.local/libexec/ralleur/blur-settings}"
mkdir -p -- "$(dirname -- "$output")"
c++ -O2 -fPIC -std=c++20 "$source_dir/blur-settings.cpp" -o "$output" \
    -I/usr/include/KF6/KConfigCore -I/usr/include/KF6/KConfig \
    $(pkg-config --cflags --libs Qt6Core Qt6DBus) -lKF6ConfigCore
