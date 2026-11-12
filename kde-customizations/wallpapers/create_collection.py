#!/usr/bin/env python3
"""Generate native vector artwork and 4K desktop exports. No bitmap dependencies."""
from pathlib import Path
from html import escape
import math, json, subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

ROOT=Path('/home/USER/Bilder/Wallpapers/ralleur-4k')
SVG=ROOT/'svg'; PNG=ROOT/'png'
for d in (SVG,PNG): d.mkdir(parents=True,exist_ok=True)
C=['#2563C9','#DF493F','#DED6C8','#E4AD22','#278F8B','#E56D2F','#3F7D44','#8F5B40']
B=[(0,0,58,22),(66,0,70,22),(4,34,22,62),(38,34,22,62),(72,34,22,62),(4,106,22,62),(38,106,22,62),(72,106,22,62)]
DARK='#101316'; PAPER='#EDE8DF'; INK='#202A2A'
def rect(x,y,w,h,c,rx=0,extra=''):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{c}" {extra}/>'
def circle(x,y,r,c,extra=''):
    return f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{c}" {extra}/>'
def path(d,c,extra=''):
    return f'<path d="{d}" fill="{c}" {extra}/>'
def line(x1,y1,x2,y2,c,w=2,extra=''):
    return f'<path d="M{x1:g} {y1:g}L{x2:g} {y2:g}" fill="none" stroke="{c}" stroke-width="{w}" {extra}/>'
def logo(x,y,s=1,colour=None,opacity=1,angle=0,outline=None):
    nodes=[]
    for i,(bx,by,w,h) in enumerate(B):
        if outline:
            nodes.append(rect(bx,by,w,h,'none',1,f'stroke="{outline}" stroke-width="0.65"'))
        else:nodes.append(rect(bx,by,w,h,colour or C[i],1))
    return f'<g transform="translate({x:g} {y:g}) rotate({angle:g}) scale({s:g})" opacity="{opacity:g}">'+''.join(nodes)+'</g>'
def grid(step,colour,opacity=1):
    return '<g opacity="%g">'%opacity+''.join(line(x,0,x,2160,colour,1) for x in range(0,3841,step))+''.join(line(0,y,3840,y,colour,1) for y in range(0,2161,step))+'</g>'
collection=[]
def save(slug,title,bg,body,description):
    text=f'''<svg xmlns="http://www.w3.org/2000/svg" width="3840" height="2160" viewBox="0 0 3840 2160">
<title>{escape(title)} — ralleur</title>
<desc>{escape(description)}. Native vector artwork; original ralleur logo geometry.</desc>
{rect(0,0,3840,2160,bg)}
{body}
</svg>\n'''
    (SVG/f'{slug}.svg').write_text(text)
    collection.append(dict(id=slug,title=title,description=description,svg=f'svg/{slug}.svg',png=f'png/{slug}.png'))

# A quiet opening, with the brand mark on the right and a hairline horizon.
save('01-nocturne','Nocturne',DARK,
     line(0,1740,3840,1740,'#20282B',2)+logo(2900,800,2.6)+line(2900,1350,3254,1350,'#343C3D',2),
     'Anthrazit, ein kleines farbiges Logo und viel freier Raum')

# Architectural crop: the image continues beyond the screen rather than squeezing in.
save('02-paper-cut','Paper Cut',PAPER,
     rect(2760,0,1080,2160,'#E1DACF')+logo(2450,520,9.5,INK)+logo(230,1660,0.85),
     'Warmer Papiergrund, monumentaler Anschnitt und kleine Farbsignatur')

# Monochrome fields preserve every original proportion.
save('03-blue-hour','Blue Hour','#19468D',
     circle(3100,1250,1170,'#2055AA')+logo(2480,620,5.2,'#EDE8DF')+line(240,1760,1240,1760,'#6486BE',3),
     'Kobaltblau, ein heller Logo-Monolith und eine weite Kreisfläche')

