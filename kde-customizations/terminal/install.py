#!/usr/bin/env python3
"""Install the Fish greeting and terminal icons; preserve system information."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime

SOURCE = Path(__file__).resolve().parent
HOME = Path.home()
DATA = Path(os.environ.get('XDG_DATA_HOME', HOME / '.local/share'))
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', HOME / '.config'))
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'flausen-terminal'


def refresh():
    for command in (['kbuildsycoca6', '--noincremental'],):
        if shutil.which(command[0]):
            subprocess.run(command, check=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', type=Path, metavar='BACKUP')
    args = parser.parse_args()
    if args.restore:
        backup = args.restore.resolve()
        entries = json.loads((backup / 'manifest.json').read_text())
        for entry in entries:
            path = Path(entry['path'])
            installed = backup / entry['installed']
            if not path.exists() or path.read_bytes() != installed.read_bytes():
                raise SystemExit(f'Geänderte Datei wird nicht überschrieben: {path}')
        for entry in reversed(entries):
            path = Path(entry['path'])
            if entry['previous'] is None:
                path.unlink()
            else:
                shutil.copy2(backup / entry['previous'], path)
        refresh()
        return

    files = {
        DATA / 'flausen-terminal/flausen.py': (SOURCE / 'flausen.py').read_bytes(),
        CONFIG / 'fish/functions/fish_greeting.fish': (SOURCE / 'fish_greeting.fish').read_bytes(),
        DATA / 'flausen-terminal/terminal.png': (SOURCE / 'terminal.png').read_bytes(),
    }
    # Keep the original desktop IDs, translations, actions and launch commands.
    for name in ('org.kde.konsole.desktop', 'foot.desktop', 'footclient.desktop', 'foot-server.desktop'):
        target = DATA / 'applications' / name
        original = target if target.exists() else Path('/usr/share/applications') / name
        if not original.exists():
            continue
        content = original.read_text()
        icon = DATA / 'flausen-terminal/terminal.png'
        content = re.sub(r'^Icon=(?:utilities-terminal|foot|flausen-terminal|' + re.escape(str(icon)) + r')$',
                         lambda _: f'Icon={icon}', content, flags=re.MULTILINE)
        files[target] = content.encode()
    changed = {p: data for p, data in files.items() if not p.exists() or p.read_bytes() != data}
    if not changed:
        print('Bereits installiert.')
        return
    backup = STATE / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    entries = []
    for number, (path, content) in enumerate(changed.items()):
        previous = None
        if path.exists():
            previous = f'{number}.previous'
            shutil.copy2(path, backup / previous)
        installed = f'{number}.installed'
        (backup / installed).write_bytes(content)
        entries.append({'path': str(path), 'previous': previous, 'installed': installed})
    (backup / 'manifest.json').write_text(json.dumps(entries, indent=2) + '\n')
    try:
        for path, content in changed.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    except Exception:
        for entry in reversed(entries):
            path = Path(entry['path'])
            if entry['previous'] is not None:
                shutil.copy2(backup / entry['previous'], path)
            else:
                path.unlink(missing_ok=True)
        raise
    refresh()
    print(f'Installiert. Sicherung: {backup}')


if __name__ == '__main__':
    main()
