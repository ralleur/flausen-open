#!/usr/bin/env python3
"""Native weather QA. Temporarily instruments two files, then restores them."""
import subprocess,json,time,statistics,argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--mock',type=Path,default=Path.home()/'Downloads/Dunkles Wetter-Popover mit Stundenprognose.png')
args=parser.parse_args()
source=Path(__file__).resolve().parent
shell=Path.home()/'.config/quickshell/caelestia';out=source.parent/'evidence'
window=shell/'modules/drawers/ContentWindow.qml'
clip=shell/'modules/bar/popouts/ClipWrapper.qml'
original=window.read_text();clipOriginal=clip.read_text()
if 'weatherTest-' in original: raise SystemExit('A weather probe already exists; remove it first.')
probe=(source/'LiveProbe.qml.inc').read_text()
patched=original.replace('import QtQuick\n','import QtQuick\nimport QtQuick.Window\nimport QtTest\n').replace('    // Bar glass uses',probe+'\n    // Bar glass uses')
clipPatched=clipOriginal.replace('    id: root\n','    id: root\n    readonly property alias weatherPoolForTest: popoutSmoke\n',1)
assert patched!=original and clipPatched!=clipOriginal
try:
 window.write_text(patched);clip.write_text(clipPatched)
 subprocess.run(['systemctl','--user','restart','caelestia-shell.service'],check=True)
 time.sleep(5)
 def call(m,*a):return subprocess.check_output(['quickshell','ipc','-p',str(shell),'call','weatherTest-HDMI-A-2',m,*map(str,a)],text=True)
 def state():return json.loads(call('inspect'))
 def nodes(s):
  r=[s]
  for c in s.get('children',[]):r+=nodes(c)
  return r
 def named(s,name):return next(n for n in nodes(s['current']) if n['name']==name)
 def click(s,name):
  n=named(s,name);call('pointer','click',n['x']+n['width']/2,n['y']+n['height']/2);time.sleep(.3)
 def capture(name,s):
  subprocess.run(['spectacle','-b','-n','-f','-o','/tmp/weather-check-full.png'],check=True)
  g=s['popout'];Image.open('/tmp/weather-check-full.png').crop((int(g['x']),int(g['y']),int(g['x']+g['width']),int(g['y']+g['height']))).save(out/name)
 call('open');time.sleep(.8);s=state();assert s['open'] and s['current'] and s['scale']==1.15
 r={'initial':{k:v for k,v in s.items() if k!='current'}}
 # Native Qt dispatch, no weather-setting changes.
 click(s,'weatherNext');s=state();assert s['offset']==3
 click(s,'weatherPrevious');s=state();assert s['offset']==0
 before=s['popout']['height'];click(s,'weatherExpand');s=state();assert not s['expanded'] and s['popout']['height']<before
 click(s,'weatherExpand');s=state();assert s['expanded'];r['navigationAndCollapse']=True
 # Open city selector, inspect input and close it without applying a location.
 city=next(n for n in nodes(s['current']) if n.get('text')=='Köln');call('pointer','click',city['x']+30,city['y']+15);time.sleep(.3)
 s=state();assert s['popout']['height']>before+60;assert any('StyledTextField' in n['type'] for n in nodes(s['current']))
 call('pointer','click',city['x']+30,city['y']+15);r['locationSelectorOpened']=True
 for case in ['large','narrow','empty','flat','rain','normal']:
  call('open');time.sleep(.15);call('scenario',case);time.sleep(.5);s=state();r[case]={k:v for k,v in s.items() if k!='current'}
  assert 0<s['popout']['height']<2000
  if case=='empty':assert any(n.get('text')=='Weather unavailable' for n in nodes(s['current']))
  if case in ['large','narrow','empty','rain','normal']:
   call('pointer','move',s['popout']['x']+10,s['popout']['y']+s['popout']['height']-10);capture('weather-smoke-'+case+'.png',s)
  if case=='normal':
   r['text']=[n['text'] for n in nodes(s['current']) if n.get('text') and len(n['text'])<100]
 call('close');r['passed']=True;(out/'weather-smoke-check.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS: paging, collapse, location selector; normal/large/narrow/empty/flat/rain views')
 
 r={}
 for extra in [False,True]:
  frames=[];pools=[]
  for i in range(3):
   call('sample',str(extra).lower());call('open');time.sleep(.7);pools.append(json.loads(call('pool')));call('close');time.sleep(.7);frames+=json.loads(call('frames'))
  frames.sort();r['withExtraBlur' if extra else 'withoutExtraBlur']={'samples':len(frames),'medianMs':statistics.median(frames),'p95Ms':frames[int(len(frames)*.95)],'maxMs':max(frames),'pools':pools}
 call('sample','true');call('frames');call('open');time.sleep(1)
 s=json.loads(call('inspect'));subprocess.run(['spectacle','-b','-n','-f','-o','/tmp/weather-final-full.png'],check=True)
 g=s['popout'];im=Image.open('/tmp/weather-final-full.png').crop((int(g['x']),int(g['y']),int(g['x']+g['width']),int(g['y']+g['height'])));im.save(out/'weather-smoke-normal.png')
 if args.mock.exists():
  mock=Image.open(args.mock).crop((113,137,973,1340));mock=mock.resize((im.width,round(mock.height*im.width/mock.width)),Image.Resampling.LANCZOS)
  comparison=Image.new('RGB',(im.width*2+60,max(im.height,mock.height)+60),'#172126');d=ImageDraw.Draw(comparison);font=ImageFont.truetype('/usr/share/fonts/noto/NotoSans-Regular.ttf',15);d.text((20,10),f'Mock · {im.width} px',font=font,fill='white');d.text((im.width+40,10),f'Live · {im.width} px',font=font,fill='white');comparison.paste(mock,(20,40));comparison.paste(im,(im.width+40,40));comparison.save(out/'weather-smoke-comparison.png');call('close')
 r['limits']='frameSwapped intervals, including idle gaps; not DRM presentation timing';(out/'weather-smoke-performance.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
finally:
 if window.read_text()!=patched or clip.read_text()!=clipPatched:
  raise RuntimeError('Shell source changed during testing; remove only the weather probe and test alias manually.')
 window.write_text(original);clip.write_text(clipOriginal)
 subprocess.run(['systemctl','--user','restart','caelestia-shell.service'],check=True)
