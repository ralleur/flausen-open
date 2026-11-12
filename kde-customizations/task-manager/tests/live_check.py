#!/usr/bin/env python3
"""Isolated real-data QtQuick checks; no signal, autostart or service mutations."""
import json
import os
import re
import psutil
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
EVIDENCE = REPO/'.cache/task-manager-evidence'
EVIDENCE.mkdir(parents=True, exist_ok=True)
SHARED = Path.home()/'.config/quickshell/caelestia'
fixture = tempfile.TemporaryDirectory(prefix='flausen-task-manager-test-')
root = Path(fixture.name)
for name in ('services', 'components', 'modules', 'utils', 'assets', 'translations'):
    (root/name).symlink_to(SHARED/name, target_is_directory=True)
shutil.copytree(HERE/'ui', root/'ui')
shutil.copy2(HERE/'shell.qml', root/'shell.qml')
shutil.copy2(HERE/'backend.py', root/'backend.py')
shutil.copytree(HERE/'locales',root/'locales')
locale_config=root/'plasma-localerc'
locale_config.write_text('[Translations]\nLANGUAGE=en_US\n')
helper=(HERE/'i18n.py').read_text()
helper=re.sub(r'^CONFIG_PATH = .+$','CONFIG_PATH = Path('+repr(str(locale_config))+')',helper,flags=re.M)
(root/'i18n.py').write_text(helper)
shutil.copy2(HERE/'icon.png', root/'icon.png')
qml = root/'ui/TaskManager.qml'
text = qml.read_text().replace('import QtQuick\n', 'import QtQuick\nimport QtTest as VisualTest\n')
text = text.replace('    property bool initialSizeApplied: false', '    property bool initialSizeApplied: false\n    property int testExtraDisks: 0\n    property bool testResizePending: false\n    property var testGraphReference: null')
text = text.replace('const data=JSON.parse(line);', '''const data=JSON.parse(line);
                    if(data.type==='snapshot' && win.testExtraDisks>0){
                        const disk=data.cards.find(c=>c.kind==='disk');
                        for(let i=0;i<win.testExtraDisks;i++)data.cards.splice(data.cards.length-1,0,Object.assign({},disk,{id:'fixture-disk-'+i,name:'Datenträger · Test '+(i+1),device:'Testlaufwerk '+(i+1)+' · 2 TB'}));
                    }
                    if(data.type==='snapshot' && win.testResizePending){win.initialSizeApplied=false;win.testResizePending=false;}''')
