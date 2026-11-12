#!/usr/bin/env python3
"""Repo-style Qwen profile, adapted to the desktop's shared RTX 5080."""
import json
import os
from pathlib import Path

ROOT = Path.home()/'.local/share/ralleur-hermes'
runtime = ROOT/'qwen38'
config = json.loads((runtime/'profile.json').read_text())
binary = next((runtime/'llama-b12052').rglob('llama-server'))
libraries = sorted({str(p.parent) for p in (runtime/'llama-b12052').rglob('*.so*')})
os.environ['LD_LIBRARY_PATH'] = ':'.join(libraries + [os.environ.get('LD_LIBRARY_PATH', '')])
args = [str(binary), '-m', str(ROOT/'models/Qwen3.8-27B-UD-Q3_K_XL.gguf'),
        '-a', 'qwen3.8:27b-hermes', '-ngl', str(config['gpu_layers']), '-fit', 'off',
        '-c', str(config['context_tokens']), '-ctk', 'q4_0', '-ctv', 'q4_0', '-fa', 'on',
        '--spec-type', 'draft-mtp', '--spec-draft-n-max', '3', '-np', '1', '--jinja', '--metrics',
        '--sleep-idle-seconds', '120', '--host', '127.0.0.1', '--port', '18038']
os.execv(binary, args)
