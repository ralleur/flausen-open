#!/usr/bin/env python3
"""User-local window controls with guarded rollback and atomic plugin updates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

HOME = Path.home()
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', HOME / '.config'))
DATA = Path(os.environ.get('XDG_DATA_HOME', HOME / '.local/share'))
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'ralleur-desktop-tweaks/window-controls.json'
THEME = 'ralleur-window-controls'


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def setting(file, group, key, value=None):
    args = ['--file', str(CONFIG / file), '--group', group, '--key', key]
    if value is None:
        return run('kreadconfig6', *args)
    subprocess.run(['kwriteconfig6', *args, *([value] if value else ['--delete'])], check=True)


def atomic(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.ralleur-new')
    temp.write_bytes(content)
    temp.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def matches(path, expected):
    if path.is_symlink():
        return False
    if digest(path) == expected:
        return True
    # KDE's GTK settings writer can strip the final newline without changing CSS.
    return path.suffix == '.css' and path.is_file() and hashlib.sha256(path.read_bytes().rstrip(b'\n') + b'\n').hexdigest() == expected


def notify():
    subprocess.run(['qdbus6', 'org.kde.KWin', '/KWin', 'org.kde.KWin.reconfigure'], check=True)
    subprocess.run(['dbus-send', '--session', '--type=signal', '/KIconLoader',
                    'org.kde.KIconLoader.iconChanged', 'int32:0'], check=True)


def install(build):
    library = build.resolve() / 'bin/org.kde.ralleur.so'
    if not library.is_file():
        raise SystemExit('Build the decoration first.')
    previous = json.loads(STATE.read_text()) if STATE.exists() else {'files': [], 'settings': []}
    for record in previous['files']:
        if not matches(Path(record['path']), record['digest']):
            raise SystemExit('Preserving manual changes to ' + record['path'])
    plugin = HOME / '.local/lib/ralleur/window-controls' / ('org.kde.ralleur-' + digest(library)[:12] + '.so')
    parent = next((r['before'] for r in previous['settings'] if r['key'] == 'Theme'), setting('kdeglobals', 'Icons', 'Theme')) or 'breeze'
    theme = DATA / 'icons' / THEME
    targets = {Path(r['path']): Path(r['path']).read_bytes() for r in previous['files'] if Path(r['path']).suffix == '.so'}
    targets[plugin] = library.read_bytes()
    index = f'''[Icon Theme]
Name=Ralleur Window Controls
Comment=Line, square and X; other icons inherit the selected theme
Inherits={parent},hicolor
FollowsColorScheme=true
Directories=scalable/actions

[scalable/actions]
Size=16
MinSize=8
MaxSize=256
Type=Scalable
Context=Actions
'''
    targets[theme / 'index.theme'] = index.encode()
    paths = {'minimize': 'M4 11.5h8', 'maximize': 'M4.5 4.5h7v7h-7Z',
             'restore': 'M4.5 4.5h7v7h-7Z', 'close': 'M4.5 4.5l7 7m0-7-7 7'}
    # GTK's symbolic loader handles filled silhouettes more consistently than strokes.
    filled = {'minimize': 'M3.4 10.9h9.2v1.2H3.4Z',
              'maximize': 'M3.9 3.9h8.2v8.2H3.9ZM5.1 5.1v5.8h5.8V5.1Z',
              'restore': 'M3.9 3.9h8.2v8.2H3.9ZM5.1 5.1v5.8h5.8V5.1Z',
              'close': 'M4.5 3.6515 12.3485 11.5 11.5 12.3485 3.6515 4.5Z M11.5 3.6515 12.3485 4.5 4.5 12.3485 3.6515 11.5Z'}
    for name, path in paths.items():
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
               '<style id="current-color-scheme">.ColorScheme-Text {color:#eff0f1;}</style>'
               f'<path class="ColorScheme-Text" d="{path}" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="square" stroke-linejoin="miter"/></svg>\n')
        for suffix in ['', '-symbolic']:
            content = svg if not suffix else ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
                f'<path d="{filled[name]}" fill="#000" fill-rule="nonzero"/></svg>\n')
            targets[theme / 'scalable/actions' / f'window-{name}{suffix}.svg'] = content.encode()
    # GTK themes sometimes draw their own images instead of requesting an icon.
    for version in ['3.0', '4.0']:
        css = CONFIG / f'gtk-{version}/gtk.css'
        old_record = next((r for r in previous['files'] if r['path'] == str(css)), None)
        base = (bytes.fromhex(old_record['before']) if old_record['before'] is not None else b'') if old_record else css.read_bytes() if css.exists() else b''
        rules = ['\n/* Ralleur window controls */\n']
        for name in ['minimize', 'maximize', 'close']:
            selectors = []
            for prefix in ['', 'window.background.chromium ', '.maximized ', 'window.background.chromium.maximized ', 'window.background headerbar ', 'window.background.maximized headerbar ']:
                for button in [f'button.titlebutton.{name}', f'windowcontrols > button.image-button.{name}']:
                    for state in ['', ':hover', ':active', ':backdrop', ':hover:backdrop']:
                        selectors.append(prefix + button + state)
            uri = (theme / 'scalable/actions' / f'window-{name}-symbolic.svg').as_uri()
            rules.append(',\n'.join(selectors) + f' {{ background-image: -gtk-recolor(url("{uri}")); background-size: 16px 16px; background-position: center; background-repeat: no-repeat; min-width: 30px; min-height: 30px; padding: 0; margin: 0; border: 0; border-radius: 4px; box-shadow: none; color: @theme_fg_color; background-color: transparent; }}\n')
        rules.append('button.titlebutton image, windowcontrols > button image { opacity: 0; }\n')
        for state, color, background in [(':backdrop', 'alpha(@theme_fg_color, .55)', 'transparent'),
                                          (':hover', '@theme_fg_color', 'alpha(@theme_fg_color, .12)'),
                                          (':active', '@theme_fg_color', 'alpha(@theme_fg_color, .20)'),
                                          (':hover:backdrop', 'alpha(@theme_fg_color, .55)', 'alpha(@theme_fg_color, .066)')]:
            selectors = [prefix + button + state for prefix in ['', 'window.background.chromium ', '.maximized ', 'window.background.chromium.maximized ', 'window.background headerbar ', 'window.background.maximized headerbar ']
                         for name in ['minimize', 'maximize', 'close'] for button in [f'button.titlebutton.{name}', f'windowcontrols > button.image-button.{name}']]
            rules.append(',\n'.join(selectors) + f' {{ color: {color}; background-color: {background}; }}\n')
        targets[css] = base + ''.join(rules).encode()
    # Dolphin uses a separate folder theme; keep its existing folders and inheritance.
    dolphin = DATA / 'icons/ralleur-rounded-folders/index.theme'
    if dolphin.exists():
        text = dolphin.read_text()
        import re
        text = re.sub(r'^Inherits=.*$', f'Inherits={THEME},hicolor', text, flags=re.M)
        targets[dolphin] = text.encode()
    records = []
    for path, content in targets.items():
        if path.is_symlink():
            raise SystemExit(f'Preserving symlink: {path}')
        old = next((r for r in previous['files'] if r['path'] == str(path)), None)
        before = old['before'] if old else path.read_bytes().hex() if path.exists() else None
        records.append({'path': str(path), 'before': before, 'digest': hashlib.sha256(content).hexdigest()})
    # KPluginMetaData prefixes a plugin namespace even for absolute IDs. A relative
    # path reaching the filesystem root loads our private library without modifying
    # system plugin directories or restarting the compositor to change its environment.
    plugin_id = '../' * 12 + str(plugin).lstrip('/')
    desired = [('kdeglobals', 'Icons', 'Theme', THEME),
               ('kwinrc', 'org.kde.kdecoration2', 'library', plugin_id),
               ('kwinrc', 'org.kde.kdecoration2', 'ButtonsOnLeft', ''),
               ('kwinrc', 'org.kde.kdecoration2', 'ButtonsOnRight', 'IAX')]
    settings = []
    for file, group, key, value in desired:
        old = next((r for r in previous['settings'] if (r['file'], r['group'], r['key']) == (file, group, key)), None)
        if old and setting(file, group, key) != old['installed']:
            raise SystemExit(f'Preserving changed setting {file}/{key}')
        settings.append(dict(file=file, group=group, key=key, before=old['before'] if old else setting(file, group, key), installed=value))
    atomic(STATE, (json.dumps({'files': records, 'settings': settings}, indent=2) + '\n').encode())
    for path, content in targets.items():
        atomic(path, content)
    for r in settings:
        setting(r['file'], r['group'], r['key'], r['installed'])
    # Empty string means KWin's default left menu; explicitly suppress it.
    subprocess.run(['kwriteconfig6', '--file', str(CONFIG/'kwinrc'), '--group', 'org.kde.kdecoration2', '--key', 'ButtonsOnLeft', ''], check=True)
    notify()
    print(f'Installed. Rollback manifest: {STATE}')


def restore():
    manifest = json.loads(STATE.read_text())
    for r in manifest['settings']:
        if setting(r['file'], r['group'], r['key']) == r['installed']:
            setting(r['file'], r['group'], r['key'], r['before'])
    for r in reversed(manifest['files']):
        path = Path(r['path'])
        if matches(path, r['digest']):
            if r['before'] is None:
                path.unlink()
            else:
                atomic(path, bytes.fromhex(r['before']))
    STATE.rename(STATE.with_suffix('.restored.json'))
    notify()
    print('Restored previous window controls; manual changes preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', type=Path)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    if args.restore:
        restore()
    elif args.build:
        install(args.build)
    else:
        parser.error('Specify --build or --restore')
