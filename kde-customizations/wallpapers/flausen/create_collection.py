#!/usr/bin/env python3
"""Original native-vector flausen. collection; editable SVG and lossless 4K exports."""
from pathlib import Path
from html import escape
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import zipfile
import json
import math
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
GEOMETRY = json.loads((HERE / 'geometry.json').read_text())
BLUE, ORANGE, PETROL, BROWN = '#2563C9', '#E56D2F', '#278F8B', '#8F5B40'
MIST, CREAM, INK, CHALK = '#ECEEF0', '#DED6C8', '#17191D', '#F5F4F0'
PARTS = ['blue-object', 'orange-wedge', 'petrol-strip', 'brown-weight']
CENTERS = [(638,455),(929,342),(1152,628),(1411,320)]
COLORS = [BLUE, ORANGE, PETROL, BROWN]
collection = []


def rect(x,y,w,h,fill,extra=''):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" {extra}/>'


def path(d,fill='none',stroke=None,width=2,extra=''):
    return f'<path d="{d}" fill="{fill}" fill-rule="evenodd"'+(f' stroke="{stroke}" stroke-width="{width:g}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '')+f' {extra}/>'


def line(x1,y1,x2,y2,color=INK,width=2):
    return path(f'M{x1:g} {y1:g}L{x2:g} {y2:g}',stroke=color,width=width)


def circle(x,y,r,fill,stroke=None,width=2):
    return f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{width:g}"' if stroke else '')+'/>'


def shape(i,x,y,s=1,angle=0,fill=None,stroke=None,width=2,opacity=1):
    cx,cy=CENTERS[i]
    return f'<g transform="translate({x:g} {y:g}) rotate({angle:g}) scale({s:g}) translate({-cx:g} {-cy:g})" opacity="{opacity:g}">'+path(GEOMETRY[PARTS[i]]['path'],fill if fill is not None else COLORS[i],stroke,width/s)+'</g>'


def anchor(i,x,y,s=1,angle=0):
    px,py=GEOMETRY[PARTS[i]]['pivot'];cx,cy=CENTERS[i]
    dx,dy=(px-cx)*s,(py-cy)*s;a=math.radians(angle)
    return x+dx*math.cos(a)-dy*math.sin(a),y+dx*math.sin(a)+dy*math.cos(a)


def hang(i,x,y,s=1,angle=0,top=-200,color=INK,fill=None):
    ax,ay=anchor(i,x,y,s,angle)
    return line(ax,top,ax,ay,color)+shape(i,x,y,s,angle,fill)+circle(ax,ay,4,color)


def mobile(x,y,s=1,wire=INK,monochrome=None,angle=0):
    wires='M766 -2000V73 M486 115Q610 68 766 74Q921 79 920 145L921 176 M921 176Q1016 190 1111 216L1378 296 M486 115V157 M921 176V291 M1111 216V353'
    body=path(wires,stroke=wire,width=2/s)
    for i,name in enumerate(PARTS):
        body+=path(GEOMETRY[name]['path'],monochrome or COLORS[i])
        px,py=GEOMETRY[name]['pivot'];body+=circle(px,py,3,wire)
    for px,py in [(486,115),(766,73),(921,176),(1111,216)]:
        body+=circle(px,py,4,'none',wire,1.5/s)
    return f'<g transform="translate({x:g} {y:g}) rotate({angle:g} 766 73) scale({s:g})">{body}</g>'


# Per-artwork companion surfaces keep the brand colors and deliberately retune
# contours, suspension lines and paper depths instead of applying a color inversion.
SURFACES = {
    '01': ('#ECEEF0', '#141B20'), '02': ('#ECEEF0', '#171E29'),
    '03': ('#E5EBEB', '#14232A'), '04': ('#EEE6D8', '#211E1C'),
    '05': ('#E3EBE6', '#101F25'), '06': ('#E7ECF4', '#142F56'),
    '07': ('#EBE8E1', '#1D2020'), '08': ('#EAE4D8', '#20262C'),
    '09': ('#E3ECE8', '#142C30'), '10': ('#F2F0E9', '#19232A'),
    '11': ('#E8ECF2', '#1A438B'), '12': ('#E8E5DF', '#191E25'),
    '13': ('#E8E3D9', '#1C2427'), '14': ('#E7ECE9', '#19282E'),
    '15': ('#E7EBEC', '#111D24'), '16': (CHALK, '#171E25'),
}


def add_variant(slug, title, bg, body, description, mode):
    collection.append({'id':slug+'-'+mode, 'family':slug, 'title':title,
        'mode':mode, 'description':description, 'background':bg,
        'svg':f'{mode}/svg/{slug}-{mode}.svg',
        'png':f'{mode}/png/{slug}-{mode}.png', 'body':body})


def companion(body, slug, target):
    root=ET.fromstring('<g>'+body+'</g>')
    if target=='light':
        mapping={
            '#8B999D':'#6D7B80', '#526265':'#849597', '#84908D':'#7F8C87',
            '#7F9F9D':'#697E7C', '#548F8A':'#4E8A83', '#326B6B':'#477C78',
            '#263E4B':'#CCD9DE', '#394046':'#C0C8C8', '#214250':'#B2C7CD',
            '#2D5360':'#A2BAC1', '#3A6870':'#91ADB4', '#83A4D6':'#A2B5D0',
        }
        # Blue-background studies get an actual blue paper form on a pale surface.
        if slug[:2] in ('06','11'):
            mapping[CHALK]=BLUE
            mapping['#93AFE0']='#B7C5DC'
    else:
        mapping={
            INK:'#B9C3C7', '#A5A6A0':'#56656D', '#C7BFB0':'#11171D',
            '#D5CCBD':'#35414A', '#CAC4B8':'#394B50', '#ABB3B1':'#677E84',
        }
    for element in root.iter():
        for attribute in ('fill','stroke'):
            color=element.get(attribute)
            if color in mapping:
                replacement=mapping[color]
                if target=='light' and attribute=='stroke' and color==CHALK:
                    replacement='#607489'
                element.set(attribute,replacement)
    return ''.join(ET.tostring(child,encoding='unicode') for child in root)


def save(slug,title,bg,body,description,mood):
    light_bg,dark_bg=SURFACES[slug[:2]]
    for mode,surface in [('light',light_bg),('dark',dark_bg)]:
        original=(mode==mood or (mode=='dark' and mood=='blue'))
        add_variant(slug,title,surface,body if original else companion(body,slug,mode),description,mode)


def compose():
    save('01-still-air','Still Air','#141B20',
         mobile(1410,0,1.56,wire='#8B999D')+circle(1110,1640,4,PETROL),
         'Ein farbiges Mobile in der rechten Bildhälfte; feine Fäden im dunklen Raum.','dark')

    save('02-paper-gravity','Paper Gravity',MIST,
         shape(0,3320,1310,2.7,-12)+hang(1,2380,500,1.5,-12,fill=ORANGE)+shape(3,1850,1760,.8,10),
         'Monumentaler blauer Anschnitt, ein aufgehängter Keil und ein winziges Gegengewicht.','light')

    body=path('M1560 1600Q2130 440 3560 590',stroke='#526265')
    body+=shape(0,2740,1090,1.4,-22)+shape(1,3460,680,1.5,25)+shape(2,2150,1460,1.2,42)+shape(3,3520,1570,1.3,-18)
    body+=circle(1560,1600,7,ORANGE)+circle(3560,590,4,CHALK)
    save('03-night-rehearsal','Night Rehearsal','#14232A',body,
         'Vier Fundstücke proben eine freie Umlaufbahn; keine starre Mitte.','dark')

    save('04-orange-pause','Orange Pause','#EEE6D8',
         hang(1,3130,1560,5.9,-9,color=BROWN)+shape(2,1720,1180,.8,0,INK),
         'Ein übergroßer orangefarbener Keil und eine einzelne schwarze, geknickte Linie.','light')

    body=''
    for i in range(7):
        body+=shape(2,2110+i*260,1570+80*math.sin(i),2.0,-34,fill=[PETROL,'#216B6C','#1C4C52'][i%3])
    body+=shape(1,3100,470,.9,-15)
    save('05-undertow','Undertow','#101F25',body,
         'Petrolfarbene Bänder ziehen als gebrochene Strömung durch die untere rechte Ecke.','dark')

    save('06-blue-interval','Blue Interval',BLUE,
         shape(0,2970,1170,2.2,8,CHALK)+shape(0,2950,1150,2.2,8,'none','#93AFE0',2)+hang(1,1950,540,1.2,0,fill=ORANGE,color=CHALK),
         'Kobaltblau, eine helle Gegenform und ein warmer Keil im weiten Zwischenraum.','blue')

    blue_x,_=anchor(0,2390,1190,1.25,8)
    orange_x,_=anchor(1,3190,1200,1.6,-18)
    brown_x,_=anchor(3,3680,1720,1.1,-12)
    body=path(f'M1360 850Q1900 650 {blue_x:g} 735Q2780 790 {orange_x:g} 1166Q3500 1260 {brown_x:g} 1318',stroke='#84908D')
    body+=hang(0,2390,1190,1.25,8,top=735,color='#84908D')
    body+=hang(1,3190,1200,1.6,-18,top=1166,color='#84908D')
    body+=hang(3,3680,1720,1.1,-12,top=1318,color='#84908D')
    body+=shape(2,1540,1130,.75,70)
    save('07-counterpoint','Counterpoint','#1D2020',body,
         'Unwahrscheinliches Gleichgewicht entlang einer durchhängenden Kurve.','dark')

    body=''
    for i,x,y,s,a in [(0,2870,1220,1.9,-14),(1,2100,740,1.6,-14),(2,3490,1000,1.5,-14)]:
        body+=shape(i,x+36,y+44,s,a,'#C7BFB0')+shape(i,x+14,y+18,s,a,'#D5CCBD')+shape(i,x,y,s,a)
    save('08-cut-and-fold','Cut & Fold','#EAE4D8',body,
         'Drei ausgeschnittene Formen als flache Papierschichten mit präzisen Vektorkanten.','light')

    body=''
    for i,(x,y,s,a) in enumerate([(2340,1000,2.0,-3),(2740,1530,1.55,4),(3160,850,1.0,-5),(3530,1330,1.7,2)]):
        body+=hang(2,x,y,s,a,color='#7F9F9D',fill=[PETROL,'#548F8A',PETROL,'#326B6B'][i])
    body+=hang(3,1870,700,.8,14,color='#7F9F9D')
    save('09-long-conversation','Long Conversation','#142C30',body,
         'Vier lange Bänder an unterschiedlich langen Drähten und ein winziger brauner Zuhörer.','dark')

    body=shape(0,2820,1100,2.0,-8,'none',INK,2)+shape(0,2840,1105,2.0,-8,'none','#A5A6A0',1)
    body+=hang(1,2180,560,1.2,-8,color=INK)+shape(3,3350,1750,1.2,8)
    ax,ay=anchor(0,2820,1100,2,-8);body+=line(ax,0,ax,ay,INK)+circle(ax,ay,4,INK)
    save('10-margin-notes','Margin Notes','#F2F0E9',body,
         'Eine großzügige Konturzeichnung mit einem farbigen, aufgehängten Keil.','light')

    body=''
    for i in range(8,0,-1):
        body+=shape(0,3020+i*45,1080-i*34,1.35+i*.17,-16,'none','#83A4D6',2,opacity=.27+i*.06)
    body+=shape(0,3020,1080,1.35,-16,CHALK)+shape(1,2130,1590,1.35,18)
    save('11-afterimage','Afterimage','#1A438B',body,
         'Versetzte blaue Konturen beschreiben die Nachbewegung einer hellen Form.','blue')

    body=shape(0,4150,1620,3.4,28,'#263E4B')+mobile(1550,120,.95,wire='#A9A093')
    body+=line(0,1850,3840,1850,'#394046',1.5)
    save('12-small-theatre','Small Theatre','#191E25',body,
         'Ein kleines Mobile vor dem angeschnittenen Schatten einer riesigen Form.','dark')

    save('13-equilibrium','Equilibrium','#E8E3D9',
         mobile(1420,150,1.55,wire=INK,angle=-3)+line(0,1960,3840,1960,'#CAC4B8',1),
         'Eine helle, leicht aus dem Lot geratene Hängung über einer feinen Bodenlinie.','light')

    body=shape(0,2980,1170,1.8,17)+shape(1,1920,560,1.7,-32)+shape(2,3320,610,1.4,62)+shape(3,2140,1720,1.4,-25)
    body+=path('M1660 1250Q1880 980 2130 1050M3330 1730Q3530 1660 3670 1480',stroke='#ABB3B1',width=1.5)
    save('14-crosswind','Crosswind','#E7ECE9',body,
         'Vier Originalformen lösen sich aus ihrer Hängung und reagieren auf einen gedachten Wind.','light')

    body=''
    for i in range(12,0,-1):
        body+=shape(0,3080,1110,1.0+i*.24,-12,'none',['#214250','#2D5360','#3A6870'][i%3],1.5)
    body+=shape(0,3080,1110,1,-12,BLUE)+shape(1,2310,1560,.95,7,ORANGE)
    save('15-resonant-room','Resonant Room','#111D24',body,
         'Dünne Konturen öffnen einen asymmetrischen Resonanzraum um einen blauen Kern.','dark')

    body=shape(0,3150,1680,3.0,32,BLUE)+shape(2,1860,1420,2.2,-45,PETROL)
    body+=hang(1,2830,530,2.1,7,color=INK)+shape(3,3420,520,1.4,-5,BROWN)
    save('16-off-script','Off Script',CHALK,body,
         'Große Anschnitte, ein hängender Keil und eine offene linke Fläche: kontrolliertes Durcheinander.','light')


    for mode in ('light','dark'):
        dark=mode=='dark'
        bg='#15292D' if dark else '#E5EDE8'
        wire='#7D999A' if dark else '#8A9D98'
        body=''
        for i in range(6):
            body+=shape(2,2330+i*190,1390-i*85,1.5,22+i*8,
                        fill=[PETROL,'#3F7776','#5B9490'][i%3])
        body+=hang(1,3210,490,1.4,16,color=wire)+shape(3,1880,1690,.9,-22)
        add_variant('17-tidal-balance','Tidal Balance',bg,body,
                    'Petrolbänder spreizen sich wie eine langsame Strömung; ein Keil hält dagegen.',mode)

        bg='#202332' if dark else '#EDE7DF'
        depth='#121624' if dark else '#D1C7B8'
        body=shape(0,3100,1280,2.5,-28,depth)+shape(1,3000,1120,4.6,13,ORANGE)
        body+=shape(0,2920,1120,2.15,-28,BLUE)+shape(3,1860,1690,1.3,12)
        add_variant('18-soft-collision','Soft Collision',bg,body,
                    'Blau und Orange überlagern sich als große, präzise geschnittene Papierkörper.',mode)

        bg='#142128' if dark else '#F0EDE5';wire='#8D9DA0' if dark else '#7F8985'
        poses=[(0,2770,1190,1.45,-13),(1,3330,1010,1.45,24),
               (2,3510,1520,1.1,-8),(3,1980,1150,1.3,6)]
        joints=[(2290,365),(2810,510),(3340,650),(1830,480)]
        body=path('M1830 480L2290 365L2810 510L3340 650',stroke=wire)
        body+=line(2290,0,2290,365,wire)
        for (i,x,y,size,angle),(jx,jy) in zip(poses,joints):
            ax,ay=anchor(i,x,y,size,angle)
            body+=line(jx,jy,ax,ay,wire)+shape(i,x,y,size,angle)+circle(jx,jy,4,wire)
        add_variant('19-thread-atlas','Thread Atlas',bg,body,
                    'Ein räumliches Netz aus vier Fäden trägt die unveränderten Fundstücke.',mode)

        bg='#242021' if dark else '#EEE6DB'
        body=shape(1,-40,1970,10.5,18,ORANGE)+shape(0,3000,790,1.18,-16,BLUE)
        body+=shape(2,3250,1550,1.0,20,PETROL)
        body+=line(2560,0,*anchor(0,3000,790,1.18,-16),'#A8958A' if dark else '#A79B8C')
        add_variant('20-diagonal-silence','Diagonal Silence',bg,body,
                    'Ein orangefarbener Anschnitt von links trifft auf eine kleine blaue Hängung rechts.',mode)

        bg='#15242D' if dark else '#E4E9EB'
        body=shape(0,2930,2300,3.8,-75,BLUE)
        body+=shape(2,2600,1540,2.8,84,PETROL)+hang(1,3350,640,1.9,-19,color='#8C9DA2' if dark else '#87949A')
        add_variant('21-folded-horizon','Folded Horizon',bg,body,
                    'Die blaue Originalform wird durch Drehung und Anschnitt zu einer offenen Landschaft.',mode)

        bg='#1C252B' if dark else '#F1EEE7';wire='#9AA7A9' if dark else '#8C9390'
        body=hang(0,2950,1180,1.7,12,color=wire)
        ax,ay=anchor(0,2110,760,.85,-18)
        body+=line(ax,0,ax,ay,wire)+shape(0,2110,760,.85,-18,'none',wire,2)
        body+=shape(1,3450,1620,1.25,30,ORANGE)
        add_variant('22-suspended-duet','Suspended Duet',bg,body,
                    'Eine volle und eine nur gezeichnete Play-Form führen ein stilles Zwiegespräch.',mode)

        bg='#1D2328' if dark else '#E9E4DA';faint='#28343C' if dark else '#D6D0C4'
        body=shape(0,3190,1370,2.4,10,faint)+shape(2,2330,1490,1.55,-8,faint)
        body+=mobile(2120,640,.7,wire='#A9B2AD' if dark else '#7A837C')
        add_variant('23-quiet-assembly','Quiet Assembly',bg,body,
                    'Ein kleines farbiges Mobile vor großen, beinahe tonalen Schatten seiner Einzelteile.',mode)

        bg='#15262C' if dark else '#E4ECE8';wire='#6C858B' if dark else '#9CAFAE'
        body=line(2180,1050,3840,1050,wire,1)+line(3000,0,3000,1050,wire,1)
        for i in range(5):
            x=1990+i*365;y=1510-120*math.sin(i*1.2)
            body+=shape(2,x,y,1.4,72,PETROL if i%2==0 else ('#387579' if dark else '#74A5A0'))
            ax,ay=anchor(2,x,y,1.4,72);body+=line(ax,1050,ax,ay,wire,1)
        body+=hang(1,2940,600,1.6,-13,color=wire)+shape(3,1800,850,1.1,9)
        add_variant('24-kinetic-score','Kinetic Score',bg,body,
                    'Fünf gedrehte Bänder schreiben eine freie Partitur aus Rhythmus und Pausen.',mode)


def make_preview(out, items, filename, columns=4):
    font=ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf',20)
    w,h,gap,label=480,270,20,44
    rows=math.ceil(len(items)/columns)
    sheet=Image.new('RGB',(columns*w+(columns+1)*gap,rows*(h+label)+(rows+1)*gap),'#11191E')
    draw=ImageDraw.Draw(sheet)
    for i,item in enumerate(items):
        x=gap+i%columns*(w+gap);y=gap+i//columns*(h+label+gap)
        with Image.open(out/item['png']) as im:
            sheet.paste(im.convert('RGB').resize((w,h),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+3,y+h+10),item['family'][:2]+'  '+item['title'],font=font,fill=CHALK)
    sheet.save(out/filename,quality=95,subsampling=0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path.home()/'Bilder/Wallpapers/flausen-4k')
    args=parser.parse_args();out=args.output.resolve()
    compose()
    assert len(collection)==48
    for mode in ('light','dark'):
        for kind in ('svg','png'):
            (out/mode/kind).mkdir(parents=True,exist_ok=True)
    for item in collection:
        body=item.pop('body')
        text=f'<svg xmlns="http://www.w3.org/2000/svg" width="3840" height="2160" viewBox="0 0 3840 2160"><title>{escape(item["title"])} / {item["mode"]} — flausen.</title><desc>{escape(item["description"])}</desc>'+rect(0,0,3840,2160,item['background'])+body+'</svg>\n'
        ET.fromstring(text)
        (out/item['svg']).write_text(text)
    def render(item):
        subprocess.run(['rsvg-convert','-w','3840','-h','2160','-o',str(out/item['png']),str(out/item['svg'])],check=True)
        print(item['id'],flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(render,collection))
    (out/'collection.json').write_text(json.dumps(collection,ensure_ascii=False,indent=2)+'\n')
    for mode in ('light','dark'):
        items=[item for item in collection if item['mode']==mode]
        assert len(items)==24
        (out/mode/'collection.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
        make_preview(out,items,f'{mode}/collection-preview.jpg')
    make_preview(out,collection,'collection-preview.jpg',columns=6)
    checks=[]
    for item in collection:
        svg=out/item['svg'];png=out/item['png']
        rgb=[int(item['background'][i:i+2],16)/255 for i in (1,3,5)]
        linear=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in rgb]
        luminance=sum(v*w for v,w in zip(linear,(0.2126,0.7152,0.0722)))
        assert luminance>0.65 if item['mode']=='light' else luminance<0.08
        for element in ET.parse(svg).iter():
            assert element.tag.rsplit('}',1)[-1] not in ['image','filter','script','foreignObject','text']
            assert not any('href' in key for key in element.attrib)
        with Image.open(png) as image:
            assert image.size==(3840,2160)
            if image.mode=='RGBA':
                assert image.getextrema()[3]==(255,255)
        checks.append({'id':item['id'],'resolution':[3840,2160],
                       'svgSha256':hashlib.sha256(svg.read_bytes()).hexdigest(),
                       'pngSha256':hashlib.sha256(png.read_bytes()).hexdigest()})
    (out/'verification.json').write_text(json.dumps({'count':len(collection),'perMode':24,
        'nativeVectors':True,'externalAssets':False,'bitmapsInSvg':False,'checks':checks},indent=2)+'\n')
    for mode in ('light','dark','all'):
        items=collection if mode=='all' else [i for i in collection if i['mode']==mode]
        members=[out/'collection.json',out/'verification.json'] if mode=='all' else []
        if mode=='all':
            members += [out/'collection-preview.jpg']
            for m in ('light','dark'):
                members += [out/m/'collection.json',out/m/'collection-preview.jpg']
        else:
            members += [out/mode/'collection.json',out/mode/'collection-preview.jpg']
        members += [out/i[kind] for i in items for kind in ('svg','png')]
        name='flausen-wallpapers-4k.zip' if mode=='all' else f'flausen-{mode}-4k.zip'
        with zipfile.ZipFile(out/name,'w',zipfile.ZIP_DEFLATED) as archive:
            if mode!='all':
                archive.writestr('flausen-4k/collection.json',json.dumps(items,ensure_ascii=False,indent=2)+'\n')
                archive.writestr('flausen-4k/verification.json',json.dumps({
                    'count':len(items),'mode':mode,'checks':[c for c in checks if c['id'].endswith('-'+mode)]},indent=2)+'\n')
            for member in sorted(members):
                archive.write(member,Path('flausen-4k')/member.relative_to(out))
    print(f'Created and verified 24 paired compositions / 48 wallpapers: {out}')

if __name__=='__main__':main()
