#!/usr/bin/env python3
"""User-local installation with backups and guarded restore; no system files."""
import argparse
import base64
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
DATA = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local/share"))
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config"))
STATE = Path(os.environ.get("XDG_STATE_HOME", HOME / ".local/state"))
INSTALLATION = STATE / "ralleur-desktop-tweaks/dolphin-header-installation.json"
ICON_THEME = "ralleur-rounded-folders"
COLOR_POLICY = CONFIG / "ralleur-dolphin/folder-colors.json"
COLOR_JOURNAL = STATE / "ralleur-desktop-tweaks/folder-icon-changes"


def places_icons(previous=None, restoring=False):
    """Own only five icon attributes, retaining bookmark IDs and all other fields."""
    path = DATA / "user-places.xbel"
    if not path.is_file():
        return previous or []
    ET.register_namespace("bookmark", "http://www.freedesktop.org/standards/desktop-bookmarks")
    ET.register_namespace("kdepriv", "http://www.kde.org/kdepriv")
    tree = ET.parse(path)
    records = []
    changed = False
    desired = {}
    for key, kind in [("DOWNLOAD", "downloads"), ("DOCUMENTS", "documents"),
                      ("PICTURES", "pictures"), ("MUSIC", "music"), ("VIDEOS", "videos")]:
        folder = subprocess.check_output(["xdg-user-dir", key], text=True).strip()
        if folder and Path(folder) != HOME:
            desired[Path(folder).as_uri()] = str(DATA / "icons" / ICON_THEME / "scalable/places" / f"ralleur-place-{kind}.svg")
    for bookmark in tree.getroot().findall("bookmark"):
        url = bookmark.get("href", "").rstrip("/")
        old = next((item for item in (previous or []) if item["url"] == url), None)
        icon = bookmark.find(".//{http://www.freedesktop.org/standards/desktop-bookmarks}icon")
        if icon is None:
            continue
        current = icon.get("name", "")
        if restoring:
            if old and current == old["installed"]:
                icon.set("name", old["before"])
                changed = True
        elif url in desired:
            # Preserve a later manual choice instead of overriding it on upgrade.
            if old and current != old["installed"]:
                continue
            records.append({"url": url, "before": old["before"] if old else current, "installed": desired[url]})
            icon.set("name", desired[url])
            changed |= current != desired[url]
    if changed:
        temporary = path.with_suffix(".xbel.ralleur-new")
        tree.write(temporary, encoding="UTF-8", xml_declaration=True)
        temporary.chmod(path.stat().st_mode & 0o7777)
        temporary.replace(path)
    return records


def restore_folder_colors(journal=COLOR_JOURNAL):
    restored, preserved = 0, 0
    for record_path in sorted(journal.glob("*.json")):
        item = json.loads(record_path.read_text())
        path = Path(item["path"])
        try:
            info = path.parent.stat()
            identity = f"{info.st_dev}:{info.st_ino}"
            if path.is_symlink() or identity != item["identity"] or not path.is_file() or digest(path) != item["lastDigest"]:
                preserved += 1
                continue
            if item["existedBefore"]:
                temporary = path.with_name(".directory.ralleur-restore")
                temporary.write_bytes(base64.b64decode(item["before"]))
                temporary.chmod(item["mode"])
                temporary.replace(path)
            else:
                path.unlink()
            record_path.unlink()
            restored += 1
        except OSError:
            preserved += 1
    return restored, preserved


def icon_theme(config_file):
    return subprocess.run(["kreadconfig6", "--file", str(CONFIG / config_file),
        "--group", "Icons", "--key", "Theme", "--default", ""],
        check=False, capture_output=True, text=True).stdout.strip()


def app_icon_theme():
    return icon_theme("dolphinrc")


def set_icon_theme(config_file, theme):
    command = ["kwriteconfig6", "--file", str(CONFIG / config_file), "--group", "Icons", "--key", "Theme"]
    command += [theme] if theme else ["--delete"]
    subprocess.run(command, check=True)


def set_app_icon_theme(theme):
    set_icon_theme("dolphinrc", theme)


def preview_plugins():
    return subprocess.run(["kreadconfig6", "--file", str(CONFIG / "dolphinrc"),
        "--group", "PreviewSettings", "--key", "Plugins", "--default", "__ralleur_unset__"],
        check=False, capture_output=True, text=True).stdout.strip()


def set_preview_plugins(plugins):
    command = ["kwriteconfig6", "--file", str(CONFIG / "dolphinrc"), "--group", "PreviewSettings", "--key", "Plugins"]
    command += ["--delete"] if plugins == "__ralleur_unset__" else [plugins]
    subprocess.run(command, check=True)


def digest(path):
    if path.is_symlink():
        return "link:" + os.readlink(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh():
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["kbuildsycoca6"], check=True)


