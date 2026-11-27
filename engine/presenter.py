"""Deterministic AI PINTAR master-presenter illustration; no external asset required."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

GREEN=(0,255,0)
NAVY=(18,39,92)
BLUE=(24,137,231)
WHITE=(246,249,255)
SKIN=(238,191,157)
DARK=(38,31,35)


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def generate_master_presenter(output, size=(1080,1920)):
    """Create a reproducible portrait presenter illustration on chroma-green."""
    w,h=size
    im=Image.new("RGB",size,GREEN)
    d=ImageDraw.Draw(im)
    # torso and shoulders
    d.polygon([(95,1920),(115,1320),(265,1125),(430,1080),(650,1080),(815,1125),(965,1320),(985,1920)],fill=WHITE)
    d.polygon([(385,1080),(540,1260),(695,1080),(650,1020),(430,1020)],fill=NAVY)
    # neck
    d.rectangle((420,900,660,1160),fill=SKIN)
    # face
    d.ellipse((290,270,790,900),fill=SKIN)
    # ears
    d.ellipse((245,500,330,640),fill=SKIN); d.ellipse((750,500,835,640),fill=SKIN)
    # hijab outer silhouette and shoulder drape
    d.polygon([(270,500),(285,255),(405,120),(535,90),(690,160),(805,310),(820,535),(900,1050),(790,1210),(640,1130),(565,1050),(475,1130),(300,1200),(180,1050),(245,640)],fill=NAVY)
    d.ellipse((315,220,765,850),fill=SKIN)
    # hijab framing the face
    d.polygon([(300,300),(385,150),(520,90),(675,150),(780,300),(760,460),(680,335),(600,260),(480,255),(390,340),(340,500)],fill=NAVY)
    d.polygon([(320,450),(370,720),(460,860),(540,940),(660,840),(760,660),(760,450),(700,540),(630,620),(500,620),(410,540)],fill=NAVY)
    # facial features
    d.line((405,485,485,485),fill=DARK,width=18); d.line((610,485,690,485),fill=DARK,width=18)
    d.ellipse((438,490,462,520),fill=DARK); d.ellipse((638,490,662,520),fill=DARK)
    d.line((540,515,525,610,565,615),fill=(180,120,100),width=10)
    d.arc((445,650,650,790),start=10,end=170,fill=(130,55,55),width=16)
    # blazer lapels
    d.polygon([(340,1100),(430,1170),(520,1370),(420,1460),(280,1180)],fill=WHITE)
    d.polygon([(740,1100),(650,1170),(560,1370),(660,1460),(800,1180)],fill=WHITE)
    d.line((430,1170,520,1370,420,1460),fill=BLUE,width=12)
    d.line((650,1170,560,1370,660,1460),fill=BLUE,width=12)
    # sleeves
    d.polygon([(130,1380),(260,1220),(370,1390),(300,1780),(160,1770)],fill=WHITE)
    d.polygon([(950,1380),(820,1220),(710,1390),(780,1780),(920,1770)],fill=WHITE)
    # clasped hands
    d.ellipse((395,1540,590,1750),fill=SKIN)
    d.ellipse((500,1530,690,1745),fill=SKIN)
    d.line((430,1640,580,1700,650,1635),fill=(180,120,100),width=8)
    # subtle circuit accent on viewer-right blazer
    d.line((730,1420,760,1420,760,1500,800,1500),fill=BLUE,width=14)
    d.line((760,1500,760,1570,820,1570),fill=BLUE,width=14)
    for x,y in [(730,1420),(800,1500),(820,1570)]:
        d.ellipse((x-16,y-16,x+16,y+16),fill=BLUE)
    # soft outline around the shoulders to preserve separation on green
    d.line([(95,1920),(115,1320),(265,1125)],fill=(210,220,240),width=10)
    d.line([(965,1920),(965,1320),(815,1125)],fill=(210,220,240),width=10)
    out=Path(output); out.parent.mkdir(parents=True,exist_ok=True)
    im.save(out,format="PNG")
    return str(out)
