#!/usr/bin/env python3
"""Build and install dock-only icon normalization, preserving a rollback backup."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import shlex
import shutil
import subprocess
import tempfile

here = Path(__file__).resolve().parent
root = Path.home() / '.config/quickshell/caelestia'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--restore', type=Path)
args = parser.parse_args()
if args.restore:
    manifest = json.loads(args.restore.read_text())
    for item in manifest:
        target = root / item['target']
        if item['backup']:
            shutil.copy2(item['backup'], target)
        else:
            target.unlink(missing_ok=True)
    print('Rückbau abgeschlossen; Shell neu starten.')
    raise SystemExit

patch = ['patch', '--batch', '--forward', '-p0', '-d', str(root),
         '-i', str(here.parent / 'dock-icon-normalization.patch')]
subprocess.run(patch + ['--dry-run'], check=True)
with tempfile.TemporaryDirectory() as directory:
    binary = Path(directory) / 'normalize-dock-icon'
    flags = shlex.split(subprocess.check_output(
        ['pkg-config', '--cflags', '--libs', 'Qt6Gui', 'Qt6Core'], text=True))
    subprocess.run(['g++', '-std=c++17', '-O2', '-fPIC', str(here / 'normalize.cpp'),
                    '-o', str(binary), *flags], check=True)
    if args.dry_run:
        print('Build und Patch geprüft; keine Installation.')
        raise SystemExit
    backup = Path.home() / '.local/state/ralleur-taskbar-backups' / (
        'dock-icons-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    backup.mkdir(parents=True)
    targets = ['modules/bar/components/Dock.qml', 'components/images/DockIcon.qml',
               'scripts/normalize-dock-icon']
    manifest = []
    for name in targets:
        target = root / name
        saved = backup / name
        if target.exists():
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        manifest.append({'target': name, 'backup': str(saved) if target.exists() else None})
    (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    try:
        subprocess.run(patch, check=True)
        shutil.copy2(here / 'DockIcon.qml', root / targets[1])
        shutil.copy2(binary, root / targets[2])
    except BaseException:
        for item in manifest:
            target = root / item['target']
            if item['backup']:
                shutil.copy2(item['backup'], target)
            else:
                target.unlink(missing_ok=True)
        raise
    print(f'Installiert. Rückbau: {backup / "manifest.json"}')
