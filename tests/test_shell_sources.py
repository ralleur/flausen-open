"""Exercise source assembly without access to the user's desktop configuration."""
import difflib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'installation/prepare-shell.py'
spec = importlib.util.spec_from_file_location('prepare_shell', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ShellSourcesTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'flausen'
        self.here = self.repo / 'installation'
        self.here.mkdir(parents=True)
        self.upstream = self.root / 'upstream'
        (self.upstream / 'shell').mkdir(parents=True)
        (self.upstream / 'shell/base.qml').write_text('upstream\n')
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.upstream), *args],
                                           stderr=subprocess.DEVNULL, text=True).strip()
        git('init')
        git('add', '.')
        git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
            'commit', '-m', 'Fixture')
        self.source = self.repo / 'canonical.qml'
        self.source.write_text('canonical\n')
        patch = ''.join(difflib.unified_diff(['canonical\n'], ['integrated\n'],
                                            fromfile='a/new.qml', tofile='b/new.qml')).encode()
        (self.here / 'shell-integration.patch').write_bytes(patch)
        self.lock = {'snapshot': 'fixture', 'upstream': {'commit': git('rev-parse', 'HEAD')},
                     'patch_sha256': module.sha(patch), 'files': [{
                         'target': 'new.qml', 'source': 'canonical.qml', 'mode': 0o644,
                         'source_sha256': module.sha(b'canonical\n'),
                         'sha256': module.sha(b'integrated\n')}]}
        self.write_lock()
        old_here, old_repo = module.HERE, module.REPO
        self.addCleanup(setattr, module, 'HERE', old_here)
        self.addCleanup(setattr, module, 'REPO', old_repo)
        module.HERE, module.REPO = self.here, self.repo
        self.output = self.root / 'assembled'

    def write_lock(self):
        (self.here / 'shell-lock.json').write_text(json.dumps(self.lock))

    def test_assembly_uses_committed_base_and_canonical_source(self):
        (self.upstream / 'shell/base.qml').write_text('uncommitted personal change\n')
        module.prepare(self.upstream, self.output)
        self.assertEqual((self.output / 'base.qml').read_text(), 'upstream\n')
        self.assertEqual((self.output / 'new.qml').read_text(), 'integrated\n')
        self.assertEqual(self.source.read_text(), 'canonical\n')

    def test_existing_destination_is_preserved(self):
        self.output.mkdir()
        (self.output / 'personal').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            module.prepare(self.upstream, self.output)
        self.assertEqual((self.output / 'personal').read_text(), 'keep')

    def test_source_drift_aborts_without_output(self):
        self.source.write_text('new development\n')
        with self.assertRaisesRegex(ValueError, 'Source changed'):
            module.prepare(self.upstream, self.output)
        self.assertFalse(self.output.exists())

    def test_bad_result_leaves_no_partial_destination(self):
        self.lock['files'][0]['sha256'] = 'invalid'
        self.write_lock()
        with self.assertRaisesRegex(ValueError, 'differs'):
            module.prepare(self.upstream, self.output)
        self.assertFalse(self.output.exists())

    def test_wrong_upstream_is_rejected(self):
        self.lock['upstream']['commit'] = '0' * 40
        self.write_lock()
        with self.assertRaisesRegex(ValueError, 'Wrong Caelestia'):
            module.prepare(self.upstream, self.output)
        self.assertFalse(self.output.exists())

    def test_manifest_cannot_escape_destination(self):
        self.lock['files'][0]['target'] = '../escape.qml'
        self.write_lock()
        with self.assertRaisesRegex(ValueError, 'escapes'):
            module.prepare(self.upstream, self.output)
        self.assertFalse((self.root / 'escape.qml').exists())


if __name__ == '__main__':
    unittest.main()
