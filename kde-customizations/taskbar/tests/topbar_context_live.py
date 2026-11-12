#!/usr/bin/env python3
"""Live Qt mouse-event regression; temporarily adds a local probe, then removes it.

Restarts Caelestia. Run in an idle KDE session with QtTest installed.
No system-wide pointer injection or remote-control permission is used.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time

SOURCE = Path(__file__).resolve().parents[1]
SHELL = Path.home()/'.config/quickshell/caelestia'
WRAPPER = SHELL/'modules/bar/BarWrapper.qml'

def restart():
    subprocess.run(['systemctl','--user','restart','caelestia-shell.service'],check=True)
    time.sleep(3)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screen',default='HDMI-A-2')
    args=parser.parse_args()
    original=WRAPPER.read_text()
    if 'topbarTest-' in original:
        raise SystemExit('A temporary probe already exists; remove it before testing.')
    probe=(SOURCE/'topbar-context/LiveProbe.qml.inc').read_text()
    patched=original.replace('import Quickshell\n','import Quickshell\nimport Quickshell.Io\nimport QtTest\n')
    patched=patched.replace('    // Grab only',probe+'\n    // Grab only')
    assert patched!=original
    prepared=False
    report={}
    def call(method,*values):
        return subprocess.check_output(['quickshell','ipc','-p',str(SHELL),'call',
            'topbarTest-'+args.screen,method,*map(str,values)],text=True)
    def state():return json.loads(call('inspect'))
    def pointer(kind,x,y,button=0):
        call('pointer',kind,x,y,button);time.sleep(.08)
    def menu():
        for _ in range(3):
            call('open');time.sleep(.4)
            s=state()
            if 'rows' in s:return s
        raise AssertionError(s)
    def action(index):
        s=menu();p=s['rows'][index]['point'];pointer('click',p['x'],p['y'],1);time.sleep(.5)
    try:
        WRAPPER.write_text(patched);restart();call('prepare');prepared=True;time.sleep(.8)
        s=state();w=s['screenWidth'];h=s['screenHeight']
        pointer('click',w/2,s['y']+s['height']/2,2);time.sleep(.4)
        report['rightClick']=state();assert report['rightClick']['open']
        s=state();p=s['rows'][2]['point'];pointer('click',p['x'],p['y'],1);time.sleep(.4)
        assert state()['unlocked']
        targets=[('left',(5,h/2)),('right',(w-5,h/2)),('bottom',(w/2,h-5)),('top',(w/2,5))]
        for edge,end in targets:
            s=state();start=(s['x']+s['width']/2,s['y']+s['height']/2)
            pointer('press',*start,1)
            for i in range(1,15):
                pointer('move',start[0]+(end[0]-start[0])*i/14,start[1]+(end[1]-start[1])*i/14,1)
            preview=state();assert preview['moving'] and preview['dropEdge']==edge,preview
            pointer('release',*end,1);time.sleep(.7)
            report[edge]=state();assert report[edge]['position']==edge,report[edge]
        action(2);assert not state()['unlocked']
        s=state();start=(w/2,s['y']+s['height']/2)
        pointer('press',*start,1);pointer('move',5,h/2,1);pointer('release',5,h/2,1)
        assert state()['position']=='top' and not state()['moving']
        report['lockedDrag']=True
        action(3);time.sleep(.8);report['autoHide']=state()
        assert not report['autoHide']['persistent'] and not report['autoHide']['visible']
        s=menu();assert s['rows'][3]['checked'] and s['visible'];report['autoHideMenu']=s
        action(3);assert state()['persistent'];report['autoHideDisabled']=True
        for index,app in [(0,'flausen-task-manager'),(1,'org.quickshell')]:
            before={v['address'] for v in json.loads(call('windows'))}
            action(index);time.sleep(1)
            windows=json.loads(call('windows'))
            found=[v for v in windows if v['class']==app and (index==0 or 'Settings' in v['title'])]
            assert found,(app,windows)
            report['taskManager' if index==0 else 'settings']=[v['title'] for v in found]
            for window in found:
                if window['address'] not in before:call('closeWindow',window['address'])
        report['passed']=True
        print('PASS: right-click, all four drag targets, lock, auto hide, both app actions')
    finally:
        if prepared:call('restore')
        # Do not overwrite a concurrent source change.
        if WRAPPER.read_text()==patched:WRAPPER.write_text(original)
        else:raise RuntimeError('Wrapper changed during the test; remove the probe manually.')
        restart()
        (SOURCE/'evidence/topbar-context-check.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
