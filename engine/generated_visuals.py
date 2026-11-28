"""Locally generated topic-specific visual cards; no stock-media API needed."""
from pathlib import Path
import subprocess, html, re

def _clean(s):
    return re.sub(r"\\s+", " ", str(s or "")).strip()

def generate_visual_clips(topic, script, outdir, duration, count=5):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    title=_clean(topic.get("title","AI PINTAR")); category=_clean(topic.get("category","AI"))
    sentences=[_clean(x) for x in re.split(r"(?<=[.!?])\\s+",script) if _clean(x)]
    scenes=[]
    for i in range(count):
        beat=sentences[min(i,len(sentences)-1)] if sentences else title
        label=html.escape(beat[:115]); cat=html.escape(category.upper()[:32]); title_text=html.escape(title[:90])
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#10182c"/><stop offset="1" stop-color="#182d55"/></linearGradient></defs>
<rect width="1080" height="1920" fill="url(#g)"/><circle cx="840" cy="280" r="520" fill="#3768c8" fill-opacity=".18"/><circle cx="150" cy="1640" r="480" fill="#3768c8" fill-opacity=".2"/>
<g stroke="#6b8bc4" stroke-opacity=".2" stroke-width="2"><path d="M80 0V1920M220 0V1920M360 0V1920M500 0V1920M640 0V1920M780 0V1920M920 0V1920"/><path d="M0 200H1080M0 340H1080M0 480H1080M0 620H1080M0 760H1080M0 900H1080M0 1040H1080M0 1180H1080M0 1320H1080M0 1460H1080M0 1600H1080M0 1740H1080"/></g>
<rect x="78" y="150" width="924" height="160" rx="36" fill="#ffffff" fill-opacity=".08" stroke="#8ab4ff" stroke-opacity=".35"/>
<text x="120" y="245" font-family="DejaVu Sans" font-size="38" font-weight="bold" fill="#b9d6ff">{cat}</text>
<rect x="78" y="430" width="924" height="980" rx="54" fill="#101c34" stroke="#6b9df0" stroke-opacity=".45" stroke-width="3"/>
<circle cx="540" cy="710" r="220" fill="#234b88" fill-opacity=".4" stroke="#6da9ff" stroke-width="5"/>
<g fill="none" stroke="#a9d0ff" stroke-width="12" stroke-linecap="round"><path d="M410 650h260M410 720h200M410 790h260"/><path d="M470 550l70-80 70 80"/></g>
<rect x="160" y="1020" width="760" height="230" rx="32" fill="#244875" fill-opacity=".55" stroke="#91baff" stroke-opacity=".5"/>
<text x="540" y="1100" text-anchor="middle" font-family="DejaVu Sans" font-size="36" fill="#b9d6ff">SCENE {i+1}</text>
<text x="540" y="1170" text-anchor="middle" font-family="DejaVu Sans" font-size="40" font-weight="bold" fill="#ffffff">{label}</text>
<rect x="78" y="1490" width="924" height="260" rx="38" fill="#ffffff" fill-opacity=".08"/>
<text x="120" y="1580" font-family="DejaVu Sans" font-size="40" fill="#ffffff" font-weight="bold">{title_text}</text>
<text x="120" y="1680" font-family="DejaVu Sans" font-size="30" fill="#c5d7f5">AI PINTAR • visual ilustratif</text></svg>'''
        svgpath=outdir/f"scene_{i+1:02d}.svg"; svgpath.write_text(svg,encoding="utf-8")
        clip=outdir/f"scene_{i+1:02d}.mp4"; seg=duration/count
        subprocess.run(["ffmpeg","-y","-loop","1","-i",str(svgpath),"-t",str(seg),"-vf","scale=1080:1920,fps=30","-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p",str(clip)],check=True,capture_output=True,timeout=90)
        scenes.append(str(clip))
    return scenes
