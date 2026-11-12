#!/usr/bin/env python3
"""Install the Shift-drag conflict fix without reloading Krohnkite's window states."""
from pathlib import Path
import datetime
import json
import shutil
import subprocess

def install_guard():
    source = Path(__file__).resolve().parent
    build = Path.home() / '.cache/ralleur-tiling-guard-build'
    target = Path.home() / '.local/share/kwin/scripts/ralleur-tiling-guard'
    def run(*args):
        return subprocess.check_output(args, text=True).strip()
    run('cmake', '-S', str(source), '-B', str(build))
    run('cmake', '--build', str(build), '--target', 'ralleurtilingguard', '--parallel', '4')
    backup = Path.home() / '.local/state/ralleur-tiling' / ('before-shift-guard-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True)
    shutil.copy2(Path.home() / '.config/kwinrc', backup / 'kwinrc')
    if target.exists():
        shutil.copytree(target, backup / 'guard-package')
    generation = 'guard-' + backup.name
    entry = target / 'contents' / generation / 'ui/main.qml'
    native = entry.parent / 'native'
    native.mkdir(parents=True)
    shutil.copy2(source / 'guard-metadata.json', target / 'metadata.json')
    shutil.copy2(source / 'guard-main.qml', entry)
    (target / 'contents/ui').mkdir(exist_ok=True)
    (target / 'contents/ui/main.qml').write_text('import QtQuick\nItem { Loader { source: "../' + generation + '/ui/main.qml" } }\n')
    (native / 'qmldir').write_text('module Ralleur.TilingShiftGuard.Run' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '\nplugin ralleurtilingguard\n')
    shutil.copy2(build / 'libralleurtilingguard.so', native)
    run('kwriteconfig6', '--file', 'kwinrc', '--group', 'Plugins', '--key', 'ralleur-tiling-guardEnabled', 'true')
    # Load the new helper directly; leave Krohnkite and its enrolled windows alive.
    run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'ralleur-tiling-guard')
    sid = run('qdbus6', 'org.kde.KWin', '/Scripting', 'loadDeclarativeScript', str(entry), 'ralleur-tiling-guard')
    run('qdbus6', 'org.kde.KWin', '/Scripting/Script' + sid, 'run')
    latest = Path.home() / '.local/state/ralleur-tiling/latest'
    if latest.exists():
        manifest = Path(latest.read_text().strip()) / 'settings.json'
        settings = json.loads(manifest.read_text())
        settings.setdefault('Plugins', {})['ralleur-tiling-guardEnabled'] = 'true'
        manifest.write_text(json.dumps(settings, indent=2) + '\n')
    print('Shift guard installed; Krohnkite window states preserved.')

if __name__ == '__main__':
    install_guard()
