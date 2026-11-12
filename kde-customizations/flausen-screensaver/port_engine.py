#!/usr/bin/env python3
"""Adapt the existing playful physics to the kinetic logo's three vector bodies."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=(ROOT.parent/'screensaver-boot/wallpaper/contents/ui/Engine.js').read_text()
start=s.index('var bars =');end=s.index('var pi =',start)
s='// Native kinetic flausen. animation, based on the existing logo spring engine.\n.import "Geometry.js" as Geometry\n'+s[start:end].replace(s[start:end],'')+s[end:]
s=s.replace('function Engine(width,height) {','function indices(n) { return Array.from({length:n},function(_,i){return i;}); }\nfunction Engine(width,height) {')
a=s.index('    this.bodies=bars.map');b=s.index('    this.time=0;',a)
s=s[:a]+'''    this.bodies=Geometry.pieces.map(function(g,i){return {i:i,w:g.w,h:g.h,home:v(g.home.x,g.home.y),
        radius:Math.hypot(g.w,g.h)/2,p:v(0,0),v:v(0,0),a:0,av:0,s:v(1,1),sv:v(0,0),override:null,
        mode:"spring",target:v(0,0),ta:0,k:140,z:0.6,ak:140,az:0.6,gravity:0,drag:0,angDrag:0,bounce:false,flag:false,
        phase:i*0.7+g.home.x*0.02};});
''' + s[b:]
s=s.replace('var x=88+rand(0,this.world.x*0.045),y=104+rand(0,this.world.y*0.045);','var x=Geometry.logoHalf.x+20+rand(0,this.world.x*0.045),y=Geometry.logoHalf.y+20+rand(0,this.world.y*0.045);')
s=s.replace('Math.max(width,1)*0.42/136','Math.max(width,1)*0.42/(Geometry.logoHalf.x*2)')
s=s.replace('this.origin.x<88||this.origin.x>this.world.x-88||this.origin.y<104||this.origin.y>this.world.y-104','this.origin.x<Geometry.logoHalf.x+20||this.origin.x>this.world.x-Geometry.logoHalf.x-20||this.origin.y<104||this.origin.y>this.world.y-104')
s=s.replace('rand(98,this.world.x-98)','rand(Geometry.logoHalf.x+30,this.world.x-Geometry.logoHalf.x-30)')
s=s.replace('shuffle([0,1,2,3,4,5,6,7])','shuffle(indices(bs.length))').replace('ri(8)','ri(bs.length)').replace('i<8;i++','i<bs.length;i++')
s=s.replace('wrap(b.a,pi)','wrap(b.a,2*pi)')
s=s.replace('[[5,6,7],[2,3,4],[0,1]]','[[2],[1],[0]]')
s=s.replace('a.perm=[2,3,4,5,6,7]','a.perm=indices(bs.length)')
s=s.replace('x=ri(6);y=ri(6)','x=ri(bs.length);y=ri(bs.length)')
s=s.replace('for(var s=0;s<6;s++)if(p[s]!==s+2)','for(var s=0;s<bs.length;s++)if(p[s]!==s)')
s=s.replace('p.indexOf(s+2)','p.indexOf(s)')
# Former spectator top-bars are now active kinetic forms, not spectators.
a=s.index('        if(focus)[0,1].forEach');b=s.index('\n        a.done=',a)
s=s[:a]+s[b:]
s=s.replace('var base=b.w>=b.h?0:pi/2;a.angOff[i]=base+pi*Math.round((b.a-(q.a+base))/pi);','var base=0;a.angOff[i]=2*pi*Math.round((b.a-q.a)/(2*pi));')
(ROOT/'wallpaper/contents/ui/Engine.js').write_text(s)
print('Ported eight animation states for',3,'kinetic forms')
