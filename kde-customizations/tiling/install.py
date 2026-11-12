#!/usr/bin/env python3
"""Install the opt-in gesture patch against the locally installed Krohnkite."""
import datetime
import json
from pathlib import Path
import shutil
import subprocess

SOURCE = Path(__file__).resolve().parent
TARGET = Path.home() / '.local/share/kwin/scripts/krohnkite'
STATE = Path.home() / '.local/state/ralleur-tiling'
BUILD = Path.home() / '.cache/ralleur-tiling-build'

def run(*args):
    return subprocess.check_output(args, text=True).strip()

def add_preview(qml):
    if 'function restoreRalleurCheckpoint' not in qml:
        qml = qml.replace('    property var runtime: null', '''    property var runtime: null
    function restoreRalleurCheckpoint(payload) {
        K.ralleurRestoreCheckpoint(runtime.driver, JSON.parse(payload));
    }''')
    if 'id: ralleurPreview' in qml:
        return qml
    return qml.replace('    property var runtime: null', '''    property var runtime: null
    Loader {
        id: ralleurPreview
        source: "drop-preview.qml"
        function showPlan(area, rectangles, selected, label) {
            if (item) item.showPlan(area, rectangles, selected, label);
        }
        function hide() { if (item) item.hide(); }
    }''')

