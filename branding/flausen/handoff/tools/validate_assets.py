#!/usr/bin/env python3
"""Run from anywhere: python3 tools/validate_assets.py (stdlib only)."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import struct
import sys
root=Path(__file__).resolve().parents[1]
problems=[]
for p in sorted((root/'assets').rglob('*.svg')):
    try:
        elem=ET.fromstring(p.read_text())
        if not elem.tag.endswith('svg'):
            problems.append(f'{p.relative_to(root)}: root must be <svg>')
    except Exception as e:
        problems.append(f'{p.relative_to(root)}: invalid SVG XML: {e}')
for p in sorted(root.rglob('*.json')):
    try: json.loads(p.read_text())
    except Exception as e: problems.append(f'{p.relative_to(root)}: invalid JSON: {e}')
for p in sorted(root.rglob('*.png')):
    try:
        b=p.read_bytes()[:24]
        if b[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('not PNG')
        w,h=struct.unpack('>II',b[16:24])
        if w<16 or h<16: raise ValueError('dimensions too small')
    except Exception as e:
        problems.append(f'{p.relative_to(root)}: invalid PNG: {e}')
for f in ['CODEX_TASK.md','BRAND_SPEC.md','DESKTOP_IMPLEMENTATION.md','DESIGN_TOKENS.json','ACCEPTANCE.md','preview/brand-board.png','reference/desktop-light.png','reference/desktop-dark.png']:
    if not (root/f).exists():problems.append(f'Missing required file: {f}')
for v in ['dark','light']:
    if not (root/'assets/logos'/f'flausen-lockup-on-{v}.svg').exists():
        problems.append(f'Missing lockup {v}')
if problems:
    for err in problems:print('FAIL',err)
    sys.exit(1)
print('PASS: validated',len(list(root.rglob('*.svg'))),'SVGs,',len(list(root.rglob('*.png'))),'PNGs and design documents.')
