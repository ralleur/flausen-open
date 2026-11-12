"""Profile isolation and native-message framing without changing the live desktop."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load('spotify_install', ROOT / 'install.py')
host = load('spotify_host', ROOT / 'spotify-header/native_host.py')


class HeaderTests(unittest.TestCase):
    def test_profile_isolation_and_reinstallation(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / 'spotify'
            extension = installer.install_header(profile)
            self.assertEqual(extension.resolve(), ROOT / 'spotify-header')
            path = profile / 'NativeMessagingHosts/org.flausen.spotify_header.json'
            first = path.read_text()
            manifest = json.loads(first)
            self.assertEqual(manifest['allowed_origins'], [
                'chrome-extension://meoppijogbjbecpogbeihlnlglegiebg/'])
            self.assertTrue(Path(manifest['path']).is_file())
            installer.install_header(profile)
            self.assertEqual(first, path.read_text())
            self.assertEqual(set(Path(tmp).iterdir()), {profile})

    def test_existing_header_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)
            (profile / 'flausen-header').mkdir()
            with self.assertRaises(SystemExit):
                installer.install_header(profile)
            self.assertFalse((profile / 'NativeMessagingHosts').exists())

    def test_partial_native_message_reads(self):
        class Fragmented(io.BytesIO):
            def read(self, size):
                return super().read(min(size, 2))
        self.assertEqual(host.read_exact(Fragmented(b'abcdef'), 6), b'abcdef')
        with self.assertRaises(EOFError):
            host.read_exact(Fragmented(b'abc'), 6)

    def test_no_action_before_window_identification(self):
        bridge = object.__new__(host.Bridge)
        bridge.window = None
        with self.assertRaisesRegex(ValueError, 'not identified'):
            bridge.handle({'action': 'enable'})
        with self.assertRaisesRegex(ValueError, 'Invalid window token'):
            bridge.handle({'action': 'identify', 'token': 'anything'})


if __name__ == '__main__':
    unittest.main()
