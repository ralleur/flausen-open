#!/usr/bin/env python3
"""Run explicitly inside a Ralleur test session; writes a machine-readable report."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--shell',type=Path,required=True)
p.add_argument('--cli',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--skip-capture',action='store_true',help='Still test fullscreen state and layer removal; record screenshot as not run')
a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
checks=[]


def ipc(target,action,*args):
    return subprocess.check_output(['qs','-p',str(a.shell),'ipc','call',target,action,*map(str,args)],text=True).strip()
def state(): return json.loads(ipc('ralleur','status'))
def query(name): return json.loads(subprocess.check_output(['hyprctl','-j',name],text=True))
def wait(test,seconds=4):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if test(): return
        time.sleep(.1)
    raise AssertionError('Timed out')
def check(name,test):
    try: test(); checks.append({'check':name,'result':'PASS'})
    except Exception as e: checks.append({'check':name,'result':'FAIL','detail':str(e)})
def assert_true(value):
    if not value: raise AssertionError('condition was false')


initial=state()
check('Live CPU/RAM/disk in range',lambda: assert_true(all(0 <= initial[x] <= 100 for x in ('cpu','memory','disk'))))


def workspace():
    ipc('ralleur','workspace',3)
    wait(lambda: state()['workspace']==3)
    ipc('ralleur','workspace',1)
    wait(lambda: state()['workspace']==1)
check('Workspace IPC uses upstream Hypr API',workspace)


def widgets():
    before=state()['widgets']
    ipc('ralleur','widgets'); wait(lambda: state()['widgets'] != before)
    ipc('ralleur','widgets'); wait(lambda: state()['widgets'] == before)
check('Widget toggle roundtrip',widgets)


def themes():
    for mode in ('light','dark'):
        subprocess.run([str(a.cli),'theme',mode],check=True,stdout=subprocess.DEVNULL)
        wait(lambda: state()['theme']==mode)
    subprocess.run([str(a.cli),'theme',initial['theme']],check=True,stdout=subprocess.DEVNULL)
check('Light/Dark roundtrip without shell restart',themes)


def focus():
    clients=query('clients')
    target=next(c for c in clients if c['class']=='kitty')
    ipc('ralleur','focusApp','terminal')
    wait(lambda: query('activewindow').get('address')==target['address'])
    assert_true(len(query('clients'))==len(clients))
check('Dock action focuses existing Kitty without duplicate',focus)


def fullscreen():
    subprocess.run(['hyprctl','eval','hl.dispatch(hl.dsp.window.fullscreen({mode="fullscreen",action="set"}))'],check=True,stdout=subprocess.DEVNULL)
    wait(lambda: any(s['active'] for s in state()['fullscreen']))
    try:
        def hidden():
            layers=query('layers')
            namespaces=[layer['namespace'] for monitor in layers.values() for level in monitor['levels'].values() for layer in level]
            return not any(n in namespaces for n in ('ralleur-top','ralleur-dock','ralleur-widgets'))
        wait(hidden)
        if not a.skip_capture: subprocess.run(['grim',str(a.out/'fullscreen.png')],check=True,timeout=10)
    finally:
        subprocess.run(['hyprctl','eval','hl.dispatch(hl.dsp.window.fullscreen({mode="fullscreen",action="unset"}))'],check=True,stdout=subprocess.DEVNULL)
    wait(lambda: not any(s['active'] for s in state()['fullscreen']))
check('Fullscreen hides own visible surfaces and restores them',fullscreen)
if a.skip_capture: checks.append({'check':'Current fullscreen screenshot','result':'NOT RUN','detail':'Explicit --skip-capture; state/layer checks still executed'})


if initial['player']:
    def media():
        ipc('mpris','pause'); wait(lambda: not state()['playing'])
        ipc('mpris','play'); wait(lambda: state()['playing'])
        if not initial['playing']: ipc('mpris','pause')
    check('Real MPRIS player Pause/Play',media)
else: checks.append({'check':'Real MPRIS player Pause/Play','result':'NOT RUN','detail':'No real player is running'})
report={'checks':checks,'initial':initial,'final':state(),'environment':{'wayland':os.environ.get('WAYLAND_DISPLAY'),'hyprland':subprocess.check_output(['hyprctl','version'],text=True).splitlines()[0]}}
(a.out/'live-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(checks,indent=2))
raise SystemExit(any(c['result']=='FAIL' for c in checks))
