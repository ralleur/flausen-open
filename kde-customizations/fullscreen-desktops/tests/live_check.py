#!/usr/bin/env python3
"""Exercise fixed-pool fullscreen routing with real temporary Wayland windows."""
from kwin import report
from pathlib import Path
import json, os, subprocess, tempfile, time

PREFIX='Flausen Fullscreen Verification '
processes=[]
checks=[]
original=report('const result={desktop:workspace.currentDesktop.id,active:workspace.activeWindow?workspace.activeWindow.internalId.toString():null,ids:workspace.desktops.map(d=>d.id)};')
assert len(original['ids'])==4

def state():
    return report('const result={current:workspace.currentDesktop.id,ids:workspace.desktops.map(d=>d.id),windows:workspace.windowList().filter(w=>w.caption.startsWith('+json.dumps(PREFIX)+')).map(w=>({name:w.caption,full:w.fullScreen,desktops:w.desktops.map(d=>d.id)}))};')
def wait(predicate):
    for _ in range(60):
        s=state()
        if predicate(s):return s
        time.sleep(.1)
    raise AssertionError(s)
def window(s,name):return next(w for w in s['windows'] if w['name']==PREFIX+name)
def change(name,code):
    return report('const w=workspace.windowList().find(w=>w.caption==='+json.dumps(PREFIX+name)+');'+code+';const result=true;')
def focus(name,index):
    change(name,'w.desktops=[workspace.desktops['+str(index)+']];workspace.currentDesktop=workspace.desktops['+str(index)+'];workspace.activeWindow=w')
def launch(directory,name,dialog=False,fullscreen=False):
    path=Path(directory)/(name+'.qml')
    path.write_text('import QtQuick\nimport QtQuick.Window\nWindow {visible:true;width:360;height:240;title:'+json.dumps(PREFIX+name)+';color:"#17191D"'+(';visibility:Window.FullScreen' if fullscreen else '')+(';Window {visible:true;flags:Qt.Dialog;width:180;height:120;title:'+json.dumps(PREFIX+name+' Dialog')+'}' if dialog else '')+'}')
    p=subprocess.Popen(['/usr/lib/qt6/bin/qml',str(path)],env={**os.environ,'QT_QPA_PLATFORM':'wayland'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    processes.append(p)
    wait(lambda s:any(w['name']==PREFIX+name for w in s['windows']))
    return p
try:
    with tempfile.TemporaryDirectory() as directory:
        launch(directory,'A');focus('A',0)
        occupancy=report('const result=workspace.desktops.map(d=>workspace.windowList().some(w=>!w.desktopWindow&&!w.dock&&!w.onAllDesktops&&w.desktops.some(x=>x.id===d.id)));')
        free=next((i for i in [1,2,3] if not occupancy[i]),None)
        assert free is not None,'Live free-target check requires an initially free desktop'
        change('A','w.fullScreen=true')
        s=wait(lambda s:window(s,'A')['full'] and window(s,'A')['desktops']==[original['ids'][free]])
        assert s['current']==original['ids'][free] and s['ids']==original['ids']
        change('A','w.fullScreen=false')
        wait(lambda s:window(s,'A')['desktops']==[original['ids'][0]])
        checks.append('Active fullscreen skips occupied desktop(s), follows nearest free target and restores source')

        launch(directory,'Dialog parent',dialog=True);focus('Dialog parent',0)
        change('Dialog parent Dialog','w.desktops=[workspace.desktops[0]]')
        change('Dialog parent','w.fullScreen=true')
        s=wait(lambda s:window(s,'Dialog parent')['desktops']!=[original['ids'][0]])
        assert window(s,'Dialog parent Dialog')['desktops']==window(s,'Dialog parent')['desktops']
        change('Dialog parent','w.fullScreen=false')
        wait(lambda s:window(s,'Dialog parent')['desktops']==[original['ids'][0]] and window(s,'Dialog parent Dialog')['desktops']==[original['ids'][0]])
        checks.append('Transient dialog follows its parent and both restore previous desktop assignments')

        for i in range(4):
            launch(directory,'Blocker'+str(i));change('Blocker'+str(i),'w.desktops=[workspace.desktops['+str(i)+']]')
        for start in [0,3]:
            focus('A',start);change('A','w.fullScreen=true')
            target=original['ids'][(start+1)%4]
            s=wait(lambda s:window(s,'A')['desktops']==[target])
            assert s['current']==target and s['ids']==original['ids']
            assert all(window(s,'Blocker'+str(i))['desktops']==[original['ids'][i]] for i in range(4))
            change('A','w.fullScreen=false');wait(lambda s:window(s,'A')['desktops']==[original['ids'][start]])
        checks.append('All four occupied: next desktop to the right, including 4→1; other windows stay put')

        focus('A',3);change('A','w.fullScreen=true');wait(lambda s:window(s,'A')['desktops']==[original['ids'][0]])
        change('A','w.desktops=[workspace.desktops[1]];w.fullScreen=false')
        assert window(state(),'A')['desktops']==[original['ids'][1]]
        checks.append('Manual move while fullscreen is preserved on exit')

        start=state()['current'];index=original['ids'].index(start)
        b=launch(directory,'Initial fullscreen',fullscreen=True)
        wait(lambda s:window(s,'Initial fullscreen')['desktops']==[original['ids'][(index+1)%4]])
        b.terminate();b.wait();wait(lambda s:not any(w['name']==PREFIX+'Initial fullscreen' for w in s['windows']))
        assert state()['ids']==original['ids']
        checks.append('Initial fullscreen start and closing retain exactly the same four desktops')
finally:
    for p in processes:
        if p.poll() is None:p.terminate();p.wait(timeout=5)
    report('workspace.currentDesktop=workspace.desktops.find(d=>d.id==='+json.dumps(original['desktop'])+');const old=workspace.windowList().find(w=>w.internalId.toString()==='+json.dumps(original['active'])+');if(old)workspace.activeWindow=old;const result=true;')
assert state()['ids']==original['ids']
result={'passed':True,'checks':checks,'desktopCount':4,'originalDesktopRestored':True}
Path(__file__).with_name('live-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
