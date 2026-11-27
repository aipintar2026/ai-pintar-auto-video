"""Media quality checks for short-form video output."""
from pathlib import Path
import json, re, subprocess
from .cover import validate_cover


def probe_video(path: str):
    p = Path(path)
    if not p.exists() or p.stat().st_size < 100_000:
        raise RuntimeError("QC: file video hilang atau terlalu kecil.")
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height,codec_name,r_frame_rate", "-of", "json", str(p)
    ], capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    duration = float(data.get("format", {}).get("duration", 0))
    streams = data.get("streams", [])
    vids = [s for s in streams if s.get("codec_type") == "video"]
    auds = [s for s in streams if s.get("codec_type") == "audio"]
    if not vids or not auds:
        raise RuntimeError("QC: stream video/audio wajib tersedia.")
    if (int(vids[0].get("width", 0)), int(vids[0].get("height", 0))) != (1080, 1920):
        raise RuntimeError("QC: resolusi harus 1080x1920.")
    if not 30 <= duration <= 46:
        raise RuntimeError(f"QC: durasi di luar target 30-46 detik (terbaca {duration:.1f}).")
    return {"duration": duration, "resolution": "1080x1920", "audio": True, "bytes": p.stat().st_size, "video_codec": vids[0].get("codec_name"), "audio_codec": auds[0].get("codec_name")}


def _validate_srt(path: Path, video_duration=None):
    text = path.read_text(encoding="utf-8").strip()
    blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    if not blocks:
        raise RuntimeError("QC: subtitle SRT tidak memiliki cue.")
    timestamp = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})$")
    def seconds(value):
        hh, mm, tail = value.split(":")
        ss, ms = tail.split(",")
        return int(hh)*3600 + int(mm)*60 + int(ss) + int(ms)/1000
    previous_end = 0.0
    stats={"cue_count":0,"max_chars_per_line":0,"max_cps":0.0,"min_cue_duration":float("inf"),"max_cue_duration":0.0}
    for expected_number, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0].strip() != str(expected_number):
            raise RuntimeError("QC: nomor atau format blok SRT tidak valid.")
        match = timestamp.match(lines[1].strip())
        if not match:
            raise RuntimeError("QC: timestamp SRT tidak valid.")
        start, end = map(seconds, match.groups())
        if start < 0 or start < previous_end or end <= start:
            raise RuntimeError("QC: timestamp SRT tumpang tindih atau durasi cue tidak valid.")
        subtitle_lines = [line.strip() for line in lines[2:] if line.strip()]
        if not subtitle_lines:
            raise RuntimeError("QC: cue SRT tanpa teks.")
        if len(subtitle_lines) > 2 or any(len(line) > 34 for line in subtitle_lines):
            raise RuntimeError("QC: subtitle melebihi batas keterbacaan 2 baris/34 karakter.")
        duration=end-start
        chars=sum(len(line) for line in subtitle_lines)
        cps=chars/duration
        if duration < 0.45:
            raise RuntimeError("QC: cue subtitle terlalu singkat untuk dibaca (minimum 0.45 detik).")
        if cps > 24:
            raise RuntimeError(f"QC: subtitle terlalu cepat (>{24} karakter/detik).")
        if video_duration is not None and end > video_duration + 0.25:
            raise RuntimeError("QC: subtitle berakhir setelah durasi video.")
        stats["cue_count"]+=1
        stats["max_chars_per_line"]=max(stats["max_chars_per_line"],max(map(len,subtitle_lines)))
        stats["max_cps"]=max(stats["max_cps"],round(cps,2))
        stats["min_cue_duration"]=min(stats["min_cue_duration"],duration)
        stats["max_cue_duration"]=max(stats["max_cue_duration"],duration)
        previous_end = end
    stats["min_cue_duration"]=round(stats["min_cue_duration"],3)
    stats["max_cue_duration"]=round(stats["max_cue_duration"],3)
    return stats


def _validate_ass(path: Path, expected_cues):
    text=path.read_text(encoding="utf-8")
    if not text.strip() or "PlayResX: 1080" not in text or "PlayResY: 1920" not in text:
        raise RuntimeError("QC: ASS subtitle canvas harus 1080x1920.")
    dialogues=[line for line in text.splitlines() if line.startswith("Dialogue: ")]
    if len(dialogues)!=expected_cues:
        raise RuntimeError("QC: jumlah ASS dialogue tidak cocok dengan cue SRT.")
    style=next((line for line in text.splitlines() if line.startswith("Style: Default,")),None)
    if not style:
        raise RuntimeError("QC: style Default ASS hilang.")
    fields=style.split(",")
    try:
        fontsize=int(fields[2]); alignment=int(fields[18]); marginv=int(fields[21])
    except (IndexError,ValueError):
        raise RuntimeError("QC: parameter style ASS tidak terbaca.")
    if not 28<=fontsize<=48:
        raise RuntimeError("QC: font subtitle ASS di luar rentang 28-48.")
    if alignment!=2 or not 200<=marginv<=450:
        raise RuntimeError("QC: subtitle ASS harus lower-center dengan margin safe-zone 200-450.")
    return {"ass_dialogue_count":len(dialogues),"font_size":fontsize,"alignment":"lower-center","margin_vertical":marginv}


def prepublish_checks(video, caption, topic_id, subtitles, cover=None, cover_title=None):
    report = probe_video(video)
    caption_path = Path(caption)
    srt_path = Path(subtitles)
    for label, path in (("caption", caption_path), ("subtitle", srt_path)):
        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            raise RuntimeError(f"QC: {label} hilang atau kosong.")
    srt_stats=_validate_srt(srt_path, video_duration=report["duration"])
    ass_path = srt_path.with_suffix(".ass")
    if not ass_path.exists() or not ass_path.read_text(encoding="utf-8").strip():
        raise RuntimeError("QC: ASS subtitle file hilang atau kosong.")
    ass_stats=_validate_ass(ass_path,srt_stats["cue_count"])
    if not topic_id:
        raise RuntimeError("QC: topic_id tidak tercatat.")
    cover_stats=validate_cover(cover,cover_title or topic_id) if cover else {"cover_qc_status":"NOT_IMPLEMENTED"}
    report.update({"caption": True,"subtitle": True,"ass_subtitle": True,"topic_id": topic_id,
                   "subtitle_qc":srt_stats,"ass_qc":ass_stats,
                   "automated_qc_status":"PASS","visual_review_required":True,
                   "cover_qc":cover_stats,"cover_qc_status":cover_stats.get("cover_qc_status","NOT_IMPLEMENTED")})
    return report
