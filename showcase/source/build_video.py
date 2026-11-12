#!/usr/bin/env python3
"""Assemble focused native UI cards and a real workflow into a silent 1080p tour."""
from pathlib import Path
import json,subprocess,textwrap
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[2];KIT=ROOT/'showcase';OUT=KIT/'exports';OUT.mkdir(exist_ok=True)
TMP=ROOT/'.cache/showcase-video';TMP.mkdir(parents=True,exist_ok=True)
W,H=1920,1080
F='/usr/share/fonts/noto/NotoSans-Regular.ttf';B='/usr/share/fonts/noto/NotoSans-Bold.ttf'
base=Image.open(KIT/'source/background.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
dark=Image.new('RGB',(W,H),'#10171b');base=Image.blend(base,dark,.87)
scenes=[
 ('intro','Your computer.\nYour playground.','Phase one. A connected desktop for everyday life and play.','desktop-hero',None,4),
 ('start','Start with an idea.','Search apps, return to a recent file or ask Hermes in the same Start menu.','launcher',(0,0,720,540),7),
 ('live','Make room as you go.','Actual Files, Kate, settings, tiling and fullscreen interactions.',None,None,40.4),
 ('hermes','Ask. See. Decide.','Read system information, see each step and approve proposed shell commands.','hermes',(0,230,720,700),6),
 ('models','Choose where it runs.','Local model, network endpoint or cloud provider. Changes apply to a new conversation.','hermes-settings',(320,235,1160,740),7),
 ('capture','Keep the useful bits.','Capture a region, window or screen. Edit shortcuts right where you use them.','capture',None,6),
 ('clipboard','Copy. Pin. Carry on.','A screenshot flows into the gallery and clipboard. Pin the things you need again.','clipboard',None,6),
 ('updates','One update overview.','See status across the desktop, games and apps. Open the responsible app to install.','updates',(0,0,520,500),6),
 ('appearance','Make this space yours.','Light and dark appearance, six accents, wallpapers and native settings in one window.','appearance',(320,125,1160,710),6),
 ('end','One desktop.\nA continuous flow.','Start an idea. Make room. Step into play. Return to what matters.','desktop-hero',None,5)
]

def font(size,bold=False):return ImageFont.truetype(B if bold else F,size)
def wrapped(draw,copy,x,y,width,size,color,leading=1.4,bold=False):
    f=font(size,bold);line=''
    for word in copy.split():
        test=(line+' '+word).strip()
        if draw.textlength(test,font=f)>width and line:
            draw.text((x,y),line,font=f,fill=color);y+=round(size*leading);line=word
        else:line=test
    if line:draw.text((x,y),line,font=f,fill=color)

segments=[];subtitles=[];timeline=0
for index,(name,title,body,shot,crop,duration) in enumerate(scenes):
    output=TMP/f'{index:02}-{name}.mp4'
    if name=='live':
        source_start=0.0
        marker_offset=4.4
        markers=json.loads((KIT/'source/workflow-markers.json').read_text())
        filters=['scale=1728:972:flags=lanczos','pad=1920:1080:96:108:color=0x10171b']
        for i,marker in enumerate(markers):
            start=max(0,marker['seconds']-marker_offset)
            end=(markers[i+1]['seconds']-marker_offset) if i+1<len(markers) else duration
            if end<=0:continue
            label=marker['name']
            if 'Fullscreen moves' in label:label='Fullscreen moves to another workspace (local video demo)'
            p=TMP/f'caption-{i}.txt';p.write_text(label)
            filters.append(f"drawtext=fontfile={F}:textfile={p}:fontsize=38:fontcolor=0xF5F4F0:x=96:y=30:enable='between(t,{start:.3f},{end:.3f})'")
        filters+=['fade=t=in:st=0:d=0.2',f'fade=t=out:st={duration-.2}:d=0.2']
        command=['ffmpeg','-y','-v','error','-ss',str(source_start),'-i',str(KIT/'desktop-workflow.mp4'),'-t',str(duration),'-vf',','.join(filters),'-an']
    else:
        frame=base.copy();draw=ImageDraw.Draw(frame)
        draw.text((80,40),'flausen.',font=font(34,True),fill='#F5F4F0')
        draw.text((1665,46),'PHASE ONE',font=font(22),fill='#B6BDC2')
        for line_number,line in enumerate(title.split('\n')):
            draw.text((80,158+line_number*84),line,font=font(60,True),fill='#F5F4F0')
        body_y=350 if '\n' in title else 290
        wrapped(draw,body,80,body_y,560,35,'#D0D5D8')
        image=Image.open(KIT/'screenshots'/f'{shot}.png').convert('RGB')
        if crop:image=image.crop(crop)
        image.thumbnail((1050,760),Image.Resampling.LANCZOS)
        frame.paste(image,(760+(1050-image.width)//2,215+(760-image.height)//2))
        draw.text((80,978),'Your computer. Your playground.',font=font(24),fill='#B6BDC2')
        if name in ['capture','clipboard','start']:
            draw.text((760,1005),'Staged example content in native UI',font=font(20),fill='#B6BDC2')
        if name=='end':
            wrapped(draw,'Current development build. Not a release or performance benchmark.',80,740,560,22,'#B6BDC2')
        path=OUT/f'{name}-1080p.png';frame.save(path)
        command=['ffmpeg','-y','-v','error','-loop','1','-i',str(path),'-t',str(duration),'-vf',f'fade=t=in:st=0:d=0.2,fade=t=out:st={duration-.2}:d=0.2','-an']
    command+=['-r','30','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    subprocess.run(command,check=True)
    segments.append(output);subtitles.append((timeline,timeline+duration,title.replace('\n',' ')+' '+body));timeline+=duration
    print(name,flush=True)
concat=TMP/'segments.txt';concat.write_text(''.join("file '"+str(p)+"'\n" for p in segments))
result=KIT/'flausen-showcase-1080p.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(result)],check=True)
def stamp(time):
    ms=round(time*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
srt='\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{copy}' for i,(a,b,copy) in enumerate(subtitles))+'\n'
(KIT/'flausen-showcase-en.srt').write_text(srt)
(KIT/'demo-script.txt').write_text('\n\n'.join(f'{a:.1f}-{b:.1f}s | {copy}' for a,b,copy in subtitles)+'\n\nLive section: real desktop actions. Fullscreen routing uses a local media clip.\nOther sections: focused native UI captures. Gallery, clipboard and recent documents are staged.\nNo voiceover or music is included.\n')
print(result,'duration',timeline,flush=True)
