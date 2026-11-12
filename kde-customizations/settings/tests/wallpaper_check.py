#!/usr/bin/env python3
"""Check wallpaper controls in an isolated settings window.
Temporarily changes wallpaper preferences and restores them, including on failure.
"""
from pathlib import Path
import json, subprocess, time, tempfile, shutil, os, argparse
HERE=Path(__file__).resolve().parent
args=argparse.Namespace(gallery=False, audit_only=False)
SOURCE=Path.home()/'.config/quickshell/caelestia'
fixture=tempfile.TemporaryDirectory(prefix='flausen-settings-live-')
SHELL=Path(fixture.name)
actual_runtime=Path(os.environ.get('XDG_RUNTIME_DIR',f'/run/user/{os.getuid()}'))
test_runtime=SHELL/'runtime';test_runtime.mkdir(mode=0o700)
runtime_env=dict(os.environ,XDG_RUNTIME_DIR=str(test_runtime),
    PIPEWIRE_RUNTIME_DIR=str(actual_runtime),PULSE_SERVER=os.environ.get('PULSE_SERVER','unix:'+str(actual_runtime/'pulse/native')))
wayland=os.environ.get('WAYLAND_DISPLAY','wayland-1')
runtime_env['WAYLAND_DISPLAY']=wayland if wayland.startswith('/') else str(actual_runtime/wayland)
for item in SOURCE.iterdir():
    if item.name not in ['modules','shell.qml']:(SHELL/item.name).symlink_to(item,target_is_directory=item.is_dir())
(SHELL/'modules').mkdir()
for item in (SOURCE/'modules').iterdir():
    if item.name!='nexus':(SHELL/'modules'/item.name).symlink_to(item,target_is_directory=item.is_dir())
shutil.copytree(SOURCE/'modules/nexus',SHELL/'modules/nexus')
factory=SHELL/'modules/nexus/WindowFactory.qml'
ft=factory.read_text().replace('            id: win','            id: win\n            visible: true\n            minimized: '+('false' if args.gallery or args.audit_only else 'true'),1).replace('flausen Settings · ','flausen Prüffenster '+SHELL.name+' · ')
a=ft.index('            function raise(): void {');b=ft.index('\n            Component.onDestruction:',a)
ft=ft[:a]+'            function raise(): void {}\n'+ft[b:]
factory.write_text(ft)
(SHELL/'shell.qml').write_text('''import QtQuick
import Quickshell
import Quickshell.Io
import Caelestia
import Caelestia.Config
import qs.modules.nexus
import qs.services
ShellRoot {
    id: root
    Binding {target:ShellState;property:"shellRoot";value:root}
    settings.watchFiles: false
    Binding {target:Translations;property:"extraSearchPaths";value:[Qt.resolvedUrl("translations")]}
    Binding {target:Translations;property:"language";value:GlobalConfig.general.language}
    IpcHandler {
        target: "nexus"
        function open(): void {WindowFactory.create();}
        function openPage(page: string,sub: string): void {WindowFactory.create(null,{initialPageIdx:parseInt(page),initialSubPageIdx:parseInt(sub)});}
        function close(): void {WindowFactory.close();}
    }
}
''')
NEXUS=SHELL/'modules/nexus/Nexus.qml'
child=None
log=open(SHELL/'test.log','w')
def run(*args):return subprocess.check_output(args,text=True).strip()
def ipc(*args):return subprocess.check_output(['quickshell','ipc','-p',str(SHELL),'call',*map(str,args)],env=runtime_env,text=True).strip()
def inspect():return json.loads(ipc('flausenSettingsTest','inspect'))
def restart():
    global child
    if child is not None:
        child.terminate()
        try:child.wait(timeout=5)
        except subprocess.TimeoutExpired:child.kill();child.wait()
    env=dict(runtime_env,QML2_IMPORT_PATH=str(Path.home()/'.local/lib/qt6/qml')+':'+str(SHELL),
        CAELESTIA_LIB_DIR=str(Path.home()/'.local/lib/caelestia'),CAELESTIA_BIN_DIR=str(Path.home()/'.local/bin'),
        QS_NO_RELOAD_POPUP='1',QS_DISABLE_CRASH_HANDLER='1')
    # Match the graphical session locale, including the absence of overrides.
    for key in list(env):
        if key=='LANGUAGE' or key.startswith('LC_'):env.pop(key)
    # Match the graphical session locale, which can differ from the tool host.
    for line in subprocess.check_output(['systemctl','--user','show-environment'],text=True).splitlines():
        key,sep,value=line.partition('=')
        if sep and (key in ['LANG','LANGUAGE'] or key.startswith('LC_')):env[key]=value
    child=subprocess.Popen(['/usr/bin/quickshell','-p',str(SHELL)],env=env,stdout=log,stderr=log)
    for _ in range(100):
        if child.poll() is not None:raise RuntimeError((SHELL/'test.log').read_text()[-6000:])
        result=subprocess.run(['quickshell','ipc','-p',str(SHELL),'call','nexus','open'],env=runtime_env,capture_output=True)
        if not result.returncode:
            try:
                s=inspect()
                if s.get('title'):return
            except (ValueError,subprocess.CalledProcessError):pass
        time.sleep(.1)
    raise RuntimeError('Isolated settings window failed to initialize: '+(SHELL/'test.log').read_text()[-6000:])
