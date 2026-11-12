#!/usr/bin/env python3
"""Real long prefill and VRAM sampling; no claim about long-context accuracy."""
import argparse
import json
from pathlib import Path
import subprocess
import threading
import time
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
url = 'http://127.0.0.1:18038'

def request(endpoint, body=None):
    req = urllib.request.Request(url+endpoint, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=900) as response:
        return json.load(response)

props = request('/props')
context = props['default_generation_settings']['n_ctx']
assert context == 90112, context
tokens = request('/tokenize', {'content':'Dies ist eine Testzeile zur Prüfung des Kontextspeichers.\n'})['tokens']
prompt = (tokens * (89000//len(tokens)+1))[:89000]
done = threading.Event()
samples = []

def sample():
    while not done.is_set():
        result = subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.free','--format=csv,noheader,nounits'],
                                capture_output=True, text=True, timeout=5, check=True)
        used, free = map(int, result.stdout.strip().splitlines()[0].split(','))
        samples.append({'seconds':round(time.monotonic()-start,2),'used_mib':used,'free_mib':free})
        done.wait(.2)

start = time.monotonic()
sampler = threading.Thread(target=sample, daemon=True)
sampler.start()
try:
    result = request('/completion', {'prompt':prompt,'n_predict':8,'temperature':0,'cache_prompt':False})
    assert result['tokens_evaluated'] == 89000, result
    assert not result.get('truncated'), result
    report = {'ok':True,'context_tokens':context,'real_prompt_tokens':89000,'result':result,
              'seconds':round(time.monotonic()-start,2)}
finally:
    done.set();sampler.join(timeout=6)
report['gpu_samples'] = samples
report['peak_gpu_used_mib'] = max(s['used_mib'] for s in samples)
report['minimum_gpu_free_mib'] = min(s['free_mib'] for s in samples)
args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('result','gpu_samples')},ensure_ascii=False))
