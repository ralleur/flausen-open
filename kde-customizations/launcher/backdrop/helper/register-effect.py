#!/usr/bin/python3
import os
import subprocess
pid = os.environ['MAINPID']
subprocess.run(['kwriteconfig6', '--file', 'kwinrc', '--group', 'Effect-ralleur-start-backdrop', '--key', 'HelperPid', pid], check=True)
loaded = subprocess.check_output(['qdbus6', 'org.kde.KWin', '/Effects', 'org.kde.kwin.Effects.isEffectLoaded', 'ralleur-start-backdrop'], text=True).strip()
if loaded != 'true':
    result = subprocess.check_output(['qdbus6', 'org.kde.KWin', '/Effects', 'org.kde.kwin.Effects.loadEffect', 'ralleur-start-backdrop'], text=True).strip()
    if result != 'true':
        raise SystemExit('Cannot load start menu fade effect')
subprocess.run(['qdbus6', 'org.kde.KWin', '/Effects', 'org.kde.kwin.Effects.reconfigureEffect', 'ralleur-start-backdrop'], check=True)
