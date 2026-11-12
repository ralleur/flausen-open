#!/usr/bin/env python3
"""Compare installed applications with publisher metadata; never install or launch."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

HOME = Path.home()
STATE = Path(os.environ.get('XDG_STATE_HOME', HOME / '.local/state')) / 'ralleur-update-hub'
ARTCRAFT_FEED = 'https://api.storyteller.ai/v1/craft_apps/release_info'
BNET = HOME / 'Games/battlenet/drive_c'
NAMES = {'wow': 'World of Warcraft · Retail', 'wowf': 'World of Warcraft · Forever',
         'wow_classic': 'WoW Classic', 'wow_classic_era': 'WoW Classic Era'}


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else (default if default is not None else {})


def keyvalues(text):
    """Parse textual Valve KeyValues without flattening nested app state."""
    tokens = re.finditer(r'"((?:[^"\\]|\\.)*)"|([{}])|(?m:^\s*//.*$)', text)
    root, stack, key = {}, [], None
    current = root
    for token in tokens:
        value, brace = token.groups()
        if value is None and brace is None:
            continue
        if brace == '{':
            child = {}
            if key is None:
                raise ValueError('Invalid Steam metadata')
            current[key] = child
            stack.append(current)
            current, key = child, None
        elif brace == '}':
            if not stack:
                raise ValueError('Invalid Steam metadata')
            current, key = stack.pop(), None
        elif key is None:
            key = value.replace('\\\\', '\\').replace('\\"', '"')
        else:
            current[key] = value.replace('\\\\', '\\').replace('\\"', '"')
            key = None
    if stack or key is not None:
        raise ValueError('Incomplete Steam metadata')
    return root


def version_tuple(value):
    value = str(value).strip().lstrip('v')
    if not re.fullmatch(r'\d+(?:\.\d+)*', value):
        return None
    return tuple(int(x) for x in value.split('.'))


def version_state(installed, latest):
    before, after = version_tuple(installed), version_tuple(latest)
    if before is None or after is None:
        return 'unknown'
    n = max(len(before), len(after))
    before += (0,) * (n - len(before))
    after += (0,) * (n - len(after))
    return 'update' if before < after else 'ahead' if before > after else 'current'


class Publisher:
    def __init__(self, path=None, local=False, opener=urlopen):
        self.path = path or STATE / 'publisher-cache.json'
        self.local, self.opener = local, opener
        self.lock = threading.Lock()
        try:
            self.cache = read_json(self.path)
        except (OSError, ValueError):
            self.cache = {}

    def text(self, url):
        old = self.cache.get(url)
        if self.local:
            if old:
                return old['text'], old['checkedAt'], old.get('error')
            raise RuntimeError('No online check available yet')
        try:
            request = Request(url, headers={'User-Agent': 'RalleurUpdateHub/1.0', 'Accept': 'application/json,text/plain,*/*'})
            with self.opener(request, timeout=12) as response:
                data = response.read(8 * 1024 * 1024 + 1)
                if len(data) > 8 * 1024 * 1024:
                    raise ValueError('Server response too large')
                text = data.decode('utf-8-sig')
            stamp = int(time.time())
            with self.lock:
                self.cache[url] = {'text': text, 'checkedAt': stamp}
            return text, stamp, None
        except (OSError, ValueError, URLError, HTTPError) as error:
            reason = 'HTTP ' + str(error.code) if isinstance(error, HTTPError) else str(error)
            if old:
                old['error'] = reason
                return old['text'], old['checkedAt'], reason
            raise RuntimeError(reason) from error

    def save(self):
        if self.local:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.cache))
        temp.replace(self.path)


def result(items, evidence, checked_at=0, error=None, **extra):
    pending = [item['name'] for item in items if item.get('state') == 'update']
    data = {'items': items, 'installed': len(items), 'pending': pending, 'evidence': evidence,
            'checkedAt': checked_at, 'stale': bool(error) or (checked_at > 0 and time.time() - checked_at > 86400), **extra}
    if error:
        data['error'] = error
    return data


def steam_status(base):
    folders = {base}
    libraries = base / 'steamapps/libraryfolders.vdf'
    if libraries.exists():
        for value in keyvalues(libraries.read_text()).get('libraryfolders', {}).values():
            if isinstance(value, dict) and value.get('path'):
                folders.add(Path(value['path']))
    games = []
    for folder in sorted(folders):
        for manifest in sorted((folder / 'steamapps').glob('appmanifest_*.acf')):
            values = keyvalues(manifest.read_text())
            app = values.get('AppState', values)
            flags = int(app.get('StateFlags', '0'))
            total = int(app.get('BytesToDownload', '0'))
            done = int(app.get('BytesDownloaded', '0'))
            active = bool(flags & (256 | 512 | 1024 | 131072))
            games.append({'name': app.get('name', manifest.stem), 'id': app.get('appid', ''),
                          'installedVersion': app.get('buildid', 'unknown'),
                          'state': 'update' if flags & 2 else 'local', 'downloading': active,
                          'bytesDownloaded': done, 'bytesTotal': total,
                          'policy': {'0': 'Automatic', '1': 'On launch', '2': 'High priority'}.get(app.get('AutoUpdateBehavior', '0'), 'Unknown')})
    return result(games, 'Steam manifest · Local download status', int(time.time()),
                  downloading=sum(item['downloading'] for item in games))


def steam_client(base, publisher):
    manifest = base / 'package/steam_client_steamrt64.manifest'
    if not manifest.exists():
        manifest = base / 'package/steam_client_ubuntu12.manifest'
    if not manifest.exists():
        return result([], 'Steam not installed')
    target = manifest.stem
    local = keyvalues(manifest.read_text())
    local = next(iter(local.values()))
    # The package manifest is a downloaded candidate, not proof that it was
    # installed. The bootstrapper explicitly records the installed version.
    installed = None
    log = base / 'logs/bootstrap_log.txt'
    if log.exists():
        matches = re.findall(r'installed version (\d+)', log.read_text(errors='replace')[-2_000_000:])
        if matches:
            installed = matches[-1]
    if not installed:
        raise RuntimeError('Steam has not logged an installed client version yet')
    beta = base / 'package/beta'
    channel = beta.read_text().strip() if beta.exists() else ''
    if channel:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', channel):
            raise ValueError('Unknown Steam channel')
        targets = re.findall(r'Downloading manifest: https://[^/\s]+/(steam_client_[A-Za-z0-9_]+)', log.read_text(errors='replace')[-2_000_000:]) if log.exists() else []
        target = next((entry for entry in reversed(targets) if channel in entry), '')
        if not target:
            raise RuntimeError('Steam beta channel not checked by the client yet')
    url = 'https://client-update.steamstatic.com/' + target
    text, checked, error = publisher.text(url)
    remote = next(iter(keyvalues(text).values()))
    latest = remote.get('version', '')
    if not latest.isdigit():
        raise ValueError('Invalid Steam version response')
    item = {'name': 'Steam Client', 'installedVersion': installed, 'latestVersion': latest,
            'state': version_state(installed, latest), 'channel': channel or 'Stable'}
    return result([item], 'Valve · ' + (channel or 'Stable'), checked, error)


def blizzard_table(text):
    lines = [line for line in text.splitlines() if line and not line.startswith('#')]
    if not lines or '|' not in lines[0]:
        raise ValueError('Invalid Blizzard version response')
    keys = [cell.split('!')[0] for cell in lines[0].split('|')]
    return [dict(zip(keys, line.split('|'))) for line in lines[1:]]


def blizzard_remote(product, region, publisher):
    if not re.fullmatch(r'[a-z0-9_]+', product) or region not in ('eu', 'us', 'kr', 'cn', 'tw'):
        raise ValueError('Unknown Blizzard product or region')
    text, stamp, error = publisher.text('https://eu.version.battle.net/' + product + '/versions')
    rows = blizzard_table(text)
    row = next((r for r in rows if r.get('Region') == region), None)
    if not row or not row.get('VersionsName') or not row.get('BuildId', '').isdigit():
        raise ValueError('No Blizzard build for ' + region)
    return row, stamp, error


def battlenet_client(base, publisher):
    executable = base / 'Program Files (x86)/Battle.net/Battle.net.exe'
    if not executable.exists():
        return result([], 'Battle.net not installed')
    info = executable.read_bytes().decode('utf-16le', errors='ignore')
    match = re.search(r'(?:FileVersion|ProductVersion)\x00+(\d+(?:\.\d+){3})', info)
    if not match:
        raise ValueError('Cannot read Battle.net file version')
    installed = match.group(1)
    latest, checked, error = blizzard_remote('bna', 'eu', publisher)
    item = {'name': 'Battle.net Client', 'installedVersion': installed, 'latestVersion': latest['VersionsName'],
            'state': version_state(installed, latest['VersionsName'])}
    return result([item], 'Blizzard · EU · Client-Build', checked, error)


def battlenet_games(base, publisher):
    items, stamps, errors = [], [], []
    for build in sorted((base / 'Program Files (x86)').glob('*/.build.info')):
        for row in blizzard_table(build.read_text()):
            if row.get('Active') != '1':
                continue
            product, region = row.get('Product', ''), row.get('Branch', 'eu')
            item = {'name': NAMES.get(product, build.parent.name + ' · ' + product), 'id': product,
                    'installedVersion': row.get('Version', ''), 'region': region}
            try:
                latest, checked, error = blizzard_remote(product, region, publisher)
                stamps.append(checked)
                item['latestVersion'] = latest['VersionsName']
                item['state'] = version_state(item['installedVersion'], item['latestVersion'])
                if error:
                    errors.append(error)
            except (RuntimeError, ValueError, OSError) as error:
                item['state'] = 'unknown'
                item['error'] = str(error)
                errors.append(str(error))
            items.append(item)
    return result(items, 'Blizzard · Installed products and regions', min(stamps) if stamps else 0,
                  '; '.join(dict.fromkeys(errors)) or None)


def artcraft_status(publisher):
    process = subprocess.run(['flatpak', 'list', '--app', '--columns=application,name,version'],
                             text=True, capture_output=True, timeout=15)
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or 'Flatpak detection failed')
    installed = [line.split('\t') for line in process.stdout.splitlines() if line.startswith('ai.storyteller.')]
    store = HOME / '.var/app/ai.storyteller.artcraft-launcher/data/ai.storyteller.artcraft-launcher/app.ron'
    match = re.search(r'"settings"\s*:\s*("(?:[^"\\]|\\.)*")', store.read_text()) if store.exists() else None
    settings = json.loads(match.group(1)) if match else ''
    auto = re.search(r'(?<![A-Za-z_])auto_update:(true|false)', settings)
    if not installed:
        return result([], 'ArtCraft not installed')
    text, checked, error = publisher.text(ARTCRAFT_FEED)
    feed = json.loads(text)
    if not feed.get('success') or not isinstance(feed.get('release_info', {}).get('apps'), dict):
        raise ValueError('Invalid ArtCraft feed')
    catalog = feed['release_info']['apps']
    items = []
    for fields in installed:
        app_id, name, version = (fields + ['', ''])[:3]
        key = app_id.removeprefix('ai.storyteller.')
        latest = catalog.get(key, {}).get('latest_release', {}).get('version', '')
        items.append({'name': name or key, 'id': app_id, 'installedVersion': version,
                      'latestVersion': latest, 'state': version_state(version, latest)})
    return result(items, 'ArtCraft · Official suite release feed', checked, error,
                  autoUpdate=auto.group(1) == 'true' if auto else None,
                  feedTimestamp=feed['release_info'].get('last_fetched'))


def wowup_status(publisher):
    state = read_json(HOME / '.local/state/linux-gaming-lab/wowup.json')
    path = Path(state.get('path', '/nonexistent'))
    if not path.exists():
        return result([], 'WowUp not installed')
    cf = 'wowup-cf' in path.name.lower()
    folder = HOME / '.config' / ('WowUpCf' if cf else 'WowUp')
    prefs = read_json(folder / 'preferences.json')
    match = re.search(r'(\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?)', path.name)
    if not match:
        raise ValueError('Cannot detect installed WowUp version')
    installed = match.group(1)
    repo = 'WowUp/WowUp.CF' if cf else 'WowUp/WowUp'
    # Channel 1 is stable in this installation; preserve beta selection by
    # declining to compare a beta with a stable release.
    text, checked, error = publisher.text('https://api.github.com/repos/' + repo + '/releases/latest')
    release = json.loads(text)
    latest = release.get('tag_name', '').lstrip('v')
    if not latest:
        raise ValueError('Invalid WowUp release response')
    item = {'name': 'WowUp CurseForge' if cf else 'WowUp', 'installedVersion': installed,
            'latestVersion': latest, 'state': version_state(installed, latest)}
    if prefs.get('wowup_release_channel_2_6', '1') != '1':
        item['state'] = 'unknown'
        item['detail'] = 'Abweichender Release-Kanal; Stable-Vergleich nur zur Information'
    addons_file = folder / 'addons.json'
    addons = read_json(addons_file)
    addons = list(addons.values()) if isinstance(addons, dict) else addons
    addon_items = []
    for addon in addons:
        if addon.get('isIgnored'):
            continue
        before, after = addon.get('installedExternalReleaseId'), addon.get('externalLatestReleaseId')
        known = before is not None and after is not None
        differs = str(before) != str(after) if known else addon.get('installedVersion') != addon.get('latestVersion')
        addon_items.append({'name': addon.get('name', 'Addon'), 'installedVersion': addon.get('installedVersion', ''),
                            'latestVersion': addon.get('latestVersion', ''), 'state': 'update' if differs else 'local',
                            'autoUpdate': addon.get('autoUpdateEnabled', False)})
    return result([item], 'WowUp · Official GitHub release', checked, error,
                  addons=addon_items, addonCheckedAt=int(addons_file.stat().st_mtime) if addons_file.exists() else 0,
                  addonPending=sum(a['state'] == 'update' for a in addon_items),
                  addonAutoUpdate=sum(a['autoUpdate'] for a in addon_items))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--local', action='store_true', help='Refresh local state using previously checked publisher metadata')
    args = parser.parse_args()
    publisher = Publisher(local=args.local)
    steam = HOME / '.local/share/Steam'
    providers = {'steam': lambda: steam_client(steam, publisher), 'steamGames': lambda: steam_status(steam),
                 'battlenet': lambda: battlenet_client(BNET, publisher),
                 'battlenetGames': lambda: battlenet_games(BNET, publisher),
                 'wowup': lambda: wowup_status(publisher), 'artcraft': lambda: artcraft_status(publisher)}
    def probe(pair):
        key, function = pair
        try:
            return key, function()
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            return key, {'error': str(error), 'items': [], 'pending': [], 'installed': 0, 'stale': True}
    with ThreadPoolExecutor(max_workers=6) as pool:
        data = dict(pool.map(probe, providers.items()))
    try:
        publisher.save()
    except OSError:
        pass  # Read-only metadata remains useful when the cache cannot be saved.
    print(json.dumps(data, ensure_ascii=False))


if __name__ == '__main__':
    main()
