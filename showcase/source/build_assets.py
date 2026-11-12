#!/usr/bin/env python3
"""Build the English overview and readable 1080p showcase cards from native captures."""
from pathlib import Path
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[2]
KIT=ROOT/'showcase'
OUT=ROOT/'output/pdf'
OUT.mkdir(parents=True,exist_ok=True)
EXPORT=KIT/'exports';EXPORT.mkdir(exist_ok=True)
DATA=json.loads((KIT/'features.json').read_text())
W,H=1920,1080
INK='#F5F4F0';MUTED='#B6BDC2';BLUE='#649DEB';ORANGE='#E56D2F'
FONT='/usr/share/fonts/noto/NotoSans-Regular.ttf'
BOLD='/usr/share/fonts/noto/NotoSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('Noto',FONT));pdfmetrics.registerFont(TTFont('NotoBold',BOLD))
pdfmetrics.registerFont(TTFont('Serif','/usr/share/fonts/TTF/DejaVuSerif.ttf'))
pdf=canvas.Canvas(str(OUT/'flausen-phase-one-overview.pdf'),pagesize=(W,H))
pdf.setTitle('flausen. | Phase one showcase');pdf.setAuthor('ralleur')

def text(x,y,copy,size=30,color=INK,font='Noto'):
    pdf.setFillColor(color);pdf.setFont(font,size);pdf.drawString(x,y,copy)

def wrap(copy,x,y,width,size=30,color=MUTED,leading=None,font='Noto'):
    leading=leading or size*1.42
    words=copy.split();line=''
    for word in words:
        test=(line+' '+word).strip()
        if pdfmetrics.stringWidth(test,font,size)>width and line:
            text(x,y,line,size,color,font);y-=leading;line=word
        else:line=test
    if line:text(x,y,line,size,color,font);y-=leading
    return y

def background(index,label):
    pdf.drawImage(str(KIT/'source/background.png'),0,0,width=W,height=H)
    pdf.setFillColor('#10171B');pdf.setFillAlpha(.91);pdf.rect(0,0,W,H,fill=1,stroke=0);pdf.setFillAlpha(1)
    text(76,1010,'flausen.',38,INK,'Serif');text(288,1014,'by ralleur',20,MUTED)
    text(76,40,label.upper(),19,MUTED)
    text(1720,40,f'PHASE ONE / {index:02}',19,MUTED)

def title(heading,subtitle):
    text(76,914,heading,64,INK,'NotoBold');text(78,855,subtitle,29,MUTED)

def image(name,x,y,w,h,crop=None):
    path=KIT/'screenshots'/f'{name}.png'
    if not path.exists():return
    im=Image.open(path).convert('RGB')
    if crop:im=im.crop(crop)
    scale=min(w/im.width,h/im.height);iw,ih=im.width*scale,im.height*scale
    pdf.drawImage(ImageReader(im),x+(w-iw)/2,y+(h-ih)/2,iw,ih,mask='auto')

def bullets(items,x,y,width,size=29):
    for line in items:
        pdf.setFillColor(ORANGE);pdf.circle(x+5,y+9,4,fill=1,stroke=0)
        y=wrap(line,x+30,y,width-30,size,INK)-20
    return y

def finish():pdf.showPage()

background(1,'Your computer. Your playground.')
text(76,909,'Your computer. Your playground.',68,INK,'NotoBold')
text(78,848,'Phase one: a connected desktop for everyday life and play.',31,MUTED)
image('desktop-hero',76,190,1768,620)
text(78,127,'CachyOS  /  KDE Plasma + KWin  /  Caelestia',26,INK)
text(78,85,'Current development build. Real UI captures. Staged example documents.',22,MUTED)
finish()

background(2,'Everyday')
title('Start with an idea.','Apps, files and an assistant in one starting point.')
image('launcher',80,105,580,710)
# Focus the real Files window; the full desktop has its own opening view.
image('files',720,365,1100,435,crop=(220,190,1840,1470))
bullets(['Files: shared header and native context menus.','Space for quick previews. Folder colors for orientation.','Open ZIPs to extract with Ark. Shared KDE file pickers.'],735,302,1050,29)
finish()

