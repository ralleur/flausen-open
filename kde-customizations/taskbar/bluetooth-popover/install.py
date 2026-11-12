#!/usr/bin/env python3
"""Install Bluetooth menu proportions, preserving adapter/device state."""
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import re
import shutil

SOURCE = Path(__file__).resolve().parent
SHELL = Path.home() / '.config/quickshell/caelestia'
CONFIG = Path.home() / '.config/caelestia/shell.json'


def install():
    files = {'modules/bar/popouts/Bluetooth.qml': (SOURCE / 'Bluetooth.qml').read_text()}
    path = 'modules/bar/popouts/Content.qml'
    text = (SHELL / path).read_text()
    text, count = re.subn(r'(name: "bluetooth"\n)(?!\s*minScale:)', r'\1            minScale: 1.15\n', text, count=1)
    if not count and not re.search(r'name: "bluetooth"\n\s*minScale: 1.15', text):
        raise SystemExit('Unerwarteter Bluetooth-Popout-Aufbau')
    files[path] = text
    path = 'modules/bar/popouts/ClipWrapper.qml'
    def extend_profile(match):
        keys = json.loads(match.group(1))
        if 'bluetooth' not in keys:
            keys.append('bluetooth')
        return json.dumps(keys) + '.includes(content.currentName)'
    text = re.sub(r'(\[[^\]\n]*"updateIndicator"[^\]\n]*\])\.includes\(content.currentName\)', extend_profile, (SHELL / path).read_text())
    if not re.search(r'\[[^\]\n]*"bluetooth"[^\]\n]*\]\.includes\(content.currentName\)', text):
        raise SystemExit('Zuerst das gemeinsame Netzwerk-/Update-Glasprofil installieren.')
    files[path] = text
    config = json.loads(CONFIG.read_text())
    bar = config.get('bar', {})
    offsets = bar.get('previewFontScales', {})
    value = offsets.get('bluetooth')
    migrate = bar.get('perElementFontScale') and isinstance(value, (int, float)) and abs(value - 0.26) < 0.00001
    changed = {name: value for name, value in files.items() if (SHELL / name).read_text() != value}
    if not changed and not migrate:
        print('Bluetooth-Proportionen sind bereits installiert.')
        return
    backup = Path.home() / '.local/state/ralleur-taskbar-backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-bluetooth-proportions')
    backup.mkdir(parents=True)
    patch = []
    for name, value in changed.items():
        target, saved = SHELL / name, backup / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        patch.extend(difflib.unified_diff(target.read_text().splitlines(True), value.splitlines(True), fromfile=name, tofile=name))
    if migrate:
        shutil.copy2(CONFIG, backup / 'shell.json')
    for name, value in changed.items():
        (SHELL / name).write_text(value)
    if migrate:
        offsets['bluetooth'] = 0
        CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=4) + '\n')
    (backup / 'migration.json').write_text(json.dumps({'bluetoothFontOffset': {'before': 0.26, 'after': 0} if migrate else None}, indent=2) + '\n')
    (SOURCE.parent / 'bluetooth-proportions.patch').write_text(''.join(patch))
    (SOURCE.parent / 'evidence/bluetooth-proportions-backup.txt').write_text(str(backup) + '\n')
    print(backup)


if __name__ == '__main__':
    install()
