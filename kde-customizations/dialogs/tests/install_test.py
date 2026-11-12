import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('installer', Path(__file__).parents[1] / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class InstallTest(unittest.TestCase):
    def test_install_upgrade_restore_and_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            installer.HOME = root
            installer.CONFIG = root / 'config'
            installer.STATE = root / 'state'
            installer.CURRENT = installer.STATE / 'dialogs-installation.json'
            installer.PLUGIN_ROOT = root / 'plugins'
            current = ['darkly']
            def setting(value=None):
                if value is not None:
                    current[0] = value
                return current[0]
            installer.setting = setting
            build = root / 'build'
            library = build / 'plugins/styles/libralleurdialogs.so'
            library.parent.mkdir(parents=True)
            library.write_bytes(b'first build')
            installer.install(build)
            self.assertEqual(current[0], 'ralleur-dialogs')
            library.write_bytes(b'second build')
            installer.install(build)
            installed = installer.PLUGIN_ROOT / 'styles/libralleurdialogs.so'
            self.assertEqual(installed.read_bytes(), b'second build')
            installed.write_bytes(b'changed externally')
            with self.assertRaises(SystemExit):
                installer.restore()
            self.assertEqual(current[0], 'ralleur-dialogs')
            installed.write_bytes(b'second build')
            installer.restore()
            self.assertEqual(current[0], 'darkly')
            self.assertFalse(installed.exists())
            self.assertFalse(installer.CURRENT.exists())

if __name__ == '__main__':
    unittest.main()
