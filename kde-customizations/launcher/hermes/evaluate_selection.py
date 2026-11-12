"""Compare first-step tool selection on unseen, naturally phrased OS questions.

Never executes model-proposed tools. Final-answer accuracy needs the separate
live Hermes tests; this report measures whether the model starts investigating.
Run inside the installed Hermes venv. Outputs private local evidence only.
"""
import argparse,copy,importlib.util,json,time,urllib.request
from pathlib import Path

CASES = [
 ('standby','Nach wie vielen Minuten geht mein Rechner automatisch in Standby?',{'read_file','search_files','system_command'}),
 ('display','Nach welcher Zeit schaltet sich mein Bildschirm von allein aus?',{'read_file','search_files','system_command'}),
 ('shortcuts','Welche Tastenkombination öffnet bei mir den Dateimanager?',{'read_file','search_files','system_command'}),
 ('dock','Welche Programme sind bei mir im Dock angeheftet?',{'read_file','search_files','system_command'}),
 ('theme','Welches KDE-Farbschema ist derzeit eingestellt?',{'read_file','search_files','system_command'}),
 ('autostart','Was startet bei meiner Anmeldung automatisch?',{'autostart_status','read_file','search_files','system_command'}),
 ('ram','Wie viel Arbeitsspeicher ist gerade noch verfügbar?',{'system_status','system_command'}),
 ('audio','Wie laut ist der Rechner momentan eingestellt?',{'desktop_status','system_command'}),
 ('processes','Welche meiner Prozesse beanspruchen gerade am meisten CPU?',{'inspect_system','system_command'}),
 ('storage','Welche Laufwerke sind vorhanden und wo sind sie eingebunden?',{'inspect_system','system_command'}),
]

def load_bridge(path):
 spec=importlib.util.spec_from_file_location('evaluated_bridge',path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module

def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--variants',default='');p.add_argument('--cases',default='');p.add_argument('--reasoning',default='none');p.add_argument('--max-tokens',type=int,default=256)
 args=p.parse_args()
 old=load_bridge(args.baseline)
 agent=old.Bridge().make_agent()
 original=copy.deepcopy(agent.tools)
 agent.close()
 from tools.file_tools import READ_FILE_SCHEMA,SEARCH_FILES_SCHEMA
 generic=original+[{'type':'function','function':copy.deepcopy(s)} for s in (READ_FILE_SCHEMA,SEARCH_FILES_SCHEMA)]
 updated=load_bridge(Path(__file__).with_name('bridge.py'))
 variants=[('lfm-original','lfm3:1.7b-hermes',original,old.SYSTEM),
           ('lfm-reading','lfm3:1.7b-hermes',generic,updated.SYSTEM),
           ('qwen-reading','qwen3.5:4b-hermes',generic,updated.SYSTEM)]
 if args.variants:variants=[v for v in variants if v[0] in args.variants.split(',')]
 cases=[c for c in CASES if not args.cases or c[0] in args.cases.split(',')]
 results=[]
 for label,model,tools,system in variants:
  for key,question,allowed in cases:
   start=time.monotonic()
   body={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':question}],
         'tools':tools,'reasoning_effort':args.reasoning,'temperature':0.1,'max_tokens':args.max_tokens,'stream':False,'keep_alive':'1m'}
   try:
    request=urllib.request.Request('http://127.0.0.1:11434/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=120) as f: response=json.load(f)
    message=response['choices'][0]['message']
    calls=[c['function'] for c in message.get('tool_calls',[])]
    passed=bool(calls) and all(c['name'] in allowed for c in calls)
    row={'variant':label,'case':key,'question':question,'investigates':passed,'calls':calls,'text':message.get('content'),'seconds':round(time.monotonic()-start,2)}
   except Exception as exc:
    row={'variant':label,'case':key,'investigates':False,'error':str(exc),'seconds':round(time.monotonic()-start,2)}
   results.append(row)
   args.output.write_text(json.dumps({'kind':'first-step tool selection, no tool execution or answer scoring','results':results},ensure_ascii=False,indent=2)+'\n')
   print(label,key,'PASS' if row['investigates'] else 'FAIL',row.get('calls',row.get('error',row.get('text'))),flush=True)
 print('SUMMARY',json.dumps({label:sum(r['investigates'] for r in results if r['variant']==label) for label,_,_,_ in variants}),flush=True)

if __name__=='__main__':main()
