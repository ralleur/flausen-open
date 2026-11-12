#!/usr/bin/env python3
"""Root-only install of a private greeter and a reversible systemd override."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

BASE = Path('/usr/local/libexec/ralleur-login')
DROPIN = Path('/etc/systemd/user/plasma-login.service.d/ralleur-style.conf')
STATE = Path('/var/lib/ralleur-login-style')
CURRENT = STATE / 'installation.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def version():
    return subprocess.check_output(['pacman', '-Q', 'plasma-login-manager'], text=True, stderr=subprocess.DEVNULL).strip()

def verify(manifest):
    for item in manifest['targets']:
        path = Path(item['path'])
        if path.is_symlink() or digest(path) != item['sha256']:
            raise SystemExit(f'Externally changed; preserving {path}')

def install(binary):
    if version() != 'plasma-login-manager 6.8.2-1':
        raise SystemExit('This greeter build requires plasma-login-manager 6.8.2-1.')
    if binary.is_symlink() or not binary.is_file() or binary.read_bytes()[:4] != b'\x7fELF':
        raise SystemExit('Expected the tested greeter ELF binary.')
    previous = json.loads(CURRENT.read_text()) if CURRENT.exists() else None
    if previous: verify(previous)
    wrapper = b'''#!/bin/sh
# Use the unmodified system greeter after a package upgrade.
if [ "$(/usr/bin/pacman -Q plasma-login-manager 2>/dev/null)" = "plasma-login-manager 6.8.2-1" ] && [ -x /usr/local/libexec/ralleur-login/plasma-login-greeter ]; then
    exec /usr/local/libexec/ralleur-login/plasma-login-greeter "$@"
fi
exec /usr/lib/plasma-login-greeter "$@"
'''
    # The greeter runs outside the user's session and needs its own catalog.
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'localization'))
    from catalog import standalone
    _, messages = standalone()
    wrapper = wrapper.replace(b'    exec /usr/local/libexec/ralleur-login/plasma-login-greeter', b'    export XDG_DATA_DIRS="/usr/local/libexec/ralleur-login/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"\n    exec /usr/local/libexec/ralleur-login/plasma-login-greeter')
    targets = {
        BASE / 'share/locale/de/LC_MESSAGES/flausen.mo': (messages, 0o644),
        BASE / 'plasma-login-greeter': (binary.read_bytes(), 0o755),
        BASE / 'start': (wrapper, 0o755),
        DROPIN: (b'[Service]\nExecStart=\nExecStart=/usr/local/libexec/ralleur-login/start\n', 0o644),
    }
    for path in targets:
        if path.is_symlink(): raise SystemExit(f'Preserving symlink {path}')
    backup = STATE / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True, mode=0o700)
    records=[]
    for index,(path,(content,mode)) in enumerate(targets.items()):
        old=next((r for r in previous['targets'] if r['path']==str(path)),None) if previous else None
        before=old['before'] if old else path.read_bytes().hex() if path.exists() else None
        before_mode=old['mode'] if old else path.stat().st_mode & 0o777 if path.exists() else mode
        if path.exists():shutil.copy2(path,backup/str(index))
        path.parent.mkdir(parents=True,exist_ok=True)
        temp=path.with_name(path.name+'.new');temp.write_bytes(content);temp.chmod(mode);temp.replace(path)
        records.append({'path':str(path),'before':before,'mode':before_mode,'sha256':digest(path)})
    CURRENT.write_text(json.dumps({'targets':records,'backup':str(backup)},indent=2)+'\n')
    CURRENT.chmod(0o600)
    shutil.copy2(CURRENT,backup/'manifest.json')
    # No display-manager or session restart. New greeter instances read the override.
    print(f'Login style installed. Backup: {backup}. Active sessions were not restarted.')

def restore():
    manifest=json.loads(CURRENT.read_text());verify(manifest)
    for item in reversed(manifest['targets']):
        path=Path(item['path'])
        if item['before'] is None:path.unlink()
        else:path.write_bytes(bytes.fromhex(item['before']));path.chmod(item['mode'])
    CURRENT.unlink()
    print('System greeter restored for the next login-manager start.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--binary',type=Path)
    mode.add_argument('--restore',action='store_true')
    args=parser.parse_args()
    if os.geteuid()!=0:raise SystemExit('Administrator authentication is needed for the system login screen.')
    restore() if args.restore else install(args.binary.resolve())
