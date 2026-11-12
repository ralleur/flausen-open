#!/usr/bin/env python3
"""Check idempotency, drift protection and complete rollback in a temporary HOME."""
from pathlib import Path
import json,os,subprocess,tempfile
ROOT=Path(__file__).resolve().parent.parent
BACKUP=Path.home()/'.local/state/flausen/settings-backups/20261102-172000-793049'
with tempfile.TemporaryDirectory(prefix='flausen-settings-test-') as tmp:
    home=Path(tmp);env=dict(os.environ,HOME=tmp)
    original={}
    for entry in json.loads((BACKUP/'manifest.json').read_text()):
        if entry['backup'] is None:continue
        p=home/Path(entry['path']).relative_to(Path.home())
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes((BACKUP/entry['backup']).read_bytes());original[p]=p.read_bytes()
    # Entry points and the color CLI already existed unchanged in version one.
    for relative in ['.local/bin/caelestia-color','.config/quickshell/caelestia/modules/launcher/Content.qml','.config/quickshell/caelestia/modules/launcher/services/HermesDesktop.qml','.config/quickshell/caelestia/services/ContextMenuStore.qml']:
        dest=home/relative
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes((Path.home()/relative).read_bytes());original[dest]=dest.read_bytes()
    def run(*args):return subprocess.run(['python',str(ROOT/'install.py'),*map(str,args)],env=env,text=True,capture_output=True)
    checked=run('--check');assert checked.returncode==0,checked.stderr+checked.stdout
    first=run();assert first.returncode==0,first.stderr
    again=run();assert again.returncode==0 and 'no changes' in again.stdout,again.stdout
    backup=next((home/'.local/state/flausen/settings-backups').iterdir())
    changed=home/'.config/quickshell/caelestia/modules/nexus/Nexus.qml'
    installed=changed.read_bytes();changed.write_bytes(installed+b'\n// later local edit\n')
    before={p:p.read_bytes() for p in home.rglob('*') if p.is_file()}
    assert run().returncode!=0
    assert run('--restore',backup).returncode!=0
    assert all(p.read_bytes()==data for p,data in before.items())
    changed.write_bytes(installed)
    restored=run('--restore',backup);assert restored.returncode==0,restored.stderr
    assert all(p.read_bytes()==data for p,data in original.items())
    for entry in json.loads((backup/'manifest.json').read_text()):
        if entry['backup'] is None:assert not Path(entry['path']).exists()
report={'temporary_home':True,'idempotent':True,'install_drift_protected':True,'rollback_drift_protected':True,'originals_restored':True,'created_files_removed':True}
(ROOT/'evidence/install-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