def restore(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text())
    if "iconTheme" in manifest and app_icon_theme() != manifest["iconTheme"]["installed"]:
        raise SystemExit("Dolphin's icon theme was changed after installation; preserving that setting.")
    if "previews" in manifest and preview_plugins() != manifest["previews"]["installed"]:
        raise SystemExit("Dolphin's preview settings were changed after installation; preserving that setting.")
    if "workerIconTheme" in manifest and icon_theme("kioworkerrc") != manifest["workerIconTheme"]["installed"]:
        raise SystemExit("KIO's thumbnail icon theme was changed after installation; preserving that setting.")
    for item in manifest["targets"]:
        path = Path(item["path"])
        if (path.exists() or path.is_symlink()) and digest(path) != item["installedDigest"]:
            raise SystemExit(f"Changed since installation; preserving {path}. Restore manually using {manifest_path.parent}.")
    for item in reversed(manifest["targets"]):
        path = Path(item["path"])
        path.unlink(missing_ok=True)
        if item["backup"] is not None:
            shutil.copy2(manifest_path.parent / item["backup"], path, follow_symlinks=False)
    if "iconTheme" in manifest:
        set_app_icon_theme(manifest["iconTheme"]["before"])
    if "previews" in manifest:
        set_preview_plugins(manifest["previews"]["before"])
    if "workerIconTheme" in manifest:
        set_icon_theme("kioworkerrc", manifest["workerIconTheme"]["before"])
        worker_config = CONFIG / "kioworkerrc"
        if not manifest["workerIconTheme"]["fileExistedBefore"] and worker_config.is_file():
            if not worker_config.read_text().replace("[Icons]", "").strip():
                worker_config.unlink()
    places_icons(manifest.get("placesIcons", []), restoring=True)
    restored, preserved = restore_folder_colors()
    refresh()
    if INSTALLATION.exists() and json.loads(INSTALLATION.read_text()).get("manifest") == str(manifest_path):
        INSTALLATION.unlink()
    print("Header extension removed. Reopen Dolphin for the native titlebar.")
    print(f"Folder metadata restored: {restored}; preserved after edits/moves: {preserved}.")