background(3,'Window flow')
title('Make room as you go.','Float freely. Tile when it helps. Return just as easily.')
image('tiling',76,188,1110,625)
# The layout is the subject here; detailed control text is shown on focused pages.
bullets(['Windows start floating.','Super + Shift + drag joins the layout.','Super + right-drag adjusts a shared boundary.','Super + drag brings a window out again.'],1250,751,570,31)
text(80,119,'Four distinct workspaces. Fullscreen routes right; original assignments return on exit.',28,INK)
text(80,76,'Fullscreen routing is demonstrated in the video with a local media clip.',22,MUTED)
finish()

background(4,'Hermes')
title('Ask. See. Decide.','Your assistant belongs to the desktop.')
image('hermes',80,112,570,700)
image('hermes-settings',690,300,1140,520)
bullets(['Read real system information; see tool steps and results.','Approve proposed shell commands individually.','Choose local, network or cloud models. Preview GPU memory needs.'],720,250,1080,27)
text(82,85,'Initial chat view; no paid request was issued for this capture. Memory previews are estimates.',21,MUTED)
finish()

background(5,'Capture and carry on')
title('Keep the useful bits.','Capture an idea. Copy it. Carry on.')
image('capture',80,132,650,665)
image('clipboard',790,422,1030,360)
bullets(['Capture region, window or screen; recognize text and search images.','Edit global shortcuts directly in the capture menu.','Copy a screenshot, open its original or pin a useful clipboard entry.'],800,351,1000,30)
text(80,88,'Gallery and clipboard contents are staged examples; private history is excluded.',23,MUTED)
finish()

background(6,'Connected controls')
title('Stay in the flow.','Small controls. One connected desktop.')
image('updates',80,114,535,680)
image('appearance',675,316,1155,499)
bullets(['A common home for appearance, devices and embedded KDE settings.','Network, VPN, Bluetooth, audio and calendar follow the same menu system.','The update hub brings sources together; each app handles its own installs.'],705,264,1090,28)
text(80,81,'Steam, Battle.net, WowUp and ArtCraft use real status sources, with unknown and offline states.',22,MUTED)
finish()

background(7,'How it connects')
title('One desktop. A continuous flow.','The features make more sense together.')
steps=[('START','Apps + recent files','launcher'),('MAKE','Files + optional tiling','tiling'),('PLAY','Fullscreen + workspaces','fullscreen')]
for i,(name,detail,shot) in enumerate(steps):
    x=80+i*600
    pdf.setFillColor('#20292E');pdf.roundRect(x,380,560,390,26,fill=1,stroke=0)
    text(x+28,709,name,23,ORANGE,'NotoBold');wrap(detail,x+28,650,500,34,INK)
    image(shot,x+25,405,510,190)
    if i<2:text(x+567,543,'>',35,MUTED)
wrap('Hermes helps you inspect and act. Capture and clipboard carry the results forward. Settings connects the controls; the update hub hands maintenance back to the right app.',82,293,1710,36,INK)
text(82,113,'One visual language: typography, glass, window controls, light/dark appearance and kinetic forms.',28,MUTED)
text(82,70,'A desktop customization showcase; no ISO release, boot demonstration or game-performance claim.',23,MUTED)
finish()

# Complete feature inventory, grouped into two readable pages.
features=DATA['features']
for page,group in enumerate([features[:14],features[14:]],8):
    background(page,'Feature index')
    title('The feature set.','A map of phase one. Details and source paths are included in features.json.')
    for i,feature in enumerate(group):
        col=i//7;row=i%7;x=82+col*910;y=772-row*94
        text(x,y,feature['name'],28,INK,'NotoBold')
        # Short feature-index text; detailed descriptions stay in the editable manifest.
        copy=feature['copy']
        if len(copy)>123:copy=copy[:120].rsplit(' ',1)[0]+'...'
        wrap(copy,x,y-34,840,21,MUTED,29)
    finish()
pdf.save()
subprocess.run(['pdftoppm','-png','-scale-to-x','1920','-scale-to-y','1080',str(OUT/'flausen-phase-one-overview.pdf'),str(EXPORT/'overview')],check=True)
print(OUT/'flausen-phase-one-overview.pdf')
