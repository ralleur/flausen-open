#!/usr/bin/env python3
"""Apply the workspace-shape patch to the current user shell, with a file backup."""
from datetime import datetime
from pathlib import Path
import json
import shutil
import subprocess

source = Path(__file__).resolve().parent
shell = Path.home() / '.config/quickshell/caelestia'
target = shell / 'modules/bar/components/workspaces'
patch = source.parent / 'flausen-workspaces.patch'
subprocess.run(['patch', '--dry-run', '--forward', '-p0', '-d', str(shell), '-i', str(patch)], check=True)
files = {target / 'FlausenWorkspaceIcon.qml': source / 'FlausenWorkspaceIcon.qml'}
files.update({target / 'flausen-shapes' / p.name: p for p in (source / 'shapes').glob('*.svg')})
if any(p.exists() for p in files):
    raise SystemExit('Destination component/assets already exist; leaving them untouched.')
backup = Path.home() / '.local/state/ralleur-desktop/backups' / (datetime.now().strftime('%Y%m%d-%H%M%S') + '-flausen-workspaces')
backup.mkdir(parents=True)
shutil.copy2(target / 'Workspace.qml', backup / 'Workspace.qml')
try:
    for dest, src in files.items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    subprocess.run(['patch', '--forward', '-p0', '-d', str(shell), '-i', str(patch)], check=True)
except BaseException:
    shutil.copy2(backup / 'Workspace.qml', target / 'Workspace.qml')
    for p in files:
        p.unlink(missing_ok=True)
    raise
(backup / 'files.json').write_text(json.dumps({'modified':str(target / 'Workspace.qml'),'added':list(map(str,files))},indent=2)+'\n')
(source.parent / 'evidence/flausen-workspaces-backup.txt').write_text(str(backup)+'\n')
print('Installed; backup:',backup)
