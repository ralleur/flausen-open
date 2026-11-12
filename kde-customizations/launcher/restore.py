#!/usr/bin/env python3
"""Restore only the launcher changes, refusing to overwrite later edits."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('backup', type=Path)
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()
root = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'quickshell/caelestia'
manifest = json.loads((args.backup / 'installed-sha256.json').read_text())
for name, digest in manifest.items():
    target = root / name
    if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise SystemExit(f'Abbruch: Datei wurde nachträglich verändert: {target}')
for name in manifest:
    target = root / name
    original = args.backup / name
    if not args.dry_run:
        if original.exists():
            shutil.copy2(original, target)
        else:
            target.unlink()
print('Rückbau geprüft.' if args.dry_run else 'Startmenü zurückgebaut. Caelestia-Shell bitte neu starten.')
