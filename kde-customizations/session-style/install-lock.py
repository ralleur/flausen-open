#!/usr/bin/env python3
"""User-local visual override for the active Caelestia Plasma screen-lock shell."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
DATA = Path(os.environ.get('XDG_DATA_HOME', HOME / '.local/share'))
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'ralleur-desktop-tweaks'
TARGET = DATA / 'plasma/shells/caelestia.desktop/contents'
CURRENT = STATE / 'session-style-lock.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def verify(manifest):
    for record in manifest['targets']:
        path = Path(record['path'])
        if path.is_symlink() or digest(path) != record['sha256']:
            raise SystemExit(f'Externally changed; preserving {path}')

def install():
    if not (TARGET.parent / 'metadata.json').is_file():
        raise SystemExit('The Caelestia Plasma shell package is not installed.')
    previous = json.loads(CURRENT.read_text()) if CURRENT.exists() else None
    if previous: verify(previous)
    files = {TARGET / 'lockscreen' / p.name: p for p in (ROOT / 'lock').iterdir() if p.is_file()}
    files.update({TARGET / 'shared' / p.name: p for p in (ROOT / 'shared').iterdir() if p.is_file()})
    if any(p.is_symlink() for p in files):
        raise SystemExit('Preserving existing symlinks.')
    backup = STATE / ('session-style-lock-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    records = []
    for index, (target, source) in enumerate(files.items()):
        old = next((r for r in previous['targets'] if r['path'] == str(target)), None) if previous else None
        before = old['before'] if old else target.read_bytes().hex() if target.exists() else None
        if target.exists(): shutil.copy2(target, backup / str(index))
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.new')
        shutil.copy2(source, temporary)
        temporary.replace(target)
        records.append({'path': str(target), 'before': before, 'sha256': digest(target)})
    manifest = {'backup': str(backup), 'targets': records}
    CURRENT.write_text(json.dumps(manifest, indent=2) + '\n')
    shutil.copy2(CURRENT, backup / 'manifest.json')
    print(f'Installed for the next screen lock. Backup: {backup}')

def restore():
    manifest = json.loads(CURRENT.read_text())
    verify(manifest)
    for record in reversed(manifest['targets']):
        path = Path(record['path'])
        if record['before'] is None: path.unlink()
        else: path.write_bytes(bytes.fromhex(record['before']))
    CURRENT.unlink()
    print('Previous screen-lock presentation restored.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    restore() if args.restore else install()
