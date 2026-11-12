#!/usr/bin/env python3
"""Upgrade gesture behavior, retaining enrolled windows and layout proportions."""
import datetime
import json
from pathlib import Path
import re
import shutil
import sys
from install import add_preview, patched_script, run

source = Path(__file__).resolve().parent
target = Path.home() / '.local/share/kwin/scripts/krohnkite'
state = Path.home() / '.local/state/ralleur-tiling'
entry = target / 'contents/ui/main.qml'
loader = entry.read_text()
match = re.search(r'source:\s*"([^"]+)"', loader)
if not match:
    raise SystemExit('Expected the installed Ralleur loader')
previous = (entry.parent / match[1]).resolve().parent.parent
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = state / ('before-gestures-' + stamp)
backup.mkdir(parents=True)
shutil.copy2(entry, backup / 'loader.qml')

# Read the real controller state, rather than inferring membership from geometry.
sys.path.insert(0, str(source / 'tests'))
from probe import OutlineProbe
probe = OutlineProbe()
try:
    checkpoint = dict(probe.api.checkpoint())
    if 'error' in checkpoint:
        raise RuntimeError(checkpoint['error'])
    checkpoint = json.loads(json.dumps(checkpoint))
except Exception:
    probe.close()
    raise
(backup / 'checkpoint.json').write_text(json.dumps(checkpoint, indent=2))

generation = target / 'contents' / ('ralleur-gestures-' + stamp)
shutil.copytree(previous, generation)
original = (target / 'contents/code/script.js').read_text()
(generation / 'code/script.js').write_text(patched_script(original))
qml = add_preview((previous / 'ui/main.qml').read_text())
# The resize patch needs requestedGeometry(). Build a fresh module at a new
# URL; never overwrite a native library that the current KWin already loaded.
build = Path.home() / '.cache/ralleur-tiling-build'
run('cmake', '-S', str(source), '-B', str(build))
run('cmake', '--build', str(build), '--target', 'ralleurtilinginput', '--parallel', '4')
native = generation / 'ui/ralleur-input'
native.mkdir(exist_ok=True)
shutil.copy2(build / 'libralleurtilinginput.so', native)
(native / 'qmldir').write_text('module Ralleur.GestureInput.Run' + stamp.replace('-', '') + '\nplugin ralleurtilinginput\n')
qml = re.sub(r'^import "[^"]*ralleur-input"$', 'import "ralleur-input"', qml, flags=re.M)
qml = re.sub(r'^\s*K\.ralleurRestoreCheckpoint\(runtime.driver, .*\);\n', '', qml, flags=re.M)
(generation / 'ui/main.qml').write_text(qml)
shutil.copy2(source / 'drop-preview.qml', generation / 'ui/drop-preview.qml')
new_loader = 'import QtQuick\nItem { Loader { source: "../' + generation.name + '/ui/main.qml" } }\n'
run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'krohnkite')
entry.write_text(new_loader)
sid = run('qdbus6', 'org.kde.KWin', '/Scripting', 'loadDeclarativeScript', str(generation / 'ui/main.qml'), 'krohnkite')
run('qdbus6', 'org.kde.KWin', '/Scripting/Script' + sid, 'run')
run('qdbus6', 'org.kde.KWin', '/Scripting', 'start')
try:
    if not probe.api.restoreCheckpoint(json.dumps(checkpoint)):
        raise RuntimeError('New runtime did not accept its window checkpoint')
finally:
    probe.close()
print('Updated gestures; checkpoint: ' + str(backup / 'checkpoint.json'))
