#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if command -v npm >/dev/null 2>&1; then exec npm run dev -- "$@"; fi
# Codex's bundled Node is available on this workstation but is not on PATH.
web_node="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
web_npm="$(pwd)/../.cache/flausen-web-tools/package/bin"
if [[ -x "$web_node/node" && -f "$web_npm/npm-cli.js" ]]; then
 export PATH="$web_node:$web_npm:$PATH"
 exec "$web_node/node" "$web_npm/npm-cli.js" run dev -- "$@"
fi
printf '%s\n' 'Install Node.js 22.12+ and npm, then run npm ci and npm run dev in website/.' >&2
exit 1
