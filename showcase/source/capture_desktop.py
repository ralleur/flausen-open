#!/usr/bin/env python3
"""Record a real, staged desktop workflow, restoring the user's workspace.

Uses only disposable showcase windows. Never starts a game or reboots the PC.
"""
from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'kde-customizations/fullscreen-desktops/tests'))
from kwin import report
sys.path.insert(0, str(ROOT/'kde-customizations/tiling/tests'))
from input import Input
SHELL = str(Path.home()/'.config/quickshell/caelestia')
OUT = ROOT/'showcase/screenshots'

def ipc(*args):
    return subprocess.check_output(['quickshell','ipc','-p',SHELL,'call',*args],text=True).strip()

def state():
    return report('const result={current:workspace.desktops.indexOf(workspace.currentDesktop),active:workspace.activeWindow?.internalId.toString(),windows:workspace.windowList().filter(w=>!w.desktopWindow&&!w.dock&&!w.onAllDesktops).map(w=>({id:w.internalId.toString(),app:w.resourceClass,desktops:w.desktops.map(d=>workspace.desktops.indexOf(d)),x:w.frameGeometry.x,y:w.frameGeometry.y,width:w.frameGeometry.width,height:w.frameGeometry.height}))};')

def action(window, code):
    return report('const w=workspace.windowList().find(w=>w.internalId.toString()==='+json.dumps(window)+');if(w){'+code+';}const result=true;')

def shot(name):
    subprocess.run(['spectacle','-b','-n','-f','-o',str(OUT/(name+'.png'))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def main():
    initial = state()
    occupied = {d for w in initial['windows'] for d in w['desktops']}
    target = next((d for d in range(4) if d not in occupied and d != initial['current']), None)
    if target is None:
        raise SystemExit('A free workspace is required for a clean recording.')
    original_ids = {w['id'] for w in initial['windows']}
    original_wallpaper = ipc('wallpaper','get')
    original_dnd = ipc('notifs','isDndEnabled') == 'true'
    owned = []
    recorder = None
    sender = None
    env = dict(os.environ,LANG='en_US.UTF-8',LANGUAGE='en_US',LC_MESSAGES='en_US.UTF-8',LC_TIME='en_US.UTF-8')
    env.pop('LC_ALL',None)
    marks = []
    began = time.monotonic()
    def mark(name):
        marks.append(dict(name=name,seconds=round(time.monotonic()-began,3)))
    def launch(command, geometry):
        before = {w['id'] for w in state()['windows']}
        subprocess.Popen(command,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(80):
            new = [w for w in state()['windows'] if w['id'] not in before]
            if new:
                w=new[-1];owned.append(w['id'])
                x,y,width,height=geometry
                action(w['id'],f'w.desktops=[workspace.desktops[{target}]];w.frameGeometry={{x:{x},y:{y},width:{width},height:{height}}};workspace.currentDesktop=workspace.desktops[{target}];workspace.activeWindow=w')
                time.sleep(1)
                return w['id']
            time.sleep(.1)
        raise RuntimeError('No new showcase window appeared.')
    try:
        ipc('notifs','enableDnd')
        report(f'workspace.currentDesktop=workspace.desktops[{target}];const result=true;')
        time.sleep(2)
        shot('desktop-hero')
        recording=ROOT/'.cache/showcase-video/desktop-workflow-raw.mp4'
        recording.parent.mkdir(parents=True,exist_ok=True)
        log=open(ROOT/'showcase/source/recording.log','w')
        recorder=subprocess.Popen(['gpu-screen-recorder','-w','HDMI-A-2','-f','30','-s','1920x1080','-k','h264','-q','high','-cursor','yes','-o',str(recording)],stdout=log,stderr=log)
        began=time.monotonic();mark('A desktop for everyday life');time.sleep(3)
        if recorder.poll() is not None:
            raise RuntimeError('Recorder failed: '+(ROOT/'showcase/source/recording.log').read_text()[-1200:])
        files=launch([str(Path.home()/'.local/bin/dolphin'),'--new-window',str(ROOT/'showcase/demo-workspace')],(280,260,1500,1100))
        mark('Files: a familiar home for your projects');shot('files');time.sleep(4)
        editor=launch(['kate','--new',str(ROOT/'showcase/demo-workspace/creative-notes.txt')],(1900,390,1450,1100))
        mark('Windows stay free until you choose a layout');shot('floating');time.sleep(3)
        settings=launch([str(Path.home()/'.local/bin/flausen-settings')],(1150,650,1380,940))
        mark('One settings window brings the desktop together');time.sleep(4)
        sender=Input()
        for window in [files,editor]:
            current=next((w for w in state()['windows'] if w['id']==window),None)
            if current is None: continue
            action(window,'workspace.activeWindow=w');time.sleep(.25)
            sender.drag((current['x']+130,current['y']+170),(current['x']+200,current['y']+210),shift=True)
            time.sleep(.6)
        mark('Super + Shift + drag: bring windows into tiling');shot('tiling');time.sleep(5)
        current=next((w for w in state()['windows'] if w['id']==editor),None)
        if current is None: raise RuntimeError('The staged editor window disappeared.')
        action(editor,'workspace.activeWindow=w');sender.drag((current['x']+130,current['y']+170),(1650,800))
        mark('Super + drag: return to a floating window');shot('untile');time.sleep(4)
        player=launch(['mpv','--force-window=yes','--keep-open=yes','--loop-file=inf','--no-audio','--title=flausen. Playground',str(ROOT/'showcase/demo-workspace/playground.mp4')],(1400,300,1600,900))
        action(player,'workspace.activeWindow=w;w.fullScreen=true')
        time.sleep(1)
        fullscreen=state()
        routed=next(w for w in fullscreen['windows'] if w['id']==player)
        assert fullscreen['current'] != target and routed['desktops'] != [target], fullscreen
        mark('Fullscreen moves to another workspace - demonstrated with video');shot('fullscreen');time.sleep(4)
        action(player,'w.fullScreen=false');time.sleep(1)
        assert next(w for w in state()['windows'] if w['id']==player)['desktops']==[target]
        action(player,'w.closeWindow()');owned.remove(player)
        report(f'workspace.currentDesktop=workspace.desktops[{target}];const result=true;')
        mark('Leave fullscreen and return to your working layout');time.sleep(4)
    finally:
        if recorder is not None and recorder.poll() is None:
            recorder.send_signal(signal.SIGINT)
            try:recorder.wait(timeout=12)
            except subprocess.TimeoutExpired:recorder.terminate();recorder.wait(timeout=5)
        if sender is not None:sender.close()
        for window in reversed(owned):action(window,'w.closeWindow()')
        ipc('nexus','close')
        report(f'workspace.currentDesktop=workspace.desktops[{initial["current"]}];const result=true;')
        if initial.get('active'):action(initial['active'],'workspace.activeWindow=w')
        if not original_dnd:ipc('notifs','disableDnd')
        (ROOT/'showcase/source/workflow-markers.json').write_text(json.dumps(marks,indent=2)+'\n')
    print('Recorded actual Files, editor, settings and tiling interactions. Workspace restored.')

if __name__=='__main__':main()
