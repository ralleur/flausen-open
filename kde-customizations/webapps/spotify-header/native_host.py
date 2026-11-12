#!/usr/bin/python3
"""Bounded native messaging bridge; only operates on its identified Spotify window."""
import json
import fcntl
import os
from pathlib import Path
import re
import signal
import struct
import subprocess
import sys
import tempfile
import time
import uuid

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

WMCLASS = "chrome-open.spotify.com__-Default"


class Bridge(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.name = f"org.flausen.SpotifyHeader.p{os.getpid()}"
        self.bus_name = dbus.service.BusName(self.name, self.bus)
        super().__init__(self.bus_name, "/Result")
        self.window = None
        self.original_border = False
        self.changed = False
        self.result = None
        self.loop = GLib.MainLoop()
        self.lock = None

    @dbus.service.method("org.flausen.SpotifyHeader", in_signature="s", out_signature="")
    def report(self, result):
        self.result = json.loads(result)
        self.loop.quit()

    def run_script(self, code, keep=False):
        def q(*args):
            return subprocess.check_output(["qdbus6", *args], text=True, timeout=3).strip()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".js") as script:
            script.write("var result; try { " + code + " } catch(e) { result={error:String(e)}; }\n"
                         f"callDBus({json.dumps(self.name)}, '/Result', 'org.flausen.SpotifyHeader', 'report', JSON.stringify(result));")
            script.flush()
            key = f"flausen-spotify-header-{os.getpid()}" + ("-drag" if keep else "")
            if keep:
                self.end_drag()
            sid = q("org.kde.KWin", "/Scripting", "loadScript", script.name, key)
            try:
                self.result = None
                q("org.kde.KWin", "/Scripting/Script" + sid, "run")
                timer = GLib.timeout_add(2500, lambda: (self.loop.quit(), False)[1])
                self.loop.run()
                if self.result is not None:
                    GLib.source_remove(timer)
                if self.result is None:
                    raise RuntimeError("KWin did not reply")
                if "error" in self.result:
                    raise RuntimeError(self.result["error"])
                return self.result
            finally:
                if not keep or self.result is None or "error" in self.result:
                    q("org.kde.KWin", "/Scripting", "unloadScript", key)

    def end_drag(self):
        subprocess.run(["qdbus6", "org.kde.KWin", "/Scripting", "unloadScript",
                        f"flausen-spotify-header-{os.getpid()}-drag"],
                       check=True, stdout=subprocess.DEVNULL, timeout=3)

    def handle(self, message):
        action = message.get("action")
        if action == "identify":
            token = message.get("token", "")
            if self.window or not re.fullmatch(r"flausen-spotify-[0-9a-f-]{36}", token):
                raise ValueError("Invalid window token")
            result = self.run_script(
                f"var matches=workspace.windowList().filter(w=>String(w.resourceClass)==={json.dumps(WMCLASS)}"
                f" && String(w.caption).includes({json.dumps(token)}));"
                "if(matches.length!==1) throw new Error('Spotify window not identified');"
                "var w=matches[0]; result={window:String(w.internalId), noBorder:w.noBorder};")
            self.window = result["window"]
            # A reload may start its new host before the previous host restored
            # the native frame. Serialize ownership of this particular window.
            directory = Path(os.environ["XDG_RUNTIME_DIR"]) / "flausen-spotify-header"
            directory.mkdir(mode=0o700, exist_ok=True)
            self.lock = (directory / (uuid.UUID(self.window).hex + ".lock")).open("a")
            deadline = time.monotonic() + 2
            while True:
                try:
                    fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise RuntimeError("Previous Spotify window bridge is still active")
                    time.sleep(.03)
            self.original_border = self.handle({"action": "state"})["noBorder"]
            return {"ok": True}
        if not self.window:
            raise ValueError("Window is not identified")
        code = (f"var w=workspace.windowList().find(w=>String(w.internalId)==={json.dumps(self.window)}"
                f" && String(w.resourceClass)==={json.dumps(WMCLASS)});"
                "if(!w) throw new Error('Spotify window closed');")
        if action == "enable":
            self.changed = True  # Also restore if KWin changes it but its reply times out.
            code += "w.noBorder=true; result={ok:true};"
        elif action in ("move", "resize"):
            # Keyboard move/resize slots anchor to the window centre and jump.
            # Track KWin's real pointer while the content script holds capture.
            # Qt value wrappers follow their source property; snapshot primitives.
            code += ("var sx=workspace.cursorPos.x,sy=workspace.cursorPos.y;"
                     "var gx=w.frameGeometry.x,gy=w.frameGeometry.y,"
                     "gw=w.frameGeometry.width,gh=w.frameGeometry.height;")
            if action == "move":
                code += ("workspace.cursorPosChanged.connect(function(){var p=workspace.cursorPos;"
                         "w.frameGeometry={x:gx+p.x-sx,y:gy+p.y-sy,width:gw,height:gh};});")
            else:
                code += ("workspace.cursorPosChanged.connect(function(){var p=workspace.cursorPos;"
                         "w.frameGeometry={x:gx,y:gy,width:Math.max(450,gw+p.x-sx),"
                         "height:Math.max(300,gh+p.y-sy)};});")
            code += "result={ok:true};"
            return self.run_script(code, keep=True)
        elif action == "end":
            self.end_drag()
            return {"ok": True}
        elif action == "state":
            code += "result={ok:true,noBorder:w.noBorder,maximized:w.maximizeMode===3};"
        else:
            raise ValueError("Unsupported action")
        return self.run_script(code)

    def restore(self):
        self.end_drag()
        if self.changed and self.window:
            self.changed = False
            self.run_script(
                f"var w=workspace.windowList().find(w=>String(w.internalId)==={json.dumps(self.window)}"
                f" && String(w.resourceClass)==={json.dumps(WMCLASS)});"
                f"if(w) w.noBorder={json.dumps(self.original_border)}; result={{ok:true}};")


def read_exact(stream, length):
    data = bytearray()
    while len(data) < length:
        chunk = stream.read(length - len(data))
        if not chunk:
            raise EOFError
        data.extend(chunk)
    return bytes(data)


def main():
    bridge = Bridge()
    def interrupted(signum, frame):
        raise SystemExit(0)

    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        while True:
            length, = struct.unpack("=I", read_exact(sys.stdin.buffer, 4))
            if not 0 < length <= 4096:
                break
            message = json.loads(read_exact(sys.stdin.buffer, length))
            if not isinstance(message, dict):
                break
            try:
                result = bridge.handle(message)
            except Exception as error:
                result = {"error": str(error)}
            result["id"] = message.get("id")
            encoded = json.dumps(result).encode()
            sys.stdout.buffer.write(struct.pack("=I", len(encoded)) + encoded)
            sys.stdout.buffer.flush()
    except (EOFError, ValueError, BrokenPipeError):
        pass
    finally:
        try:
            bridge.restore()
        except Exception as error:
            print(f"Spotify frame restore: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
