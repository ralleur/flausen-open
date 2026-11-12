#!/usr/bin/env python3
"""Verify the selected Dolphin window's real compositor states on KWin."""
import argparse
import json
from pathlib import Path
import subprocess
import time
import tempfile


def qdbus(*args):
    return subprocess.check_output(["qdbus6", *args], text=True).strip()


def info(uuid):
    output = qdbus("org.kde.KWin", "/KWin", "org.kde.KWin.getWindowInfo", uuid)
    return dict(line.split(": ", 1) for line in output.splitlines() if ": " in line)


def await_state(uuid, check):
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        result = info(uuid)
        if check(result):
            return result
        time.sleep(.08)
    raise AssertionError(result)


def restore_visible(uuid):
    # xdg-shell does not report minimization back to Qt. Re-selecting the
    # window through KWin mirrors restoring it from the taskbar.
    name = "ralleur-header-live-check"
    code = "for (const w of workspace.windowList()) { if (String(w.internalId) === " + json.dumps(uuid) + ") { w.minimized = false; workspace.activeWindow = w; break; } }"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js") as script:
        script.write(code)
        script.flush()
        script_id = qdbus("org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting.loadScript", script.name, name)
        try:
            qdbus("org.kde.KWin", "/Scripting/Script" + script_id, "org.kde.kwin.Script.run")
        finally:
            qdbus("org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting.unloadScript", name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--window", default="Dolphin_1")
    parser.add_argument("--uuid", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    header = "/org/ralleur/DolphinHeader/" + args.window
    window = "/dolphin/" + args.window
    original = info(args.uuid)
    if original.get("resourceClass") not in {"org.kde.dolphin", "dolphin"}:
        raise SystemExit("The selected window is not Dolphin.")
    if original.get("pid") != args.service.removeprefix("org.kde.dolphin-"):
        raise SystemExit("Window and D-Bus service refer to different processes.")
    if original.get("maximizeHorizontal") != "0" or original.get("maximizeVertical") != "0":
        raise SystemExit("Start with a restored test window.")
    report = {"service": args.service, "uuid": args.uuid, "original": original}
    assert qdbus(args.service, header, "org.ralleur.DolphinHeader.decorated") == "false"
    restore_visible(args.uuid)
    await_state(args.uuid, lambda state: state.get("minimized") == "false")
    try:
        qdbus(args.service, header, "org.ralleur.DolphinHeader.maximizeRestore")
        report["maximized"] = await_state(args.uuid, lambda state:
            state.get("maximizeHorizontal") != "0" and state.get("maximizeVertical") != "0")
        qdbus(args.service, header, "org.ralleur.DolphinHeader.maximizeRestore")
        report["restored"] = await_state(args.uuid, lambda state:
            state.get("maximizeHorizontal") == "0" and state.get("maximizeVertical") == "0")
        qdbus(args.service, header, "org.ralleur.DolphinHeader.minimize")
        report["minimized"] = await_state(args.uuid, lambda state: state.get("minimized") == "true")
    finally:
        restore_visible(args.uuid)
        if original.get("minimized") == "true":
            qdbus(args.service, header, "org.ralleur.DolphinHeader.minimize")
    report["final"] = await_state(args.uuid, lambda state:
        state.get("minimized") == original.get("minimized"))
    report["shadowCreated"] = qdbus(args.service, header, "org.ralleur.DolphinHeader.shadowCreated") == "true"
    assert report["shadowCreated"], "The expected KWin client shadow was not created."
    report["passed"] = True
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("KWin confirms maximize, restore, minimize, original visibility and native shadow.")


if __name__ == "__main__":
    main()
