#!/usr/bin/python3
"""Share the password dialog's subtle KWin blur with open start menus."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

state_dir = Path(os.environ.get('XDG_RUNTIME_DIR', '/run/user/' + str(os.getuid()))) / 'minimal-polkit'
state_dir.mkdir(mode=0o700, exist_ok=True)
saved = state_dir / 'blur-settings.json'
leases = state_dir / 'blur-owners.json'
settings = {'BlurStrength': '1', 'NoiseStrength': '0', 'Saturation': '100'}

def read(key):
    return subprocess.check_output(['kreadconfig6', '--file', 'kwinrc', '--group', 'Effect-blur', '--key', key, '--default', '__unset__'], text=True).strip()

def write(key, value):
    args = ['kwriteconfig6', '--file', 'kwinrc', '--group', 'Effect-blur', '--key', key]
    subprocess.run(args + (['--delete'] if value == '__unset__' else [value]), check=True)

action = sys.argv[1]
owner = sys.argv[2] if len(sys.argv) > 2 else 'polkit'
if action not in ('on', 'off', 'off-launchers'):
    sys.exit('Expected on, off or off-launchers')
with (state_dir / 'lock').open('w') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    # Compatibility with a password dialog opened by the previous helper.
    owners = set(json.loads(leases.read_text())) if leases.exists() else ({'polkit'} if saved.exists() else set())
    if action == 'on':
        owners.add(owner)
    elif action == 'off':
        owners.discard(owner)
    else:
        owners = {item for item in owners if not item.startswith('launcher:')}
    if owners:
        if not saved.exists():
            saved.write_text(json.dumps({key: read(key) for key in settings}))
        desired = settings
    elif saved.exists():
        desired = json.loads(saved.read_text())
    else:
        leases.unlink(missing_ok=True)
        sys.exit(0)
    changed = False
    for key, value in desired.items():
        if read(key) != value:
            write(key, value)
            changed = True
    if changed:
        subprocess.run(['qdbus6', 'org.kde.KWin', '/Effects', 'org.kde.kwin.Effects.reconfigureEffect', 'blur'], check=True)
    if owners:
        leases.write_text(json.dumps(sorted(owners)))
    else:
        saved.unlink(missing_ok=True)
        leases.unlink(missing_ok=True)