text = text.rsplit('}', 1)[0]+'''
    VisualTest.TestCase {id: captureTest; name: "TaskManagerCapture"; when:false}
    IpcHandler {
        target: "test"
        function inspect(): string {
            let bars=[],histories=[],nativeGraphs=[],texts=[],windowControls=[];
            function find(item){if(item.visible && item.controlAction!==undefined)windowControls.push(item.controlAction);if(item.visible && typeof item.text==='string')texts.push(item.text);if(item.toString().includes('SparklineItem')&&item.visible)nativeGraphs.push({phase:item.slideProgress,count:item.line1?.count??0});if(item.objectName.startsWith('performanceProcessors-')&&item.visible)bars.push({id:item.objectName,count:item.units.length,historyMode:item.historyMode,historyLengths:item.units.map(u=>(u.history??[]).length)});if(item.objectName.startsWith('performanceHistory-')&&item.visible)histories.push(item.objectName);for(const child of item.children??[])find(child);}
            find(frame);
            return JSON.stringify({connected:win.connected,count:processList.count,all:win.snapshot.count,
            windowControls:windowControls,language:win.uiLanguage,texts:texts,title:win.title,graphPhase:graphTimeline.slideProgress,graphRevision:graphTimeline.sampleRevision,graphAnimating:graphTimeline.animating,graphInterval:graphTimeline.interval,graphSameSeries:win.testGraphReference===graphTimeline.streams['cpu'],nativeGraphs:nativeGraphs,processorBars:bars,visibleHistories:histories,backgroundExpanded:win.backgroundExpanded,backgroundRows:win.rows().filter(p=>!p.heading&&!p.application).length,appId:Quickshell.appId,logoReady:appLogo.status===Image.Ready,
            cards:win.snapshot.cards.length,detail:win.detail,search:search.text,page:win.page,message:win.message,
            rows:win.rows().filter(p=>!p.heading).map(p=>({pid:p.pid,name:p.name,cpu:p.cpu,child:p.child})),
            cardDevices:win.snapshot.cards.map(c=>c.device),resourceColumns:resourceGrid.columns,
            performanceContentHeight:performanceView.contentHeight,performanceViewportHeight:performanceView.availableHeight,
            services:win.serviceRows.length,startup:win.startupRows.length,width:win.width,height:win.height,screenHeight:win.screen?.height,initialSizeApplied:win.initialSizeApplied,
            frameless:!!(win.contentItem.Window.window.flags & Qt.FramelessWindowHint)});}
        function toggleProcessor(id:string): bool {function find(item){if(item.objectName==='processorMode-'+id)return item;for(const child of item.children??[]){const result=find(child);if(result)return result;}return null;}const button=find(frame);if(!button)return false;captureTest.mouseClick(button,button.width/2,button.height/2);return true;}
        function closeByButton(): void {Qt.callLater(()=>captureTest.mouseClick(closeButton,closeButton.width/2,closeButton.height/2));}
        function rememberGraph(): void {win.testGraphReference=graphTimeline.streams['cpu'];}
        function refresh(seconds:real): void {win.refreshSeconds=seconds;win.send({action:'interval',value:seconds});}
        function toggleBackground(): void {const index=win.rows().findIndex(p=>p.heading);const item=processList.itemAtIndex(index);if(item)captureTest.mouseClick(item,item.width/2,item.height/2);}
        function disks(count:int): void {win.testExtraDisks=count;win.testResizePending=true;}
        function choose(): void {const rows=win.rows().filter(p=>p.own&&!p.heading);win.select(rows.find(p=>p.children.length>0)??rows[0]);}
        function query(value:string): void {search.text=value;}
        function sort(): void {win.sortKey='name';win.descending=false;}
        function page(value:string): void {win.changePage(value);}
        function expand(): void {let state={};if(win.selected)state[win.selected.pid]=true;win.expanded=state;}
        function extra(value:string): void {win.selectExtra(value);}
        function resize(width:int,height:int): void {win.contentItem.Window.window.width=width;win.contentItem.Window.window.height=height;}
        function light(value:bool): void {Colours.currentLight=value;}
        function capture(path:string): bool {captureTest.grabImage(frame).save(path);return true;}
    }
}
'''
qml.write_text(text)
runtime = root/'runtime'
runtime.mkdir(mode=0o700)
actual_runtime = os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}')
wayland = os.environ.get('WAYLAND_DISPLAY', 'wayland-1')
env = dict(os.environ, FLAUSEN_SESSION_RUNTIME=actual_runtime, XDG_RUNTIME_DIR=str(runtime), WAYLAND_DISPLAY=wayland if wayland.startswith('/') else actual_runtime+'/'+wayland,
           DBUS_SESSION_BUS_ADDRESS=os.environ.get('DBUS_SESSION_BUS_ADDRESS', 'unix:path='+actual_runtime+'/bus'),
           QML2_IMPORT_PATH=str(Path.home()/'.local/lib/qt6/qml'), CAELESTIA_LIB_DIR=str(Path.home()/'.local/lib/caelestia'),
           CAELESTIA_BIN_DIR=str(Path.home()/'.local/bin'), QS_DISABLE_CRASH_HANDLER='1', QS_APP_ID='flausen-task-manager')
log = (EVIDENCE/'live.log').open('w')
process = subprocess.Popen(['quickshell', '-p', str(root), '--no-color'], env=env, stdout=log, stderr=log)


def ipc(function, *args):
    return subprocess.check_output(['quickshell', 'ipc', '-p', str(root), 'call', 'test', function, *map(str, args)], env=env, text=True, stderr=subprocess.DEVNULL).strip()


def state():
    return json.loads(ipc('inspect'))


def until(predicate):
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError((EVIDENCE/'live.log').read_text())
        try:
            current = state()
            if predicate(current):
                return current
        except subprocess.CalledProcessError:
            pass
        time.sleep(.1)
    raise AssertionError('Timed out: '+str({k:v for k,v in current.items() if k not in ('rows','detail')} if 'current' in locals() else 'startup'))


def capture(name):
    time.sleep(.25)
    assert ipc('capture', str(EVIDENCE/(name+'.png'))) == 'true'


