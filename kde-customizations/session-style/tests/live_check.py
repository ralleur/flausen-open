#!/usr/bin/env python3
"""Render real native greeters in testing mode; never locks the current session."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--login',type=Path,required=True)
parser.add_argument('--probe',type=Path,required=True)
parser.add_argument('--shell',type=Path,default=Path.home()/'.local/share/plasma/shells/caelestia.desktop')
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--avatar-user',help='Account whose configured avatar must load in both screens')
parser.add_argument('--avatar-source',help='Expected file URL for --avatar-user')
args=parser.parse_args()
args.out.mkdir(parents=True,exist_ok=True)
report={'loginSha256':hashlib.sha256(args.login.read_bytes()).hexdigest(),'checks':[]}
for kind in ['lock','login']:
    for mode in ['light','dark']:
        capture=(args.out/f'{kind}-{mode}.png').resolve()
        auth=(args.out/f'auth-{mode}.json').resolve()
        avatar=(args.out/f'avatar-{kind}-{mode}.json').resolve()
        env=os.environ.copy()
        env.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',
                   QT_PLUGIN_PATH=str(args.probe.resolve()),QT_QPA_GENERIC_PLUGINS='ralleurstyleprobe',
                   RALLEUR_PROBE_MODE=mode,RALLEUR_PROBE_CAPTURE=str(capture),
                   RALLEUR_PROBE_AVATAR=str(avatar),QT_FORCE_STDERR_LOGGING='1')
        avatar.unlink(missing_ok=True)
        command=['/usr/lib/kscreenlocker_greet','--testing','--shell',str(args.shell.resolve())]
        if kind=='login':
            env['RALLEUR_PROBE_AUTH']=str(auth)
            command=[str(args.login.resolve()),'--test']
        result=subprocess.run(command,env=env,capture_output=True,text=True,timeout=10)
        output=result.stdout+result.stderr
        (args.out/f'{kind}-{mode}.log').write_text(output)
        check={'kind':kind,'mode':mode,'exitCode':result.returncode,'captured':capture.is_file(),
               'qmlError':any(text in output for text in ['Error loading','is not a type','is not defined','Cannot assign','Failed to load','falling back'])}
        if kind=='login':check['auth']=json.loads(auth.read_text()) if auth.is_file() else {}
        check['avatars']=json.loads(avatar.read_text()) if avatar.is_file() else []
        report['checks'].append(check)
(args.out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert all(c['exitCode']==0 and c['captured'] and not c['qmlError'] for c in report['checks'])
assert all(all(c['auth'].get(k) is True for k in ['invoked','failureDisplayed','readyForRetry']) for c in report['checks'] if c['kind']=='login')
if args.avatar_user:
    assert args.avatar_source, '--avatar-source is required with --avatar-user'
    assert all(any(a['userName']==args.avatar_user and a['source']==args.avatar_source and a['loaded']
                   for a in c['avatars']) for c in report['checks']), 'Configured OS avatar did not load'
