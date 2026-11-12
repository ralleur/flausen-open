#!/usr/bin/env python3
"""Install a user-local Qt6 dialog style, preserving the existing base style."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess

HOME = Path.home()
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', HOME / '.config'))
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'ralleur-desktop-tweaks'
CURRENT = STATE / 'dialogs-installation.json'
PLUGIN_ROOT = HOME / '.local/lib/ralleur/dialogs/plugins'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def setting(value=None):
    args = ['--file', str(CONFIG / 'kdeglobals'), '--group', 'KDE', '--key', 'widgetStyle']
    if value is None:
        return subprocess.check_output(['kreadconfig6', *args], text=True).strip()
    subprocess.run(['kwriteconfig6', *args, *([value] if value else ['--delete'])], check=True)


def atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.ralleur-new')
    temporary.write_bytes(content)
    temporary.replace(path)


def install(build):
    library = build.resolve() / 'plugins/styles/libralleurdialogs.so'
    if not library.is_file():
        raise SystemExit('Build and test the plugin first.')
    previous = json.loads(CURRENT.read_text()) if CURRENT.exists() else None
    base = previous['baseStyle'] if previous else setting()
    if base.lower() == 'ralleur-dialogs':
        raise SystemExit('Cannot determine the original widget style.')
    if previous:
        verify(previous)
    targets = {
        PLUGIN_ROOT / 'styles/libralleurdialogs.so': library.read_bytes(),
        CONFIG / 'ralleur-dialogs.ini': f'[General]\nBaseStyle={base or "Breeze"}\n'.encode(),
        CONFIG / 'plasma-workspace/env/ralleur-dialogs.sh': (
            '#!/bin/sh\nexport QT_PLUGIN_PATH=' + shlex.quote(str(PLUGIN_ROOT))
            + '${QT_PLUGIN_PATH:+:$QT_PLUGIN_PATH}\n').encode(),
        CONFIG / 'environment.d/60-ralleur-dialogs.conf': (
            f'QT_PLUGIN_PATH={PLUGIN_ROOT}:${{QT_PLUGIN_PATH}}\n').encode(),
    }
    # Existing Dolphin launcher already searches this private plugin root.
    dolphin = HOME / '.local/lib/ralleur/dolphin-header/plugins'
    if dolphin.is_dir():
        targets[dolphin / 'styles/libralleurdialogs.so'] = library.read_bytes()
    for path in targets:
        if path.is_symlink():
            raise SystemExit(f'Preserving symlink: {path}')
    backup = STATE / ('dialogs-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True)
    records = []
    for index, (path, content) in enumerate(targets.items()):
        original = next((r for r in previous['targets'] if r['path'] == str(path)), None) if previous else None
        old = original['before'] if original else path.read_bytes().hex() if path.exists() else None
        if path.is_symlink():
            raise SystemExit(f'Preserving symlink: {path}')
        if path.exists():
            shutil.copy2(path, backup / str(index))
        atomic(path, content)
        records.append({'path': str(path), 'before': old, 'installedDigest': digest(path)})
    setting('ralleur-dialogs')
    manifest = {'baseStyle': base, 'backup': str(backup), 'targets': records}
    atomic(CURRENT, (json.dumps(manifest, indent=2) + '\n').encode())
    shutil.copy2(CURRENT, backup / 'manifest.json')
    print(f'Installed. Original style: {base}. Backup: {backup}')
    print('New Dolphin processes can use the style now; log in again for all KDE/Qt6 apps.')


def verify(manifest):
    if setting() != 'ralleur-dialogs':
        raise SystemExit('Widget style changed externally; preserving it.')
    for record in manifest['targets']:
        path = Path(record['path'])
        if path.is_symlink() or digest(path) != record['installedDigest']:
            raise SystemExit(f'Installation file changed; preserving {path}')


def restore():
    manifest = json.loads(CURRENT.read_text())
    verify(manifest)
    # Restore KDE's original selection before removing the plugin.
    setting(manifest['baseStyle'])
    for record in reversed(manifest['targets']):
        path = Path(record['path'])
        if record['before'] is None:
            path.unlink()
        else:
            atomic(path, bytes.fromhex(record['before']))
    CURRENT.unlink()
    print('Original widget style restored. Reopen apps; log in again to refresh the environment.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--build', type=Path)
    mode.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    restore() if args.restore else install(args.build)