try:
    current = until(lambda s:s['connected'] and s['cards']>=5 and s['all']>10 and s['count']>0)
    assert current['frameless']
    assert current['windowControls']==['close']
    assert current['appId']=='flausen-task-manager'
    assert current['logoReady']
    assert current['language']=='en'
    assert 'Processes' in current['texts'] and 'Task Manager' in current['texts']
    assert all('nicht auslesbar' not in device for device in current['cardDevices'])
    assert not current['backgroundExpanded'] and current['backgroundRows']==0
    capture('background-collapsed')
    ipc('toggleBackground')
    until(lambda s:s['backgroundExpanded'] and s['backgroundRows']>0)
    capture('background-expanded')
    ipc('toggleBackground')
    until(lambda s:not s['backgroundExpanded'] and s['backgroundRows']==0)
    ipc('choose')
    current = until(lambda s:s['detail'] and not s['detail'].get('exited'))
    selected = current['detail']['pid']
    until(lambda s:len(s['detail']['cpuHistory'])>=3)
    capture('processes-dark')
    ipc('expand')
    until(lambda s:any(r['child'] for r in s['rows']))
    capture('expanded')
    ipc('query', 'this-query-matches-no-process-887311')
    until(lambda s:s['count']==0)
    capture('empty-search')
    ipc('query', '')
    ipc('sort')
    until(lambda s:s['all']>10 and s['count']>0)
    ipc('extra', 'files')
    until(lambda s:s['detail'] and 'files' in s['detail'])
    capture('open-files')
    ipc('extra', 'connections')
    until(lambda s:s['detail'] and 'connections' in s['detail'])
    capture('connections')
    for page in ('performance', 'startup', 'services'):
        ipc('page', page)
        until(lambda s:s['page']==page and (page=='performance' or s['startup' if page=='startup' else 'services']>0))
        if page=='performance':
            until(lambda s:s['performanceContentHeight']<=s['performanceViewportHeight']+1 and len(s['processorBars'])>=2)
            chart_state=state()
            assert any(bar['id']=='performanceProcessors-cpu' and bar['count']>0 for bar in chart_state['processorBars'])
            assert not any(name.startswith(('performanceHistory-cpu','performanceHistory-gpu:')) for name in chart_state['visibleHistories'])
        capture({'performance':'performance','startup':'startup','services':'services'}[page])
    ipc('page', 'performance')
    until(lambda s:len(s['processorBars'])>=2)
    chart_state=state()
    assert all(b['historyMode'] for b in chart_state['processorBars'])
    assert ipc('toggleProcessor','cpu')=='true'
    until(lambda s:not next(b for b in s['processorBars'] if b['id']=='performanceProcessors-cpu')['historyMode'])
    time.sleep(1.2)
    chart_state=state()
    assert not next(b for b in chart_state['processorBars'] if b['id']=='performanceProcessors-cpu')['historyMode']
    assert all(b['historyMode'] for b in chart_state['processorBars'] if b['id']!='performanceProcessors-cpu')
    assert all(length>=2 for b in chart_state['processorBars'] for length in b['historyLengths'])
    assert ipc('toggleProcessor','cpu')=='true'
    until(lambda s:all(b['historyMode'] for b in s['processorBars']))
    capture('cpu-unit-histories')
    gpu_id=next(b['id'].replace('performanceProcessors-','') for b in chart_state['processorBars'] if b['id'].startswith('performanceProcessors-gpu:'))
    assert ipc('toggleProcessor',gpu_id)=='true'
    until(lambda s:not next(b for b in s['processorBars'] if b['id']=='performanceProcessors-'+gpu_id)['historyMode'])
    assert next(b for b in state()['processorBars'] if b['id']=='performanceProcessors-cpu')['historyMode']
    assert ipc('toggleProcessor',gpu_id)=='true'
    until(lambda s:all(b['historyMode'] for b in s['processorBars']))
    capture('cpu-gpu-unit-histories')
    ipc('rememberGraph')
    prior=state()
    until(lambda s:s['graphRevision']>prior['graphRevision'])
    assert state()['graphSameSeries']
    # Rendering must advance between samples, not only on the backend's 1 Hz ticks.
    previous=state()
    interpolated=False
    for _ in range(20):
        time.sleep(.04)
        current_graph=state()
        if current_graph['graphRevision']==previous['graphRevision'] and current_graph['graphPhase']>previous['graphPhase']+.005:
            assert current_graph['nativeGraphs'] and all(abs(g['phase']-current_graph['graphPhase'])<.001 for g in current_graph['nativeGraphs'])
            interpolated=True
            break
        previous=current_graph
    assert interpolated, 'Native graphs did not advance between samples'
    for seconds in (.5,2,1):
        revision=state()['graphRevision']
        ipc('refresh',seconds)
        until(lambda s:s['graphRevision']>revision and s['graphInterval']==seconds*1000)
        assert state()['graphSameSeries']

    assert ipc('toggleProcessor','cpu')=='true'
    until(lambda s:not next(b for b in s['processorBars'] if b['id']=='performanceProcessors-cpu')['historyMode'])
    assert next(b for b in state()['processorBars'] if b['id']=='performanceProcessors-'+gpu_id)['historyMode']
    assert ipc('toggleProcessor',gpu_id)=='true'
    until(lambda s:not next(b for b in s['processorBars'] if b['id']=='performanceProcessors-'+gpu_id)['historyMode'])
    for id in ('cpu',gpu_id):
        ipc('toggleProcessor',id)
    until(lambda s:all(b['historyMode'] for b in s['processorBars']))
    ipc('page', 'performance')
    base_cards=state()['cards']
    ipc('disks', 2)
    until(lambda s:s['cards']==base_cards+2 and s['performanceContentHeight']<=s['performanceViewportHeight']+1)
    capture('multiple-disks')
    assert state()['resourceColumns']<state()['cards']
    ipc('disks', 0)
    until(lambda s:s['cards']==base_cards)
    # Change only the isolated KDE language file; production preferences stay untouched.
    locale_config.write_text('[Translations]\nLANGUAGE=de_DE\n')
    until(lambda s:s['language']=='de' and 'Leistung' in s['texts'] and any('Kern 1'==text for text in s['texts']))
    assert state()['page']=='performance'
    assert all(b['historyMode'] for b in state()['processorBars'])
    capture('performance-german')
    locale_config.write_text('[Translations]\nLANGUAGE=en_US\n')
    until(lambda s:s['language']=='en' and 'Performance' in s['texts'] and 'Core 1' in s['texts'])
    capture('performance-english')
    ipc('page', 'processes')
    ipc('resize', 1140, 700)
    until(lambda s:s['width']==1140)
    capture('minimum-size')
    ipc('resize', 1410, 866)
    ipc('light', 'true')
    capture('processes-light')
    ipc('light', 'false')
    capture('processes-final')
    children=psutil.Process(process.pid).children(recursive=True)
    backend_children=[]
    for child in children:
        try:
            if any('backend.py' in arg for arg in child.cmdline()):backend_children.append(child)
        except psutil.NoSuchProcess:
            pass
    assert backend_children, 'Telemetry process missing before close test'
    ipc('closeByButton')
    assert process.wait(timeout=5)==0, 'Close button did not exit the application cleanly'
    for _ in range(30):
        if all(not child.is_running() for child in backend_children):
            break
        time.sleep(.1)
    assert all(not child.is_running() for child in backend_children), 'Close button left telemetry running'
    # Logs from Qt are checked after the complete set of real views has rendered.
    log.flush()
    errors = [line for line in (EVIDENCE/'live.log').read_text().splitlines() if any(word in line for word in (' ERROR:', 'TypeError', 'ReferenceError', 'Binding loop', 'Unable to assign', 'Cannot assign', 'failed to load'))]
    assert not errors, '\n'.join(errors)
    result = dict(result='passed', count=current['all'], selectedPid=selected, captures=18,
                  checks=['close button exits application and backend','only close control remains','history is default','system language English/German switches live','locale-independent navigation','native graphs advance between samples','stable graph buffers','0.5/1/2 second graph intervals','independent CPU/GPU history toggles','per-unit histories survive refresh','CPU/GPU segmented meters','CPU/GPU curves removed','hardware labels without unavailable text','multiple disk layout fits','logo ready','app ID','background collapsed by default','background mouse toggle','real telemetry','frameless window','selection','bounded histories','group expansion','empty search','sort','files','connections','four tabs','performance fits initial window','minimum width','light/dark','runtime log'])
    (EVIDENCE/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
finally:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    log.close()
    fixture.cleanup()