def install(build):
    library = Path(build).resolve() / "plugins/generic/libralleurdolphin.so"
    if not library.is_file():
        raise SystemExit("Build the plugin and run its tests first.")
    wrapper = HOME / ".local/bin/ralleur-dolphin"
    alias = HOME / ".local/bin/dolphin"
    plugin = HOME / ".local/lib/ralleur/dolphin-header/plugins/generic/libralleurdolphin.so"
    desktop = DATA / "applications/org.kde.dolphin.desktop"
    service = DATA / "dbus-1/services/org.kde.dolphin.FileManager1.service"
    dropin = CONFIG / "systemd/user/plasma-dolphin.service.d/ralleur-header.conf"
    targets = [plugin, wrapper, alias, desktop, service, dropin, COLOR_POLICY]
    icon_files = sorted(path for path in (ROOT / "icons").rglob("*") if path.is_file())
    if not icon_files:
        raise SystemExit("Generate the folder SVGs first with generate_icons.py.")
    targets += [DATA / "icons" / ICON_THEME / path.relative_to(ROOT / "icons") for path in icon_files]
    previous = None
    if INSTALLATION.is_file():
        previous_path = Path(json.loads(INSTALLATION.read_text())["manifest"])
        previous = json.loads(previous_path.read_text())
        for record in previous["targets"]:
            path = Path(record["path"])
            if not (path.exists() or path.is_symlink()) or digest(path) != record["installedDigest"]:
                raise SystemExit(f"Preserving an externally changed installation target: {path}")
        if "iconTheme" in previous and app_icon_theme() != previous["iconTheme"]["installed"]:
            raise SystemExit("Preserving an externally changed Dolphin icon theme.")
        if "previews" in previous and preview_plugins() != previous["previews"]["installed"]:
            raise SystemExit("Preserving externally changed Dolphin preview settings.")
        if "workerIconTheme" in previous and icon_theme("kioworkerrc") != previous["workerIconTheme"]["installed"]:
            raise SystemExit("Preserving an externally changed KIO thumbnail icon theme.")
    icon_before = previous["iconTheme"]["before"] if previous and "iconTheme" in previous else app_icon_theme()
    previews_before = previous["previews"]["before"] if previous and "previews" in previous else preview_plugins()
    worker_before = previous["workerIconTheme"]["before"] if previous and "workerIconTheme" in previous else icon_theme("kioworkerrc")
    worker_existed = previous["workerIconTheme"]["fileExistedBefore"] if previous and "workerIconTheme" in previous else (CONFIG / "kioworkerrc").exists()
    effective_previews = preview_plugins()
    if effective_previews == "__ralleur_unset__":
        global_previews = subprocess.run(["kreadconfig6", "--file", "kdeglobals", "--group", "PreviewSettings", "--key", "Plugins", "--default", "__ralleur_unset__"],
            check=False, capture_output=True, text=True).stdout.strip()
        effective_previews = global_previews if global_previews != "__ralleur_unset__" else subprocess.run(
            [str(Path(build).resolve() / "preview_defaults")], check=True, capture_output=True, text=True).stdout.strip()
    # The worker draws the folder shell independently of Dolphin. Give that
    # renderer the same SVG overlay and retain KDE's native contents previews.
    rounded_previews = ",".join(dict.fromkeys([*filter(None, effective_previews.split(",")), "directorythumbnail"]))
    if alias.exists() or alias.is_symlink():
        if not (alias.is_symlink() and os.readlink(alias) == "ralleur-dolphin"):
            raise SystemExit(f"Preserving existing command: {alias}. Resolve this entry before installation.")
    backup = STATE / "ralleur-desktop-tweaks" / ("dolphin-header-install-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    records = []
    for index, target in enumerate(targets):
        exists = target.exists() or target.is_symlink()
        old = next((entry for entry in previous["targets"] if entry["path"] == str(target)), None) if previous else None
        if exists:
            (backup / "before-update").mkdir(exist_ok=True)
            shutil.copy2(target, backup / "before-update" / str(index), follow_symlinks=False)
        if old:
            had_original = old["backup"] is not None
            if had_original:
                shutil.copy2(previous_path.parent / old["backup"], backup / str(index), follow_symlinks=False)
        else:
            had_original = exists
            if exists:
                shutil.copy2(target, backup / str(index), follow_symlinks=False)
        records.append({"path": str(target), "backup": str(index) if had_original else None})
    # Keep native app configuration as evidence, not as an unconditional restore
    # target: it may acquire unrelated preferences after this installation.
    for path in [CONFIG / "dolphinrc", CONFIG / "kioworkerrc", STATE / "dolphinstaterc"]:
        if path.exists():
            shutil.copy2(path, backup / (path.name + ".before"))
    if (DATA / "user-places.xbel").is_file():
        shutil.copy2(DATA / "user-places.xbel", backup / "user-places.xbel.before")
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
    if not COLOR_POLICY.is_file():
        inventory = subprocess.check_output([str(Path(build).resolve() / "preview_defaults"), "--home-folders"], text=True)
        policy = json.loads(inventory)
        if policy.get("version") != 1 or policy.get("home") != str(HOME):
            raise SystemExit("Invalid Home folder inventory; stopping installation.")
        COLOR_POLICY.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n")
    # Atomic replacement avoids changing a library that a live process mapped.
    temporary = plugin.with_suffix(".so.new")
    shutil.copy2(library, temporary)
    temporary.replace(plugin)
    shutil.copy2(ROOT / "ralleur-dolphin", wrapper)
    wrapper.chmod(0o755)
    alias.unlink(missing_ok=True)
    alias.symlink_to("ralleur-dolphin")
    source = desktop.read_text() if desktop.exists() else Path("/usr/share/applications/org.kde.dolphin.desktop").read_text()
    lines = []
    section = ""
    for line in source.splitlines():
        if line.startswith("["):
            section = line
        if section == "[Desktop Entry]" and (line.startswith("Name=") or line.startswith("Name[")):
            line = line.split("=", 1)[0] + "=Files"
        if line.startswith(("Exec=dolphin", "Exec=/usr/bin/dolphin", f"Exec={wrapper}")):
            _, arguments = line.split("=", 1)
            parts = arguments.split(" ", 1)
            line = f"Exec={wrapper}" + (" " + parts[1] if len(parts) > 1 else "")
        lines.append(line)
    desktop.write_text("\n".join(lines) + "\n")
    service.write_text(f"[D-BUS Service]\nName=org.freedesktop.FileManager1\nExec={wrapper} --daemon\nSystemdService=plasma-dolphin.service\n")
    dropin.write_text(f"[Service]\nExecStart=\nExecStart={wrapper} --daemon\n")
    parent_theme = subprocess.run(["kreadconfig6", "--file", "kdeglobals", "--group", "Icons", "--key", "Theme", "--default", "breeze"],
        check=True, capture_output=True, text=True).stdout.strip()
    for source_icon in icon_files:
        destination = DATA / "icons" / ICON_THEME / source_icon.relative_to(ROOT / "icons")
        destination.write_text(source_icon.read_text().replace("@PARENT@", parent_theme))
    set_app_icon_theme(ICON_THEME)
    set_icon_theme("kioworkerrc", ICON_THEME)
    set_preview_plugins(rounded_previews)
    place_records = places_icons(previous.get("placesIcons", []) if previous else [])
    for record in records:
        record["installedDigest"] = digest(Path(record["path"]))
    manifest_path = backup / "manifest.json"
    manifest_path.write_text(json.dumps({"source": str(ROOT), "targets": records, "placesIcons": place_records,
        "iconTheme": {"before": icon_before, "installed": ICON_THEME},
        "previews": {"before": previews_before, "installed": rounded_previews},
        "workerIconTheme": {"before": worker_before, "installed": ICON_THEME,
                            "fileExistedBefore": worker_existed}}, indent=2) + "\n")
    INSTALLATION.write_text(json.dumps({"manifest": str(manifest_path)}, indent=2) + "\n")
    refresh()
    print(f"Installed Dolphin header. Backup and restore manifest: {manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", type=Path)
    mode.add_argument("--restore", type=Path)
    args = parser.parse_args()
    if args.restore:
        restore(args.restore)
    else:
        install(args.build)
