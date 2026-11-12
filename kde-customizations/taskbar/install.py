#!/usr/bin/env python3
"""Install the version-checked Caelestia split-bar patch with a guarded rollback."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as out:
        out.write(data)
        temporary = Path(out.name)
    if path.exists():
        temporary.chmod(path.stat().st_mode & 0o777)
    temporary.replace(path)

def patch(root, dry=False):
    args = ['patch', '--batch', '--forward', '-p0', '-d', str(root), '-i', str(HERE / 'split-taskbar.patch')]
    if dry:
        args.append('--dry-run')
    subprocess.run(args, check=True, capture_output=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restore', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.restore:
        manifest = json.loads(args.restore.read_text())
        # Preflight ALL files before changing anything.
        for item in manifest['files']:
            if digest(Path(item['path'])) != item['installed_sha256']:
                raise SystemExit(f"Geändert seit Installation; Rückbau abgebrochen: {item['path']}")
        config = Path(manifest['config'])
        data = json.loads(config.read_text())
        if data.get('bar', {}).get('position') != 'top':
            raise SystemExit('Bar-Position seit Installation geändert; Rückbau abgebrochen.')
        if args.dry_run:
            print('Rückbau geprüft.')
            return
        for item in manifest['files']:
            target = Path(item['path'])
            if item['backup']:
                atomic_write(target, Path(item['backup']).read_bytes())
            else:
                target.unlink()
        if manifest['previous_position'] is None:
            data['bar'].pop('position', None)
        else:
            data['bar']['position'] = manifest['previous_position']
        atomic_write(config, (json.dumps(data, indent=4) + '\n').encode())
        print('Rückbau abgeschlossen. Shell neu starten: systemctl --user restart caelestia-shell.service')
        return

    config_home = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    state_home = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state'))
    root = config_home / 'quickshell/caelestia'
    config = config_home / 'caelestia/shell.json'
    hashes = json.loads((HERE / 'base-sha256.json').read_text())
    overlays = list((HERE / 'overlay').rglob('*.qml'))
    for name, expected in hashes.items():
        if digest(root / name) != expected:
            raise SystemExit(f'Unbekannte oder bereits angepasste Version: {root / name}')
    for source in overlays:
        if (root / source.relative_to(HERE / 'overlay')).exists():
            raise SystemExit(f'Zieldatei existiert bereits: {source.name}')
    data = json.loads(config.read_text())
    patch(root, dry=True)
    if args.dry_run:
        print('Version, Patch und Ziele geprüft; keine Änderungen.')
        return
    backup = state_home / 'ralleur-taskbar-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    backup.mkdir(parents=True)
    shutil.copy2(config, backup / 'shell.json')
    manifest = {'config': str(config), 'previous_position': data.get('bar', {}).get('position'), 'files': []}
    targets = list(hashes) + [str(s.relative_to(HERE / 'overlay')) for s in overlays]
    for name in targets:
        target = root / name
        saved = backup / name if target.exists() else None
        if saved:
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        manifest['files'].append({'path': str(target), 'backup': str(saved) if saved else None, 'installed_sha256': None})
    # Prepare the complete result in isolation, then replace each file atomically.
    with tempfile.TemporaryDirectory() as staging:
        stage = Path(staging)
        for name in hashes:
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / name, target)
        patch(stage)
        for source in overlays:
            target = stage / source.relative_to(HERE / 'overlay')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        try:
            for item, name in zip(manifest['files'], targets):
                atomic_write(Path(item['path']), (stage / name).read_bytes())
                item['installed_sha256'] = digest(Path(item['path']))
            data.setdefault('bar', {})['position'] = 'top'
            atomic_write(config, (json.dumps(data, indent=4) + '\n').encode())
        except BaseException:
            for item in manifest['files']:
                target = Path(item['path'])
                if item['backup']:
                    atomic_write(target, Path(item['backup']).read_bytes())
                else:
                    target.unlink(missing_ok=True)
            atomic_write(config, (backup / 'shell.json').read_bytes())
            raise
    output = backup / 'manifest.json'
    output.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Installiert. Rückbau-Manifest: {output}')
    print('Shell neu starten: systemctl --user restart caelestia-shell.service')

if __name__ == '__main__':
    main()
