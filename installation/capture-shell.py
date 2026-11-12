#!/usr/bin/env python3
from pathlib import Path
import subprocess,hashlib,json,difflib,collections
import argparse
parser=argparse.ArgumentParser(description='Capture reviewed shell SOURCE changes into a NEW directory; no installation.')
parser.add_argument('--upstream',type=Path,required=True)
parser.add_argument('--shell',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--snapshot',required=True)
args=parser.parse_args()
repo=Path(__file__).resolve().parents[1];up=args.upstream.resolve();live=args.shell.resolve()
revision=subprocess.check_output(['git','-C',str(up),'rev-parse','HEAD'],text=True).strip()
expected=json.loads((repo/'installation/shell-lock.json').read_text())['upstream']
if revision!=expected['commit']:raise SystemExit('Use the pinned upstream revision.')
if subprocess.check_output(['git','-C',str(up),'status','--porcelain','--untracked-files=no']):raise SystemExit('Upstream tracked files must be clean.')
if args.output.exists():raise SystemExit('Choose a new output directory.')
sha=lambda d:hashlib.sha256(d).hexdigest()
files=subprocess.check_output(['git','-C',str(repo),'ls-files','-z']).decode().split('\0')
sources={};byname=collections.defaultdict(list);byhash=collections.defaultdict(list)
for f in files:
 p=repo/f
 if f.startswith(('kde-customizations/','branding/')) and p.is_file() and '/evidence/' not in f and '/tests/' not in f:
  sources[f]=p.read_bytes();byname[p.name].append(f);byhash[sha(sources[f])].append(f)
items=[];patch=[];added=[]
for p in sorted(live.rglob('*')):
 rel=p.relative_to(live).as_posix()
 if not p.is_file() or p.is_symlink() or p.suffix not in ('.qml','.js','.py','.sh','.svg','.ts') or rel.startswith('assets/icons/'):continue
 data=p.read_bytes();base=up/'shell'/rel;old=base.read_bytes() if base.is_file() else b''
 if old==data:continue
 item={'target':rel,'sha256':sha(data),'mode':p.stat().st_mode&0o777}
 if sha(data) in byhash:
  source=sorted(byhash[sha(data)],key=lambda f:(len(f),f))[0];old=sources[source]
  item.update(source=source,source_sha256=sha(old))
 else:
  # Reuse the nearest canonical component source before encoding the remaining delta.
  candidates=byname[p.name]
  ratio=lambda d:difflib.SequenceMatcher(None,d.decode().splitlines(),data.decode().splitlines(),autojunk=False).ratio()
  best=max(candidates,key=lambda f:ratio(sources[f]),default=None)
  if best and ratio(sources[best])>ratio(old):
   old=sources[best];item.update(source=best,source_sha256=sha(old))
  if not old and not base.exists():added.append(rel)
  if old and not old.endswith(b'\n') or not data.endswith(b'\n'):raise SystemExit('Missing final newline '+rel)
  patch+=list(difflib.unified_diff(old.decode().splitlines(True),data.decode().splitlines(True),fromfile='a/'+rel if old else '/dev/null',tofile='b/'+rel))
 items.append(item)
patchdata=''.join(patch).encode();args.output.mkdir(parents=True);(args.output/'shell-integration.patch').write_bytes(patchdata)
lock={'schema_version':1,'snapshot':args.snapshot,'upstream':expected,'patch_sha256':sha(patchdata),'files':items,'excluded':['Personal shell.json, context_menu.json and Qt settings','Compiled binaries and translation catalogs','Updater metadata and checkout paths','Icons installed by the upstream installer']}
(args.output/'shell-lock.json').write_text(json.dumps(lock,indent=2,ensure_ascii=False)+'\n')
print(len(items),'files;',sum('source'in x for x in items),'canonical references;',len(patchdata),'patch bytes; new files:',added)
print('Review the diff and privacy of every captured change before updating installation/.')
