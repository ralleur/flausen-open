"""Verify reversible integration without touching the user's session."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('branding',Path(__file__).with_name('install.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class InstallationTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        self.patch=patch.dict(os.environ,{'XDG_CONFIG_HOME':str(root/'config')});self.patch.start();self.addCleanup(self.patch.stop)
        m.DATA=root/'data';m.STATE=root/'state';m.CURRENT=m.STATE/'branding.json';m.CONFIG=root/'config/caelestia/shell.json'
        m.CONFIG.parent.mkdir(parents=True);m.CONFIG.write_text(json.dumps({'general':{'logo':'original'},'volume':42}))
        supported=root/'config/quickshell/caelestia/utils/SysInfo.qml';supported.parent.mkdir(parents=True);supported.write_text('GlobalConfig.general.logo')
    def test_restore_preserves_other_changes(self):
        m.install();m.install()
        cfg=m.config();cfg['volume']=75;m.CONFIG.write_text(json.dumps(cfg))
        m.restore()
        self.assertEqual(m.config(),{'general':{'logo':'original'},'volume':75})
        self.assertFalse((m.DATA/'applications/flausen-os-about.desktop').exists())
    def test_refuse_changed_assets(self):
        m.install()
        (m.DATA/'flausen-os/branding/About.qml').write_text('manual change')
        with self.assertRaises(SystemExit):m.restore()
        self.assertTrue(m.CURRENT.exists())
    def test_refuse_changed_logo(self):
        m.install();cfg=m.config();cfg['general']['logo']='my logo';m.CONFIG.write_text(json.dumps(cfg))
        with self.assertRaises(SystemExit):m.restore()
    def test_rollback_after_write_failure(self):
        original=m.save
        def fail(path,content):
            if path.name=='About.qml':raise OSError('simulated write failure')
            original(path,content)
        with patch.object(m,'save',fail):
            with self.assertRaises(OSError):m.install()
        self.assertEqual(m.config()['general']['logo'],'original')
        self.assertFalse(m.CURRENT.exists())
if __name__=='__main__':unittest.main()
