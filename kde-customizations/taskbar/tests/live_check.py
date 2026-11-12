#!/usr/bin/env python3
"""Exercise a temporary Qt window against the running Caelestia/KWin session."""
import dbus, dbus.service, dbus.mainloop.glib
from gi.repository import GLib
from pathlib import Path
import argparse, tempfile, subprocess, json, time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--shell',type=Path,default=Path.home()/'.config/quickshell/caelestia')
parser.add_argument('--screen',required=True)
parser.add_argument('--out',required=True,type=Path)
args=parser.parse_args()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SessionBus(); name=dbus.service.BusName('org.ralleur.TaskbarVerification',bus)
class Receiver(dbus.service.Object):
 def __init__(self):
  super().__init__(bus,'/Result');self.data=None;self.loop=GLib.MainLoop()
 @dbus.service.method('org.ralleur.TaskbarVerification',in_signature='s',out_signature='')
 def report(self,data):
  self.data=json.loads(data);self.loop.quit()
r=Receiver()
def kwin(code):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.js') as f:
  f.write(code);f.flush()
  def q(*args):return subprocess.check_output(['qdbus6',*args],text=True).strip()
  key='ralleur-taskbar-verification'
  id=q('org.kde.KWin','/Scripting','loadScript',f.name,key)
  try:
   r.data=None
   q('org.kde.KWin','/Scripting/Script'+id,'run')
   timeout=GLib.timeout_add(3000,lambda:(r.loop.quit(),False)[1]);r.loop.run();GLib.source_remove(timeout)
   assert r.data is not None
   return r.data
  finally:q('org.kde.KWin','/Scripting','unloadScript',key)
def report(code):return kwin(code+'\ncallDBus("org.ralleur.TaskbarVerification","/Result","org.ralleur.TaskbarVerification","report", JSON.stringify(result));')
def state():return json.loads(subprocess.check_output(['quickshell','ipc','-p',str(args.shell),'call','ralleurTaskbar-'+args.screen,'inspect'],text=True))
p=subprocess.Popen(['/usr/lib/qt6/bin/qml',str(Path(__file__).with_name('window.qml'))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
lookup='const w=workspace.windowList().find(w=>w.caption==="Ralleur Taskbar Verification"); if(!w) throw "missing test window";'
results={}
try:
 time.sleep(1)
 results['normal']=state()
 results['maximize_request']=report(lookup+'w.setMaximize(true,true); const result={id:String(w.internalId)};')
 time.sleep(.5)
 results['maximized']=report(lookup+'const result={geometry:w.frameGeometry,area:workspace.clientArea(KWin.MaximizeArea,w.output,w.desktops[0])};')
 a=results['maximized']['geometry'];s=results['normal']
 assert a['y']>=s['top']['height'],a
 assert a['y']+a['height']<=s['dock']['y'],a
 report(lookup+'w.fullScreen=true;workspace.activeWindow=w; const result=true;')
 time.sleep(.6)
 results['fullscreen']=state()
 assert results['fullscreen']['fullscreen'] is True,results['fullscreen']
 assert results['fullscreen']['dock']['visible'] is False
 assert results['fullscreen']['top']['height']==0
 report(lookup+'w.fullScreen=false;const result=true;')
 time.sleep(.6)
 results['restored']=state()
 assert results['restored']['dock']['visible'] is True
 results['passed']=True
finally:
 p.terminate();p.wait()
 args.out.write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({k:results[k] for k in ['maximized','passed']}))
