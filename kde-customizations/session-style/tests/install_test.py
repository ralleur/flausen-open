import importlib.util
from pathlib import Path
import tempfile
import unittest

def load(name, filename):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parents[1]/filename)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

class InstallerTest(unittest.TestCase):
    def test_lock_roundtrip(self):
        mod=load('lock','install-lock.py')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);mod.TARGET=root/'shell/contents';mod.STATE=root/'state';mod.CURRENT=mod.STATE/'current.json'
            mod.TARGET.mkdir(parents=True);(mod.TARGET.parent/'metadata.json').write_text('{}')
            old=mod.TARGET/'lockscreen/LockScreen.qml';old.parent.mkdir();old.write_text('previous UI')
            mod.install();mod.install();self.assertNotEqual(old.read_text(),'previous UI')
            mod.restore();self.assertEqual(old.read_text(),'previous UI')
            self.assertFalse((mod.TARGET/'shared/RalleurSessionScreen.qml').exists())
    def test_login_guard_and_restore(self):
        mod=load('login','install-login.py')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);mod.BASE=root/'private';mod.DROPIN=root/'units/style.conf';mod.STATE=root/'state';mod.CURRENT=mod.STATE/'current.json'
            mod.version=lambda:'plasma-login-manager 6.8.2-1'
            binary=root/'tested-binary';binary.write_bytes(b'\x7fELFtest')
            mod.install(binary);mod.install(binary)
            mod.DROPIN.write_text('manual change')
            with self.assertRaises(SystemExit):mod.restore()
            mod.DROPIN.write_bytes(b'[Service]\nExecStart=\nExecStart=/usr/local/libexec/ralleur-login/start\n')
            mod.restore();self.assertFalse(mod.DROPIN.exists())

if __name__=='__main__':unittest.main()
