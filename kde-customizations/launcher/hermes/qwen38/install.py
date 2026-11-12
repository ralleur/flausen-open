#!/usr/bin/env python3
"""Install a pinned CUDA runtime and checksum-verified GGUF without root."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = Path.home()/'.local/share/ralleur-hermes'
RUNTIME = ROOT/'qwen38'
DOWNLOADS = RUNTIME/'downloads'
ASSETS = {
    'llama-b12052-bin-ubuntu-cuda-13.4-x64.tar.gz': 'c2f6ff5e944eea808902fa05b46421d3b9abde576835d9bd3dc5d78dcfe6c0a0',
    'cudart-llama-b12052-bin-ubuntu-cuda-13.4-x64.tar.gz': 'd67b01141a6384967f7077c365c5f9603468ce8d1e574987ecfeaf9772cdf48c',
}

def verified(url, path, sha):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        partial = path.with_suffix(path.suffix+'.install-part')
        print('Downloading', path.name, flush=True)
        with urllib.request.urlopen(url, timeout=120) as response, partial.open('wb') as out:
            shutil.copyfileobj(response, out, length=8*1024*1024)
        with partial.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != sha:
                raise RuntimeError('Checksum mismatch: '+path.name)
        partial.replace(path)
    with path.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != sha:
            raise RuntimeError('Checksum mismatch: '+path.name)
    return path

for name, sha in ASSETS.items():
    archive = verified('https://github.com/ggml-org/llama.cpp/releases/download/b12052/'+name, DOWNLOADS/name, sha)
    with tarfile.open(archive) as tar:
        tar.extractall(RUNTIME/'llama-b12052', filter='data')
verified('https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-UD-Q3_K_XL.gguf',
         ROOT/'models/Qwen3.8-27B-UD-Q3_K_XL.gguf',
         '8c2a45ff85e7674ca185ec8eb6cdeab0e617ed9d8018caed0b64380eb2a67a5e')
shutil.copy2(HERE/'serve.py', RUNTIME/'serve.py')
# Preserve a locally tuned profile on subsequent installs.
if not (RUNTIME/'profile.json').exists():
    shutil.copy2(HERE/'profile.json', RUNTIME/'profile.json')
unit = Path.home()/'.config/systemd/user/ralleur-hermes-qwen.service'
unit.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(HERE/unit.name, unit)
subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
print('Qwen installed. Hermes starts the server on the first Qwen request.')
