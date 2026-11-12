"""Private settings transport. Credentials travel on stdin and never in replies."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import shlex
import tempfile
import csv
import io
import subprocess
import urllib.request
from urllib.parse import urlsplit
import yaml

def dotenv_values(path):
    values={}
    if not path.exists():return values
    for line in path.read_text().splitlines():
        match=re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$',line)
        if not match:continue
        try:
            parts=shlex.split(match[2],comments=True)
            values[match[1]]=' '.join(parts)
        except ValueError:continue
    return values

PROFILE = Path.home()/'.local/state/ralleur-hermes/profile'
MODELS = {
    'local-endpoint': dict(provider='custom', context_length=32768),
    'chatgpt': dict(provider='openai',base_url='https://api.openai.com/v1',context_length=500000),
    'deepseek-flash': dict(provider='deepseek', base_url='https://api.deepseek.com', context_length=1000000),
    'lfm3:1.7b-hermes': dict(provider='custom', base_url='http://127.0.0.1:11434/v1', context_length=65536),
    'qwen3.8:27b-hermes': dict(provider='custom', base_url='http://127.0.0.1:18038/v1', context_length=90112),
}

def validate_endpoint(url, model_id):
    if not isinstance(url,str) or not isinstance(model_id,str):
        raise ValueError('Bitte Endpoint-Adresse und Modellkennung angeben.')
    url=url.strip().rstrip('/')
    try:
        parsed=urlsplit(url)
        valid=parsed.scheme in ('http','https') and parsed.hostname and parsed.port != 0
        valid=valid and not (parsed.username or parsed.password or parsed.query or parsed.fragment)
    except ValueError:
        valid=False
    if not valid or any(c.isspace() or ord(c)<32 for c in url):
        raise ValueError('Bitte eine HTTP(S)-Basisadresse ohne Zugangsdaten, Suchparameter oder Fragment angeben, z. B. http://192.168.1.20:1234/v1.')
    model_id=model_id.strip()
    if not model_id or len(model_id)>256 or any(ord(c)<33 for c in model_id):
        raise ValueError('Bitte die vom Server angebotene Modellkennung ohne Leerzeichen angeben.')
    return dict(base_url=url, model=model_id)

def gpu_snapshot():
    """Dedicated memory only. Keep adapters separate; never add their capacities."""
    gpus=[]
    try:
        result=subprocess.run(['nvidia-smi','--query-gpu=uuid,name,memory.total,memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=2,check=True)
        for row in csv.reader(io.StringIO(result.stdout)):
            uid,name,total,used=[part.strip() for part in row]
            total,used=float(total)*1048576,float(used)*1048576
            if total>0:gpus.append(dict(id=uid,name=name,total=total,used=min(total,max(0,used))))
    except (OSError,ValueError,subprocess.SubprocessError):pass
    for card in sorted(Path('/sys/class/drm').glob('card[0-9]*')):
        device=card/'device'
        try:
            if (device/'vendor').read_text().strip()!='0x1002':continue
            total=int((device/'mem_info_vram_total').read_text());used=int((device/'mem_info_vram_used').read_text())
            if total>0:gpus.append(dict(id=card.name,name='AMD · '+card.name,total=total,used=min(total,max(0,used))))
        except (OSError,ValueError):pass
    return gpus

def ollama_read(endpoint, data=None):
    request=urllib.request.Request('http://127.0.0.1:11434/api/'+endpoint,
        data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=2) as response:return json.load(response)

def kv_budget(info, tokens):
    """Conservative FP16 K+V budget, one sequence, no sliding-window savings.

    Zero-KV (recurrent) layers must not be charged as attention layers.
    Unknown architectures remain unknown rather than inventing a cache size.
    """
    arch=info.get('general.architecture','')
    heads=info.get(arch+'.attention.head_count_kv')
    layers=info.get(arch+'.block_count')
    key=info.get(arch+'.attention.key_length')
    value=info.get(arch+'.attention.value_length')
    if not all(isinstance(v,int) and v>0 for v in (layers,key,value,tokens)):return None
    if isinstance(heads,int) and heads>0:heads=[heads]*layers
    if not isinstance(heads,list) or len(heads)!=layers or any(type(h) is not int or h<0 for h in heads):return None
    return sum(heads)*(key+value)*2*tokens

QWEN_ROOT = Path.home()/'.local/share/ralleur-hermes/qwen38'

def qwen_preview():
    """Use the installed runtime's estimator; never load weights or start a server."""
    profile=json.loads((QWEN_ROOT/'profile.json').read_text())
    configured,layers=profile['context_tokens'],profile['gpu_layers']
    if type(configured) is not int or not 0<configured<=262144 or type(layers) is not int or not 0<=layers<=66:
        raise ValueError('Invalid Qwen profile')
    runtime=QWEN_ROOT/'llama-b12052'
    binary=runtime/'llama-b12052/llama-fit-params'
    model=QWEN_ROOT.parent/'models/Qwen3.8-27B-UD-Q3_K_XL.gguf'
    libraries=sorted({str(p.parent) for p in runtime.rglob('*.so*')})
    env=dict(os.environ,LD_LIBRARY_PATH=':'.join(libraries+[os.environ.get('LD_LIBRARY_PATH','')]))
    contexts=[]
    for tokens in sorted(set([16384,32768,65536,90112,131072,262144,configured])):
        output=subprocess.run([str(binary),'-m',str(model),'-ngl',str(layers),'-c',str(tokens),
            '-ctk','q4_0','-ctv','q4_0','-fa','on','-fit','off','-fitp','on'],
            env=env,capture_output=True,text=True,check=True,timeout=5).stdout
        rows={parts[0]:[int(n)*1048576 for n in parts[1:]] for line in output.splitlines()
              if len(parts:=line.split())==4}
        weights,cache,compute=rows['CUDA0']
        # Estimator excludes MTP draft 3 (~978 MiB), CUDA context (~282 MiB),
        # and the driver's unavailable reserve (~462 MiB). Conservative budget.
        overhead=compute+(978+282+462)*1048576
        contexts.append(dict(tokens=tokens,bytes=cache,modelBytes=weights,runtimeBytes=overhead))
    return dict(name='qwen3.8:27b-hermes',label='Qwen 3.8 · 27B',modelBytes=contexts[0]['modelBytes'],
                cpuOnly=False,contextTokens=configured,contexts=contexts,gpuLayers=layers,kind='qwen')

