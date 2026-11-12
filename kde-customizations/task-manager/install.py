#!/usr/bin/env python3
"""Install only task-manager-owned files; shared Caelestia sources stay linked."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from datetime import datetime

HERE = Path(__file__).resolve().parent
HOME = Path.home()
ROOT = HOME/'.local/share/flausen-task-manager'
STATE = HOME/'.local/state/flausen/task-manager-installed.json'
SHARED = HOME/'.config/quickshell/caelestia'
LINKS = ('services', 'components', 'modules', 'utils', 'assets', 'translations')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def payload():
    result = {ROOT/'shell.qml': ((HERE/'shell.qml').read_bytes(), 0o644),
              ROOT/'backend.py': ((HERE/'backend.py').read_bytes(), 0o644),
              ROOT/'icon.png': ((HERE/'icon.png').read_bytes(), 0o644),
              ROOT/'i18n.py': ((HERE/'i18n.py').read_bytes(), 0o644)}
    for file in (HERE/'ui').glob('*.qml'):
        result[ROOT/'ui'/file.name] = (file.read_bytes(), 0o644)
    for file in (HERE/'locales').glob('*.json'):
        result[ROOT/'locales'/file.name] = (file.read_bytes(), 0o644)
    launcher = '''#!/bin/sh
export QML2_IMPORT_PATH="$HOME/.local/lib/qt6/qml${QML2_IMPORT_PATH:+:$QML2_IMPORT_PATH}"
export CAELESTIA_LIB_DIR="$HOME/.local/lib/caelestia"
export CAELESTIA_BIN_DIR="$HOME/.local/bin"
export QS_DISABLE_CRASH_HANDLER=1
export QS_APP_ID=flausen-task-manager
# Keep Caelestia's per-process tracker sockets separate from the desktop shell.
export FLAUSEN_SESSION_RUNTIME="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
case "${WAYLAND_DISPLAY:-wayland-1}" in
    /*) ;;
    *) export WAYLAND_DISPLAY="$FLAUSEN_SESSION_RUNTIME/${WAYLAND_DISPLAY:-wayland-1}" ;;
esac
export PIPEWIRE_RUNTIME_DIR="${PIPEWIRE_RUNTIME_DIR:-$FLAUSEN_SESSION_RUNTIME}"
export PULSE_SERVER="${PULSE_SERVER:-unix:$FLAUSEN_SESSION_RUNTIME/pulse/native}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=$FLAUSEN_SESSION_RUNTIME/bus}"
export XDG_RUNTIME_DIR="$FLAUSEN_SESSION_RUNTIME/flausen-task-manager"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
app="$HOME/.local/share/flausen-task-manager"
if /usr/bin/quickshell ipc -p "$app" call taskmanager open >/dev/null 2>&1; then exit 0; fi
exec /usr/bin/quickshell -n -p "$app" "$@"
'''
    result[HOME/'.local/bin/flausen-task-manager'] = (launcher.encode(), 0o755)
    desktop = f'''[Desktop Entry]
Type=Application
Name=flausen Task Manager
Name[de]=flausen Task-Manager
GenericName=System Monitor
GenericName[de]=Systemmonitor
Comment=Processes, performance, startup and user services
Comment[de]=Prozesse, Leistung, Autostart und Benutzerdienste
Exec=flausen-task-manager
Icon={ROOT}/icon.png
StartupWMClass=flausen-task-manager
Terminal=false
Categories=System;Monitor;
Keywords=Task;Manager;Processes;Prozesse;CPU;RAM;Systemmonitor;
StartupNotify=false
'''
    result[HOME/'.local/share/applications/flausen-task-manager.desktop'] = (desktop.encode(), 0o644)
    return result


def install(dry_run=False):
    for path in [SHARED/'services/MenuStyle.qml', SHARED/'components/MenuText.qml',
                 SHARED/'modules/nexus/flausen/FlausenStyle.qml', HOME/'.local/lib/qt6/qml/Flausen/Settings/qmldir']:
        if not path.exists():
            raise SystemExit(f'Voraussetzung fehlt: {path}')
    import psutil  # Installation must fail early if telemetry cannot run.
    previous = json.loads(STATE.read_text()) if STATE.exists() else {}
    files = payload()
    updates = {}
    for target, (data, mode) in files.items():
        old = target.read_bytes() if target.exists() else None
        if old == data and target.stat().st_mode & 0o777 == mode:
            continue
        if old is not None and digest(old) != previous.get(str(target)):
            raise SystemExit(f'Lokale Änderung geschützt: {target}')
        updates[target] = (data, mode)
    links = {}
    for name in LINKS:
        target = ROOT/name
        source = SHARED/name
        if target.is_symlink() and target.readlink() == source:
            continue
        if target.exists() or target.is_symlink():
            raise SystemExit(f'Vorhandener Pfad geschützt: {target}')
        links[target] = source
    print(f'{len(updates)} Dateien, {len(links)} Verknüpfungen')
    if dry_run:
        for target in [*updates, *links]:
            print(target)
        return
    if not updates and not links:
        return
    backup = HOME/'.local/state/flausen/task-manager-backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    records = []
    for target, (data, mode) in updates.items():
        entry = dict(path=str(target), installed=digest(data), before=None, mode=None)
        if target.exists():
            entry['before'] = str(len(records))
            entry['mode'] = target.stat().st_mode & 0o777
            shutil.copy2(target, backup/entry['before'])
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(target.name+'.flausen-tmp')
        temp.write_bytes(data)
        temp.chmod(mode)
        temp.replace(target)
        records.append(entry)
    for target, source in links.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source, target_is_directory=True)
        records.append(dict(path=str(target), link=str(source)))
    # Preserve the previous ownership record so updates can also be rolled back.
    state_before = STATE.read_text() if STATE.exists() else None
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({str(p): digest(data) for p, (data, _) in files.items()}, indent=2)+'\n')
    (backup/'manifest.json').write_text(json.dumps(dict(files=records, state=state_before), indent=2)+'\n')
    print(f'Sicherung und Rückbau: {backup}')


def restore(backup):
    backup = Path(backup)
    manifest = json.loads((backup/'manifest.json').read_text())
    # Validate every path before making any changes.
    for entry in manifest['files']:
        target = Path(entry['path'])
        if 'link' in entry:
            if not target.is_symlink() or str(target.readlink()) != entry['link']:
                raise SystemExit(f'Geänderte Verknüpfung geschützt: {target}')
        elif not target.exists() or digest(target.read_bytes()) != entry['installed']:
            raise SystemExit(f'Geänderte Datei geschützt: {target}')
    for entry in reversed(manifest['files']):
        target = Path(entry['path'])
        if 'link' in entry or entry['before'] is None:
            target.unlink()
        else:
            shutil.copy2(backup/entry['before'], target)
            target.chmod(entry['mode'])
    if manifest['state'] is None:
        STATE.unlink(missing_ok=True)
    else:
        STATE.write_text(manifest['state'])
    print('Task-Manager zurückgebaut.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--restore', metavar='BACKUP')
    args = parser.parse_args()
    restore(args.restore) if args.restore else install(args.dry_run)
