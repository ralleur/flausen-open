#!/usr/bin/env python3
"""Open ZIP files by extracting them beside the archive with KDE Ark."""
from datetime import datetime
from pathlib import Path
import shutil
import subprocess


def main():
    for command in ("ark", "xdg-mime", "kbuildsycoca6"):
        if not shutil.which(command):
            raise SystemExit(f"Required command missing: {command}")

    home = Path.home()
    backup = home / ".local/state/ralleur-desktop-tweaks" / (
        "zip-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    )
    backup.mkdir(parents=True)
    desktop_id = "ralleur-extract-zip.desktop"
    desktop = home / ".local/share/applications" / desktop_id
    mimeapps = home / ".config/mimeapps.list"
    # xdg-mime can also select a desktop-specific mimeapps.list.
    paths = {desktop, mimeapps}
    for folder in (home / ".config", home / ".local/share/applications"):
        paths.update(folder.glob("*mimeapps.list"))
    for path in paths:
        if path.exists():
            destination = backup / path.relative_to(home)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        else:
            with (backup / "created-files.txt").open("a") as record:
                record.write(str(path) + "\n")

    desktop.parent.mkdir(parents=True, exist_ok=True)
    desktop.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Extract ZIP here\n"
        "Name[de]=ZIP hier entpacken\n"
        "Comment=Extract beside the ZIP archive\n"
        "Comment[de]=Im gleichen Ordner wie die ZIP-Datei entpacken\n"
        # One archive per invocation: each gets its own source directory.
        "Exec=ark --batch --autodestination %f\n"
        "Icon=archive-extract\n"
        "Terminal=false\n"
        "NoDisplay=true\n"
        "MimeType=application/zip;\n"
        "Categories=Utility;Archiving;\n"
        "StartupNotify=false\n"
    )
    subprocess.run(["kbuildsycoca6", "--noincremental"], check=True)
    subprocess.run(["xdg-mime", "default", desktop_id, "application/zip"], check=True)
    result = subprocess.check_output(
        ["xdg-mime", "query", "default", "application/zip"], text=True
    ).strip()
    if result != desktop_id:
        raise SystemExit(f"Unexpected ZIP association: {result}. Backup: {backup}")
    print(f"ZIP extraction installed. Backups: {backup}")


if __name__ == "__main__":
    main()
