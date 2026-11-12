import dbus, dbus.service, dbus.mainloop.glib
from gi.repository import GLib
from pathlib import Path
import tempfile, subprocess, json, time

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SessionBus(); bus_name=dbus.service.BusName('org.ralleur.FullscreenVerification',bus)
class Receiver(dbus.service.Object):
    def __init__(self):
        super().__init__(bus,'/Result');self.data=None;self.loop=GLib.MainLoop()
    @dbus.service.method('org.ralleur.FullscreenVerification',in_signature='s',out_signature='')
    def report(self,data):
        self.data=json.loads(data);self.loop.quit()
r=Receiver()
def q(*args):return subprocess.check_output(['qdbus6',*args],text=True).strip()
def report(code):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.js') as f:
        f.write('try { '+code+'\ncallDBus("org.ralleur.FullscreenVerification","/Result","org.ralleur.FullscreenVerification","report",JSON.stringify(result)); } catch(e) { callDBus("org.ralleur.FullscreenVerification","/Result","org.ralleur.FullscreenVerification","report",JSON.stringify({error:String(e)})); }');f.flush()
        key='ralleur-fullscreen-verification'
        sid=q('org.kde.KWin','/Scripting','loadScript',f.name,key)
        try:
            r.data=None
            q('org.kde.KWin','/Scripting/Script'+sid,'run')
            timer=GLib.timeout_add(4000,lambda:(r.loop.quit(),False)[1]);r.loop.run();GLib.source_remove(timer)
            assert r.data is not None,'No reply'
            assert not isinstance(r.data,dict) or 'error' not in r.data,r.data
            return r.data
        finally:q('org.kde.KWin','/Scripting','unloadScript',key)