def qwen_loaded():
    try:
        with urllib.request.urlopen('http://127.0.0.1:18038/props',timeout=1) as response:
            return not json.load(response)['is_sleeping']
    except urllib.error.HTTPError:return None
    except urllib.error.URLError as error:
        return False if isinstance(error.reason,ConnectionRefusedError) else None
    except (OSError,ValueError,KeyError):return None

def resources():
    result=dict(ok=True,gpus=gpu_snapshot(),local=None,locals={},ollamaAvailable=False,loadedVram=None)
    try:
        result['locals']['qwen3.8:27b-hermes']=qwen_preview()
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError):pass
    try:
        running=ollama_read('ps').get('models',[])
        result.update(ollamaAvailable=True,loadedVram=sum(max(0,m.get('size_vram',0)) for m in running))
        name='lfm3:1.7b-hermes'
        tags=ollama_read('tags').get('models',[])
        model=next((m for m in tags if m.get('name')==name),None)
        if model:
            detail=ollama_read('show',{'model':name})
            params=dict(re.findall(r'^(num_gpu|num_ctx)\s+(-?\d+)\s*$',detail.get('parameters',''),re.M))
            configured=int(params.get('num_ctx',65536))
            tokens=sorted(set([16384,32768,65536,131072,262144,configured]))
            maximum=detail.get('model_info',{}).get('lfm3.context_length',262144)
            result['local']=dict(name=name,label='LFM3',kind='lfm',modelBytes=model['size'],cpuOnly=params.get('num_gpu')=='0',contextTokens=configured,
                contexts=[dict(tokens=n,bytes=kv_budget(detail.get('model_info',{}),n)) for n in tokens if 0<n<=maximum])
            result['locals'][name]=result['local']
    except (OSError,ValueError,KeyError,TypeError):pass
    if qwen_loaded() is not False:result['loadedVram']=None
    return result

def revision():
    return hashlib.sha256(b'\0'.join((PROFILE/name).read_bytes() if (PROFILE/name).exists() else b'' for name in ('config.yaml','.env'))).hexdigest()

def codex_status():
    try:
        result=subprocess.run([str(Path.home()/'.local/share/ralleur-hermes/venv/bin/python'),
            str(Path(__file__).with_name('openai_auth.py')),'status'],capture_output=True,text=True,check=True,timeout=8)
        data=json.loads(result.stdout)
        return bool(data.get('ok') and data.get('loggedIn') and not data.get('expired'))
    except (OSError,ValueError,subprocess.SubprocessError):return False

