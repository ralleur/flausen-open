#!/usr/bin/env python3
"""Install the effect without changing window rules or global animation speed."""
from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
EFFECT = "flausen-inactive-window-fade"


def main():
    data = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    state = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    target = data / "kwin/effects" / EFFECT
    backup = state / "flausen-inactive-window-fade" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup.mkdir(parents=True)
    if target.exists():
        shutil.copytree(target, backup / "effect")
    if (config / "kwinrc").exists():
        shutil.copy2(config / "kwinrc", backup / "kwinrc")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "metadata.json", target / "metadata.json")
    shutil.copytree(ROOT / "contents", target / "contents", dirs_exist_ok=True)
    subprocess.run(["kwriteconfig6", "--file", str(config / "kwinrc"), "--group", "Plugins",
                    "--key", EFFECT + "Enabled", "true"], check=True)
    subprocess.run(["qdbus6", "org.kde.KWin", "/Effects", "org.kde.kwin.Effects.unloadEffect", EFFECT], check=True)
    result = subprocess.check_output(["qdbus6", "org.kde.KWin", "/Effects",
                                      "org.kde.kwin.Effects.loadEffect", EFFECT], text=True).strip()
    if result != "true":
        raise SystemExit("KWin could not load the effect; backup: " + str(backup))
    print("Effect installed and loaded. Backup: " + str(backup))


if __name__ == "__main__":
    main()
