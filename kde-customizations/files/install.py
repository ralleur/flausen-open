#!/usr/bin/env python3
"""Use one KDE file chooser and the existing Dolphin-based Files app."""
from datetime import datetime
from pathlib import Path
import shutil
import subprocess

home = Path.home()
config = home / ".config"
data = home / ".local/share"
backup = home / ".local/state/ralleur-desktop-tweaks" / ("files-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
backup.mkdir(parents=True)

def write(path, content):
    if path.exists():
        if path.read_text() == content:
            return
        destination = backup / path.relative_to(home)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    else:
        with (backup / "created-files.txt").open("a") as record:
            record.write(str(path) + "\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

def setting(path, group, key, value):
    # Preserve unrelated settings and keep a complete copy before the first edit.
    destination = backup / path.relative_to(home)
    if path.exists() and not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
    elif not path.exists():
        with (backup / "created-files.txt").open("a") as record:
            record.write(str(path) + "\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["kwriteconfig6", "--file", str(path), "--group", group,
                    "--key", key, str(value)], check=True)

portal = "[preferred]\ndefault=kde\norg.freedesktop.impl.portal.FileChooser=kde\n"
write(config / "xdg-desktop-portal/portals.conf", portal)
write(config / "xdg-desktop-portal/kde-portals.conf", portal)
write(config / "environment.d/60-files.conf", "GTK_USE_PORTAL=1\n")
write(config / "plasma-workspace/env/files.sh", "#!/bin/sh\nexport GTK_USE_PORTAL=1\n")

# The portal is a separate KDE application, so Dolphin's per-app icon and
# Places preferences do not reach it automatically.
portal_config = config / "xdg-desktop-portal-kderc"
setting(portal_config, "Icons", "Theme", "ralleur-rounded-folders")
for path in [config / "kdeglobals", portal_config]:
    for key, value in {
        "Places Icons Auto-resize": "false", "Places Icons Static Size": "16",
        "Speedbar Width": "200", "View Style": "Simple",
        "Show Preview": "false", "Allow Expansion": "false",
    }.items():
        setting(path, "KFileDialog Settings", key, value)

# Reuse Files' own header implementation for the portal's KFileWidget dialogs.
# Only this service loads the integration; other portal windows stay native.
header_plugins = home / ".local/lib/ralleur/dolphin-header/plugins"
if not (header_plugins / "generic/libralleurdolphin.so").is_file():
    raise SystemExit("Install kde-customizations/dolphin-header first.")
style_plugins = home / ".local/lib/ralleur/dialogs/plugins"
write(config / "systemd/user/plasma-xdg-desktop-portal-kde.service.d/files.conf",
      "[Service]\nEnvironment=QT_QPA_GENERIC_PLUGINS=ralleurdolphin\n"
      f"Environment=QT_PLUGIN_PATH={header_plugins}:{style_plugins}\n")

# Existing apps inherit their environment at startup. Give the desktop launcher
# an explicit setting so restarting the app is sufficient before the next login.
desktop = data / "applications/chatgpt.desktop"
source = desktop if desktop.exists() else Path("/usr/share/applications/chatgpt.desktop")
if source.exists():
    lines = source.read_text().splitlines()
    for index, line in enumerate(lines):
        if line.startswith("Exec=") and "GTK_USE_PORTAL=1" not in line:
            lines[index] = "Exec=env GTK_USE_PORTAL=1 " + line.removeprefix("Exec=")
    write(desktop, "\n".join(lines) + "\n")

subprocess.run(["systemctl", "--user", "set-environment", "GTK_USE_PORTAL=1"], check=True)
subprocess.run(["dbus-update-activation-environment", "GTK_USE_PORTAL=1"], check=True)
mimeapps = config / "mimeapps.list"
if mimeapps.exists():
    shutil.copy2(mimeapps, backup / "mimeapps.list.before")
subprocess.run(["xdg-mime", "default", "org.kde.dolphin.desktop", "inode/directory"], check=True)
subprocess.run(["kbuildsycoca6", "--noincremental"], check=True)
subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
subprocess.run(["systemctl", "--user", "restart", "xdg-desktop-portal.service"], check=True)
subprocess.run(["systemctl", "--user", "restart", "plasma-xdg-desktop-portal-kde.service"], check=True)
print(f"Files integration installed. Backups: {backup}")
