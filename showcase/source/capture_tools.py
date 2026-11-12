#!/usr/bin/env python3
"""Render real capture/clipboard UI with explicitly staged, non-private content."""
from pathlib import Path
import json,os,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path.home()/'.config/quickshell/caelestia'
OUT=ROOT/'showcase/screenshots'
with tempfile.TemporaryDirectory(prefix='flausen-tools-showcase-') as directory:
    base=Path(directory);(base/'modules').mkdir()
    for item in SOURCE.iterdir():
        if item.name not in ['shell.qml','modules']:(base/item.name).symlink_to(item,target_is_directory=item.is_dir())
    for item in (SOURCE/'modules').iterdir():
        if item.name in ['launcher','utilities','bar']:shutil.copytree(item,base/'modules'/item.name)
        else:(base/'modules'/item.name).symlink_to(item,target_is_directory=item.is_dir())
    gallery=base/'gallery';gallery.mkdir()
    for name in ['desktop-hero','tiling','appearance','launcher']:shutil.copy2(OUT/(name+'.png'),gallery/(name+'.png'))
    for path in (base/'modules').rglob('*.qml'):
        if path.is_symlink(): continue
        original=path.read_text()
        if 'GlobalConfig.paths.screenshotsDir' in original:
            path.write_text(original.replace('GlobalConfig.paths.screenshotsDir',json.dumps(str(gallery))))
    entries=[dict(id=1,isPinned=True,pinId='demo-1',isImage=False,preview='Your computer. Your playground.'),dict(id=2,isPinned=True,pinId='demo-2',isImage=True,preview='Desktop capture',imagePath=str(OUT/'desktop-hero.png')),dict(id=3,isPinned=False,isImage=False,preview='Capture an idea. Copy it. Carry on.')]
    clipboard='''pragma Singleton
import QtQuick
QtObject {
    readonly property bool available: true
    readonly property var items: []
    readonly property var pinnedItems: []
    signal imageReady(int id, string path)
    function getSortedItems(): var { return ENTRIES; }
    function reload(): void {}
    function copyPinned(pinId: string): void {}
    function pin(id: int): void {}
    function unpin(id: string): void {}
    function isImageCached(id: int): bool { return false; }
    function getImagePath(id: int): string { return ""; }
}
'''.replace('ENTRIES',json.dumps(entries))
    (base/'modules/launcher/services/Clipboard.qml').write_text(clipboard)
    qml='''import QtQuick
import QtQuick.Window
import Quickshell
import Caelestia.Config
import qs.components
import qs.services
import qs.modules.bar.popouts as Popouts
ShellRoot {
    Window {
        id: window; visible:true; width:520; height:surface.height; color:"#17191d"
        Tokens.screen: screen?.name ?? ""
        Popouts.PopoutState { id: popouts }
        DrawerVisibilities { id: visibilityState }
        Rectangle {
            id: surface; width:window.width; height:loader.implicitHeight+40; radius:28
            color:MenuStyle.surface; border.width:1; border.color:MenuStyle.border
            Loader {
                id:loader; x:(surface.width-width)/2; y:20; width:480
                sourceComponent:Quickshell.env("SHOWCASE_KIND")==="capture" ? capture : clipboard
            }
            Component {id:capture;Popouts.ScreenCapture {popouts:popouts;visibilities:visibilityState}}
            Component {id:clipboard;Popouts.ClipboardHistory {popouts:popouts;scaleOffset:1.15;fontScale:1.15}}
        }
        Timer {interval:4000;running:true;onTriggered:surface.grabToImage(result=>{result.saveToFile(Quickshell.env("SHOWCASE_OUTPUT"));Qt.quit();})}
        Timer {interval:10000;running:true;onTriggered:Qt.quit()}
    }
}
'''
    (base/'shell.qml').write_text(qml)
    runtime=base/'runtime';runtime.mkdir(mode=0o700)
    actual=os.environ.get('XDG_RUNTIME_DIR','/run/user/'+str(os.getuid()));wayland=os.environ.get('WAYLAND_DISPLAY','wayland-1')
    env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime),WAYLAND_DISPLAY=wayland if wayland.startswith('/') else actual+'/'+wayland,
             QML2_IMPORT_PATH=str(Path.home()/'.local/lib/qt6/qml')+':'+str(base),CAELESTIA_LIB_DIR=str(Path.home()/'.local/lib/caelestia'),
             CAELESTIA_BIN_DIR=str(Path.home()/'.local/bin'),QS_NO_RELOAD_POPUP='1',QS_DISABLE_CRASH_HANDLER='1',LANG='en_US.UTF-8',LANGUAGE='en_US')
    for kind in ['capture','clipboard']:
        with open(base/'log','w') as log:
            result=subprocess.run(['/usr/bin/quickshell','-p',str(base)],env=dict(env,SHOWCASE_KIND=kind,SHOWCASE_OUTPUT=str(OUT/(kind+'.png'))),stdout=log,stderr=log,timeout=15)
        if not (OUT/(kind+'.png')).exists():raise RuntimeError((base/'log').read_text()[-4000:])
        print(kind,flush=True)
