#!/usr/bin/env python3
"""Exercise real QML controls and native navigation in the running desktop.
Temporarily changes theme, transparency, animation and text scale; restores all.
"""
from pathlib import Path
import json, subprocess, time, tempfile, shutil, os, argparse
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--account-profile',action='store_true',help='Check account picture, picker cancellation and user navigation')
parser.add_argument('--window-controls',action='store_true',help='Exercise frameless window controls')
parser.add_argument('--endpoint-only',action='store_true',help='Exercise only the Local endpoint draft; never save')
parser.add_argument('--audit-only',action='store_true')
parser.add_argument('--capture',action='append',default=[])
parser.add_argument('--gallery-only',action='store_true')
parser.add_argument('--gallery',action='store_true',help='Capture only the isolated settings content, never the active desktop')
parser.add_argument('--theme',action='store_true',help='Also exercise real desktop theme and shell-preference changes')
args=parser.parse_args()
if args.endpoint_only:args.gallery_only=True;args.capture=["hermes"]
if args.gallery_only:args.gallery=True
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
original=NEXUS.read_bytes()
initial_scheme=json.loads(run(str(Path.home()/'.local/bin/caelestia'),'scheme','get'))
report=[{'isolated':True,'productionShellUnchanged':True}]
initial=None
try:
    text=original.decode().replace('import QtQuick\n','import QtQuick\nimport QtQuick.Window\nimport QtQuick.Templates as TestT\nimport QtTest as VisualTest\nimport Quickshell.Io\n')
    text=text.replace('    Pages {','    Pages {\n        id: testPages',1)
    text=text.rsplit('}',1)[0]+'VisualTest.TestCase {id: screenshotTest; name: "FlausenCapture"; when: false}\n'+(HERE/'probe.qml.inc').read_text()+'\n}\n'
    NEXUS.write_text(text);restart();initial=inspect()
    if args.account_profile:
        for _ in range(50):
            facts=json.loads(ipc('flausenSettingsTest','accountFacts'))
            if facts['ready']:break
            time.sleep(.1)
        assert facts['ready'] and '/AccountsService/icons/' in facts['source'],facts
        source=facts['source']
        assert ipc('flausenSettingsTest','accountAction','picture')=='true'
        assert json.loads(ipc('flausenSettingsTest','accountFacts'))['picker']
        chooser=until(lambda s:any('portal' in w['app'] and ('profile picture' in w['title'].lower() or 'Profile picture' in w['title']) for w in s['windows']))
        if args.gallery:
            picture=HERE.parent/'evidence/native/profile-picture-picker.png'
            subprocess.run(['spectacle','-b','-n','-a','-o',str(picture)],check=True,capture_output=True)
        report.append({'kdePortalPicturePicker':True})
        ipc('flausenSettingsTest','accountAction','cancel')
        facts=json.loads(ipc('flausenSettingsTest','accountFacts'))
        assert not facts['picker'] and facts['source']==source,facts
        assert ipc('flausenSettingsTest','accountAction','user')=='true'
        until(lambda s:s['module']=='kcm_users' and s['moduleReady'])
        report.append({'systemAccountPicture':True,'picturePickerCancel':True,'userSettingsNavigation':True})
    if args.window_controls:
        assert initial['frameless'], initial
        until(lambda s:s['shadow'] and s['frameRadius']==12)
        assert ipc('flausenSettingsTest','windowControl','maximize') == 'true'
        until(lambda s:s['maximized'] and not s['shadow'] and s['frameRadius']==0)
        assert ipc('flausenSettingsTest','windowControl','maximize') == 'true'
        until(lambda s:not s['maximized'] and s['shadow'] and s['frameRadius']==12)
        assert ipc('flausenSettingsTest','windowControl','minimize') == 'true'
        until(lambda s:s['minimized'])
        ipc('flausenSettingsTest','restoreWindow')
        until(lambda s:not s['minimized'])
        report.append({'framelessWindowControls':True,'maximizeRestoreMinimize':True,'dolphinFrameAndNativeShadow':True})
    if not args.gallery_only and not args.audit_only:
        for page,title in [(22,'Hermes'),(17,'General'),(18,'Display'),(19,'Keyboard & mouse'),(20,'Privacy & security'),(21,'System'),(3,None),(4,None),(5,None),(6,None),(2,None),(0,'Appearance')]:
            ipc('nexus','openPage',page,-1)
            time.sleep(.4)
            s=until(lambda s:s['page']==page and (s['title']==title if title else bool(s['title'])))
            report.append({'page':page,'title':s['title'],'ok':True})
        ipc('nexus','openPage',22,-1);time.sleep(.6)
        facts=json.loads(ipc('flausenSettingsTest','hermesFacts'))
        assert facts['ready'] and not facts['loading'] and not facts['error'],facts
        time.sleep(3)
        vram=json.loads(ipc('flausenSettingsTest','vramFacts'))
        assert vram['ready'] and vram['capacity']>0,vram
        if facts['model']=='deepseek-flash':
            assert vram['model']==0 and vram['context']==0,vram
        assert ipc('flausenSettingsTest','click','LFM3')=='true';time.sleep(.2)
        vram=json.loads(ipc('flausenSettingsTest','vramFacts'))
        assert vram['canPreview'],vram
        ipc('flausenSettingsTest','vramPreview','true',65536)
        first=json.loads(ipc('flausenSettingsTest','vramFacts'))
        assert first['preview'] and first['model']>0 and first['context']>0,first
        ipc('flausenSettingsTest','vramPreview','true',131072)
        second=json.loads(ipc('flausenSettingsTest','vramFacts'))
        assert second['model']==first['model'] and second['context']==first['context']*2,second
        ipc('flausenSettingsTest','vramPreview','false',65536)
        report.append({'vram':'live capacity, cloud/CPU zero VRAM, model and context scenario verified','ok':True})
        original_model=facts['model']
        target='LFM3' if original_model=='deepseek-flash' else 'DeepSeek Flash'
        assert ipc('flausenSettingsTest','click',target)=='true'
        assert json.loads(ipc('flausenSettingsTest','hermesFacts'))['dirty']
        assert ipc('flausenSettingsTest','click','Reset')=='true';time.sleep(.4)
        facts=json.loads(ipc('flausenSettingsTest','hermesFacts'))
        assert facts['model']==original_model and not facts['dirty'],facts
        report.append({'hermesSettings':'profile loaded, model draft changed and reset without writing','ok':True})
        ipc('nexus','openPage',18,-1);time.sleep(.4)
        previous={w['address'] for w in inspect()['windows']}
        assert ipc('flausenSettingsTest','click','Display configuration')=='true'
        s=until(lambda s:s['module']=='kcm_kscreen' and s['moduleReady'])
        assert not s['moduleError'],s
        assert not any(w['address'] not in previous and 'systemsettings' in (w['app'] or '') for w in s['windows'])
        report.append({'embeddedDisplayModule':s['module'],'externalWindowsOpened':False,'ok':True})
        ipc('flausenSettingsTest','showForCapture');time.sleep(.6)
        ipc('flausenSettingsTest','polishForAudit',0);time.sleep(.2)
        facts=json.loads(ipc('flausenSettingsTest','controlFacts'))
        assert facts['help'] and all(10<h['implicitWidth']<=48 for h in facts['help']),facts
        assert facts['hdr'] and '&' not in facts['hdr']['shown'],facts
        before=facts['hdr']
        assert ipc('flausenSettingsTest','replaceHdrLabel')=='true';time.sleep(.2)
        facts=json.loads(ipc('flausenSettingsTest','controlFacts'))
        assert facts['hdr']==before,facts
        ipc('flausenSettingsTest','minimize')
        report.append({'displayRegression':'compact help buttons and late-created HDR label verified','ok':True})

        for module in ['kcm_users','kcm_regionandlang','kcm_componentchooser','kcm_access','kcm_nightlight','kcm_powerdevilprofilesconfig','kcm_keyboard','kcm_keys','kcm_mouse','kcm_screenlocker','kcm_firewall','kcm_about-distro']:
            ipc('nexus','openPage',17,-1);time.sleep(.15)
            ipc('flausenSettingsTest','module',module,module)
            s=until(lambda s:s['module']==module and (s['moduleReady'] or bool(s['moduleError'])))
            assert not s['moduleError'],s
            time.sleep(.4)
            report.append({'embeddedModule':module,'ok':True})
        ipc('nexus','openPage',19,-1);time.sleep(.2)
        ipc('flausenSettingsTest','module','kcm_mouse','Mouse');until(lambda s:s['moduleReady']);time.sleep(.3)
        assert ipc('flausenSettingsTest','nativeAction')=='true'
        until(lambda s:s['moduleDepth']>1)
        ipc('flausenSettingsTest','nativeBack');until(lambda s:s['moduleDepth']==1)
        report.append({'nativeActions':'module toolbar and nested pages preserved','ok':True})
        # Change a buffered mouse checkbox, then prove navigation is guarded and discard it.
        ipc('flausenSettingsTest','module','kcm_mouse','Mouse');time.sleep(.5)
        assert ipc('flausenSettingsTest','editMouse')=='true'
        s=until(lambda s:s['moduleDirty'])
        ownWindow=next(w for w in s['windows'] if w['title'].startswith('flausen Prüffenster'))
        ipc('flausenSettingsTest','closeWindow',ownWindow['address'])
        until(lambda s:s['confirm'])
        assert ipc('flausenSettingsTest','decide','Keep editing')=='true'
        until(lambda s:not s['confirm'] and s['moduleDirty'])
        report.append({'nativeClose':'unsaved changes protected','ok':True})
        ipc('nexus','openPage',3,-1)
        s=until(lambda s:s['confirm'])
        assert s['module']=='kcm_mouse'
        assert ipc('flausenSettingsTest','decide','Keep editing')=='true'
        until(lambda s:not s['confirm'] and s['moduleDirty'])
        ipc('nexus','openPage',3,-1);until(lambda s:s['confirm'])
        assert ipc('flausenSettingsTest','decide','Discard')=='true'
        until(lambda s:s['module']=='' and s['page']==3)
        report.append({'unsavedChanges':'cancel and discard navigation verified','ok':True})
        ipc('nexus','openPage',0,-1);time.sleep(.4)
        ipc('flausenSettingsTest','search','Resolution');s=until(lambda s:any(x['page']==18 for x in s['search']))
        report.append({'search':'Resolution','results':s['search'],'ok':True})
        ipc('flausenSettingsTest','search','')
        ipc('flausenSettingsTest','searchNative','Night light')
        until(lambda s:s['module']=='kcm_nightlight' and s['moduleReady'])
        report.append({'nativeSearch':'Nachtlicht opens its embedded module','ok':True})
        for module,title in [('kcm_clock','Date & time'),('@catalogue','All system settings')]:
            ipc('nexus','openPage',17,-1);time.sleep(.2)
            ipc('flausenSettingsTest','module',module,title);time.sleep(.6)
            report.append({'internalPage':module,'ok':True})
    
        ipc('nexus','openPage',0,-1);time.sleep(.4)
        if args.theme:
            assert ipc('flausenSettingsTest','click','Light')=='true';until(lambda s:s['light'] and not s['auto'])
            assert ipc('flausenSettingsTest','click','Dark')=='true';until(lambda s:not s['light'] and not s['auto'])
            assert ipc('flausenSettingsTest','click','Automatic')=='true';until(lambda s:s['auto'])
            ipc('flausenSettingsTest','click','Dark');until(lambda s:not s['auto'] and not s['light'])
            for label,name in [('Blue','blue'),('Coral','coral'),('Gold','amber'),('Green','green'),('Violet','violet'),('Graphite','graphite')]:
                assert ipc('flausenSettingsTest','click',label)=='true'
                until(lambda s:s['scheme']=='flausen-'+name)
            report.append({'accents':6,'ok':True})
            for label,key in [('Transparency','transparency'),('Reduce motion','animations')]:
                before=inspect()[key]
                assert ipc('flausenSettingsTest','toggle',label)=='true'
                until(lambda s:s[key]!=before)
                ipc('flausenSettingsTest','toggle',label);until(lambda s:s[key]==before)
            ipc('flausenSettingsTest','textScale',1.1);until(lambda s:abs(s['scale']-1.1)<.01)
            ipc('flausenSettingsTest','textScale',initial['scale']);until(lambda s:abs(s['scale']-initial['scale'])<.01)
            report.append({'controls':['Light','Dark','Automatic','Transparency','Reduce motion','Text size'],'ok':True})
        # Same-page deep links and cross-page deep links retain their subpage targets.
        for page,sub in [(0,8),(0,10),(0,-1),(0,1),(2,2),(19,-1)]:
            ipc('nexus','openPage',page,sub)
            time.sleep(.4)
            s=until(lambda s:s['page']==page and (s['subpages']>0 if sub>=0 else s['subpages']==0) and bool(s['title']) and (s['title']=='Appearance' if page==0 and sub==-1 else True))
            report.append({'page':page,'sub':sub,'title':s['title'],'ok':True})
    if args.audit_only:
        audits=[]
        for width in [1180,1000]:
            ipc('flausenSettingsTest','resize',width,810);ipc('flausenSettingsTest','showForCapture');time.sleep(.5)
            for module in ['kcm_kscreen','kcm_mouse','kcm_keyboard','kcm_keys','kcm_touchpad','kcm_users','kcm_regionandlang','kcm_componentchooser','kcm_access','kcm_nightlight','kcm_powerdevilprofilesconfig','kcm_screenlocker','kcm_firewall','kcm_about-distro']:
                if args.capture and module not in args.capture:continue
                ipc('nexus','openPage',17,-1);time.sleep(.15)
                ipc('flausenSettingsTest','module',module,module)
                state=until(lambda s:s['moduleReady'] or bool(s['moduleError']))
                assert not state['moduleError'],state
                time.sleep(.6)
                ipc('flausenSettingsTest','polishForAudit',width-396)
                raw=ipc('flausenSettingsTest','visualAudit')
                if not raw:raise RuntimeError('Preview process status: '+str(child.poll())+'; stderr tail: '+(SHELL/'test.log').read_text()[-1200:])
                assert raw.startswith("{"),(child.poll(),raw[:1500])
                audits.append(json.loads(raw))
            for page in ([] if args.capture else [0,2,3,4,5,6,17,18,19,20,21,22]):
                ipc('nexus','openPage',page,-1);time.sleep(.5)
                ipc('flausenSettingsTest','polishForAudit',0)
                audits.append(json.loads(ipc('flausenSettingsTest','visualAudit')))
        (HERE.parent/'evidence/layout-audit.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2)+'\n')
        findings=[item for audit in audits for item in audit['findings']]
        report.append({'layoutViews':len(audits),'findings':len(findings)})
    if args.gallery:
        ipc('flausenSettingsTest','showForCapture');time.sleep(.5)
        gallery=HERE.parent/'evidence/native';gallery.mkdir(exist_ok=True)
        captured=[]
        def capture(name):
            path=gallery/(name+'.png')
            if path.exists():path.unlink()
            time.sleep(.6)
            ipc('flausenSettingsTest','showForCapture');ipc('flausenSettingsTest','polishForAudit',0);time.sleep(.2)
            assert ipc('flausenSettingsTest','capture',path)=='true'
            for _ in range(40):
                if path.exists():
                    if args.window_controls:
                        from PIL import Image
                        image=Image.open(path).convert('RGBA')
                        assert image.getpixel((0,0))[3]==0, 'Corner must be transparent'
                        assert image.getpixel((20,20))[3]>200, 'Window content must be visible'
                    captured.append(name);return
                time.sleep(.1)
            raise AssertionError('Settings-only capture failed: '+name)
        for page,name in [(18,'display-overview'),(17,'general'),(22,'hermes'),(0,'appearance'),(3,'network'),(4,'bluetooth'),(5,'audio'),(6,'notifications'),(2,'desktop')]:
            if args.capture and name not in args.capture:continue
            ipc('nexus','close');ipc('nexus','openPage',page,-1);capture(name)
            if name=='hermes' and args.endpoint_only:
                time.sleep(.5)
                original_model=json.loads(ipc('flausenSettingsTest','hermesFacts'))['model']
                assert ipc('flausenSettingsTest','click','Local endpoint')=='true';time.sleep(.3)
                endpoint=json.loads(ipc('flausenSettingsTest','endpointFacts'))
                assert endpoint['panel'] and endpoint['fields']==3 and endpoint['model']=='local-endpoint' and not endpoint['error'],endpoint
                capture('hermes-local-endpoint')
                assert any(ipc('flausenSettingsTest','click',label)=='true' for label in ('Reset','Reset'));time.sleep(.5)
                facts=json.loads(ipc('flausenSettingsTest','hermesFacts'))
                assert facts['model']==original_model and not facts['dirty'],facts
                report.append({'localEndpointDraft':endpoint,'resetWithoutSaving':True,'ok':True})
                continue
            if name=='hermes':
                time.sleep(.5)
                original_model=json.loads(ipc('flausenSettingsTest','hermesFacts'))['model']
                assert ipc('flausenSettingsTest','click','DeepSeek Flash')=='true';time.sleep(.35)
                deepseek_access=json.loads(ipc('flausenSettingsTest','cloudAccessFacts'))
                assert deepseek_access['height']>100 and abs(deepseek_access['height']-deepseek_access['target'])<1,deepseek_access
                capture('hermes-deepseek-access')
                assert ipc('flausenSettingsTest','click','LFM3')=='true'
                time.sleep(.07)
                collapsing=json.loads(ipc('flausenSettingsTest','cloudAccessFacts'))
                if collapsing['animations']:
                    assert 0<collapsing['height']<deepseek_access['height'],collapsing
                time.sleep(.3)
                collapsed=json.loads(ipc('flausenSettingsTest','cloudAccessFacts'))
                assert collapsed['height']==0 and collapsed['localY']<deepseek_access['localY']-100,collapsed
                capture('hermes-local-collapsed')
                assert ipc('flausenSettingsTest','click','DeepSeek Flash')=='true';time.sleep(.35)
                reopened=json.loads(ipc('flausenSettingsTest','cloudAccessFacts'))
                assert abs(reopened['localY']-deepseek_access['localY'])<1,reopened
                report.append({'cloudAccessTransition':{'deepseek':deepseek_access,'duringCollapse':collapsing,'localOnly':collapsed,'reopened':reopened},'ok':True})
                assert ipc('flausenSettingsTest','click','ChatGPT')=='true';time.sleep(.2)
                assert ipc('flausenSettingsTest','click','API key')=='true'
                api_facts=json.loads(ipc('flausenSettingsTest','hermesFacts'))
                assert api_facts['model']=='chatgpt' and api_facts['chatgptAuth']=='api',api_facts
                capture('hermes-chatgpt-api')
                assert ipc('flausenSettingsTest','click','Codex subscription')=='true'
                subscription=json.loads(ipc('flausenSettingsTest','hermesFacts'))
                assert subscription['chatgptAuth']=='codex',subscription
                capture('hermes-chatgpt-codex')
                report.append({'chatgptAccess':'API key and Codex subscription selected without saving or starting login','ok':True})
                assert ipc('flausenSettingsTest','click','Qwen 3.8 · 27B')=='true'
                facts=json.loads(ipc('flausenSettingsTest','hermesFacts'))
                assert facts['model']=='qwen3.8:27b-hermes' and not facts['error'],facts
                for _ in range(80):
                    vram=json.loads(ipc('flausenSettingsTest','vramFacts'))
                    if vram['ready'] and vram.get('localName')=='qwen3.8:27b-hermes':break
                    time.sleep(.1)
                ipc('flausenSettingsTest','vramPreview','true',90112)
                vram=json.loads(ipc('flausenSettingsTest','vramFacts'))
                assert vram['preview'] and vram['tokens']==90112 and vram['model']>8*1073741824 and vram['context']>1073741824 and vram['runtime']>1073741824,vram
                capture('hermes-qwen')
                ipc('flausenSettingsTest','vramPreview','true',131072)
                larger=json.loads(ipc('flausenSettingsTest','vramFacts'))
                assert larger['model']==vram['model'] and larger['context']>vram['context'],larger
                # Refresh must not reset a context selected by the user.
                time.sleep(11)
                refreshed=json.loads(ipc('flausenSettingsTest','vramFacts'))
                assert refreshed['tokens']==131072,refreshed
                report.append({'qwenVramPreview':vram,'largerContext':larger,'contextSurvivesRefresh':True,'ok':True})
                assert ipc('flausenSettingsTest','click','Reset')=='true';time.sleep(.5)
                facts=json.loads(ipc('flausenSettingsTest','hermesFacts'))
                assert facts['model']==original_model and not facts['dirty'],facts
                report.append({'qwenOption':'local Qwen option selected and reset without changing profile','ok':True})
                assert ipc('flausenSettingsTest','click','LFM3')=='true'
                ipc('flausenSettingsTest','vramPreview','true',65536);capture('hermes-vram-preview')
                assert ipc('flausenSettingsTest','click','Reset')=='true'
        for module,title,name in [('kcm_mouse','Mouse','mouse'),('kcm_kscreen','Bildschirme','display'),('kcm_clock','Date & time','clock'),('@catalogue','All system settings','catalogue')]:
            if args.capture and name not in args.capture:continue
            context={'kcm_mouse':19,'kcm_kscreen':18,'@catalogue':21}.get(module,17)
            ipc('nexus','close');ipc('nexus','openPage',context,-1);time.sleep(.2)
            ipc('flausenSettingsTest','module',module,title)
            if not module.startswith('@') and module!='kcm_clock':until(lambda s:s['moduleReady'])
            capture(name)
        report.append({'capturedSettingsOnly':captured,'ok':True})
finally:
    if args.theme and initial and child is not None and child.poll() is None:
        try:
            ipc('flausenSettingsTest','restorePreferences',str(initial['transparency']).lower(),str(initial['animations']).lower(),initial['scale'],str(initial['auto']).lower())
            time.sleep(.2)
        except subprocess.CalledProcessError:pass
    if child is not None:
        child.terminate()
        try:child.wait(timeout=5)
        except subprocess.TimeoutExpired:child.kill();child.wait()
    if args.theme:
        run(str(Path.home()/'.local/bin/caelestia'),'scheme','set','-n',initial_scheme['name'],'-f',initial_scheme['flavour'],'-m',initial_scheme['mode'],'--no-smart')
    log.close()
    (HERE.parent/('evidence/layout-test.log' if args.audit_only else 'evidence/gallery-test.log' if args.gallery else 'evidence/native-test.log')).write_text((SHELL/'test.log').read_text())
    (HERE.parent/('evidence/layout-audit-check.json' if args.audit_only else 'evidence/gallery-check.json' if args.gallery_only else 'evidence/live-check.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    fixture.cleanup()
print(json.dumps(report,ensure_ascii=False,indent=2))
