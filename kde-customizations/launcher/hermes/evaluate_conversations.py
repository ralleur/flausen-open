"""Real Hermes conversations, natural questions, real read tools, no system writes.

Checks actual returned facts against the current machine, rather than only
counting calls or a successful process exit. Run using the Hermes venv.
"""
import argparse,importlib.util,json,os,re,time
from pathlib import Path


def main():
 p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--only',default='')
 args=p.parse_args();os.environ['RALLEUR_HERMES_MODEL']=args.model
 spec=importlib.util.spec_from_file_location('evaluated_bridge',Path(__file__).with_name('bridge.py'))
 b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 # Known values were independently checked in the active AC profile and current files.
 cases=[('standby','Nach wie vielen Minuten geht mein Rechner automatisch in Standby?',lambda s:bool(re.search(r'180|10800|10[. ]800|3\s*Stund',s,re.I))),
        ('display','Nach welcher Zeit schaltet sich mein Bildschirm von allein aus?',lambda s:bool(re.search(r'175|10500|10[. ]500|2\s*Stunden.{0,15}55',s,re.I))),
        ('theme','Welches KDE-Farbschema ist derzeit eingestellt?',lambda s:'matugen alt' in s.lower()),
        ('dock','Welche Programme sind bei mir im Dock angeheftet?',lambda s:'dolphin' in s.lower() and 'steam' in s.lower()),
        ('autostart','Was startet bei meiner Anmeldung automatisch?',lambda s:'wowup' in s.lower() and bool(re.search('vnc|krfb',s,re.I))),
        ('audio','Wie laut ist der Rechner momentan eingestellt?',lambda s:bool(re.search(r'40\s*%',s))),
        ('missing_battery','Welcher Wert ist bei mir für die Akku-Standbyzeit ausdrücklich hinterlegt?',lambda s:bool(re.search(r'nicht|kein|nur.*(AC|Netz)',s,re.I)))]
 if args.only:cases=[c for c in cases if c[0] in args.only.split(',')]
 results=[]
 for key,question,check in cases:
  runner=b.Bridge();events=[]
  def emit(event,**data):
   events.append({'event':event,**data})
   if event=='approval':runner.handle({'action':'approve','id':data['id'],'allowed':False})
  b.emit=emit
  agent=runner.make_agent();runner.agent=agent
  from tools.registry import registry
  for name in ('open_app','set_volume'):
   entry=registry.get_entry(name)
   registry.register(name=name,toolset=entry.toolset,schema=entry.schema,
                     handler=lambda *a,**k:json.dumps({'error':'Read-only evaluation: no system changes allowed.'}))
  start=time.monotonic()
  print('START',args.model,key,flush=True)
  try:
   result=agent.run_conversation(question,system_message=b.SYSTEM,conversation_history=[])
   answer=result.get('final_response') or ''
   calls=[e['name'] for e in events if e['event']=='tool_start']
   passed=bool(calls) and not result.get('error') and check(answer)
   row={'case':key,'model':args.model,'question':question,'passed':passed,'answer':answer,'calls':calls,
        'seconds':round(time.monotonic()-start,2),'events':events,'error':result.get('error')}
  except Exception as exc:
   row={'case':key,'model':args.model,'question':question,'passed':False,'error':str(exc),'seconds':round(time.monotonic()-start,2),'events':events}
  finally:agent.close()
  results.append(row)
  args.output.write_text(json.dumps({'kind':'actual Hermes conversations with real read-only tools; facts checked against current machine','results':results},ensure_ascii=False,indent=2)+'\n')
  print('RESULT',key,'PASS' if row['passed'] else 'FAIL',row.get('answer',row.get('error')),flush=True)
 print('SUMMARY',sum(r['passed'] for r in results),'/',len(results),flush=True)

if __name__=='__main__':main()
