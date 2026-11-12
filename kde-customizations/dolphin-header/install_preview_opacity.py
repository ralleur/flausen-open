#!/usr/bin/env python3
"""Install a narrowly matched KWin opacity exception, preserving other rules."""
import configparser
from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess


def install():
    config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    state = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    target = config / "kwinrulesrc"
    backup = state / "ralleur-desktop-tweaks" / ("preview-opacity-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    if target.exists():
        shutil.copy2(target, backup / "kwinrulesrc.before")
    rules = configparser.ConfigParser(interpolation=None)
    rules.optionxform = str
    rules.read(Path(__file__).with_name("preview-opacity.rules"))
    group = "ralleur-dolphin-preview-opacity"
    order = subprocess.check_output(["kreadconfig6", "--file", str(target), "--group", "General", "--key", "Order"], text=True).strip()
    # KWin uses the first matching rule for each property: put this exception
    # before Caelestia's general inactive-window opacity, without changing it.
    order = ",".join([group, *[item for item in order.split(",") if item and item != group]])
    for key, value in rules[group].items():
        subprocess.run(["kwriteconfig6", "--file", str(target), "--group", group, "--key", key, value], check=True)
    subprocess.run(["kwriteconfig6", "--file", str(target), "--group", "General", "--key", "Order", order], check=True)
    subprocess.run(["qdbus6", "org.kde.KWin", "/KWin", "reconfigure"], check=True)
    print(f"Installed preview opacity rule. Backup: {backup}")


if __name__ == "__main__":
    install()
