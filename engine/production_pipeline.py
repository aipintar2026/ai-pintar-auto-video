"""Staging pipeline: topic -> Pixabay -> TTS -> subtitles -> render -> QC -> optional cloud upload/queue."""
from __future__ import annotations
import json, hashlib, os, subprocess, re, textwrap
from pathlib import Path
from .topic_memory import TopicMemory
from .production import make_story
from .integrations import create_tts, cloudinary_upload, buffer_queue
from .generated_visuals import generate_visual_clips
from .qc import probe_video, prepublish_checks
from .publish_guard import check_publish_allowed
from .cover import create_cover_from_video

ROOT=Path(__file__).resolve().parent.parent


def _publish_content_key(topic_id, caption):
    """Stable per-topic/caption key so regenerated media cannot bypass reconciliation."""
    return hashlib.sha256((str(topic_id) + "|" + str(caption).strip()).encode("utf-8")).hexdigest()


def _duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], text=True).strip())


def _validate_footage(clips):
    """Reject unusably short/low-resolution source clips before assembly."""
    reports=[]
    for clip in clips:
        raw=subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-show_entries","format=duration","-of","json",str(clip)],text=True)
        data=json.loads(raw); streams=data.get("streams") or []
        if not streams: raise RuntimeError(f"Footage QC: video stream missing in {Path(clip).name}")
        w=int(streams[0].get("width") or 0); h=int(streams[0].get("height") or 0); d=float((data.get("format") or {}).get("duration") or 0)
        if min(w,h)<480 or d<3:
            raise RuntimeError(f"Footage QC: {Path(clip).name} unusable (resolution {w}x{h}, duration {d:.1f}s).")
        reports.append({"file":Path(clip).name,"resolution":f"{w}x{h}","duration":round(d,2)})
    return reports


