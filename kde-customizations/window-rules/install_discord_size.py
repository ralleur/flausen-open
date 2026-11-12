#!/usr/bin/env python3
"""Remember a Chromium app's window size using KWin rules (default: Discord)."""
import argparse
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess

APPS = {
    "discord": ("Discord", "chrome-discord.com__app-Default"),
    "spotify": ("Spotify", "chrome-open.spotify.com__-Default"),
}


def main(app="discord"):
    name, wmclass = APPS[app]
    group = f"flausen-{app}-size"
    parser = argparse.ArgumentParser(description=f"Remember the {name} Chromium app's window size using KWin rules.")
    parser.add_argument("--size", help="Initial frame size WIDTH,HEIGHT; existing remembered size takes precedence")
    args = parser.parse_args()
    if args.size and not re.fullmatch(r"[1-9][0-9]*,[1-9][0-9]*", args.size):
        parser.error("--size must be WIDTH,HEIGHT with positive integers")
    config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    state = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    target = config / "kwinrulesrc"

    def read(group, key):
        return subprocess.check_output(["kreadconfig6", "--file", str(target),
                                        "--group", group, "--key", key], text=True).strip()

    size = read(group, "size") or args.size
    if not size:
        parser.error(f"First installation requires --size with the current {name} frame size")
    backup = state / "flausen-window-rules" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup.mkdir(parents=True)
    if target.exists():
        shutil.copy2(target, backup / "kwinrulesrc")
    order = [item for item in read("General", "Order").split(",") if item and item != group]
    values = {
        "Description": f"{name}: letzte Fenstergröße merken",
        "wmclass": wmclass,
        "wmclassmatch": "1",
        "wmclasscomplete": "false",
        "types": "1",  # Normal windows only.
        "size": size,
        "sizerule": "4",  # Rules::Remember, never force the size.
    }
    for key, value in values.items():
        subprocess.run(["kwriteconfig6", "--file", str(target), "--group", group,
                        "--key", key, value], check=True)
    subprocess.run(["kwriteconfig6", "--file", str(target), "--group", "General",
                    "--key", "Order", ",".join([group, *order])], check=True)
    subprocess.run(["qdbus6", "org.kde.KWin", "/KWin", "reconfigure"], check=True)
    print(f"{name} size remembered by KWin; initial size {size}. Backup: {backup}")


if __name__ == "__main__":
    main()
