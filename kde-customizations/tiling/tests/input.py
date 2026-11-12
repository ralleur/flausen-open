"""Small libei sender for real KWin gesture verification (Wayland)."""
import ctypes as C
import dbus
import time

class Input:
    def __init__(self):
        self.lib=C.CDLL('libei.so.1')
        P=C.c_void_p; I=C.c_int; U=C.c_uint32; D=C.c_double
        signatures={
          'ei_new_sender':(P,[P]),'ei_configure_name':(None,[P,C.c_char_p]),
          'ei_setup_backend_fd':(I,[P,I]),'ei_dispatch':(I,[P]),'ei_get_event':(P,[P]),
          'ei_event_get_type':(I,[P]),'ei_event_get_seat':(P,[P]),'ei_event_get_device':(P,[P]),
          'ei_event_unref':(P,[P]),'ei_device_ref':(P,[P]),'ei_device_unref':(P,[P]),
          'ei_device_has_capability':(C.c_bool,[P,I]),'ei_device_start_emulating':(None,[P,U]),
          'ei_device_frame':(None,[P,C.c_uint64]),'ei_device_keyboard_key':(None,[P,U,C.c_bool]),
          'ei_device_button_button':(None,[P,U,C.c_bool]),
          'ei_device_pointer_motion_absolute':(None,[P,D,D]),'ei_unref':(P,[P]),
        }
        for name,(ret,args) in signatures.items():
            f=getattr(self.lib,name);f.restype=ret;f.argtypes=args
        self.lib.ei_seat_bind_capabilities.argtypes=[P]
        bus=dbus.SessionBus()
        obj=bus.get_object('org.kde.KWin','/org/kde/KWin/EIS/RemoteDesktop')
        self.remote=dbus.Interface(obj,'org.kde.KWin.EIS.RemoteDesktop')
        fd,self.cookie=self.remote.connectToEIS(1|2|4)
        self.ei=self.lib.ei_new_sender(None)
        self.lib.ei_configure_name(self.ei,b'Ralleur tiling gesture verification')
        assert self.lib.ei_setup_backend_fd(self.ei,fd.take())==0
        self.devices={}
        deadline=time.monotonic()+3
        while time.monotonic()<deadline and not all(c in self.devices for c in (2,4,32)):
            self.lib.ei_dispatch(self.ei)
            while event:=self.lib.ei_get_event(self.ei):
                kind=self.lib.ei_event_get_type(event)
                if kind==3:
                    self.lib.ei_seat_bind_capabilities(self.lib.ei_event_get_seat(event),I(1),I(2),I(4),I(32),I(0))
                if kind==8:
                    device=self.lib.ei_event_get_device(event)
                    self.lib.ei_device_start_emulating(device,1)
                    for cap in (2,4,32):
                        if self.lib.ei_device_has_capability(device,cap):
                            self.devices[cap]=self.lib.ei_device_ref(device)
                self.lib.ei_event_unref(event)
            time.sleep(.01)
        assert all(c in self.devices for c in (2,4,32)),self.devices
    def frame(self,cap):
        self.lib.ei_device_frame(self.devices[cap],time.monotonic_ns()//1000)
        self.lib.ei_dispatch(self.ei)
        time.sleep(.035)
        self.lib.ei_dispatch(self.ei)
        while event:=self.lib.ei_get_event(self.ei):
            kind=self.lib.ei_event_get_type(event)
            self.lib.ei_event_unref(event)
            if kind==2: raise RuntimeError('EIS disconnected')
    def key(self,key,down):
        self.lib.ei_device_keyboard_key(self.devices[4],key,down);self.frame(4)
    def button(self,button,down):
        self.lib.ei_device_button_button(self.devices[32],button,down);self.frame(32)
    def move(self,x,y):
        self.lib.ei_device_pointer_motion_absolute(self.devices[2],x,y);self.frame(2)
    def drag(self,start,end,shift=False,right=False,late_shift=False,meta=True):
        self.move(*start)
        if meta:self.key(125,True)
        if shift and not late_shift:self.key(42,True)
        self.button(273 if right else 272,True)
        for i in range(1,13):
            if shift and late_shift and i==4:self.key(42,True)
            self.move(start[0]+(end[0]-start[0])*i/12,start[1]+(end[1]-start[1])*i/12)
            if hasattr(self,'on_drag_step'):self.on_drag_step()
        self.button(273 if right else 272,False)
        if shift:self.key(42,False)
        if meta:self.key(125,False)
        time.sleep(.4)
    def close(self):
        for key in (42,125):self.key(key,False)
        for button in (272,273):self.button(button,False)
        for dev in self.devices.values():self.lib.ei_device_unref(dev)
        self.lib.ei_unref(self.ei)
        self.remote.disconnect(self.cookie)
