#!/usr/bin/env python3
"""Render the production QML components, with live data, without a compositor.

These are explicitly NOT desktop screenshots or proof of compositor behavior.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
records=[]
with tempfile.TemporaryDirectory(prefix='ralleur-render-') as tmp:
    tmp=Path(tmp)
    shutil.copy2(ROOT/'preview.qml',tmp/'shell.qml')
    (tmp/'qml').symlink_to(ROOT/'qml')
    env=os.environ.copy()
    env.update(RALLEUR_ROOT=str(ROOT),RALLEUR_STATE=str(tmp/'state'),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software')
    def cli(*args): return subprocess.run([str(ROOT/'bin/ralleur'),*args],env=env,check=True,stdout=subprocess.DEVNULL)
    def ipc(action,*args): return subprocess.run(['qs','-p',str(tmp/'shell.qml'),'ipc','call','preview',action,*map(str,args)],env=env,check=True,capture_output=True)
    cli('theme','dark')
    with (out/'render.log').open('w') as log:
        for mode in ('light','dark'):
            cli('theme',mode)
            for width,height in [(1586,992),(1280,800),(1920,1080),(2560,1600),(3440,1440)]:
                env.update(RALLEUR_WIDTH=str(width),RALLEUR_HEIGHT=str(height))
                process=subprocess.Popen(['qs','-p',str(tmp/'shell.qml')],env=env,stdout=log,stderr=log)
                try:
                    for _ in range(50):
                        result=subprocess.run(['qs','-p',str(tmp/'shell.qml'),'ipc','show'],env=env,capture_output=True)
                        if result.returncode==0: break
                        if process.poll() is not None: raise RuntimeError('QML engine failed; see render.log')
                        time.sleep(.1)
                    time.sleep(3.2)  # First actual /proc metrics sample; no placeholder values.
                    path=out/f'components-{mode}-{width}x{height}.png'
                    path.unlink(missing_ok=True)
                    ipc('capture',path)
                    from PIL import Image
                    for attempt in range(100):
                        try:
                            with Image.open(path) as image:
                                image.load()
                                assert image.size==(width,height), (path,image.size)
                            break
                        except (OSError, SyntaxError):
                            if attempt == 99: raise
                            time.sleep(.05)
                    records.append({'theme':mode,'size':[width,height],'file':path.name,'dimensionCheck':'PASS','kind':'Production QML component render, live data; not a compositor screenshot'})
                finally:
                    process.terminate()
                    try: process.wait(timeout=3)
                    except subprocess.TimeoutExpired: process.kill(); process.wait()
(out/'render-matrix.json').write_text(json.dumps(records,indent=2)+'\n')
print(f'{len(records)} QML component renders, both themes; no compositor assertions.')