def until(pred):
    for _ in range(70):
        state=inspect()
        if pred(state) and not state.get('busy'):return state
        time.sleep(.1)
    raise AssertionError(state)

report=[]
initial_background=json.loads((Path.home()/'.config/caelestia/shell.json').read_text())['background']
original=None
try:
    text=NEXUS.read_text().replace('import QtQuick\n','import QtQuick\nimport QtQuick.Window\nimport QtTest as VisualTest\nimport Quickshell.Io\n')
    text=text.replace('    Pages {','    Pages {\n        id: testPages',1)
    text=text.rsplit('}',1)[0]+'''VisualTest.TestCase {id:screenshotTest; name:"WallpaperCapture"; when:false}
    IpcHandler {
        target:"wallpaperTest"
        function leaf(): var {const page=testPages.currentItem;return page?.currentItem ?? page;}
        function find(item,name): var {if(item.objectName===name)return item;for(const c of item.children ?? []){const f=find(c,name);if(f)return f;}return null;}
        function facts(): string {
            const page=leaf(), button=find(page,"wallpaper-random"), interval=find(page,"wallpaper-interval"), set=find(page,"wallpaper-set-0");
            return JSON.stringify({ready:!!button,enabled:Config.background.slideshowEnabled,random:Config.background.slideshowRandom,interval:Config.background.slideshowInterval,intervalEnabled:interval?.enabled,label:button?.text,setY:set?.mapToItem(page,0,0).y,buttonY:button?.mapToItem(page,0,0).y,current:Wallpapers.actualCurrent});
        }
        function restore(enabled:bool, random:bool, interval:real, path:string): void {GlobalConfig.background.slideshowEnabled=enabled;GlobalConfig.background.slideshowRandom=random;GlobalConfig.background.slideshowInterval=interval;GlobalConfig.save();if(path)Wallpapers.setWallpaper(path);}
        function toggle(): void {find(leaf(),"wallpaper-random").clicked();}
        function interval(minutes:int): void {find(leaf(),"wallpaper-interval").moved(minutes);}
        function manual(path:string): void {leaf().selectImage(path);}
        function capture(path:string): void {find(leaf(),"wallpaper-grid").positionViewAtBeginning();WindowFactory.openWindow.width=858;WindowFactory.openWindow.height=1000;const image=screenshotTest.grabImage(root);image.save(path);}
    }
}'''
    NEXUS.write_text(text)
    # restart() expects the standard inspect hook during startup.
    NEXUS.write_text(NEXUS.read_text().replace('    IpcHandler {\n        target:"wallpaperTest"','    '+(HERE/'probe.qml.inc').read_text()+'\n    IpcHandler {\n        target:"wallpaperTest"'))
    restart()
    ipc('nexus','openPage',0,1)
    ipc('flausenSettingsTest','showForCapture')
    time.sleep(.8)
    def facts():return json.loads(ipc('wallpaperTest','facts'))
    for _ in range(80):
        f=facts()
        if f['ready']:break
        time.sleep(.1)
    assert f['ready'],f
    time.sleep(1);f=facts();original=f['current']
    if f['enabled']:
        ipc('wallpaperTest','toggle');time.sleep(.2);f=facts()
    assert not f['enabled'] and not f['intervalEnabled'],f
    assert f['setY']>f['buttonY']+240,f
    ipc('wallpaperTest','toggle');time.sleep(.6)
    f=facts();assert f['enabled'] and f['random'] and f['intervalEnabled'],f
    ipc('wallpaperTest','interval',45);time.sleep(.3)
    assert facts()['interval']==.75,facts()
    ipc('wallpaperTest','toggle');time.sleep(.2)
    assert not facts()['enabled'],facts()
    ipc('wallpaperTest','toggle');time.sleep(.3)
    ipc('wallpaperTest','manual',original);time.sleep(.4)
    assert not facts()['enabled'],facts()
    ipc('wallpaperTest','interval',30);time.sleep(1.5)
    stored=json.loads((Path.home()/'.config/caelestia/shell.json').read_text())['background']
    assert stored['slideshowEnabled'] is False and stored['slideshowInterval']==.5,stored
    ipc('wallpaperTest','capture',str(HERE.parent/'evidence/native/wallpaper-controls.png'));time.sleep(.8)
    ipc('wallpaperTest','capture',str(HERE.parent/'evidence/native/wallpaper-controls.png'));time.sleep(.2)
    report.append(dict(ok=True,toggle=True,intervalMinutes=True,persisted=True,manualStopsTimer=True,setsBelowPreview=True,facts=facts()))
finally:
    if child is not None:
        try:
            ipc('wallpaperTest','restore',str(initial_background.get('slideshowEnabled',False)).lower(),str(initial_background.get('slideshowRandom',True)).lower(),initial_background.get('slideshowInterval',.5),original or '')
            time.sleep(1.5)
        finally:
            child.terminate();child.wait(timeout=5)
    log.close()
    (HERE.parent/'evidence/wallpaper-controls-test.log').write_text((SHELL/'test.log').read_text())
    (HERE.parent/'evidence/wallpaper-controls-check.json').write_text(json.dumps(report,indent=2)+'\n')
    fixture.cleanup()
print(json.dumps(report,indent=2))
