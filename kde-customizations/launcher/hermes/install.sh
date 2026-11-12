#!/bin/bash
set -euo pipefail
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
runtime_dir="$HOME/.local/share/ralleur-hermes"
shell_dir="$HOME/.config/quickshell/caelestia"
runtime_commit=c7da41dd522dc19cc08bbfcfa69d4b078224b45d
test -f "$shell_dir/modules/launcher/Content.qml"
mkdir -p "$runtime_dir" "$HOME/.local/bin" "$HOME/.local/state/ralleur-hermes/profile"
chmod 700 "$HOME/.local/state/ralleur-hermes" "$HOME/.local/state/ralleur-hermes/profile"
if ! test -d "$runtime_dir/runtime/.git"; then
    git clone https://github.com/NousResearch/hermes-agent.git "$runtime_dir/runtime"
    git -C "$runtime_dir/runtime" checkout "$runtime_commit"
fi
if test "$(git -C "$runtime_dir/runtime" rev-parse HEAD)" != "$runtime_commit"; then
    echo "Die vorhandene Hermes-Version weicht vom geprüften Stand ab. Bitte zuerst vergleichen." >&2
    exit 1
fi
if ! test -x "$runtime_dir/venv/bin/python"; then python -m venv "$runtime_dir/venv"; fi
if ! test -x "$runtime_dir/venv/bin/uv"; then "$runtime_dir/venv/bin/pip" install uv; fi
UV_PROJECT_ENVIRONMENT="$runtime_dir/venv" "$runtime_dir/venv/bin/uv" sync --project "$runtime_dir/runtime" --locked --no-dev
selected_model=$("$runtime_dir/venv/bin/python" - "$source_dir/config.yaml" <<'PY'
from pathlib import Path
from ruamel.yaml import YAML
import sys
print(YAML(typ='safe').load(Path(sys.argv[1]).read_text())['model']['default'])
PY
)
case "$selected_model" in
    deepseek-flash) source_model=; model_file= ;;
    gpt-6.1-sol) source_model=; model_file= ;;
    qwen3.8:27b-hermes) source_model=; model_file=; python "$source_dir/qwen38/install.py" ;;
    lfm3:1.7b-hermes) source_model=lfm3:1.7b; model_file=Modelfile ;;
    qwen3.5:4b-hermes) source_model=qwen3.5:4b; model_file=Qwen.Modelfile ;;
    qwen3.5:9b-hermes) source_model=qwen3.5:9b; model_file=Qwen9.Modelfile ;;
    *) echo "Nicht unterstütztes Modell: $selected_model" >&2; exit 1 ;;
esac
if test -n "$source_model"; then
    command -v ollama >/dev/null
    ollama pull "$source_model"
    ollama create "$selected_model" -f "$source_dir/$model_file"
fi
python - "$source_dir" <<'PY'
from pathlib import Path
import datetime, hashlib, json, shutil, sys
src = Path(sys.argv[1])
home = Path.home()
shell = home / '.config/quickshell/caelestia'
backup = home / '.local/state/ralleur-desktop/backups' / (datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-hermes-launcher')
backup.mkdir(parents=True)
files = {f'modules/launcher/{f}': src.parent/'overlay/modules/launcher'/f for f in ('Content.qml', 'Wrapper.qml', 'HermesChat.qml', 'services/HermesDesktop.qml')}
for component in ('ExperimentalTag.qml', 'AgentSafetyNotice.qml'):
    files['components/'+component] = src.parent.parent/'settings/overlay/components'/component
manifest = {}
for name, source in files.items():
    target = shell/name
    original = backup/name
    original.parent.mkdir(parents=True, exist_ok=True)
    if target.exists(): shutil.copy2(target, original)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    manifest[name] = hashlib.sha256(target.read_bytes()).hexdigest()
(backup/'installed-sha256.json').write_text(json.dumps(manifest, indent=2)+'\n')
config = home/'.local/state/ralleur-hermes/profile/config.yaml'
if config.exists(): shutil.copy2(config, backup/'hermes-config.yaml')
shutil.copy2(src/'config.yaml', config)
config.chmod(0o600)
shutil.copy2(src/'bridge.py', home/'.local/share/ralleur-hermes/bridge.py')
wrapper = home/'.local/bin/ralleur-hermes'
shutil.copy2(src/'ralleur-hermes', wrapper)
wrapper.chmod(0o755)
print(f'Sicherung: {backup}')
PY
systemctl --user restart caelestia-shell.service
