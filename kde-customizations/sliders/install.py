#!/usr/bin/env python3
"""Install shared slider visuals after a backup; preserve the first baseline."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime
HERE=Path(__file__).resolve().parent
shell=Path.home()/'.config/quickshell/caelestia'
state=Path.home()/'.local/state/flausen/sliders'
ledger=state/'installed.json'
previous=json.loads(ledger.read_text()) if ledger.exists() else {}
files={shell/p.relative_to(HERE/'overlay'):p for p in (HERE/'overlay').rglob('*.qml')}
style=HERE.parent/'taskbar/menu-style'
for helper in ['MenuPrimarySurface','PrimaryControlFill']:
    files[shell/('components/'+helper+'.qml')]=style/(helper+'.qml')
files[shell/'services/MenuStyle.qml']=style/'MenuStyle.qml'
files[shell/'modules/osd/SegmentedSlider.qml']=HERE.parent/'taskbar/osd-glass/SegmentedSlider.qml'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
for dest,src in files.items():
    if dest.is_symlink():raise SystemExit(f'Preserving symlink: {dest}')
    if str(dest) in previous and digest(dest) not in (previous[str(dest)],digest(src)):raise SystemExit(f'Preserving local change: {dest}')
changed={d:s for d,s in files.items() if digest(d)!=digest(s)}
if changed:
    backup=state/datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup.mkdir(parents=True)
    manifest=[]
    for dest,src in changed.items():
        rel=dest.relative_to(shell);old=backup/rel
        if dest.exists():old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,old)
        manifest.append({'path':str(dest),'existed':dest.exists(),'installed':digest(src)})
        dest.parent.mkdir(parents=True,exist_ok=True)
        tmp=dest.with_suffix('.qml.new');shutil.copyfile(src,tmp);tmp.replace(dest)
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Installed {len(changed)} files. Backup: {backup}')
state.mkdir(parents=True,exist_ok=True)
ledger.write_text(json.dumps({str(d):digest(d) for d in files},indent=2)+'\n')