body=''
for radius in [350,560,820,1130]:
    body+=circle(2920,1080,radius,'none',f'stroke="#30424B" stroke-width="2"')
for angle,radius,col in [(215,560,C[3]),(315,820,C[0]),(100,1130,C[1])]:
    a=math.radians(angle);body+=circle(2920+radius*math.cos(a),1080+radius*math.sin(a),12,col)
body+=logo(2750,870,2.5)
save('04-orbit','Orbit','#101C24',body,'Feine Umlaufbahnen um das farbige Zeichen auf tiefem Nachtblau')

body=grid(120,'#4A6666',0.19)+logo(2430,490,7.0,outline='#9DB0A9')
body+=line(2320,430,3490,430,'#658078',2)+line(2320,1770,3490,1770,'#658078',2)
for x,y in [(2320,430),(3490,430),(2320,1770),(3490,1770)]:body+=circle(x,y,6,C[3])
body+=logo(240,1590,1.2)
save('05-blueprint','Blueprint','#172C2C',body,'Ein konstruktives Raster mit der originalen Logo-Geometrie als feiner Kontur')

# Abstract the symbol into a landscape of eight horizontal strata.
body=''
for i,col in enumerate(C):
    y=1460+i*84;left=850+150*math.sin(i*0.9)
    body+=rect(left,y,3840-left,58,col)
body+=logo(2680,700,2.5)
save('06-strata','Strata','#15191C',body,'Die acht Markenfarben werden zu einem ruhigen grafischen Horizont')

save('07-red-eclipse','Red Eclipse','#171719',
     circle(3190,1580,1110,C[1])+circle(2580,690,1010,'#171719')+logo(2970,1250,2.8,'#F1DFCE'),
     'Eine rote Sichel und ein helles Logo, aus zwei präzisen Kreisflächen')

body=''
for row in range(4):
    for col in range(7):
        x=230+col*600+(row%2)*220;y=210+row*550
        body+=logo(x,y,0.85,'#96A99D',0.11,angle=-15)
body+=logo(2690,770,3.2)
save('08-night-garden','Night Garden','#15231F',body,'Ein zurückhaltendes grünes Logo-Muster mit einer einzelnen farbigen Signatur')

# Flat isometric vector extrusion: no baked shadows, filters or texture.
body='<g transform="translate(2740 430) matrix(1 .48 -1 .48 0 0) scale(5.5)">'
for i,(x,y,w,h) in enumerate(B):
    depth=22
    body+=path(f'M{x} {y+h}h{w}v{depth}h{-w}Z','#A8A396')
    body+=path(f'M{x+w} {y}v{h}l{depth} {depth}v{-h}Z','#B7AE9E')
    body+=rect(x,y,w,h,C[i],1)
body+='</g>'+logo(240,1680,0.8,INK)
save('09-workshop','Workshop','#E5DFD2',body,'Das Logo als farbige Bauklötze in flacher isometrischer Projektion')

body='<g transform="rotate(-32 1150 1600)">'
for i,col in enumerate(C):body+=rect(-1100,1110+i*98,3450,62,col,2)
body+='</g>'+logo(2820,520,3.7,'#EEE5D8')
save('10-colour-current','Colour Current','#172125',body,'Acht lange Farbbänder strömen diagonal durch einen dunklen Bildraum')

# Pieces of the mark become a monumental sculpture, retaining the original lockup.
save('11-monument','Monument','#26282A',
     logo(2360,260,9.2)+line(0,2020,3840,2020,'#474546',2)+logo(230,1650,0.8,'#AEB3AE'),
     'Ein großes farbiges Zeichen als Skulptur mit ruhiger linker Bildschirmhälfte')

body=''
for x,y,w,h in B:
    cx=2680+(x+w/2)*3.6;cy=700+(y+h/2)*3.6
    body+=line(480,1080,cx,cy,'#283840',1.5)
