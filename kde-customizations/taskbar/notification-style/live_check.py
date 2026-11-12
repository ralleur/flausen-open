from pathlib import Path
import subprocess,json,time,statistics
shell=Path.home()/'.config/quickshell/caelestia';out=Path(__file__).resolve().parent.parent/'evidence'
def call(method,*args):return subprocess.check_output(['quickshell','ipc','-p',str(shell),'call','notificationTest-HDMI-A-2',method,*map(str,args)],text=True)
def state():return json.loads(call('inspect'))
r={}
production=shell/'modules/drawers/ContentWindow.qml'
original=production.read_text()
if 'notificationTest-' in original: raise SystemExit('Remove an existing notification probe first.')
probe=(Path(__file__).resolve().parent/'LiveProbe.qml.inc').read_text()
patched=original.replace('import QtQuick\n','import QtQuick\nimport QtQuick.Window\nimport QtTest\n').replace('    // Bar glass uses',probe+'\n    // Bar glass uses')
assert patched != original
try:
 production.write_text(patched)
 subprocess.run(['systemctl','--user','restart','caelestia-shell.service'],check=True)
 time.sleep(5)
 time.sleep(1)
 for extra in [False,True]:
  allframes=[]
  for n in range(3):
   call('sample',str(extra).lower());call('prepare');time.sleep(.7)
   s=state();assert s['visible'] and s['pool']['count']==8 and len([x for x in s['slots'] if x['width']])==3,s
   call('cleanup');time.sleep(.7);allframes+=json.loads(call('samples'))
  allframes.sort();r['framesWithExtraBlur' if extra else 'framesWithoutExtraBlur']={'samples':len(allframes),'medianMs':statistics.median(allframes),'p95Ms':allframes[int(len(allframes)*.95)],'maxMs':max(allframes)}
 call('prepare');time.sleep(.7);s=state();r['stack']=s
 # Primary action, close, hover timeout and swipe use native Qt pointer dispatch.
 g=s['slots'][0];call('pointer','click',g['right']-78,g['bottom']-36);assert state()['invoked']==1
 call('pointer','move',g['x']+95,g['y']+50);time.sleep(.1)
 d=json.loads(call('detail'))
 def find(item):
  result=[]
  if 'expanded' in item:result.append(item)
  for c in item.get('children',[]):result+=find(c)
  return result
 cards=find(d);assert cards[0]['timerRunning']==False,cards[0];r['hoverPausesTimeout']=True
 call('pointer','move',2000,700)
 # Close first card.
 call('pointer','click',g['right']-32,g['y']+26);time.sleep(.5)
 assert len([g for g in state()['slots'] if g['width']])==2;r['close']=True
 call('cleanup');time.sleep(.5);call('prepare');time.sleep(.5);call('longText');time.sleep(.5)
 s=state();assert s['slots'][2]['height']>160,s;r['longText']=s
 subprocess.run(['spectacle','-b','-n','-f','-o','/tmp/notification-long.png'],check=True)
 # Swipe first card to the right, outside its clearing threshold.
 g=s['slots'][0];x=g['x']+80;y=g['y']+55
 call('pointer','press',x,y)
 for i in range(1,11):call('pointer','move',x+i*30,y)
 call('pointer','release',x+300,y);time.sleep(.6)
 assert len([g for g in state()['slots'] if g['width']])==2;r['swipeDismiss']=True
 call('cleanup');time.sleep(.5);call('prepare');time.sleep(.7)
 call('pointer','move',2000,700);time.sleep(.1)
 subprocess.run(['spectacle','-b','-n','-f','-o',str(out/'notification-smoke-live.png')],check=True)
 r['finalStack']=state()
 from PIL import Image
 slots=[g for g in r['finalStack']['slots'] if g['width']]
 image=Image.open(out/'notification-smoke-live.png')
 image.crop((int(slots[0]['x'])-16,int(slots[0]['y'])-16,int(slots[0]['right'])+16,int(slots[-1]['bottom'])+16)).save(out/'notification-smoke-cards.png')
 (out/'notification-smoke-live.png').unlink()
 call('cleanup');time.sleep(.5);r['closedPool']=state();assert r['closedPool']['pool']['count']==8 and r['closedPool']['pool']['active']==0
 r['primaryAction']=True
 r['dndPreserved']=subprocess.check_output(['quickshell','ipc','-p',str(shell),'call','notifs','isDndEnabled'],text=True).strip()
 r['passed']=True;(out/'notification-style-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
finally:
 try: call('cleanup')
 except subprocess.CalledProcessError: pass
 if production.read_text()!=patched: raise RuntimeError('Production file changed during testing; remove the probe manually.')
 production.write_text(original)
 subprocess.run(['systemctl','--user','restart','caelestia-shell.service'],check=True)
