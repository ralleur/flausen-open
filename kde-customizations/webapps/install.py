#!/usr/bin/env python3
"""Install the Spotify Chromium webapp for the current user."""
import os
import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def install_header(profile):
    """Keep the extension and native host limited to this Chromium profile."""
    source = Path(__file__).resolve().with_name('spotify-header')
    extension = profile / 'flausen-header'
    extension.parent.mkdir(parents=True, exist_ok=True)
    if extension.is_symlink() and extension.resolve() == source:
        pass
    elif extension.exists() or extension.is_symlink():
        raise SystemExit(f'Header-Pfad bereits anderweitig belegt: {extension}')
    else:
        extension.symlink_to(source, target_is_directory=True)
    manifest = json.loads((source / 'manifest.json').read_text())
    digest = hashlib.sha256(base64.b64decode(manifest['key'])).hexdigest()[:32]
    extension_id = ''.join(chr(ord('a') + int(char, 16)) for char in digest)
    host = profile / 'NativeMessagingHosts/org.flausen.spotify_header.json'
    content = json.dumps({
        'name': 'org.flausen.spotify_header',
        'description': 'Spotify window controls for KWin',
        'path': str(source / 'native_host.py'),
        'type': 'stdio',
        'allowed_origins': [f'chrome-extension://{extension_id}/'],
    }, indent=2) + '\n'
    host.parent.mkdir(parents=True, exist_ok=True)
    if host.exists() and host.read_text() != content:
        backup_file(host)
    host.write_text(content)
    return extension


def backup_file(target):
    from datetime import datetime
    state = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state')))
    backup = state / 'flausen-webapps'
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, backup / f'{target.name}-{datetime.now():%Y%m%d-%H%M%S-%f}')


def escape_exec(value):
    return str(value).replace('\\', '\\\\\\\\').replace('"', '\\\\"').replace('`', '\\\\`').replace('$', '\\\\$').replace('%', '%%')


def main():
    if not Path('/usr/bin/chromium').is_file():
        raise SystemExit('Chromium fehlt: /usr/bin/chromium')
    data = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))
    profile = data / 'flausen-webapps/spotify'
    extension = install_header(profile)
    # Desktop Exec quoted arguments require both shell-independent backslash
    # escaping and escaping of the desktop-entry string value itself.
    escaped = escape_exec(profile)
    source = Path(__file__).with_name('spotify.desktop.in')
    icon = Path.home() / '.config/quickshell/caelestia/assets/icons/yet-another-monochrome-icon-set/apps/scalable/spotify.svg'
    icon_value = str(icon) if icon.is_file() else 'spotify'
    content = source.read_text().replace('@PROFILE@', escaped).replace('@ICON@', icon_value).replace('@HEADER@', escape_exec(extension))
    target = data / 'applications/flausen-spotify.desktop'
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text() != content:
        backup_file(target)
    target.write_text(content)
    if shutil.which('desktop-file-validate'):
        subprocess.run(['desktop-file-validate', str(target)], check=True)
    if shutil.which('update-desktop-database'):
        subprocess.run(['update-desktop-database', str(target.parent)], check=True)
    if shutil.which('kbuildsycoca6'):
        subprocess.run(['kbuildsycoca6', '--noincremental'], check=True)
    print(f'Installiert: {target}')


if __name__ == '__main__':
    main()
