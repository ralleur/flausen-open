import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1]/'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        installer.HOME = Path(self.temp.name)
        installer.ROOT = installer.HOME/'.local/share/flausen-task-manager'
        installer.SHARED = installer.HOME/'.config/quickshell/caelestia'
        installer.STATE = installer.HOME/'.local/state/flausen/task-manager-installed.json'
        for rel in ['services/MenuStyle.qml', 'components/MenuText.qml', 'modules/nexus/flausen/FlausenStyle.qml']:
            path = installer.SHARED/rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture')
        module = installer.HOME/'.local/lib/qt6/qml/Flausen/Settings/qmldir'
        module.parent.mkdir(parents=True)
        module.write_text('fixture')

    def tearDown(self):
        self.temp.cleanup()

    def test_preview_idempotence_and_guarded_rollback(self):
        with contextlib.redirect_stdout(io.StringIO()):
            installer.install(dry_run=True)
            self.assertFalse(installer.ROOT.exists())
            installer.install()
            backups = list((installer.HOME/'.local/state/flausen/task-manager-backups').iterdir())
            self.assertEqual(len(backups), 1)
            installer.install()
            self.assertEqual(len(list(backups[0].parent.iterdir())), 1)
            file = installer.ROOT/'shell.qml'
            original = file.read_bytes()
            file.write_text('local edit')
            with self.assertRaises(SystemExit):
                installer.install()
            with self.assertRaises(SystemExit):
                installer.restore(backups[0])
            self.assertEqual(file.read_text(), 'local edit')
            file.write_bytes(original)
            installer.restore(backups[0])
            self.assertFalse(file.exists())
            self.assertFalse(installer.STATE.exists())
            self.assertFalse((installer.ROOT/'services').is_symlink())


if __name__ == '__main__':
    unittest.main()
