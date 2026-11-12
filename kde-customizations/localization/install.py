#!/usr/bin/env python3
"""Install bilingual desktop messages following KDE settings, with guarded rollback.

Does not change KDE language or regional formats. Use --check for a dry run.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HOME = Path.home()
SHELL = HOME / '.config/quickshell/caelestia'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write(path, data, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.language-tmp')
    temporary.write_bytes(data)
    temporary.chmod(mode)
    os.replace(temporary, path)

def plan(dolphin_build=None):
    from qml_messages import convert
    from catalog import build, standalone
    result = {}
    for path in SHELL.rglob('*.qml'):
        before = path.read_text()
        after = convert(before)
        if path == SHELL/'shell.qml':
            after = after.replace('value: GlobalConfig.general.language\n',
                'value: GlobalConfig.general.language === "system" ? SystemLanguage.language : GlobalConfig.general.language\n')
        if path == SHELL/'services/ContextMenuStore.qml' and 'function retranslateEntries()' not in after:
            source = (REPO/'kde-customizations/desktop-context-menu/services/ContextMenuStore.qml').read_text()
            block = source[source.index('    function retranslateEntries()'):source.index('    function iconsShownOn')]
            if 'import Caelestia\n' not in after: after = after.replace('import Caelestia.Config', 'import Caelestia\nimport Caelestia.Config')
            after = after.replace('    function iconsShownOn', block+'    function iconsShownOn')
        if path == SHELL/'services/ContextMenuStore.qml':
            after = after.replace('function onActiveLanguageChanged(): void { root.retranslateEntries(); }', 'function onActiveLanguageChanged(): void { Qt.callLater(root.retranslateEntries); }')
        if after != before:
            result[path] = after.encode()
    result[SHELL/'services/SystemLanguage.qml'] = (HERE/'SystemLanguage.qml').read_bytes()
    configpath = HOME/'.config/caelestia/shell.json'
    config = json.loads(configpath.read_text())
    config.setdefault('general', {})['language'] = 'system'
    result[configpath] = (json.dumps(config, ensure_ascii=False, indent=4) + '\n').encode()
    # Remove only the exact overrides installed by the old one-way English script.
    overrides = {
        HOME/'.config/environment.d/90-flausen-language.conf': b'LANG=en_US.UTF-8\nLANGUAGE=en_US\nLC_MESSAGES=en_US.UTF-8\nLC_TIME=en_US.UTF-8\n',
        HOME/'.config/plasma-workspace/env/flausen-language.sh': b'#!/bin/sh\nexport LANG=en_US.UTF-8 LANGUAGE=en_US LC_MESSAGES=en_US.UTF-8\nLC_TIME=en_US.UTF-8\n',
    }
    for path, old in overrides.items():
        if path.exists() and path.read_bytes() == old:
            result[path] = None
    result[SHELL/'translations/caelestia_de.qm'] = build(SHELL, result)
    qm, mo = standalone()
    shared = HOME/'.local/share/flausen/localization'
    for name in ['language.py', 'runtime.py', 'messages-de.json', 'english-strings.json']:
        result[shared/name] = (HERE/name).read_bytes()
    result[shared/'flausen_de.qm'] = qm
    result[HOME/'.local/share/locale/de/LC_MESSAGES/flausen.mo'] = mo
    branding = HOME/'.local/share/flausen-os/branding'
    if (branding/'About.qml').exists():
        for name in ['About.qml', 'flausen-about']:
            result[branding/name] = (REPO/'branding/flausen'/name).read_bytes()
    desktop_entries = {
        'flausen-settings.desktop': ('Name=flausen Settings', 'Name[de]=flausen Einstellungen'),
        'flausen-os-about.desktop': ('Name=About flausen.', 'Name[de]=Über flausen.'),
    }
    for name, (default, german) in desktop_entries.items():
        path = HOME/'.local/share/applications'/name
        if not path.exists(): continue
        text = path.read_text()
        if 'Name[de]=' not in text: text = text.replace(default, default+'\n'+german)
        result[path] = text.encode()
    bridge = HOME/'.local/share/ralleur-hermes/bridge.py'
    if bridge.exists():
        text = bridge.read_text()
        source = (REPO/'kde-customizations/launcher/hermes/bridge.py').read_text()
        if 'from runtime import t' not in text:
            block = source[source.index('# The same resolver'):source.index('os.umask(0o077)')]
            text = text.replace('os.umask(0o077)', block+'os.umask(0o077)')
            text = text.replace('def emit(event, **values):\n', "def emit(event, **values):\n    if event in ('error', 'status') and 'text' in values:\n        values['text'] = t(values['text'])\n")
        text = text.replace('Reply in English by default,\nor in another language when the user explicitly requests it.', 'Follow the desktop language supplied below by default,\nor another language when the user explicitly requests it.')
        text = text.replace('system_message=SYSTEM,', 'system_message=SYSTEM + "\\nDesktop language: " + language(),')
        text = text.replace('What does this command do? Explain briefly in English.', 'What does this command do? Explain briefly in the desktop language.')
        result[bridge] = text.encode()
    session = HOME/'.local/share/plasma/shells/caelestia.desktop/contents/shared/RalleurSessionScreen.qml'
    if session.exists():
        text = session.read_text().replace('qsTr("Press Enter to continue")', 'i18nd("flausen", "Press Enter to continue")')
        text = text.replace('Qt.formatDate(root.now, Qt.locale(), "dddd, MMMM d, yyyy")', 'Qt.formatDate(root.now, Qt.locale(), Qt.locale().dateFormat(Locale.LongFormat))')
        result[session] = text.encode()
    lock = HOME/'.local/share/plasma/shells/caelestia.desktop/contents/lockscreen/LockScreenUi.qml'
    if lock.exists():
        result[lock] = lock.read_text().replace('qsTr("Herunterfahren")', 'i18nd("flausen", "Shut down")').encode()
    # Keep ownership manifests in step with this explicit migration. A later
    # component install still rejects unrelated edits and can be localized again.
    state = HOME/'.local/state/flausen/settings-installed.json'
    if state.exists():
        hashes = json.loads(state.read_text())
        for path, data in result.items():
            if str(path) in hashes and data is not None and path.exists() and hashes[str(path)] == digest(path.read_bytes()):
                hashes[str(path)] = digest(data)
        result[state] = (json.dumps(hashes, indent=2, sort_keys=True)+'\n').encode()

    if dolphin_build:
        source = dolphin_build/'plugins/generic/libralleurdolphin.so'
        if not source.is_file(): raise SystemExit('Build the Dolphin plugin first.')
        pointer = HOME/'.local/state/ralleur-desktop-tweaks/dolphin-header-installation.json'
        manifest_path = Path(json.loads(pointer.read_text())['manifest'])
        manifest = json.loads(manifest_path.read_text())
        target = HOME/'.local/lib/ralleur/dolphin-header/plugins/generic/libralleurdolphin.so'
        record = next(row for row in manifest['targets'] if row['path'] == str(target))
        if digest(target.read_bytes()) != record['installedDigest']:
            raise SystemExit(f'Local plugin changes protected: {target}')
        result[target] = source.read_bytes()
        record['installedDigest'] = digest(result[target])
        result[manifest_path] = (json.dumps(manifest, indent=2)+'\n').encode()
    return {path: data for path, data in result.items()
            if (path.exists() if data is None else not path.exists() or path.read_bytes() != data)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--restore', type=Path)
    parser.add_argument('--dolphin-build', type=Path, help='Upgrade only the recorded native plugin, preserving unrelated icon changes')
    args = parser.parse_args()
    if args.restore:
        manifest = json.loads((args.restore / 'manifest.json').read_text())
        for row in manifest:
            path = Path(row['path'])
            if (digest(path.read_bytes()) if path.exists() else None) != row['installed']:
                raise SystemExit(f'Later changes protected: {path}')
        for row in reversed(manifest):
            path = Path(row['path'])
            if row['backup'] is None:
                path.unlink()
            else:
                write(path, (args.restore / row['backup']).read_bytes(), row['mode'])
        print('Files restored. Sign out and back in to reload the former session language.')
        return
    planned = plan(args.dolphin_build)
    if args.check:
        print(f'{len(planned)} files would change.')
        return
    if planned:
        backup = HOME / '.local/state/flausen/language-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup.mkdir(parents=True)
        manifest = []
        for index, (path, data) in enumerate(planned.items()):
            saved = f'{index:03}.bak' if path.exists() else None
            mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
            if saved:
                shutil.copy2(path, backup / saved)
            manifest.append(dict(path=str(path), backup=saved, mode=mode, installed=digest(data) if data is not None else None))
        (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        for row, (path, data) in zip(manifest, planned.items()):
            if data is None: path.unlink()
            else: write(path, data, row['mode'])
        print(f'Installed {len(planned)} files. Backup: {backup}')
    print('System language enabled. Restart caelestia-shell.service to load the integration. Applications use the new session locale after signing in again.')

if __name__ == '__main__':
    main()