def patched_script(text):
    if '// RALLEUR OPT-IN BEGIN' in text:
        raise RuntimeError('Use the original saved script when reapplying')
    replacements = {
        'this.control.onWindowMoveStart(window);': 'this.control.onWindowMoveStart(window, this);',
        '    onWindowMoveStart(window) {\n    }': '''    onWindowMoveStart(window, ctx) {
        if (RALLEUR_INPUT) ralleurMoveStart(this, ctx, window);
    }''',
        '    onWindowDragging(ctx, window, windowRect, reason) {': '''    onWindowDragging(ctx, window, windowRect, reason) {
        if (RALLEUR_INPUT) {
            ralleurMoveStep(this, ctx, window);
            return;
        }''',
        '    onWindowMoveOver(ctx, window, reason) {': '''    onWindowMoveOver(ctx, window, reason) {
        if (RALLEUR_INPUT) return ralleurMoveOver(this, ctx, window);''',
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise RuntimeError('Krohnkite changed; patch requires review: ' + old)
        text = text.replace(old, new)
    from resize_patch import patched_resize
    return patched_resize(text + '\n// RALLEUR OPT-IN BEGIN\n' + (SOURCE / 'gesture.js').read_text())

def main():
    original = (TARGET / 'contents/code/script.js').read_text()
    qml = (TARGET / 'contents/ui/main.qml').read_text()
    if '// RALLEUR OPT-IN BEGIN' in original:
        raise SystemExit('Already installed. Restore the saved original before reapplying.')
    script = patched_script(original)
    assert qml.count('import "../code/script.js" as K') == 1
    assert qml.count('        runtime = new K.KWinRuntime(api);') == 1
    qml = qml.replace('import "../code/script.js" as K', 'import "../code/script.js" as K\nimport "ralleur-input"')
    qml = qml.replace('    property var runtime: null', '    property var runtime: null\n    TilingInput { id: tilingInput }')
    qml = add_preview(qml)
    qml = qml.replace('        runtime = new K.KWinRuntime(api);', '        K.RALLEUR_INPUT = tilingInput;\n        runtime = new K.KWinRuntime(api);')
    run('cmake', '-S', str(SOURCE), '-B', str(BUILD))
    run('cmake', '--build', str(BUILD), '--parallel', '4')
    backup = STATE / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup.mkdir(parents=True)
    shutil.copytree(TARGET, backup / 'krohnkite')
    shutil.copy2(Path.home() / '.config/kwinrc', backup / 'kwinrc')
    shutil.copy2(Path.home() / '.config/kglobalshortcutsrc', backup / 'kglobalshortcutsrc')
    settings = {
        'Script-krohnkite': {
            'floatAsDefault': 'true', 'floatDefaultSizeEnable': 'false',
            'floatRandomEnable': 'false', 'tileNothing': 'false',
            'floatUtility': 'true', 'adjustLayout': 'true', 'adjustLayoutLive': 'true',
            'keepTilingOnDrag': 'true', 'limitTileWidth': 'false',
            'noTileBorder': 'false', 'screenGapBetween': '8',
            'screenGapTop': '8', 'screenGapBottom': '8', 'screenGapLeft': '8', 'screenGapRight': '8',
            **{name + 'LayoutOrder': '0' for name in ['tile', 'monocle', 'threeColumn', 'spiral', 'stacked', 'columns', 'spread', 'stair', 'binaryTree', 'cascade', 'floating']},
            'quarterLayoutOrder': '1',
        },
        'MouseBindings': {'CommandAllKey': 'Meta', 'CommandAll1': 'Move', 'CommandAll3': 'Resize'},
        'Plugins': {'krohnkiteEnabled': 'true'},
    }
    (backup / 'settings.json').write_text(json.dumps(settings, indent=2))
    run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'krohnkite')
    # A fresh URL avoids KWin's in-process QML/JS cache during a live reload.
    generation = 'ralleur-' + backup.name
    contents = TARGET / 'contents' / generation
    shutil.copytree(backup / 'krohnkite/contents', contents)
    (contents / 'code/script.js').write_text(script)
    (contents / 'ui/main.qml').write_text(qml)
    shutil.copy2(SOURCE / 'drop-preview.qml', contents / 'ui/drop-preview.qml')
    native = contents / 'ui/ralleur-input'
    native.mkdir(exist_ok=True)
    shutil.copy2(SOURCE / 'native/qmldir', native)
    shutil.copy2(BUILD / 'libralleurtilinginput.so', native)
    metadata = json.loads((TARGET / 'metadata.json').read_text())
    metadata['X-Plasma-MainScript'] = 'ui/main.qml'
    (TARGET / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    # KWin resolves the standard ui/main.qml entry independently of this metadata.
    # Future sessions enter through this loader; this session uses the fresh URL.
    (TARGET / 'contents/ui/main.qml').write_text(
        'import QtQuick\nItem { Loader { source: "../' + generation + '/ui/main.qml" } }\n')
    for group, entries in settings.items():
        for key, value in entries.items():
            run('kwriteconfig6', '--file', 'kwinrc', '--group', group, '--key', key, value)
    run('qdbus6', 'org.kde.KWin', '/KWin', 'reconfigure')
    # start() loads scripts enabled by reconfigure without restarting the session.
    run('qdbus6', 'org.kde.KWin', '/Scripting', 'start')
    run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'krohnkite')
    script_id = run('qdbus6', 'org.kde.KWin', '/Scripting', 'loadDeclarativeScript', str(contents / 'ui/main.qml'), 'krohnkite')
    run('qdbus6', 'org.kde.KWin', '/Scripting/Script' + script_id, 'run')
    (STATE / 'latest').write_text(str(backup))
    if not (STATE / 'baseline').exists():
        (STATE / 'baseline').write_text(str(backup))
    from install_guard import install_guard
    guard = Path.home() / '.local/share/kwin/scripts/ralleur-tiling-guard'
    if not guard.exists():
        install_guard()
    else:
        run('kwriteconfig6', '--file', 'kwinrc', '--group', 'Plugins', '--key', 'ralleur-tiling-guardEnabled', 'true')
        run('qdbus6', 'org.kde.KWin', '/KWin', 'reconfigure')
        run('qdbus6', 'org.kde.KWin', '/Scripting', 'start')
        settings['Plugins']['ralleur-tiling-guardEnabled'] = 'true'
        (backup / 'settings.json').write_text(json.dumps(settings, indent=2))
    print('Installed; backup: ' + str(backup))

if __name__ == '__main__':
    main()
