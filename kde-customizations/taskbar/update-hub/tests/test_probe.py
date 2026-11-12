import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch
from urllib.error import URLError

spec = importlib.util.spec_from_file_location('probe', Path(__file__).parents[1] / 'probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeTests(unittest.TestCase):
    def test_valve_nested_keys_and_escaped_library_path(self):
        data = probe.keyvalues('// comment\n"AppState" { "name" "Game" "buildid" "123" "nested" { "buildid" "999" } "empty" "" }')
        self.assertEqual(data['AppState']['buildid'], '123')
        self.assertEqual(data['AppState']['empty'], '')
        with self.assertRaises(ValueError):
            probe.keyvalues('"AppState" { "name" "Partial"')

    def test_multiple_steam_libraries_and_download_state(self):
        with tempfile.TemporaryDirectory() as temp:
            base, extra = Path(temp) / 'Steam', Path(temp) / 'Other Library'
            for folder in (base, extra):
                (folder / 'steamapps').mkdir(parents=True)
            (base / 'steamapps/libraryfolders.vdf').write_text(f'"libraryfolders" {{ "0" {{ "path" "{base}" }} "1" {{ "path" "{extra}" }} }}')
            for folder, name, flags in ((base, 'Ready', 4), (extra, 'Pending', 6), (extra, 'Downloading', 1030)):
                (folder / f'steamapps/appmanifest_{name}.acf').write_text(f'"AppState" {{ "name" "{name}" "StateFlags" "{flags}" "BytesToDownload" "1000" "BytesDownloaded" "250" }}')
            data = probe.steam_status(base)
            self.assertEqual(data['installed'], 3)
            self.assertEqual(data['pending'], ['Downloading', 'Pending'])
            self.assertEqual(data['downloading'], 1)
            self.assertEqual(data['items'][1]['bytesDownloaded'], 250)

    def test_versions_do_not_offer_downgrades_or_guess_prereleases(self):
        self.assertEqual(probe.version_state('v2.9', '2.10'), 'update')
        self.assertEqual(probe.version_state('2.10', '2.10.0'), 'current')
        self.assertEqual(probe.version_state('2.11', '2.10'), 'ahead')
        self.assertEqual(probe.version_state('2.10-beta1', '2.10'), 'unknown')

    def test_offline_cache_keeps_last_success_and_error_across_local_refresh(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / 'cache.json'
            stamp = int(time.time()) - 3600
            url = 'https://publisher.example/versions'
            cache.write_text(json.dumps({url: {'text': 'known release', 'checkedAt': stamp}}))
            def offline(*args, **kwargs):
                raise URLError('offline')
            publisher = probe.Publisher(cache, opener=offline)
            text, checked, error = publisher.text(url)
            publisher.save()
            self.assertEqual((text, checked), ('known release', stamp))
            self.assertIn('offline', error)
            local = probe.Publisher(cache, local=True)
            self.assertEqual(local.text(url), (text, checked, error))

    def test_network_recovery_clears_old_error(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / 'cache.json'
            url = 'https://publisher.example/versions'
            cache.write_text(json.dumps({url: {'text': 'old', 'checkedAt': 1, 'error': 'offline'}}))
            publisher = probe.Publisher(cache, opener=lambda *a, **kw: io.BytesIO(b'new'))
            self.assertEqual(publisher.text(url)[0], 'new')
            self.assertNotIn('error', publisher.cache[url])

    def test_offline_without_cache_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            publisher = probe.Publisher(Path(temp) / 'absent', local=True)
            with self.assertRaisesRegex(RuntimeError, 'No online check'):
                publisher.text('https://publisher.example')

    def test_blizzard_region_not_first_row(self):
        data = 'Region!STRING:0|BuildId!DEC:4|VersionsName!String:0\n## seqn = 1\nus|100|1.0.100\neu|101|1.0.101\n'
        publisher = type('FakePublisher', (), {'text': lambda self, url: (data, 123, None)})()
        row, stamp, error = probe.blizzard_remote('wow', 'eu', publisher)
        self.assertEqual(row['VersionsName'], '1.0.101')
        self.assertEqual(stamp, 123)
        with self.assertRaises(ValueError):
            probe.blizzard_remote('wow', 'invalid', publisher)

    def test_blizzard_games_ignores_inactive_build(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build = root / 'Program Files (x86)/World of Warcraft/.build.info'
            build.parent.mkdir(parents=True)
            build.write_text('Branch!STRING:0|Active!DEC:1|Version!STRING:0|Product!STRING:0\neu|1|1.0.100|wow\neu|0|1.0.1|wow\n')
            remote = {'VersionsName': '1.0.101', 'BuildId': '101'}
            with patch.object(probe, 'blizzard_remote', return_value=(remote, int(time.time()), None)):
                status = probe.battlenet_games(root, None)
            self.assertEqual(len(status['items']), 1)
            self.assertEqual(status['pending'], ['World of Warcraft · Retail'])

    def test_steam_manifest_candidate_is_not_installed_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'package').mkdir()
            (root / 'logs').mkdir()
            (root / 'package/steam_client_steamrt64.manifest').write_text('"steamrt64" { "version" "200" }')
            (root / 'logs/bootstrap_log.txt').write_text('installed version 100, existing pending version 200')
            publisher = type('FakePublisher', (), {'text': lambda self, url: ('"steamrt64" { "version" "200" }', int(time.time()), None)})()
            status = probe.steam_client(root, publisher)
            self.assertEqual(status['items'][0]['installedVersion'], '100')
            self.assertEqual(status['pending'], ['Steam Client'])

    def test_artcraft_compares_live_feed_not_disabled_flatpak_origins(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            store = home / '.var/app/ai.storyteller.artcraft-launcher/data/ai.storyteller.artcraft-launcher/app.ron'
            store.parent.mkdir(parents=True)
            store.write_text('{"settings": "(auto_update:false,check_every:Hour)",\n}')
            process = subprocess.CompletedProcess([], 0, 'ai.storyteller.photocraft\tPhotoCraft\t0.18.0\n', '')
            feed = {'success': True, 'release_info': {'apps': {'photocraft': {'latest_release': {'version': '0.19.0'}}}}}
            publisher = type('FakePublisher', (), {'text': lambda self, url: (json.dumps(feed), int(time.time()), None)})()
            with patch.object(probe, 'HOME', home), patch.object(probe.subprocess, 'run', return_value=process):
                status = probe.artcraft_status(publisher)
            self.assertFalse(status['autoUpdate'])
            self.assertEqual(status['pending'], ['PhotoCraft'])
            self.assertEqual(status['items'][0]['latestVersion'], '0.19.0')

    def test_wowup_separates_online_app_and_cached_addons(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            state = home / '.local/state/linux-gaming-lab/wowup.json'
            state.parent.mkdir(parents=True)
            app = home / 'WowUp-CF-2.24.1.AppImage'
            app.touch()
            state.write_text(json.dumps({'path': str(app)}))
            store = home / '.config/WowUpCf'
            store.mkdir(parents=True)
            (store / 'addons.json').write_text(json.dumps({'one': {'name': 'Pending Addon', 'installedVersion': '1', 'latestVersion': '2', 'installedExternalReleaseId': '10', 'externalLatestReleaseId': '11', 'autoUpdateEnabled': True}, 'two': {'name': 'Ignored', 'isIgnored': True}}))
            publisher = type('FakePublisher', (), {'text': lambda self, url: ('{"tag_name":"v2.24.2"}', int(time.time()), None)})()
            with patch.object(probe, 'HOME', home):
                status = probe.wowup_status(publisher)
            self.assertEqual(status['pending'], ['WowUp CurseForge'])
            self.assertEqual(status['addonPending'], 1)
            self.assertEqual(status['addonAutoUpdate'], 1)
            self.assertGreater(status['addonCheckedAt'], 0)
            self.assertEqual(len(status['addons']), 1)

    def test_stale_result_never_becomes_current_just_because_read_now(self):
        status = probe.result([{'name': 'App', 'state': 'current'}], 'Publisher', int(time.time()) - 90000)
        self.assertTrue(status['stale'])
        self.assertLess(status['checkedAt'], time.time() - 86400)


if __name__ == '__main__':
    unittest.main()
