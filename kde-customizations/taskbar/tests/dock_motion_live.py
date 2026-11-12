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

from pathlib import Path
test_file=Path('/tmp/ralleur-dock-verification.txt')
test_file.write_text('Dock verification\n')
config_file=Path.home()/'.config/caelestia/shell.json'
initial_favourites=json.loads(config_file.read_text())['bar']['dock']['pinnedApps']
out={};p=subprocess.Popen(['kate','-n','/tmp/ralleur-dock-verification.txt'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 time.sleep(2);move(1900,1950);s=state();out['before']=s
 a=s['dock']['sections'];src=next(app for app in a['apps'] if not app['pinned'] and app['windows'])
 ox=a['origin']['x'];oy=a['origin']['y'];size=a['itemSize'];start=ox+src['offset']+size/2;dest=ox+3.4*(size+19.2)
 move(start,oy+size/2);button(True)
 for j in range(1,25):move(start+(dest-start)*j/24,oy+size/2)
 out['drag']=state();print('DRAG',out['drag']['dock']['sections']['drag']);shot('dock-motion-drag')
 button(False);time.sleep(.4);out['pinned']=state();print('ORDER',[(app['id'],app['pinned']) for app in out['pinned']['dock']['sections']['apps']])
 # Return the test app to the right; other favourites must retain their order.
 a=out['pinned']['dock']['sections'];src=next(app for app in a['apps'] if app.get('desktopId')=='org.kde.kate');start=a['origin']['x']+src['offset']+size/2;dest=a['separatorPosition']['x']+size/2
 move(1900,1950);time.sleep(.25);move(start,oy+size/2);button(True)
 for j in range(1,25):move(start+(dest-start)*j/24,oy+size/2)
 out['unpinDrag']=state();button(False);time.sleep(.4);out['restored']=state()
 before=[a['desktopId'] for a in out['before']['dock']['sections']['apps'] if a['pinned']]
 pinned=[a['desktopId'] for a in out['pinned']['dock']['sections']['apps'] if a['pinned']]
 restored=[a['desktopId'] for a in out['restored']['dock']['sections']['apps'] if a['pinned']]
 assert pinned[3]=='org.kde.kate',(pinned,3)
 assert restored==before,(restored,before)
 move(1900,1950);move(1865,2115);time.sleep(.2);out['hover']=state();assert out['hover']['dock']['sections']['magnification']['active'];shot('dock-motion-hover')
 move(1865,2070);out['raisedHover']=state();assert out['raisedHover']['dock']['sections']['magnification']['active']
 move(1900,1950);time.sleep(.2);out['leftHover']=state();assert not out['leftHover']['dock']['sections']['magnification']['active'];shot('dock-motion-rest')
 out['passed']=True
finally:
 button(False);p.terminate();p.wait()
 current_config=json.loads(config_file.read_text())
 if current_config['bar']['dock']['pinnedApps'] != initial_favourites:
  current_config['bar']['dock']['pinnedApps']=initial_favourites
  config_file.write_text(json.dumps(current_config,indent=4)+'\n')
 test_file.unlink(missing_ok=True)
 Path('/home/USER/ralleurOS/kde-customizations/taskbar/evidence/dock-motion-check.json').write_text(json.dumps(out,indent=2)+'\n')
