#!/usr/bin/env python3
"""Verify preview order and actual rendered icon positions through pin/reorder/unpin.

Moves the pointer on the 3840x2160 HDMI-A-2 desktop. Run only in an idle session.
"""
from pathlib import Path
import json,time
#!/usr/bin/env python3
"""Live regression for this 3840×2160 HDMI-A-2 desktop. Moves the pointer and opens a temporary Kate window; run only in an idle desktop session."""
import ctypes,time,subprocess,json
x=ctypes.CDLL('libX11.so.6');t=ctypes.CDLL('libXtst.so.6');x.XOpenDisplay.restype=ctypes.c_void_p;d=x.XOpenDisplay(None)
t.XTestFakeMotionEvent.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ulong]
t.XTestFakeButtonEvent.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_int,ctypes.c_ulong];x.XFlush.argtypes=[ctypes.c_void_p]
def move(a,b):
 t.XTestFakeMotionEvent(d,-1,int(a),int(b),0);x.XFlush(d);time.sleep(.12)
def button(down):
 t.XTestFakeButtonEvent(d,1,int(down),0);x.XFlush(d);time.sleep(.15)
def state():
 return json.loads(subprocess.check_output(['quickshell','ipc','-p','/home/USER/.config/quickshell/caelestia','call','ralleurTaskbar-HDMI-A-2','inspect'],text=True))
def shot(name):
 subprocess.run(['spectacle','-b','-n','-f','-o','/tmp/'+name+'.png'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 from PIL import Image
 im=Image.open('/tmp/'+name+'.png');im.crop((1150,1970,2700,2160)).save('/tmp/'+name+'-crop.png')


config=Path.home()/'.config/caelestia/shell.json';initial=json.loads(config.read_text())['bar']['dock']['pinnedApps'];report={}
source_id='org.quickshell'
def leave():
 move(1900,1900);time.sleep(.5)
def apps():return state()['dock']['sections']['apps']
def geometry(label):
 leave();a=state()['dock']['sections'];errors=[]
 for i,app in enumerate(a['apps']):
  expected=a['origin']['x']+app['offset']+a['itemSize']/2
  if abs(app['actualCenter']['x']-expected)>.75:errors.append((app['id'],app['actualCenter']['x'],expected,app['iconInset']))
 report[label+'GeometryErrors']=errors;assert not errors,errors
 return a

def drag(label,destination,grip=.5):
 leave();a=state()['dock']['sections'];source=next(v for v in a['apps'] if v['id']==source_id)
 for _ in range(4):
  center=source['actualCenter'];move(center['x']+(grip-.5)*a['itemSize'],center['y']);source=next(v for v in apps() if v['id']==source_id)
 button(True);assert state()['dock']['sections']['drag']['active'],label
 # Use a stable global pointer destination; source geometry may animate on press.
 start=source['actualCenter']['x'];y=a['origin']['y']+a['itemSize']/2;end=destination(a)
 for j in range(1,25):move(start+(end-start)*j/24,y)
 preview=state()['dock']['sections']['drag'];assert preview['preview'],preview
 report[label+'Preview']=preview
 button(False);result=geometry(label);report[label+'Result']=result['apps']
 assert [app['id'] for app in result['apps']]==preview['preview'],(label,preview,result['apps'])
try:
 geometry('initial')
 drag('pin',lambda a:a['origin']['x']+8*83.2+32,.3)
 drag('reorder',lambda a:a['origin']['x']+3*83.2+32,.7)
 drag('unpin',lambda a:a['separatorPosition']['x']+32,.3)
 assert json.loads(config.read_text())['bar']['dock']['pinnedApps']==initial
 report['passed']=True
 print(json.dumps({k:v for k,v in report.items() if 'Errors' in k or k=='passed'}))
finally:
 button(False);leave();c=json.loads(config.read_text())
 if c['bar']['dock']['pinnedApps']!=initial:
  c['bar']['dock']['pinnedApps']=initial;config.write_text(json.dumps(c,indent=4)+'\n')
 Path('/home/USER/ralleurOS/kde-customizations/taskbar/evidence/dock-drop-position-check.json').write_text(json.dumps(report,indent=2)+'\n')
