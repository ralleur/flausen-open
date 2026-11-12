#!/usr/bin/env python3
"""Stage the tested resize fix for next login. Never contact the running KWin."""
import argparse
import datetime
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from resize_patch import patched_resize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', default=shutil.which('node'))
    args = parser.parse_args()
    if not args.node:
        parser.error('Pass --node /path/to/node to run the isolated regression tests')
    source = Path(__file__).resolve().parent
    target = Path.home() / '.local/share/kwin/scripts/krohnkite'
    entry = target / 'contents/ui/main.qml'
    match = re.search(r'source:\s*"([^"]+)"', entry.read_text())
    if not match:
        raise RuntimeError('Expected the installed Ralleur loader')
    previous = (entry.parent / match[1]).resolve().parent.parent
    original = (previous / 'code/script.js').read_text()
    if '// RALLEUR RESIZE BEGIN' in original:
        raise RuntimeError('Resize fix is already staged')
    script = patched_resize(original)
    with tempfile.TemporaryDirectory(prefix='ralleur-resize-test-') as directory:
        test_script = Path(directory) / 'script.js'
        test_script.write_text(script)
        subprocess.run([args.node, str(source / 'tests/resize.test.cjs'), str(test_script)], check=True)
    build = Path.home() / '.cache/ralleur-tiling-build'
    subprocess.run(['cmake', '-S', str(source), '-B', str(build)], check=True)
    subprocess.run(['cmake', '--build', str(build), '--target', 'ralleurtilinginput', '--parallel', '4'], check=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = Path.home() / '.local/state/ralleur-tiling' / ('before-resize-' + stamp)
    backup.mkdir(parents=True)
    shutil.copy2(entry, backup / 'loader.qml')
    (backup / 'previous-generation.txt').write_text(str(previous) + '\n')
    generation = target / 'contents' / ('ralleur-resize-' + stamp)
    shutil.copytree(previous, generation)
    (generation / 'code/script.js').write_text(script)
    native = generation / 'ui/ralleur-input'
    native.mkdir(exist_ok=True)
    shutil.copy2(build / 'libralleurtilinginput.so', native)
    (native / 'qmldir').write_text('module Ralleur.ResizeInput.Run' + stamp.replace('-', '') + '\nplugin ralleurtilinginput\n')
    qml = (generation / 'ui/main.qml').read_text()
    qml, count = re.subn(r'^import "[^"]*ralleur-input"$', 'import "ralleur-input"', qml, flags=re.M)
    if count != 1:
        raise RuntimeError('Expected exactly one input module import; loader left unchanged')
    (generation / 'ui/main.qml').write_text(qml)
    # The running script has already loaded its QML. Only the next session reads
    # this entry; do not unload scripts, reconfigure KWin, or use a live probe.
    replacement = entry.with_suffix('.qml.next')
    replacement.write_text('import QtQuick\nItem { Loader { source: "../' + generation.name + '/ui/main.qml" } }\n')
    replacement.replace(entry)
    print('Staged for next login; current KWin untouched. Backup: ' + str(backup))


if __name__ == '__main__':
    main()
