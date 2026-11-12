#!/usr/bin/env python3
"""Install smoke notification cards on the existing Caelestia shell."""
from datetime import datetime
from pathlib import Path
import argparse
import json
import shutil
import subprocess

SOURCE = Path(__file__).resolve().parent
SHELL = Path.home() / '.config/quickshell/caelestia'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--restore', type=Path)
    args = parser.parse_args()
    if args.restore:
        manifest = json.loads((args.restore / 'manifest.json').read_text())
        for name, existed in manifest.items():
            target = SHELL / name
            if existed:
                shutil.copy2(args.restore / name, target)
            else:
                target.unlink(missing_ok=True)
        return
    patch = (SOURCE / 'integration.patch').read_text()
    # Apply independently per file, allowing safe repeat installs and later edits.
    sections = ['--- ' + part for part in patch.split('--- ')[1:]]
    pending = []
    for section in sections:
        name = section.splitlines()[0][4:]
        command = ['patch', '--batch', '--silent', '-p0', '--dry-run']
        forward = subprocess.run(command + ['--forward'], input=section, text=True, cwd=SHELL, capture_output=True)
        if forward.returncode == 0:
            pending.append((name, section))
        else:
            reverse = subprocess.run(command + ['--reverse'], input=section, text=True, cwd=SHELL, capture_output=True)
            if reverse.returncode:
                raise SystemExit(f'Unbekannter Quellstand: {name}\n{forward.stdout}{forward.stderr}')
    copies = {'modules/notifications/Notification.qml': SOURCE / 'Notification.qml'}
    copies = {name: source for name, source in copies.items() if not (SHELL/name).exists() or (SHELL/name).read_bytes() != source.read_bytes()}
    print(json.dumps({'patches': [name for name, _ in pending], 'copies': list(copies), 'dryRun': args.dry_run}, indent=2))
    if args.dry_run or not (pending or copies):
        return
    backup = Path.home() / '.local/state/flausen/notification-style-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    manifest = {}
    for name in [name for name, _ in pending] + list(copies):
        target = SHELL / name
        manifest[name] = target.exists()
        if target.exists():
            saved = backup / name
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
    (backup/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    for name, section in pending:
        subprocess.run(['patch', '--batch', '--forward', '--no-backup-if-mismatch', '-p0'], input=section, text=True, cwd=SHELL, check=True)
    for name, source in copies.items():
        shutil.copy2(source, SHELL / name)
    (SOURCE.parent/'evidence/notification-style-backup.txt').write_text(str(backup)+'\n')
    print(f'Backup: {backup}')

if __name__ == '__main__':
    main()
