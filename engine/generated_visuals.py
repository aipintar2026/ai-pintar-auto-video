"""High-quality animated illustrative scene cards generated locally for AI PINTAR."""
from pathlib import Path
import subprocess, re, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H=1080,1920
PALETTES=[((13,24,48),(28,76,130),(76,194,255)),((18,22,44),(67,44,120),(187,124,255)),((12,38,43),(29,112,90),(125,255,190)),((40,25,27),(128,57,47),(255,179,106)),((20,34,54),(43,86,115),(135,218,255))]

def _clean(s):
    return re.sub(r"\\s+", " ", str(s or "")).strip()

def _font(size,bold=False):
    paths=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for p in paths:
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()

def _wrap(draw,text,font,width):
    lines=[];current=""
    for word in text.split():
        candidate=(current+" "+word).strip()
        if draw.textbbox((0,0),candidate,font=font)[2]<=width:current=candidate
        elif current:lines.append(current);current=word
        else:lines.append(word);current=""
    if current:lines.append(current)
    return lines

def _gradient(bg,accent):
    im=Image.new("RGB",(W,H));p=im.load()
    for y in range(H):
        t=y/H
        row=tuple(int(bg[k]*(1-t)+accent[k]*t*.42) for k in range(3))
        for x in range(W):p[x,y]=row
    return im

def _icon(draw,kind,cx,cy,accent):
    # Clean vector-like icons tailored to scene beat, not random stock scenery.
    draw.ellipse((cx-175,cy-175,cx+175,cy+175),fill=(24,45,78),outline=accent,width=6)
    if kind in ("prompt","text","menulis","instruksi"):
        draw.rounded_rectangle((cx-95,cy-115,cx+95,cy+115),radius=24,fill=(18,31,55),outline=accent,width=5)
        for y,ww in [(cy-45,130),(cy,160),(cy+45,110)]:draw.rounded_rectangle((cx-ww//2,y-8,cx+ww//2,y+8),radius=8,fill=accent)
        draw.line((cx+65,cy+80,cx+110,cy+125),fill=(255,255,255),width=12)
    elif kind in ("video","konten","media"):
        draw.rounded_rectangle((cx-125,cy-85,cx+125,cy+85),radius=25,fill=(18,31,55),outline=accent,width=6)
        draw.polygon([(cx-35,cy-55),(cx+65,cy),(cx-35,cy+55)],fill=accent)
        draw.rectangle((cx-70,cy+110,cx+70,cy+125),fill=(255,255,255))
    elif kind in ("bisnis","produk","jualan"):
        draw.rounded_rectangle((cx-115,cy-100,cx+115,cy+110),radius=30,fill=(18,31,55),outline=accent,width=6)
        draw.arc((cx-65,cy-130,cx+65,cy+10),180,360,fill=accent,width=12)
        draw.line((cx-65,cy+25,cx+65,cy+25),fill=(255,255,255),width=8)
    elif kind in ("keamanan","privasi"):
        draw.polygon([(cx,cy-130),(cx+110,cy-65),(cx+85,cy+65),(cx,cy+130),(cx-85,cy+65),(cx-110,cy-65)],fill=(18,31,55),outline=accent)
        draw.arc((cx-55,cy-60,cx+55,cy+65),180,360,fill=accent,width=12)
        draw.rounded_rectangle((cx-65,cy-5,cx+65,cy+75),radius=15,fill=accent)
    else:
        draw.rounded_rectangle((cx-120,cy-85,cx+120,cy+85),radius=30,fill=(18,31,55),outline=accent,width=6)
        draw.ellipse((cx-48,cy-48,cx+48,cy+48),outline=accent,width=12)
        draw.line((cx+30,cy+30,cx+90,cy+90),fill=(255,255,255),width=14)

def _scene_kind(topic,beat):
    text=(str(topic.get("category",""))+" "+str(topic.get("title",""))+" "+beat).lower()
    if any(x in text for x in ("prompt","instruksi","menulis","teks","caption")):return "prompt"
    if any(x in text for x in ("video","konten","media","editing")):return "video"
    if any(x in text for x in ("bisnis","produk","jualan","umkm")):return "bisnis"
    if any(x in text for x in ("keamanan","privasi","aman","data")):return "keamanan"
    return "technology"

def generate_visual_clips(topic,script,outdir,duration,count=5):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    title=_clean(topic.get("title","AI PINTAR"));category=_clean(topic.get("category","AI"))
    sentences=[_clean(x) for x in re.split(r"(?<=[.!?])\\s+",str(script)) if _clean(x)]
    if not sentences:sentences=[title]
    scenes=[]
    for i in range(count):
        beat=sentences[min(i,len(sentences)-1)]
        bg,mid,accent=PALETTES[i%len(PALETTES)]
        im=_gradient(bg,mid);d=ImageDraw.Draw(im)
        # Soft luminous backdrop and decorative orbital motifs.
        glow=Image.new("RGBA",(W,H),(0,0,0,0));gd=ImageDraw.Draw(glow)
        gd.ellipse((W-650,-120,W+150,680),fill=(*accent,45));gd.ellipse((-360,1200,450,2050),fill=(*accent,28))
        glow=glow.filter(ImageFilter.GaussianBlur(110));im=Image.alpha_composite(im.convert("RGBA"),glow);d=ImageDraw.Draw(im)
        d.rounded_rectangle((72,130,1008,305),radius=36,fill=(255,255,255,15),outline=(*accent,160),width=3)
        d.text((125,185),category.upper()[:30],font=_font(42,True),fill=(*accent,255))
        d.text((125,252),f"AI PINTAR  /  {i+1:02d}",font=_font(26),fill=(210,225,245,255))
        d.rounded_rectangle((72,390,1008,1390),radius=60,fill=(8,16,32,170),outline=(*accent,140),width=3)
        _icon(d,_scene_kind(topic,beat),540,760,(*accent,255))
        d.text((540,1065),"VISUAL IDE",font=_font(30,True),fill=(*accent,255),anchor="mm")
        lines=_wrap(d,beat,_font(38,True),780)
        y=1150
        for line in lines[:4]:
            d.text((540,y),line,font=_font(38,True),fill=(255,255,255,255),anchor="mm");y+=58
        d.rounded_rectangle((72,1480,1008,1780),radius=40,fill=(255,255,255,18),outline=(*accent,140),width=2)
        title_lines=_wrap(d,title,_font(40,True),800);y=1560
        for line in title_lines[:3]:
            d.text((120,y),line,font=_font(40,True),fill=(255,255,255,255));y+=58
        d.text((120,1720),"Visual ilustratif • AI PINTAR",font=_font(28),fill=(*accent,255))
        image_path=outdir/f"scene_{i+1:02d}.png";im.convert("RGB").save(image_path)
        clip=outdir/f"scene_{i+1:02d}.mp4";seg=duration/count
        # Slow, controlled camera drift / zoom on each scene, with scene-specific motion direction.
        xexpr="iw/2-(iw/zoom/2)" if i%2==0 else "iw/2-(iw/zoom/2)+8"
        vf=f"scale=1080:1920,fps=30,zoompan=z='min(zoom+0.00035,1.035)':x='{xexpr}':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920"
        subprocess.run(["ffmpeg","-y","-loop","1","-i",str(image_path),"-t",str(seg),"-vf",vf,"-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p",str(clip)],check=True,capture_output=True,timeout=90)
        scenes.append(str(clip))
    return scenes
