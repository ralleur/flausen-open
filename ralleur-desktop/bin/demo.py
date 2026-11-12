#!/usr/bin/env python3
"""Open three REAL apps on a new, explicitly requested demonstration workspace."""
import json
import os
from pathlib import Path
import subprocess
import time

if not os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
    raise SystemExit('Hyprland required.')
root=Path(os.environ['RALLEUR_ROOT'])


def query(name): return json.loads(subprocess.check_output(['hyprctl','-j',name],text=True))
def lua(code): subprocess.run(['hyprctl','eval',code],check=True,stdout=subprocess.DEVNULL)
def dispatch(code): lua('hl.dispatch('+code+')')


workspace='name:ralleur-demo'
if any(w['workspace']['name']=='ralleur-demo' for w in query('clients')):
    raise SystemExit('The demo workspace already contains windows. Move or close those explicitly before starting another demo.')
dispatch('hl.dsp.focus({workspace='+json.dumps(workspace)+'})')
monitor=next(m for m in query('monitors') if m['focused'])
w,h=monitor['width']/monitor['scale'],monitor['height']/monitor['scale']
ox,oy=monitor['x'],monitor['y']
roles=[('browser',['firefox','chromium','zen'],(.067,.067,.625,.52)),('terminal',['kitty','konsole','foot'],(.067,.6,.364,.35)),('files',['dolphin','thunar','nemo'],(.443,.6,.472,.35))]
for role,classes,rect in roles:
    before={c['address'] for c in query('clients')}
    subprocess.Popen([str(root/'bin/ralleur'),'app',role],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    client=None
    for _ in range(100):
        clients=query('clients')
        client=next((c for c in clients if c['address'] not in before and any(k in c['class'].lower() for k in classes)),None)
        if client: break
        time.sleep(.1)
    if not client: raise SystemExit('No new window appeared for '+role+'. Check installed app roles with ralleur-desktop doctor.')
    # No global window rules: only the new demonstration window is arranged.
    target=json.dumps('address:'+client['address'])
    dispatch('hl.dsp.window.move({window='+target+',workspace='+json.dumps(workspace)+'})')
    if w >= 1500:
        x,y,width,height=rect
        dispatch('hl.dsp.window.float({window='+target+',action="set"})')
        dispatch(f'hl.dsp.window.resize({{window={target},x={round(w*width)},y={round(h*height)},relative=false}})')
        dispatch(f'hl.dsp.window.move({{window={target},x={round(ox+w*x)},y={round(oy+h*y)},relative=false}})')
print('Three real app windows on ralleur-demo. Super+V returns a window to tiling; Super+F toggles fullscreen.')
