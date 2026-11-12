#!/usr/bin/env python3
"""Install the network menu proportions without changing any connections."""
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
    backup = Path.home() / '.local/state/ralleur-taskbar-backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-network-proportions')
    files = {f'modules/bar/popouts/{name}': (SOURCE / name).read_text() for name in ('Network.qml', 'WirelessPassword.qml')}
    path = 'modules/bar/popouts/Content.qml'
    text = (SHELL / path).read_text()
    for name in ('network', 'ethernet', 'wirelesspassword'):
        text, count = re.subn(r'(name: "' + name + r'"\n)(?!\s*minScale:)', r'\1            minScale: 1.15\n', text, count=1)
        if not count and not re.search(r'name: "' + name + r'"\n\s*minScale: 1.15', text):
            raise SystemExit('Unerwarteter Popout-Aufbau: ' + name)
    files[path] = text
    path = 'modules/bar/popouts/ClipWrapper.qml'
    text = (SHELL / path).read_text()
    text = text.replace('content.currentName === "updateIndicator"', '["updateIndicator", "network", "ethernet", "wirelesspassword"].includes(content.currentName)')
    if not re.search(r'\[[^\]\n]*"wirelesspassword"[^\]\n]*\]\.includes\(content.currentName\)', text):
        raise SystemExit('Unerwarteter Glas-Aufbau; zuerst den aktuellen Update-Hub-Stil installieren.')
    files[path] = text
    config = json.loads(CONFIG.read_text())
    bar = config.get('bar', {})
    # The previous network style used +0.27 to compensate for a 0.648-wide
    # popover scale. With a 1.15 minimum this would enlarge the text twice.
    # Only migrate that known legacy value; retain custom accessibility values.
    font_scales = bar.get('previewFontScales', {})
    migrate_font = abs(font_scales.get('network', -1) - 0.27) < 0.00001
    changed = {name: text for name, text in files.items() if (SHELL / name).read_text() != text}
    if not changed and not migrate_font:
        print('Netzwerk-Proportionen sind bereits installiert.')
        return
    backup.mkdir(parents=True)
    patch = []
    for name, value in changed.items():
        target = SHELL / name
        saved = backup / name
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        patch.extend(difflib.unified_diff(target.read_text().splitlines(True), value.splitlines(True), fromfile=name, tofile=name))
    if migrate_font:
        shutil.copy2(CONFIG, backup / 'shell.json')
    for name, value in changed.items():
        (SHELL / name).write_text(value)
    if migrate_font:
        font_scales['network'] = 0
        CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=4) + '\n')
    (backup / 'migration.json').write_text(json.dumps({'networkFontOffset': {'before': 0.27, 'after': 0} if migrate_font else None}, indent=2) + '\n')
    (SOURCE.parent / 'network-proportions.patch').write_text(''.join(patch))
    (SOURCE.parent / 'evidence/network-proportions-backup.txt').write_text(str(backup) + '\n')
    print(backup)


if __name__ == '__main__':
    install()
