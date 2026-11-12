#!/usr/bin/env python3
"""Add the dock's one-window tiling request to the current Krohnkite generation."""
import datetime
import json
from pathlib import Path
import re
import shutil
import sys
from install import run

source = Path(__file__).resolve().parent
target = Path.home() / '.local/share/kwin/scripts/krohnkite'
entry = target / 'contents/ui/main.qml'
match = re.search(r'source:\s*"([^"]+)"', entry.read_text())
if not match:
    raise SystemExit('Expected the installed Ralleur Krohnkite loader')
previous = (entry.parent / match[1]).resolve().parent.parent
if 'function ralleurArmLaunch' in (previous / 'code/script.js').read_text():
    raise SystemExit('Dock launch support is already installed')
script = (previous / 'code/script.js').read_text()
needle = '    onWindowAdded(ctx, window, reason) {\n        this.engine.manage(window);'
assert script.count(needle) == 1, 'Krohnkite window-added hook changed'
script = script.replace(needle, needle + '\n        ralleurApplyLaunch(this, ctx, window);')
script += '\n' + (source / 'launch.js').read_text()
qml = (previous / 'ui/main.qml').read_text()
qml = qml.replace('import "ralleur-input"', 'import "' + (previous / 'ui/ralleur-input').as_uri() + '"')
qml = qml.replace('    property var runtime: null', '''    property var runtime: null
    LaunchBridge {
        onRequested: payload => {
            if (scriptRoot.runtime) K.ralleurArmLaunch(payload);
        }
    }''')
qml = qml.replace('Item {\n    id: scriptRoot', 'import "ralleur-launch"\n\nItem {\n    id: scriptRoot')
qml = re.sub(r'function restoreRalleurCheckpoint\(payload\) \{[^}]*\}',
             'function restoreRalleurCheckpoint(payload) {\n        K.ralleurRestoreCheckpoint(runtime.driver, JSON.parse(payload));\n    }', qml)
assert 'LaunchBridge {' in qml and 'import "ralleur-launch"' in qml
build = Path.home() / '.cache/ralleur-tiling-build'
run('cmake', '-S', str(source), '-B', str(build))
run('cmake', '--build', str(build), '--target', 'ralleurtilinglaunch', '--parallel', '4')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = Path.home() / '.local/state/ralleur-tiling' / ('before-dock-launch-' + stamp)
backup.mkdir(parents=True)
shutil.copy2(entry, backup / 'loader.qml')
sys.path.insert(0, str(source / 'tests'))
from probe import OutlineProbe
probe = OutlineProbe()
try:
    checkpoint = json.loads(json.dumps(dict(probe.api.checkpoint())))
    assert 'error' not in checkpoint, checkpoint
    (backup / 'checkpoint.json').write_text(json.dumps(checkpoint, indent=2))
    generation = target / 'contents' / ('ralleur-launch-' + stamp)
    shutil.copytree(previous, generation)
    (generation / 'code/script.js').write_text(script)
    (generation / 'ui/main.qml').write_text(qml)
    native = generation / 'ui/ralleur-launch'
    native.mkdir()
    (native / 'qmldir').write_text('module Ralleur.TilingLaunch.Run' + stamp.replace('-', '') + '\nplugin ralleurtilinglaunch\n')
    shutil.copy2(build / 'libralleurtilinglaunch.so', native)
    run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'krohnkite')
    try:
        entry.write_text('import QtQuick\nItem { Loader { source: "../' + generation.name + '/ui/main.qml" } }\n')
        sid = run('qdbus6', 'org.kde.KWin', '/Scripting', 'loadDeclarativeScript', str(generation / 'ui/main.qml'), 'krohnkite')
        run('qdbus6', 'org.kde.KWin', '/Scripting/Script' + sid, 'run')
        run('qdbus6', 'org.kde.KWin', '/Scripting', 'start')
        assert probe.api.restoreCheckpoint(json.dumps(checkpoint)), 'Checkpoint restore failed'
        after = json.loads(json.dumps(dict(probe.api.checkpoint())))
        assert [(w['id'],w['tiled']) for w in checkpoint['windows']] == [(w['id'],w['tiled']) for w in after['windows']], after
        # Verify that the bridge rejects an empty request without leaving a pending launch.
        assert run('qdbus6','org.kde.KWin','/RalleurTilingLaunch','org.ralleur.TilingLaunch.arm','[]') == 'false'
    except Exception:
        run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'krohnkite')
        shutil.copy2(backup / 'loader.qml', entry)
        sid = run('qdbus6','org.kde.KWin','/Scripting','loadDeclarativeScript',str(previous / 'ui/main.qml'),'krohnkite')
        run('qdbus6','org.kde.KWin','/Scripting/Script' + sid,'run')
        raise
finally:
    probe.close()
(source / 'tests/dock-launch-backup.txt').write_text(str(backup) + '\n')
print('Installed dock tiling bridge; preserved window checkpoint; backup: ' + str(backup))
