"""Run an offline, synthetic-media pipeline test. No API calls and no publishing."""
import json, subprocess
from pathlib import Path
from engine.production_pipeline import caption_and_srt, ffmpeg_render
from engine.production import make_story
from engine.qc import prepublish_checks
from engine.cover import create_cover_from_video
from engine.presenter import generate_master_presenter

BASE=Path(__file__).resolve().parent
OUT=Path("output_offline")
OUT.mkdir(parents=True,exist_ok=True)
MEDIA=OUT/"media"
MEDIA.mkdir(exist_ok=True)
TOPIC={"id":"OFFLINE-TEST","title":"AI PINTAR offline pipeline test","angle":"testing pipeline"}
STORY=make_story(TOPIC)
SCRIPT=STORY.narration()
(OUT/"script.txt").write_text(SCRIPT,encoding="utf-8")
DURATION=35
clips=[]
for i in range(5):
    clip=MEDIA/f"synthetic_{i}.mp4"
    cmd=["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x10182c:s=540x960:d={DURATION/5}:r=30","-f","lavfi","-i",f"sine=frequency={440+i*30}:duration={DURATION/5}","-shortest","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",str(clip)]
    subprocess.run(cmd,check=True,capture_output=True,timeout=120)
    clips.append(str(clip))
voice=OUT/"synthetic_voice.mp3"
subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"sine=frequency=600:duration={DURATION}","-c:a","libmp3lame","-q:a","5",str(voice)],check=True,capture_output=True,timeout=120)
caption=caption_and_srt(TOPIC,SCRIPT,DURATION,OUT)
avatar=generate_master_presenter(OUT/"presenter_master.png")
music=OUT/"synthetic_music.mp3"
subprocess.run(["ffmpeg","-y","-f","lavfi","-i",f"sine=frequency=120:duration={DURATION}","-c:a","libmp3lame","-q:a","5",str(music)],check=True,capture_output=True,timeout=60)
video=OUT/"final_video.mp4"
ffmpeg_render(clips,voice,OUT/"subtitles.srt",avatar,video,music=music,fps=10)
cover=OUT/"cover.jpg"
cover_qc=create_cover_from_video(clips[0],cover,TOPIC["title"])
qc=prepublish_checks(video,OUT/"caption.txt",TOPIC["id"],OUT/"subtitles.srt",cover=cover,cover_title=TOPIC["title"],cover_layout=cover_qc)
manifest={"mode":"offline_synthetic","topic":TOPIC,"qc":qc,"external_calls":False,"publish":False,"presenter_overlay":True,"presenter_master_generated":True,"cover_qc":cover_qc,"music_mix":True}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(manifest,indent=2,ensure_ascii=False))
