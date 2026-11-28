"""Locally generated topic-specific visual cards; no stock-media API needed."""
from pathlib import Path
import subprocess, re
from PIL import Image, ImageDraw, ImageFont

def _clean(s):
    return re.sub(r"\\s+", " ", str(s or "")).strip()

def _font(size, bold=False):
    paths=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for p in paths:
        try: return ImageFont.truetype(p,size)
        except OSError: pass
    return ImageFont.load_default()

def _wrap(draw,text,font,width):
    words=text.split(); lines=[]; current=""
    for word in words:
        trial=(current+" "+word).strip()
        if draw.textbbox((0,0),trial,font=font)[2]<=width: current=trial
        elif current: lines.append(current);current=word
        else:lines.append(word);current=""
    if current:lines.append(current)
    return lines

def generate_visual_clips(topic, script, outdir, duration, count=5):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    title=_clean(topic.get("title","AI PINTAR")); category=_clean(topic.get("category","AI"))
    sentences=[_clean(x) for x in re.split(r"(?<=[.!?])\\s+",script) if _clean(x)]
    scenes=[]
    for i in range(count):
        beat=sentences[min(i,len(sentences)-1)] if sentences else title
        im=Image.new("RGB",(1080,1920),(16,24,44));d=ImageDraw.Draw(im)
        # Abstract, branded but not misleading, consistent portrait layout.
        for y in range(1920):
            col=(16,int(24+y*0.012),int(44+y*0.025))
            d.line((0,y,1080,y),fill=col)
        for x in range(80,1080,140):d.line((x,0,x,1920),fill=(36,52,79),width=2)
        for y in range(80,1920,140):d.line((0,y,1080,y),fill=(36,52,79),width=2)
        d.rounded_rectangle((72,140,1008,330),radius=38,fill=(27,49,82),outline=(103,157,237),width=3)
        d.text((120,210),category.upper()[:28],font=_font(44,True),fill=(190,220,255))
        d.rounded_rectangle((72,430,1008,1400),radius=56,fill=(18,32,56),outline=(75,130,200),width=4)
        d.ellipse((300,530,780,1010),fill=(35,75,130),outline=(110,170,250),width=8)
        d.rounded_rectangle((390,680,690,860),radius=28,fill=(22,42,75),outline=(190,220,255),width=4)
        d.line((440,740,640,740),fill=(190,220,255),width=14);d.line((440,790,590,790),fill=(190,220,255),width=14)
        d.text((540,1080),f"SCENE {i+1}",font=_font(40,True),fill=(160,200,255),anchor="mm")
        font=_font(40,True); lines=_wrap(d,beat,font,740)
        y=1150
        for line in lines[:5]:
            d.text((540,y),line,font=font,fill=(255,255,255),anchor="mm");y+=58
        d.rounded_rectangle((72,1490,1008,1760),radius=36,fill=(27,49,82))
        title_lines=_wrap(d,title,_font(38,True),820)
        y=1570
        for line in title_lines[:3]:
            d.text((120,y),line,font=_font(38,True),fill=(255,255,255));y+=55
        d.text((120,1700),"AI PINTAR • visual ilustratif",font=_font(28),fill=(190,220,255))
        image_path=outdir/f"scene_{i+1:02d}.png";im.save(image_path)
        clip=outdir/f"scene_{i+1:02d}.mp4";seg=duration/count
        subprocess.run(["ffmpeg","-y","-loop","1","-i",str(image_path),"-t",str(seg),"-vf","scale=1080:1920,fps=30","-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p",str(clip)],check=True,capture_output=True,timeout=90)
        scenes.append(str(clip))
    return scenes
