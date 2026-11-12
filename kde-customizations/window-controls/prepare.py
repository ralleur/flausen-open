#!/usr/bin/env python3
"""Prepare a narrowly patched, separately named Darkly decoration."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
REVISION = '812546ed69ff7e55cf3cb0fe2b79379e85101bef'  # Darkly v0.5.42
parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
args = parser.parse_args()
source = args.source.resolve()
if not source.exists():
    subprocess.run(['git', 'clone', '--depth', '1', '--branch', 'v0.5.42',
                    'https://github.com/Bali10050/Darkly.git', str(source)], check=True)
assert subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() == REVISION
check = subprocess.run(['git', '-C', str(source), 'apply', '--reverse', '--check', str(ROOT / 'darkly.patch')], capture_output=True)
if check.returncode != 0:
    subprocess.run(['git', '-C', str(source), 'apply', '--check', str(ROOT / 'darkly.patch')], check=True)
    subprocess.run(['git', '-C', str(source), 'apply', str(ROOT / 'darkly.patch')], check=True)
metadata = source / 'kdecoration/darkly.json'
data = json.loads(metadata.read_text())
data['KPlugin'] = {'Id': 'org.kde.ralleur', 'Name': 'Ralleur',
                   'Description': 'Darkly with line, square and X window controls'}
metadata.write_text(json.dumps(data, indent=4) + '\n')

shutil.copy2(ROOT / 'controls.h', source / 'kdecoration/ralleurcontrols.h')
