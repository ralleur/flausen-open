#!/usr/bin/env python3
"""Exercise actual modifier/button gestures against temporary Wayland windows."""
import dbus, dbus.service, dbus.mainloop.glib
from gi.repository import GLib
from pathlib import Path
import tempfile, subprocess, json, time
from input import Input
from probe import OutlineProbe

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SessionBus(); bus_name=dbus.service.BusName('org.ralleur.TilingVerification',bus)
class Receiver(dbus.service.Object):
    def __init__(self):
        super().__init__(bus,'/Result');self.data=None;self.loop=GLib.MainLoop()
    @dbus.service.method('org.ralleur.TilingVerification',in_signature='s',out_signature='')
    def report(self,data):
        self.data=json.loads(data);self.loop.quit()
r=Receiver()
def q(*args):return subprocess.check_output(['qdbus6',*args],text=True).strip()
def report(code):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.js') as f:
        f.write('try { '+code+'\ncallDBus("org.ralleur.TilingVerification","/Result","org.ralleur.TilingVerification","report",JSON.stringify(result)); } catch(e) { callDBus("org.ralleur.TilingVerification","/Result","org.ralleur.TilingVerification","report",JSON.stringify({error:String(e)})); }');f.flush()
        key='ralleur-tiling-verification'
        sid=q('org.kde.KWin','/Scripting','loadScript',f.name,key)
        try:
            r.data=None
            q('org.kde.KWin','/Scripting/Script'+sid,'run')
            timer=GLib.timeout_add(4000,lambda:(r.loop.quit(),False)[1]);r.loop.run();GLib.source_remove(timer)
            assert r.data is not None,'No reply'
            assert not isinstance(r.data,dict) or 'error' not in r.data,r.data
            return r.data
        finally:q('org.kde.KWin','/Scripting','unloadScript',key)
def windows():
    return report('const result=workspace.windowList().filter(w=>w.caption.startsWith("Ralleur Tiling Test ")).map(w=>({name:w.caption.slice(-1),x:w.frameGeometry.x,y:w.frameGeometry.y,width:w.frameGeometry.width,height:w.frameGeometry.height,tile:w.tile!==null}));')
def snapshot(label):
    time.sleep(.3);v={w['name']:w for w in windows()};results[label]=v;return v
