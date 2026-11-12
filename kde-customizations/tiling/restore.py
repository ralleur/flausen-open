#!/usr/bin/env python3
"""Restore the saved Krohnkite package and only the settings changed here."""
import configparser
import json
from pathlib import Path
import shutil
import subprocess

state = Path.home() / '.local/state/ralleur-tiling'
backup = Path((state / 'baseline').read_text().strip())
settings = json.loads((Path((state / 'latest').read_text().strip()) / 'settings.json').read_text())
original = configparser.RawConfigParser(strict=False, delimiters=('=',), interpolation=None)
original.optionxform = str
original.read(backup / 'kwinrc')
def run(*args):
    return subprocess.check_output(args, text=True).strip()
target = Path.home() / '.local/share/kwin/scripts/krohnkite'
# Rename the current package for recovery; never delete the saved original.
retired = state / 'restored-package'
if retired.exists():
    raise SystemExit('A previous restored-package exists; move it aside before restoring again.')
run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'ralleur-tiling-guard')
run('qdbus6', 'org.kde.KWin', '/Scripting', 'unloadScript', 'krohnkite')
target.rename(retired)
shutil.copytree(backup / 'krohnkite', target)
for group, entries in settings.items():
    for key in entries:
        command = ['kwriteconfig6', '--file', 'kwinrc', '--group', group, '--key', key]
        if original.has_option(group, key):
            command.append(original.get(group, key))
        else:
            command.append('--delete')
        run(*command)
run('qdbus6', 'org.kde.KWin', '/KWin', 'reconfigure')
run('qdbus6', 'org.kde.KWin', '/Scripting', 'start')
print('Restored package and changed settings from ' + str(backup))
