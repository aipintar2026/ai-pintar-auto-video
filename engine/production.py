"""Staging video renderer. Demo mode is local/offline; production media providers are not connected."""
import json, subprocess, textwrap
from pathlib import Path
from .topic_memory import TopicMemory
from .script_engine import Story

BASE=Path(__file__).resolve().parent.parent

def make_story(topic):
    title=topic['title']; angle=topic.get('angle','')
    # Compact narration template designed to fit the real-production 30-46s window.
    return Story(
      hook=f"Pernah bingung menggunakan AI untuk {title.lower()}?",
      problem="Instruksi terlalu umum sering membuat jawaban AI meleset. Karena itu, jangan langsung memakai hasil pertama.",
      solution=f"Tulis tujuan, konteks, dan format jawaban dengan jelas. Fokus pada {angle.lower()}. Tambahkan satu contoh dan batasan agar AI memahami kebutuhan, lalu minta langkah yang praktis.",
      extra="Periksa fakta, hindari data pribadi, dan sesuaikan hasil AI dengan kebutuhanmu. Uji hasilnya, revisi instruksi bila belum sesuai, serta bandingkan beberapa jawaban sebelum memilih. AI hanya membantu; keputusan akhir tetap milikmu.",
      cta="Simpan tips ini dan ikuti AI PINTAR."
    )

def render_demo(topic, story, out):
    # Offline demo rendering, not a publishable content sample: synthetic background/audio.
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    text=topic['title'].replace("'","\\'")
    draw=f"drawtext=text='{text}':fontcolor=white:fontsize=58:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.65:boxborderw=30"
    cmd=['ffmpeg','-y','-f','lavfi','-i','color=c=0x10182c:s=1080x1920:d=35:r=30','-f','lavfi','-i','sine=frequency=440:duration=35','-vf',draw,'-shortest','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k',str(out)]
    subprocess.run(cmd,check=True,capture_output=True)
    return out

def run(outdir=BASE/'output', demo=False, seed=None):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    memory=TopicMemory(); chosen=memory.choose(seed=seed)
    if chosen['bank_exhausted']: return chosen
    topic=chosen['topic']; story=make_story(topic)
    script=story.narration()
    # structured draft and caption/subtitle assets
    (outdir/'script.txt').write_text(script,encoding='utf-8')
    caption=f"{topic['title']}\n\nBelajar AI secara praktis bersama AI PINTAR. #AI #BelajarAI #AIIndonesia"
    (outdir/'caption.txt').write_text(caption,encoding='utf-8')
    srt='1\n00:00:00,000 --> 00:00:35,000\n'+script+'\n'
    (outdir/'subtitles.srt').write_text(srt,encoding='utf-8')
    manifest={'topic':topic,'script':script,'demo_mode':demo,'media_status':'synthetic demo' if demo else 'script-only; real media provider not configured'}
    (outdir/'production.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    if demo: render_demo(topic,story,outdir/'demo.mp4')
    return manifest
