#!/usr/bin/env python3
"""Capture native, isolated flausen UI without collecting desktop pixels.

The Start menu uses explicitly staged recent documents. All device and update
states remain real. Clipboard history and network addresses are not captured.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'showcase/screenshots'
SOURCE = Path.home() / '.config/quickshell/caelestia'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='flausen-showcase-') as temporary:
        base = Path(temporary)
        for item in SOURCE.iterdir():
            if item.name not in ['shell.qml', 'modules']:
                (base / item.name).symlink_to(item, target_is_directory=item.is_dir())
        (base / 'modules').mkdir()
        for item in (SOURCE / 'modules').iterdir():
            if item.name != 'launcher':
                (base / 'modules' / item.name).symlink_to(item, target_is_directory=item.is_dir())
        shutil.copytree(SOURCE / 'modules/launcher', base / 'modules/launcher')
        # Staging affects only this temporary UI process, never the user's history.
        staged = dict(name='ralleur', detail='Showcase workspace', face='', recent=[
            dict(title='A little out of line', detail='Showcase / Creative notes', icon='text-x-generic', uri=(ROOT/'showcase/demo-workspace/creative-notes.txt').as_uri()),
            dict(title='Your next adventure', detail='Showcase / Play', icon='folder-games', uri=(ROOT/'showcase/demo-workspace').as_uri()),
            dict(title='Make room for everyday', detail='Showcase / Project brief', icon='text-x-generic', uri=(ROOT/'showcase/demo-workspace/project-brief.txt').as_uri())])
        (base/'modules/launcher/start-data.py').write_text('import json\nprint('+repr(json.dumps(staged))+')\n')
        content = base/'modules/launcher/Content.qml'
        text = content.read_text().replace('    function askHermes(): void {', '''    function showcaseHermes(): void { hermes.expanded = true; }
    function askHermes(): void {''')
        # Do not start a model merely to photograph the empty assistant UI.
        chat = base/'modules/launcher/HermesChat.qml'
        chat.write_text(chat.read_text().replace('if (!bridge.running) bridge.running = true;', 'root.ready = false;'))
        content.write_text(text)
        runtime = base/'runtime';runtime.mkdir(mode=0o700)
        actual_runtime = os.environ.get('XDG_RUNTIME_DIR', '/run/user/'+str(os.getuid()))
        wayland = os.environ.get('WAYLAND_DISPLAY', 'wayland-1')
        env = dict(os.environ, LANG='en_US.UTF-8', LANGUAGE='en_US', LC_MESSAGES='en_US.UTF-8',
                   XDG_RUNTIME_DIR=str(runtime), WAYLAND_DISPLAY=wayland if wayland.startswith('/') else actual_runtime+'/'+wayland,
                   PIPEWIRE_RUNTIME_DIR=actual_runtime, PULSE_SERVER='unix:'+actual_runtime+'/pulse/native',
                   QML2_IMPORT_PATH=str(Path.home()/'.local/lib/qt6/qml')+':'+str(base),
                   CAELESTIA_LIB_DIR=str(Path.home()/'.local/lib/caelestia'), CAELESTIA_BIN_DIR=str(Path.home()/'.local/bin'),
                   QS_NO_RELOAD_POPUP='1', QS_DISABLE_CRASH_HANDLER='1')
        preview = (ROOT/'kde-customizations/taskbar/network-popover/proportions/preview.qml').read_text()
        preview = preview.replace('        visible: true', '        visible: true\n        Tokens.screen: screen?.name ?? ""', 1)
        preview = preview.replace('interval: 2000;', 'interval: 6000;')
        for kind in ['updates', 'audio', 'clock']:
            (base/'shell.qml').write_text(preview)
            output = OUT/(kind+'.png')
            runenv = dict(env, NETWORK_PREVIEW_KIND=kind, NETWORK_PREVIEW_OUTPUT=str(output))
            result = subprocess.run(['/usr/bin/quickshell', '-p', str(base)], env=runenv, capture_output=True, text=True, timeout=25)
            if not output.exists():
                raise RuntimeError(result.stdout[-3000:]+result.stderr[-3000:])
            print(kind, flush=True)
        launcher = '''import QtQuick
import QtQuick.Window
import Quickshell
import Caelestia.Config
import qs.components
import qs.services
import qs.modules.launcher as Launcher
ShellRoot {
    id: harness
    Window {
        id: win; visible: true; width: 720; height: 880; color: "#17191d"
        Tokens.screen: screen?.name ?? ""
        DrawerVisibilities { id: visibilityState; launcher: true }
        QtObject { id: panelStub; signal closed(); property bool isOpen: true }
        Launcher.Content {
            id: content; anchors.fill: parent
            maxWidth: 760; maxHeight: 880
            visibilities: visibilityState; panels: ({launcher:panelStub})
        }
        Timer { interval: 2500; running: true; onTriggered: {
            if (Quickshell.env("SHOWCASE_KIND") === "hermes") content.showcaseHermes();
        } }
        Timer { interval: 6000; running: true; onTriggered: content.grabToImage(result => {
            result.saveToFile(Quickshell.env("SHOWCASE_OUTPUT")); Qt.quit();
        }) }
        Timer { interval: 15000; running: true; onTriggered: Qt.quit() }
    }
}
'''
        for kind in ['launcher', 'hermes']:
            (base/'shell.qml').write_text(launcher)
            output = OUT/(kind+'.png')
            result = subprocess.run(['/usr/bin/quickshell','-p',str(base)], env=dict(env, SHOWCASE_KIND=kind, SHOWCASE_OUTPUT=str(output)), capture_output=True, text=True, timeout=25)
            if not output.exists():
                raise RuntimeError(result.stdout[-3500:]+result.stderr[-3500:])
            print(kind, flush=True)

if __name__ == '__main__':
    main()
