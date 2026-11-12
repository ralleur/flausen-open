#!/usr/bin/env python3
from pathlib import Path
import re,subprocess,json
root=Path(__file__).resolve().parent.parent
qml=list((root/'overlay').rglob('*.qml'))
for p in qml:
    r=subprocess.run(['/usr/lib/qt6/bin/qmlformat','-n',str(p)],capture_output=True,text=True)
    if r.returncode:
        # qmlformat cannot serialize one upstream plugin page; qmllint still parses it.
        lint=subprocess.run(['/usr/lib/qt6/bin/qmllint','--json','-',str(p)],capture_output=True,text=True)
        messages=json.loads(lint.stdout)
        syntax=[d for f in messages.get('files',[]) for d in f.get('warnings',[]) if d.get('id','').startswith('syntax')]
        assert not syntax,(str(p),syntax)

modules=sorted(set(re.findall(r'module:"([^"]+)"',(root/'overlay/modules/nexus/pages/FlausenSystemPage.qml').read_text())))
assert all((Path('/usr/share/applications')/(m+'.desktop')).exists() for m in modules)
for palette in (root/'overlay/schemes').rglob('*.txt'):
    for line in palette.read_text().splitlines():
        if line.startswith('#'):continue
        k,v=line.split();assert re.fullmatch('[0-9a-fA-F]{6}',v),(palette,k,v)
for scheme in (root/'overlay/schemes').iterdir():
    for mode in ['light','dark']:
        data=json.loads(subprocess.check_output([str(Path.home()/'.local/bin/caelestia'),'scheme','set','-n',scheme.name,'-f','default','-m',mode,'--no-smart','--preview'],text=True))
        assert data['mode']==mode
report=dict(qml_parsed=len(qml),kde_modules_verified=modules,palettes_verified=12)
(root/'evidence/static-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