def status():
    config=yaml.safe_load((PROFILE/'config.yaml').read_text()) or {}
    model=config.get('model') or {}
    selected='chatgpt' if model.get('provider') in ('openai','openai-codex') else model.get('default','lfm3:1.7b-hermes')
    return dict(ok=True, model=selected, thinking=model.get('reasoning_effort','medium')!='none',
                endpointUrl=(config.get('local_endpoint') or {}).get('base_url',''),
                endpointModel=(config.get('local_endpoint') or {}).get('model',''),
                endpointKeyConfigured=bool(dotenv_values(PROFILE/'.env').get('LOCAL_ENDPOINT_API_KEY')),
                chatgptAuth=config.get('desktop_chatgpt_auth','codex' if model.get('provider')=='openai-codex' else 'api'),
                openaiKeyConfigured=bool(dotenv_values(PROFILE/'.env').get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')),
                codexLoggedIn=codex_status(),
                keyConfigured=bool(dotenv_values(PROFILE/'.env').get('DEEPSEEK_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')),
                revision=revision())

def atomic(path, text):
    fd,name=tempfile.mkstemp(prefix='.hermes-settings-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as file:
            file.write(text);file.flush();os.fsync(file.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)

def save(request):
    if request.get('model') not in MODELS or type(request.get('thinking')) is not bool:
        raise ValueError('Please select a supported model.')
    key=request.get('apiKey','')
    if not isinstance(key,str) or (key and not re.fullmatch(r'[A-Za-z0-9_-]{16,256}',key)):
        raise ValueError('The API key has an invalid format.')
    openai_key=request.get('openaiApiKey','')
    method=request.get('chatgptAuth','api')
    if method not in ('api','codex') or not isinstance(openai_key,str) or (openai_key and not re.fullmatch(r'[A-Za-z0-9_-]{16,512}',openai_key)):
        raise ValueError('Select a valid OpenAI access method and provide a valid API key.')
    if request.get('revision')!=revision():
        raise ValueError('The Hermes profile has changed. Please reload.')
    config=yaml.safe_load((PROFILE/'config.yaml').read_text()) or {}
    if request['model']=='deepseek-flash' and not key and not status()['keyConfigured']:
        raise ValueError('Save an API key for DeepSeek.')
    if request['model']=='chatgpt':
        if method=='api' and not openai_key and not status()['openaiKeyConfigured']:
            raise ValueError('Save an OpenAI API key or choose Codex subscription sign-in.')
        if method=='codex' and not codex_status():
            raise ValueError('Sign in with your Codex subscription first.')
    endpoint_key=request.get('endpointApiKey','')
    if not isinstance(endpoint_key,str) or len(endpoint_key)>1024 or any(ord(c)<33 for c in endpoint_key):
        raise ValueError('The endpoint key must not contain whitespace or control characters.')
    endpoint=None
    if request['model']=='local-endpoint':
        endpoint=validate_endpoint(request.get('endpointUrl'),request.get('endpointModel'))
    model=config.setdefault('model',{})
    model.update(MODELS[request['model']],default=request['model'],reasoning_effort='high' if request['thinking'] else 'none')
    model['api_mode']='chat_completions'
    config['desktop_chatgpt_auth']=method
    if endpoint:
        config['local_endpoint']=endpoint
        model['base_url']=endpoint['base_url']
    if request['model']=='chatgpt':
        model.update(default='gpt-6.1-sol',provider='openai-codex' if method=='codex' else 'openai',
                     base_url='https://chatgpt.com/backend-api/codex' if method=='codex' else 'https://api.openai.com/v1',
                     api_mode='codex_responses')
    if key or openai_key or endpoint_key:
        env=PROFILE/'.env'
        text=env.read_text() if env.exists() else ''
        replacements={name:value for name,value in [('DEEPSEEK_API_KEY',key),('OPENAI_API_KEY',openai_key),('LOCAL_ENDPOINT_API_KEY',endpoint_key)] if value}
        lines=[line for line in text.splitlines() if not any(re.match(r'^\s*(?:export\s+)?'+name+r'\s*=',line) for name in replacements)]
        lines.extend(name+'='+json.dumps(value) for name,value in replacements.items())
        atomic(env,'\n'.join(lines)+'\n')
    atomic(PROFILE/'config.yaml',yaml.safe_dump(config,allow_unicode=True,sort_keys=False))
    return status()

def main():
    os.umask(0o077)
    try:
        request=json.loads(sys.stdin.readline(8192))
        if not isinstance(request,dict):raise ValueError('Invalid request.')
        if request.get('action')=='resources':
            print(json.dumps(resources(),ensure_ascii=False));return
        if not (PROFILE/'config.yaml').exists():raise ValueError('Hermes is not configured yet.')
        with (PROFILE/'.settings.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            result=save(request) if request.get('action')=='save' else status()
    except ValueError as error:
        result=dict(ok=False,error=str(error))
    except Exception:
        result=dict(ok=False,error='Could not read or save the Hermes profile.')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
