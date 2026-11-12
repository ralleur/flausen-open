import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bin'))
import generate
import metrics


class DesignTests(unittest.TestCase):
    def test_generated_consumers(self):
        tokens=generate.generate()
        for mode,c in tokens['modes'].items():
            base=ROOT/'build/modes'/mode
            self.assertIn(c['text'],(base/'kitty.conf').read_text())
            self.assertIn(c['surface'],(base/'gtk.css').read_text())
            self.assertEqual(json.loads((base/'scheme.json').read_text())['colours']['onSurface'],c['text'][1:])
            import xml.etree.ElementTree as ET
            ET.parse(ROOT/f'assets/wallpapers/ralleur-{mode}.svg')

    def test_live_metrics_and_missing_filesystem(self):
        self.assertTrue(0 <= metrics.memory_stat() <= 100)
        self.assertTrue(0 <= metrics.disk_stat() <= 100)
        with self.assertRaises(OSError): metrics.disk_stat('/does-not-exist/ralleur')
        total,idle=metrics.cpu_stat()
        self.assertGreaterEqual(total,idle)

    def test_reference_integrity(self):
        import hashlib
        handoff=ROOT.parent/'ralleur-caelestia-codex-handoff'
        if not handoff.exists(): self.skipTest('handoff is outside release archive')
        for line in (handoff/'SHA256SUMS').read_text().splitlines():
            checksum,name=line.split(maxsplit=1)
            path=handoff/name.lstrip('*')
            if path.exists(): self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),checksum)


@unittest.skipUnless(os.environ.get('RALLEUR_TEST_UPSTREAM'),'set RALLEUR_TEST_UPSTREAM to the pinned git checkout')
class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.base=Path(self.temp.name)
        self.env=os.environ.copy()
        self.env.update(XDG_CONFIG_HOME=str(self.base/'user-config'),RALLEUR_CONFIG=str(self.base/'config'),RALLEUR_STATE=str(self.base/'state'),RALLEUR_DATA=str(self.base/'data'))
        self.original=self.base/'user-config/caelestia/shell.json'; self.original.parent.mkdir(parents=True)
        self.original.write_text('{"untouched":"existing KDE session"}\n')
        self.bin=self.base/'bin'; self.bin.mkdir()
        (self.bin/'ralleur-desktop').write_text('previous entrypoint')
        self.args=['install','--upstream',self.env['RALLEUR_TEST_UPSTREAM'],'--bin-dir',str(self.bin)]

    def tearDown(self): self.temp.cleanup()
    def run_cli(self,*args,ok=True):
        result=subprocess.run([str(ROOT/'bin/ralleur'),*args],env=self.env,text=True,capture_output=True)
        if ok: self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        else: self.assertNotEqual(result.returncode,0)
        return result

    def test_install_idempotence_themes_and_rollback(self):
        original=self.original.read_bytes()
        self.run_cli(*self.args)
        info=json.loads((self.base/'state/installation.json').read_text())
        self.assertTrue((Path(info['backup'])/'manifest.json').is_file())
        self.assertIn('Already installed',self.run_cli(*self.args).stdout)
        self.run_cli('theme','light'); self.run_cli('theme','toggle')
        self.assertEqual(json.loads((self.base/'state/theme.json').read_text())['mode'],'dark')
        self.assertEqual(self.original.read_bytes(),original)
        self.run_cli('rollback')
        self.assertEqual((self.bin/'ralleur-desktop').read_text(),'previous entrypoint')
        self.assertFalse((self.base/'config').exists())
        self.assertFalse((self.base/'data').exists())
        self.assertEqual(self.original.read_bytes(),original)

    def test_rollback_preserves_postinstall_changes(self):
        self.run_cli(*self.args)
        custom=self.base/'config/local.lua'; custom.write_text('-- personal settings\n')
        self.run_cli('rollback',ok=False)
        self.run_cli('rollback','--force')
        backups=self.base/'ralleur-desktop-backups'
        self.assertTrue(any(p.read_text()=='-- personal settings\n' for p in backups.rglob('local.lua')))

    def test_upgrade_preserves_user_extensions(self):
        self.run_cli(*self.args)
        custom=self.base/'config/local.lua'; custom.write_text('-- personal settings\n')
        native=self.base/'config/session/caelestia/shell.json'
        config=json.loads(native.read_text()); config['dashboard']['showWeather']=False
        native.write_text(json.dumps(config))
        self.run_cli(*self.args)
        self.assertEqual(custom.read_text(),'-- personal settings\n')
        self.assertFalse(json.loads(native.read_text())['dashboard']['showWeather'])

    def test_dry_run_and_wrong_revision(self):
        self.run_cli(*self.args,'--dry-run')
        self.assertFalse((self.base/'data').exists())
        bad=self.base/'bad-upstream'; bad.mkdir()
        self.run_cli('install','--upstream',str(bad),'--bin-dir',str(self.bin),ok=False)
        self.assertEqual((self.bin/'ralleur-desktop').read_text(),'previous entrypoint')

    def test_foreign_backup_cannot_overwrite_other_roots(self):
        self.run_cli(*self.args)
        info=json.loads((self.base/'state/installation.json').read_text())
        manifest=Path(info['backup'])/'manifest.json'
        content=json.loads(manifest.read_text())
        victim=self.base/'unrelated-config'; victim.write_text('preserve me')
        content['targets'][0]['path']=str(victim)
        manifest.write_text(json.dumps(content))
        self.run_cli('rollback','--force',ok=False)
        self.assertEqual(victim.read_text(),'preserve me')
        self.assertTrue((self.base/'data').is_dir())


if __name__=='__main__': unittest.main(verbosity=2)