body+=circle(480,1080,7,C[4])+logo(2680,700,3.6)
for x,y in [(520,360),(1120,1680),(1640,530),(2110,1780),(3320,390)]:body+=circle(x,y,3,'#7B9197')
save('12-connections','Connections','#101A20',body,'Feine Verbindungslinien führen von einem Punkt in die acht Logo-Elemente')

body=rect(2640,0,1200,2160,'#223538')
body+=logo(2140,540,6.4,INK)
# Clip a second identical mark to reveal its light half against the dark panel.
body+='<defs><clipPath id="right"><rect x="2640" width="1200" height="2160"/></clipPath></defs>'
body+='<g clip-path="url(#right)">'+logo(2140,540,6.4,'#EDE8DF')+'</g>'
body+=logo(220,1690,0.75)
save('13-counterform','Counterform',PAPER,body,'Ein Logo über einer Hell-Dunkel-Kante, dessen Farbe mit dem Untergrund wechselt')

body=''
for i in range(14,0,-1):
    s=1.7+i*0.5;body+=logo(2950-68*s,1080-84*s,s,outline=['#253A46','#2D4652','#34515B'][i%3],opacity=0.8)
body+=logo(2834.4,937.2,1.7)
save('14-resonance','Resonance','#111D24',body,'Das Zeichen als Folge größer werdender Konturen um einen farbigen Kern')

body=rect(2740,0,1100,2160,'#D59A1C')+logo(2430,560,6.0,'#24302D')
body+=line(240,1670,1450,1670,'#6C581E',3)+circle(240,1670,8,'#24302D')
save('15-golden-state','Golden State',C[3],body,'Ein sonniges Ockerfeld mit dunklem Zeichen und einer einzigen präzisen Linie')

body=rect(2390,420,1000,1330,'none',0,'stroke="#414744" stroke-width="2"')
body+=logo(2686,840,3.0)
for i,col in enumerate(C):body+=rect(240+i*42,1730,24,6,col,1)
save('16-gallery','Gallery','#1B211F',body,'Das Logo als gerahmtes Exponat auf tiefem Olivgrau, mit einer kleinen Farbskala')

# Each export is independent; parallel rendering does not touch live settings.
def render(item):
    src=SVG/f"{item['id']}.svg";dst=PNG/f"{item['id']}.png"
    subprocess.run(['rsvg-convert','-w','3840','-h','2160','-o',str(dst),str(src)],check=True)
    with Image.open(dst) as im:
        assert im.size==(3840,2160)
    return item['id']
with ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(render,collection):print(result,flush=True)
(ROOT/'collection.json').write_text(json.dumps(collection,ensure_ascii=False,indent=2)+'\n')

# Contact sheet uses raster previews only; the deliverables remain editable SVG.
font_path='/usr/share/fonts/TTF/DejaVuSans.ttf'
try:font=ImageFont.truetype(font_path,23)
except OSError:font=ImageFont.load_default(size=23)
thumb_w,thumb_h=640,360;gap=24;label=52
sheet=Image.new('RGB',(4*thumb_w+5*gap,4*(thumb_h+label)+5*gap),'#0C1114')
draw=ImageDraw.Draw(sheet)
for i,item in enumerate(collection):
    x=gap+(i%4)*(thumb_w+gap);y=gap+(i//4)*(thumb_h+label+gap)
    with Image.open(PNG/f"{item['id']}.png") as im:sheet.paste(im.convert('RGB').resize((thumb_w,thumb_h),Image.Resampling.LANCZOS),(x,y))
    draw.text((x+4,y+thumb_h+12),f"{i+1:02d}  {item['title']}",font=font,fill='#E4E9E6')
sheet.save(ROOT/'collection-preview.jpg',quality=94,subsampling=0)
print(f'Created {len(collection)} SVG originals and 4K PNG exports in {ROOT}')
