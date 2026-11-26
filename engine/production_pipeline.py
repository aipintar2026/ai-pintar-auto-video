"""Staging pipeline: topic -> Pixabay -> TTS -> subtitles -> render -> QC -> optional cloud upload/queue."""
from __future__ import annotations
import json, hashlib, os, subprocess, re, textwrap
from pathlib import Path
from .topic_memory import TopicMemory
from .production import make_story
from .integrations import pixabay_download, create_tts, cloudinary_upload, buffer_queue
from .qc import probe_video, prepublish_checks
from .publish_guard import check_publish_allowed

ROOT=Path(__file__).resolve().parent.parent


def _duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], text=True).strip())


def _escape_filter_path(path):
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def ffmpeg_render(clips, narration, subtitles, avatar, out, music=None, fps=30):
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
    avatar_index=None
    avatar_kind=None
    if avatar and Path(avatar).exists():
        avatar_path=Path(avatar)
        avatar_kind="video" if avatar_path.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"} else "image"
        if avatar_kind == "image":
            inputs += ["-loop", "1", "-i", str(avatar_path)]
        else:
            inputs += ["-stream_loop", "-1", "-i", str(avatar_path)]
        avatar_index=narration_index+1
    music_index=None
    if music and Path(music).exists():
        music_index=len(clips)+(2 if avatar_index is not None else 1)
        inputs += ["-stream_loop", "-1", "-i", str(music)]
    segment=duration/len(clips)
    filters=[]
    for i, clip in enumerate(clips):
        filters.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps={fps},trim=duration={segment:.6f},setpts=PTS-STARTPTS[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(len(clips)))+f"concat=n={len(clips)}:v=1:a=0[bg]")
    sub_path=_escape_filter_path(subtitles)
    filters.append(f"[bg]subtitles='{sub_path}':force_style='FontSize=34,Outline=2,Shadow=1,MarginV=300,Alignment=6'[sub]")
    if avatar_index is not None:
        if avatar_kind == "video":
            filters.append(f"[{avatar_index}:v]scale=280:-2,fps={fps},trim=duration={duration:.6f},setpts=PTS-STARTPTS[avatar]")
        else:
            filters.append(f"[{avatar_index}:v]scale=280:-2,trim=duration={duration:.6f}[avatar]")
        filters.append("[sub][avatar]overlay=W-w-56:120:eof_action=repeat[vout]")
        video_label="vout"
    else:
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
    weights=[max(1,len(chunk.split())) for chunk in chunks]
    total=sum(weights)
    elapsed=0.0
    cues=[]
    for index,(chunk,weight) in enumerate(zip(chunks,weights),1):
        start=elapsed
        elapsed=duration if index==len(chunks) else elapsed+(duration*weight/total)
        wrapped="\n".join(textwrap.wrap(chunk,width=34,break_long_words=False,break_on_hyphens=False))
        cues.append(f"{index}\n{_srt_timestamp(start)} --> {_srt_timestamp(elapsed)}\n{wrapped}")
    (Path(output)/'subtitles.srt').write_text("\n\n".join(cues)+"\n",encoding='utf-8')
    return caption

def _srt_timestamp(seconds):
    total_ms=int(round(float(seconds)*1000))
    hours=total_ms//3_600_000
    minutes=(total_ms//60_000)%60
    secs=(total_ms//1000)%60
    millis=total_ms%1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


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


def run_pipeline(outdir='output_production', publish=False, avatar=None, channel_ids=None, upload_cloudinary=False, music=None):
    if publish and not check_publish_allowed():
        raise RuntimeError('Publish Guard: PUBLISH_ENABLED=true dan PUBLISH_DRY_RUN=false harus diset secara eksplisit.')
    if publish and not channel_ids:
        raise RuntimeError('Publish Guard: channel IDs wajib diisi sebelum publikasi.')
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True);work=out/'media';work.mkdir(exist_ok=True)
    key=os.environ.get('PIXABAY_API_KEY')
    if not key: raise RuntimeError('PIXABAY_API_KEY belum diset.')
    mem=TopicMemory(); selected=mem.choose()
    if selected.get('bank_exhausted'): return selected
    topic=selected['topic']; topic_id=topic['id']; story=make_story(topic); script=story.narration()
    (out/'script.txt').write_text(script,encoding='utf-8')
    media_ids_path=ROOT/'state'/'pixabay_used_ids.json'
    used_ids=_load_media_ids(media_ids_path)
    try:
        clips,ids=pixabay_download(topic.get('angle') or topic['title'],key,work,used_ids=used_ids,count=5)
        if len(clips) < 5:
            raise RuntimeError(f'QC: dibutuhkan 5 footage berbeda, hanya {len(clips)} tersedia.')
        (out/'pixabay_ids.json').write_text(json.dumps(ids,indent=2),encoding='utf-8')
        audio=out/'narration.mp3';create_tts(script,audio)
        dur=_duration(audio)
        caption=caption_and_srt(topic,script,dur,out)
        vid=out/'final_video.mp4';ffmpeg_render(clips,audio,out/'subtitles.srt',avatar,vid,music=music)
        qc=prepublish_checks(vid,out/'caption.txt',topic_id,out/'subtitles.srt')
        manifest={'topic':topic,'pixabay_ids':ids,'duration':qc['duration'],'resolution':qc['resolution'],'avatar_overlay':bool(avatar and Path(avatar).exists()),'music_overlay':bool(music and Path(music).exists()),'qc':qc,'publish_requested':publish,'publish_result':'not attempted','cloudinary_result':'not attempted'}
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
            manifest['publish_result']=buffer_queue(manifest['cloudinary_result']['secure_url'],caption,channel_ids or [],enabled=True,manifest_path=out/'publish_manifest.json',content_key=hashlib.sha256((topic_id+'|'+hashlib.sha256(vid.read_bytes()).hexdigest()+'|'+caption.strip()).encode()).hexdigest())
            (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        return manifest
    except Exception as exc:
        mem.mark_failed(topic_id,reason=str(exc)[:300])
        raise