def center(w):return (w['x']+w['width']/2,w['y']+w['height']/2)
def same(a,b):return all(abs(a[k]-b[k])<4 for k in ('x','y','width','height'))
results={};procs=[];sender=None;old=None;temp=None;probe=None
try:
    probe=OutlineProbe()
    old=report('const result=workspace.currentDesktop.id;')
    temp=report('workspace.createDesktop(workspace.desktops.length,"Ralleur Tiling Verification");workspace.currentDesktop=workspace.desktops[workspace.desktops.length-1];const result=workspace.currentDesktop.id;')
    time.sleep(.3)
    with tempfile.TemporaryDirectory() as directory:
        for index in range(3):
            name=chr(65+index);f=Path(directory)/(name+'.qml')
            f.write_text('import QtQuick\nimport QtQuick.Window\nWindow { visible:true; x:'+str(200+index*720)+';y:300;width:600;height:400;title:"Ralleur Tiling Test '+name+'";color:"#304050";Text {anchors.centerIn:parent;text:"Tiling-Test '+name+'";color:"white";font.pixelSize:32}}')
            procs.append(subprocess.Popen(['/usr/lib/qt6/bin/qml',str(f)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL))
        time.sleep(.8);v=snapshot('initial_floating');assert len(v)==3,v
        assert all(w['width']<700 and w['height']<500 for w in v.values()),v
        sender=Input()
        sender.on_drag_step=probe.check
        # Shift alone on a titlebar must neither preview nor assign a native tile.
        report('const w=workspace.windowList().find(w=>w.caption==="Ralleur Tiling Test C");workspace.activeWindow=w;workspace.raiseWindow(w);const result=true;')
        c=v['C']
        sender.drag((c['x']+200,c['y']+12),(800,500),shift=True,meta=False)
        v=snapshot('shift_only_floating')
        assert not v['C']['tile'] and abs(v['C']['width']-c['width'])<1 and abs(v['C']['height']-c['height'])<1,v
        results['initial_floating']=v
        # Raise only our test window, then drag within its body.
        def drag(name,end,shift=False,right=False,late_shift=False):
            report('workspace.activeWindow=workspace.windowList().find(w=>w.caption==="Ralleur Tiling Test '+name+'");workspace.raiseWindow(workspace.activeWindow);const result=true;')
            time.sleep(.15);w={w['name']:w for w in windows()}[name]
            start=(w['x']+40,w['y']+200) if right else center(w)
            sender.drag(start,end,shift,right,late_shift)
            if shift:
                title='Ralleur Tiling Test '+name
                assert title in probe.previews, ('Missing target indicator for '+name,dict(probe.api.inspect()))
                expected=probe.previews[title]
                actual={w['name']:w for w in windows()}[name]
                assert same(expected,actual), {'preview':expected,'actual':actual}
                assert not probe.api.inspect().get('previewVisible'), 'Indicator did not hide after drop'
        drag('A',(600,650),shift=True)
        v=snapshot('first_tiled');assert v['A']['width']>2500,v
        assert same(v['B'],results['initial_floating']['B']) and same(v['C'],results['initial_floating']['C']),v
        drag('B',(2900,700),shift=True)
        v=snapshot('two_tiled');assert v['A']['width']>1000 and v['B']['width']>1000,v
        assert v['A']['width']<2500 and same(v['C'],results['initial_floating']['C']),v
        drag('A',center(v['B']),shift=True)
        v=snapshot('swapped');assert abs(v['A']['x']-results['two_tiled']['B']['x'])<4,v
        a=v['A'];start=(a['x']+40,a['y']+200)
        drag('A',(start[0]+250,start[1]),right=True)
        v=snapshot('resized');assert abs(v['A']['width']-a['width'])>100,v
        assert not same(v['B'],results['swapped']['B']),v
        # A third opted-in window creates a nested split.
        drag('C',(2800,1400),shift=True)
        v=snapshot('three_tiled');assert v['C']['width']>700 or v['C']['height']>600,v
        # A fourth enrolled window must produce all four quarters.
        f=Path(directory)/'D.qml'
        f.write_text('import QtQuick\nimport QtQuick.Window\nWindow { visible:true;width:600;height:400;title:"Ralleur Tiling Test D";color:"#405030" }')
        procs.append(subprocess.Popen(['/usr/lib/qt6/bin/qml',str(f)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL))
        time.sleep(.6)
        drag('D',(1000,1500),shift=True,late_shift=True)
        v=snapshot('four_quarters')
        assert len(v)==4,v
        assert len({(w['x']>1920,w['y']>1000) for w in v.values()})==4,v
        assert all(1000<w['width']<2500 and 700<w['height']<1400 for w in v.values()),v
        procs[3].terminate();procs[3].wait();time.sleep(.3)
        drag('C',(1800,900))
        v=snapshot('detached');assert same(v['A'],results['resized']['A']) and same(v['B'],results['resized']['B']),v
        original=results['initial_floating']['C']
        assert abs(v['C']['width']-original['width'])<2 and abs(v['C']['height']-original['height'])<2,v
        assert any(abs(w-original['width'])<2 and abs(h-original['height'])<2 for w,h in probe.restored_sizes),probe.restored_sizes
        # Closing an enrolled window lets the remaining tile occupy the area.
        procs[1].terminate();procs[1].wait();v=snapshot('closed_tile')
        assert v['A']['width']>2500,v
        assert probe.samples>20,probe.samples
        results['shift_drag_samples_without_native_grid']=probe.samples
        results['preview_targets_matched_drops']=len(probe.previews)
        results['floating_size_restored_during_drag']=True
        results['passed']=True
finally:
    if sender:sender.close()
    for proc in procs:
        if proc.poll() is None:proc.terminate();proc.wait()
    if old:report('workspace.currentDesktop=workspace.desktops.find(d=>d.id==='+json.dumps(old)+');const result=true;')
    if temp:report('workspace.removeDesktop(workspace.desktops.find(d=>d.id==='+json.dumps(temp)+'));const result=true;')
    if probe:probe.close()
    out=Path(__file__).with_name('live-result.json');out.write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
