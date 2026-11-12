#!/usr/bin/env python3
"""Derive vector pieces from the original kinetic symbol, retaining its paths."""
from pathlib import Path
import re,math,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'branding/flausen/kinetic/flausen-symbol.svg'

def bounds(d):
    tokens=re.findall(r'[MLCQZmlcqz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',d)
    i=0;x=y=0;points=[];sx=sy=0
    def val():
        nonlocal i
        n=float(tokens[i]);i+=1;return n
    while i<len(tokens):
        cmd=tokens[i];i+=1
        if cmd=='M':x,y=val(),val();sx,sy=x,y;points.append((x,y))
        elif cmd=='L':x,y=val(),val();points.append((x,y))
        elif cmd in ('Q','C'):
            n=2 if cmd=='Q' else 3
            p=[(x,y)]+[(val(),val()) for _ in range(n)]
            ts={0.,1.}
            for axis in (0,1):
                q=[a[axis] for a in p]
                if n==2:
                    den=q[0]-2*q[1]+q[2]
                    if abs(den)>1e-12:ts.add((q[0]-q[1])/den)
                else:
                    a=-q[0]+3*q[1]-3*q[2]+q[3];b=2*(q[0]-2*q[1]+q[2]);c=q[1]-q[0]
                    if abs(a)<1e-12:
                        if abs(b)>1e-12:ts.add(-c/b)
                    elif b*b-4*a*c>=0:
                        disc=math.sqrt(b*b-4*a*c);ts.update(((-b+disc)/(2*a),(-b-disc)/(2*a)))
            for t in ts:
                if 0<=t<=1:points.append(tuple(sum(math.comb(n,k)*(1-t)**(n-k)*t**k*p[k][axis] for k in range(n+1)) for axis in (0,1)))
            x,y=p[-1]
        elif cmd=='Z':x,y=sx,sy
        else:raise ValueError(cmd)
    return min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)

items=[]
for node in ET.parse(SOURCE).getroot():
    if node.tag.endswith('path'):
        b=bounds(node.attrib['d']);items.append({'id':node.attrib['id'],'path':node.attrib['d'],'color':node.attrib['fill'],'bounds':b})
loX=min(p['bounds'][0] for p in items);loY=min(p['bounds'][1] for p in items)
hiX=max(p['bounds'][2] for p in items);hiY=max(p['bounds'][3] for p in items)
scale=168/(hiY-loY);origin=((loX+hiX)/2,(loY+hiY)/2)
for p in items:
    x,y,r,b=p.pop('bounds');p.update(cx=(x+r)/2,cy=(y+b)/2,w=(r-x)*scale,h=(b-y)*scale,
        home={'x':((x+r)/2-origin[0])*scale,'y':((y+b)/2-origin[1])*scale},scale=scale)
(ROOT/'wallpaper/contents/ui/Geometry.js').write_text('// Generated from branding/flausen/kinetic/flausen-symbol.svg. Paths unchanged.\nvar pieces = '+json.dumps(items,indent=2)+';\nvar logoHalf = '+json.dumps({'x':(hiX-loX)*scale/2,'y':84})+';\n')
print('Extracted original paths:',', '.join(p['id'] for p in items))
