#!/usr/bin/env python3
"""Use KWin's shared controls instead of PhotoCraft's built-in Breeze captions."""
import argparse
import json
import os
from pathlib import Path

HOME = Path.home()
PREFERENCES = HOME / '.var/app/ai.storyteller.photocraft/config/photocraft/preferences.json'
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'ralleur-desktop-tweaks/photocraft-window-controls.json'


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.ralleur-new')
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    temp.replace(path)


def configure(restore=False):
    # PhotoCraft writes preferences on exit. Close it normally before editing.
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if (entry / 'comm').read_text().strip() == 'photocraft':
                raise SystemExit('Close PhotoCraft normally before changing its title bar preference.')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            pass
    data = json.loads(PREFERENCES.read_text())
    interface = data.setdefault('interface', {})
    previous = json.loads(STATE.read_text()) if STATE.exists() else None
    if restore:
        if not previous:
            raise SystemExit('No saved title bar preference.')
        if interface.get('systemTitleBar') is not True:
            raise SystemExit('Preserving a subsequently changed title bar preference.')
        if previous['existed']:
            interface['systemTitleBar'] = previous['before']
        else:
            interface.pop('systemTitleBar', None)
        atomic(PREFERENCES, data)
        STATE.rename(STATE.with_suffix('.restored.json'))
    else:
        if not previous:
            atomic(STATE, {'existed': 'systemTitleBar' in interface, 'before': interface.get('systemTitleBar')})
        interface['systemTitleBar'] = True
        atomic(PREFERENCES, data)
    print('PhotoCraft title bar preference ' + ('restored.' if restore else 'set to native KWin controls.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--restore', action='store_true')
    configure(parser.parse_args().restore)
