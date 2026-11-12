from pathlib import Path
import dbus
import shutil
import subprocess
import tempfile
import uuid

class OutlineProbe:
    def __init__(self):
        source = Path(__file__).resolve().parent
        build = Path.home() / '.cache/ralleur-tiling-probe-build'
        def run(*args):
            return subprocess.check_output(args, text=True).strip()
        self.run = run
        run('cmake', '-S', str(source), '-B', str(build))
        run('cmake', '--build', str(build), '--parallel', '4')
        self.directory = tempfile.TemporaryDirectory(prefix='ralleur-tiling-probe-')
        root = Path(self.directory.name)
        native = root / 'native';native.mkdir()
        shutil.copy2(build / 'libralleurtilingprobe.so', native)
        (native / 'qmldir').write_text('module Ralleur.TilingProbe.Run' + uuid.uuid4().hex + '\nplugin ralleurtilingprobe\n')
        (root / 'main.qml').write_text('import QtQuick\nimport "native"\nItem { Probe {} }\n')
        sid = run('qdbus6', 'org.kde.KWin', '/Scripting', 'loadDeclarativeScript', str(root / 'main.qml'), 'ralleur-tiling-probe')
        run('qdbus6', 'org.kde.KWin', '/Scripting/Script' + sid, 'run')
        run('qdbus6', 'org.kde.KWin', '/Scripting', 'start')
        self.api = dbus.Interface(dbus.SessionBus().get_object('org.kde.KWin', '/RalleurTilingProbe'), 'org.ralleur.TilingProbe')
        self.api.inspect()
        self.samples = 0
        self.previews = {}
        self.restored_sizes = []
    def check(self):
        state = dict(self.api.inspect())
        if state['moving'] and state['shift']:
            self.samples += 1
            assert not state['outline'], 'Native Shift grid appeared during drag'
            if state.get('previewVisible'):
                self.previews[str(state['caption'])] = dict(state['previewTarget'])
        if state['moving'] and not state['shift'] and str(state.get('caption','')).endswith('Test C'):
            self.restored_sizes.append((float(state['width']),float(state['height'])))
    def close(self):
        self.run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'ralleur-tiling-probe')
        self.directory.cleanup()