def _escape_filter_path(path):
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def ffmpeg_render(clips, narration, subtitles, out, music=None, fps=30):
    if not clips:
        raise ValueError("Render membutuhkan minimal satu footage.")
    duration = _duration(narration)
    if not 30 <= duration <= 46:
        raise RuntimeError(f"TTS berdurasi {duration:.1f}s; target 30-46s. Perbaiki naskah sebelum render.")
    inputs=[]
    for clip in clips:
        inputs += ["-stream_loop", "-1", "-i", str(clip)]
    narration_index=len(clips)
    inputs += ["-i", str(narration)]
    music_index=None
    if music and Path(music).exists():
        music_index=narration_index+1
        inputs += ["-stream_loop", "-1", "-i", str(music)]
    segment=duration/len(clips)
    filters=[]
    for i, clip in enumerate(clips):
        # Keep the full source frame visible; use a softened, cropped backdrop
        # to fill portrait canvas instead of aggressively cropping the subject.
        filters.append(f"[{i}:v]split=2[bg{i}][fg{i}];[bg{i}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:12[blur{i}];[fg{i}]scale=1080:1920:force_original_aspect_ratio=decrease[fit{i}];[blur{i}][fit{i}]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={fps},trim=duration={segment:.6f},setpts=PTS-STARTPTS[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(len(clips)))+f"concat=n={len(clips)}:v=1:a=0[bg]")
    ass_path=Path(subtitles).with_suffix(".ass")
    render_subtitles=ass_path if ass_path.exists() else Path(subtitles)
    sub_path=_escape_filter_path(render_subtitles)
    filters.append(f"[bg]subtitles='{sub_path}'[sub]")
    video_label="sub"
    if music_index is not None:
        filters.append(f"[{narration_index}:a]aformat=sample_rates=48000:channel_layouts=stereo[voice]")
        filters.append(f"[{music_index}:a]volume=0.12,atrim=duration={duration:.6f},aformat=sample_rates=48000:channel_layouts=stereo[music]")
        filters.append("[voice][music]amix=inputs=2:duration=first:dropout_transition=0[aout]")
        audio_label="aout"
    else:
        audio_label=f"{narration_index}:a"
    audio_map=f"[{audio_label}]" if music_index is not None else f"{narration_index}:a"
    cmd=["ffmpeg","-y"]+inputs+["-filter_complex",";".join(filters),"-map",f"[{video_label}]","-map",audio_map,"-t",str(duration),"-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",str(out)]
    subprocess.run(cmd,check=True,timeout=300,capture_output=True)
    return out


def _subtitle_chunks(script, max_chars=34, max_lines=2, max_words=14):
    sentences=[s.strip() for s in re.split(r"(?<=[.!?])\s+", script.strip()) if s.strip()]
    if not sentences:
        sentences=[script.strip()]
    chunks=[]
    for sentence in sentences:
        current=[]
        for word in sentence.split():
            candidate=current+[word]
            lines=textwrap.wrap(" ".join(candidate),width=max_chars,break_long_words=False,break_on_hyphens=False)
            if current and (len(lines)>max_lines or len(candidate)>max_words):
                chunks.append(" ".join(current))
                current=[word]
            else:
                current=candidate
        if current:
            chunks.append(" ".join(current))
    return chunks


def caption_and_srt(topic, script, duration, output):
    caption=f"{topic['title']}\n\nBelajar AI secara praktis bersama AI PINTAR. #AI #BelajarAI #AIIndonesia"
    Path(output/'caption.txt').write_text(caption,encoding='utf-8')
    chunks=_subtitle_chunks(script)
    weights=[max(11,len(chunk)) for chunk in chunks]
    total=sum(weights)
    elapsed=0.0
    cues=[]
    ass_events=[]
    for index,(chunk,weight) in enumerate(zip(chunks,weights),1):
        start=elapsed
        elapsed=duration if index==len(chunks) else elapsed+(duration*weight/total)
        wrapped=textwrap.wrap(chunk,width=34,break_long_words=False,break_on_hyphens=False)
        srt_text="\n".join(wrapped)
        cues.append(f"{index}\n{_srt_timestamp(start)} --> {_srt_timestamp(elapsed)}\n{srt_text}")
        ass_text=r"\N".join(wrapped).replace("{",r"\{").replace("}",r"\}")
        ass_events.append(f"Dialogue: 0,{_ass_timestamp(start)},{_ass_timestamp(elapsed)},Default,,0,0,0,,{ass_text}")
    (Path(output)/'subtitles.srt').write_text("\n\n".join(cues)+"\n",encoding='utf-8')
    ass_header="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,DejaVu Sans,34,&H00FFFFFF,&H0000FFFF,&H00101010,&H90000000,1,0,0,0,100,100,0,0,1,4,2,2,90,90,340,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    (Path(output)/'subtitles.ass').write_text(ass_header+"\n".join(ass_events)+"\n",encoding='utf-8')
    return caption

def _srt_timestamp(seconds):
    total_ms=int(round(float(seconds)*1000))
    hours=total_ms//3_600_000
    minutes=(total_ms//60_000)%60
    secs=(total_ms//1000)%60
    millis=total_ms%1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _ass_timestamp(seconds):
    total_cs=max(0,int(round(float(seconds)*100)))
    hours=total_cs//360000
    minutes=(total_cs//6000)%60
    secs=(total_cs//100)%60
    centiseconds=total_cs%100
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def _load_media_ids(path):
    path=Path(path)
    if not path.exists(): return []
    data=json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data,list) else []


def _save_media_ids(path, ids):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    current=set(_load_media_ids(path)); current.update(str(x) for x in ids)
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps(sorted(current),indent=2),encoding="utf-8")
    tmp.replace(path)



def _scene_queries(topic, script, count=5):
    """Generate grounded, topic-specific searches rather than concatenated long Indonesian sentences."""
    category = str(topic.get("category") or "").lower()
    title = str(topic.get("title") or "").lower()
    angle = str(topic.get("angle") or "").lower()
    # Explicit visual vocabulary for common AI PINTAR topic categories.
    mappings = [
        (("prompt", "instruksi"), ["typing prompt laptop", "chatbot text prompt", "computer typing instructions", "AI chat interface", "person reviewing text on laptop"]),
        (("produkt", "dokumen", "email", "tugas"), ["document editing laptop", "organizing tasks computer", "person working laptop office", "digital notes screen", "reviewing document"]),
        (("konten", "video", "caption", "hook"), ["video editing timeline", "content creator laptop", "social media content planning", "writing caption laptop", "digital content workspace"]),
        (("umkm", "produk", "pelanggan", "promosi"), ["small business laptop workspace", "online shop product photography", "customer service chat screen", "product listing laptop", "small business packaging"]),
        (("keamanan", "fakta", "rahasia"), ["cybersecurity laptop", "checking information computer", "privacy lock computer", "research sources laptop", "secure digital data"]),
        (("bisnis digital", "ebook", "template"), ["digital product laptop", "ebook editing computer", "online business workspace", "digital templates screen", "planning digital product"]),
        (("belajar", "bahasa"), ["online learning laptop", "language learning computer", "student studying desk", "digital education screen", "practice writing computer"]),
        (("eksperimen", "rencana belajar"), ["testing software laptop", "planning notebook computer", "comparing results screen", "working laptop desk", "digital experiment"]),
        (("ai pintar", "otomatisasi", "membangun"), ["automation workflow computer", "video production workstation", "software workflow screen", "developer laptop workspace", "digital media production"]),
        (("chatgpt", "jawaban", "ai"), ["AI chatbot interface", "person using AI laptop", "chatbot response screen", "reviewing AI output", "computer artificial intelligence"]),
    ]
    selected=None
    for keywords, queries in mappings:
        if any(k in category or k in title or k in angle for k in keywords):
            selected=queries
            break
    if selected is None:
        selected=["AI chatbot interface", "person using computer", "digital workspace", "technology screen", "typing on laptop"]
    return selected[:count]

def run_pipeline(outdir='output_production', publish=False, channel_ids=None, upload_cloudinary=False, music=None):
    if publish and not check_publish_allowed():
        raise RuntimeError('Publish Guard: PUBLISH_ENABLED=true dan PUBLISH_DRY_RUN=false harus diset secara eksplisit.')
    if publish and not channel_ids:
        raise RuntimeError('Publish Guard: channel IDs wajib diisi sebelum publikasi.')
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True);work=out/'media';work.mkdir(exist_ok=True)
    key=os.environ.get('PIXABAY_API_KEY')
    if not key: raise RuntimeError('PIXABAY_API_KEY belum diset.')
    mem=TopicMemory(); selected=mem.choose()
    if selected.get('bank_exhausted'): return selected
    topic=selected['topic']; topic_id=topic['id']
    try:
        story=make_story(topic); script=story.narration()
        (out/'script.txt').write_text(script,encoding='utf-8')
        audio=out/'narration.mp3';create_tts(script,audio)
        dur=_duration(audio)
        # Generate designed, topic-labeled visual scenes locally. No stock-media
        # API or downloaded generic clips are used for this production path.
        clips=generate_visual_clips(topic,script,work,dur,count=5)
        footage_qc=_validate_footage(clips)
        caption=caption_and_srt(topic,script,dur,out)

        # Faceless format: footage, narration, dynamic subtitles and optional licensed music.
        vid=out/'final_video.mp4';ffmpeg_render(clips,audio,out/'subtitles.srt',vid,music=music)
        cover=out/'cover.jpg';cover_qc=create_cover_from_video(clips[0],cover,topic['title'])
        qc=prepublish_checks(vid,out/'caption.txt',topic_id,out/'subtitles.srt',cover=cover,cover_title=topic['title'],cover_layout=cover_qc)
        manifest={'topic':topic,'visual_source':'local_generated_visual_cards','footage_qc':footage_qc,'duration':qc['duration'],'resolution':qc['resolution'],
                  'video_format':'faceless','cover':cover_qc,
                  'music_overlay':bool(music and Path(music).exists()),'qc':qc,
                  'publish_requested':publish,'publish_result':'not attempted','cloudinary_result':'not attempted'}
        (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        _save_media_ids(media_ids_path,ids)
        if upload_cloudinary:
            cloud=cloudinary_upload(vid,public_id=f"staging_{topic_id}_{hashlib.sha256(vid.read_bytes()).hexdigest()[:8]}")
            manifest['cloudinary_result']=cloud
            (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        if publish:
            if not upload_cloudinary:
                cloud=cloudinary_upload(vid,public_id=f"staging_{topic_id}_{hashlib.sha256(vid.read_bytes()).hexdigest()[:8]}")
                manifest['cloudinary_result']=cloud
            manifest['publish_result']=buffer_queue(manifest['cloudinary_result']['secure_url'],caption,channel_ids or [],enabled=True,manifest_path=out/'publish_manifest.json',content_key=_publish_content_key(topic_id,caption))
            (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        return manifest
    except Exception as exc:
        mem.mark_failed(topic_id,reason=str(exc)[:300])
        raise
