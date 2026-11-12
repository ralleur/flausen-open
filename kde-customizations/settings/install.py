#!/usr/bin/env python3
"""Install the reviewed Caelestia overlay, recording a guarded rollback manifest."""
import argparse, hashlib, json, os, shutil, subprocess
from datetime import datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent
HOME=Path.home()
SHELL=HOME/'.config/quickshell/caelestia'
def digest(data): return hashlib.sha256(data).hexdigest()
def atomic(path,data,mode=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.flausen-tmp')
    tmp.write_bytes(data)
    if mode is not None: tmp.chmod(mode)
    os.replace(tmp,path)
def changes():
    expected=json.loads((HERE/'baseline.json').read_text())
    installed_path=HOME/'.local/state/flausen/settings-installed.json'
    installed=json.loads(installed_path.read_text()) if installed_path.exists() else {}
    result={}
    for source in (HERE/'overlay').rglob('*'):
        if not source.is_file():continue
        rel=source.relative_to(HERE/'overlay')
        dest=(HOME/'.local/lib/caelestia'/rel) if rel.parts[0]=='schemes' else SHELL/rel
        data=source.read_bytes()
        before=dest.read_bytes() if dest.exists() else None
        if before is not None and before != data:
            valid=expected.get(str(rel))
            valid=[valid] if isinstance(valid,str) else (valid or [])
            if digest(before) not in valid and digest(before)!=installed.get(str(dest)): raise SystemExit(f'Local changes or incompatible Caelestia version: {dest}')
        result[dest]=(data,None)
    module=HERE.parents[1]/'.cache/flausen-settings-native/Flausen/Settings'
    for name in ['qmldir','flausensettings.qmltypes','libflausensettings.so','libflausensettingsplugin.so']:
        source=module/name
        if not source.exists():raise SystemExit('Build the native module first (see README).')
        dest=HOME/'.local/lib/qt6/qml/Flausen/Settings'/name
        data=source.read_bytes()
        if dest.exists() and dest.read_bytes()!=data and digest(dest.read_bytes())!=installed.get(str(dest)):
            raise SystemExit(f'Local native-module changes protected: {dest}')
        result[dest]=(data,0o755 if name.endswith('.so') else 0o644)
    result[HOME/'.local/share/flausen-settings/hermes_settings.py']=((HERE/'helpers/hermes_settings.py').read_bytes(),0o644)
    result[HOME/'.local/share/flausen-settings/openai_auth.py']=((HERE/'helpers/openai_auth.py').read_bytes(),0o644)
    # Patch just the two settings entry points, preserving unrelated local work.
    for rel,old,new in [
        ('modules/launcher/Content.qml','command: ["systemsettings"], power: false','command: ["flausen-settings"], power: false'),
        ('modules/launcher/services/HermesDesktop.qml','einstellungen: ["systemsettings", "org.kde.systemsettings"]','einstellungen: ["flausen-settings", "systemsettings", "org.kde.systemsettings"]'),
        ('services/ContextMenuStore.qml','label: qsTr("System Settings"), icon: "settings", command: "systemsettings"','label: qsTr("Settings"), icon: "settings", command: "flausen-settings"')]:
        dest=SHELL/rel;text=dest.read_text()
        if rel=='services/ContextMenuStore.qml':
            text=text.replace('label: qsTr("Einstellungen"), icon: "settings", command: "flausen-settings"',new)
        if old not in text and new not in text:raise SystemExit(f'Entrypoint changed: {dest}')
        result[dest]=(text.replace(old,new).encode(),None)
    # New Hermes conversations reload the same profile edited by this page.
    bridge=HOME/'.local/share/ralleur-hermes/bridge.py'
    if bridge.exists():
        text=bridge.read_text()
        old="            emit('reset')"
        new="            self.model = configured_model()\n            emit('ready', model=self.model, location='cloud' if self.model == 'deepseek-flash' else 'local')\n            emit('reset')"
        reset_start=text.find("        elif action == 'reset'")
        reset_end=text.find("        elif action == 'prompt'",reset_start)
        if reset_start<0 or reset_end<0:raise SystemExit(f'Hermes reset handler changed: {bridge}')
        reset_handler=text[reset_start:reset_end]
        if "self.model = configured_model()" not in reset_handler or "emit('ready', model=self.model" not in reset_handler:
            if text.count(old)!=1:raise SystemExit(f'Hermes reset handler changed: {bridge}')
            text=text.replace(old,new)
        result[bridge]=(text.encode(),None)
    # Shared scratch files in the installed color CLI need a single writer.
    # Release before user hooks, which may themselves invoke the CLI.
    cli=HOME/'.local/bin/caelestia-color'
    text=cli.read_text()
    lock_old='    mkdir -p "$WORK_DIR"\n\n    case "$group" in'
    lock_new='    mkdir -p "$WORK_DIR"\n    # flausen: serialize writers to the shared matugen scratch files.\n    if [[ "$group" == "wallpaper" || ( "$group" == "scheme" && "${1:-}" == "set" ) ]]; then\n        exec {flausen_colour_lock}>"$STATE_DIR/colour-pipeline.lock"\n        flock "$flausen_colour_lock"\n    fi\n\n    case "$group" in'
    hook_old='run_hook() {\n    local label='
    hook_new='run_hook() {\n    # Rendering and commit are complete; hooks may re-enter the CLI.\n    if [[ -n "${flausen_colour_lock:-}" ]]; then\n        flock -u "$flausen_colour_lock"\n        exec {flausen_colour_lock}>&-\n        unset flausen_colour_lock\n    fi\n    local label='
    if lock_old not in text and lock_new not in text:raise SystemExit(f'Color CLI changed: {cli}')
    if hook_old not in text and hook_new not in text:raise SystemExit(f'Color CLI hook changed: {cli}')
    result[cli]=(text.replace(lock_old,lock_new).replace(hook_old,hook_new).encode(),0o755)
    menu=SHELL/'context_menu.json'
    if menu.exists():
        entries=json.loads(menu.read_text())
        for entry in entries:
            if entry.get('id')=='system_settings' and entry.get('command')=='systemsettings':entry.update(command='flausen-settings',label='flausen Settings')
        result[menu]=((json.dumps(entries,ensure_ascii=False,indent=2)+'\n').encode(),None)
    script=b'#!/bin/sh\nexec /usr/bin/quickshell ipc -p "$HOME/.config/quickshell/caelestia" call nexus open\n'
    result[HOME/'.local/bin/flausen-settings']=(script,0o755)
    desktop='''[Desktop Entry]
Type=Application
Name=flausen Settings
Name[de]=flausen Einstellungen
GenericName=System Settings
GenericName[de]=Systemeinstellungen
Comment=Configure your desktop, devices and system
Exec=flausen-settings
Icon=flausen-os
Terminal=false
Categories=Settings;DesktopSettings;
Keywords=System;Settings;Einstellungen;Caelestia;flausen;KDE;
StartupNotify=false
'''
    result[HOME/'.local/share/applications/flausen-settings.desktop']=(desktop.encode(),None)
    result[installed_path]=((json.dumps({str(p):digest(v[0]) for p,v in result.items()},indent=2,sort_keys=True)+'\n').encode(),0o600)
    return result
parser=argparse.ArgumentParser()
parser.add_argument('--restore',type=Path)
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
if args.restore:
    manifest=json.loads((args.restore/'manifest.json').read_text())
    # Validate every entry before changing any file.
    for entry in manifest:
        p=Path(entry['path'])
        if not p.exists() or digest(p.read_bytes())!=entry['installed']:raise SystemExit(f'Later edits protected: {p}')
    for entry in reversed(manifest):
        p=Path(entry['path'])
        if entry['backup'] is None:p.unlink()
        else:atomic(p,(args.restore/entry['backup']).read_bytes(),entry['mode'])
    print('Restored. Restart caelestia-shell.service to load the previous state.')
else:
    if not args.check:
        build=HERE.parents[1]/'.cache/flausen-settings-native'
        subprocess.run(['cmake','-S',str(HERE/'native'),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release'],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['cmake','--build',str(build),'-j4'],check=True,stdout=subprocess.DEVNULL)
    planned=changes()
    changed={p:v for p,v in planned.items() if not p.exists() or p.read_bytes()!=v[0]}
    if args.check:print(f'{len(planned)} files checked, {len(changed)} changes pending.')
    elif not changed:print('Already installed; no changes.')
    else:
        backup=HOME/'.local/state/flausen/settings-backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True)
        manifest=[]
        for i,(dest,(data,mode)) in enumerate(changed.items()):
            exists=dest.exists();name=f'{i:03d}.bak' if exists else None
            oldmode=dest.stat().st_mode & 0o777 if exists else None
            if exists:shutil.copy2(dest,backup/name)
            manifest.append(dict(path=str(dest),backup=name,mode=oldmode,installed=digest(data)))
        (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
        for dest,(data,mode) in changed.items():atomic(dest,data,mode if mode is not None else (dest.stat().st_mode & 0o777 if dest.exists() else 0o644))
        subprocess.run(['update-desktop-database',str(HOME/'.local/share/applications')],check=True)
        print(f'Installed {len(changed)} files. Backup: {backup}')
