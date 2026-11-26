"""Media quality checks for short-form video output."""
from pathlib import Path
import json, re, subprocess


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


def _validate_srt(path: Path):
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
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit():
            raise RuntimeError("QC: format blok SRT tidak valid.")
        match = timestamp.match(lines[1].strip())
        if not match:
            raise RuntimeError("QC: timestamp SRT tidak valid.")
        start, end = map(seconds, match.groups())
        if start < previous_end or end <= start:
            raise RuntimeError("QC: timestamp SRT tumpang tindih atau durasi cue tidak valid.")
        if not any(line.strip() for line in lines[2:]):
            raise RuntimeError("QC: cue SRT tanpa teks.")
        previous_end = end
    return len(blocks)


def prepublish_checks(video, caption, topic_id, subtitles):
    report = probe_video(video)
    caption_path = Path(caption)
    srt_path = Path(subtitles)
    for label, path in (("caption", caption_path), ("subtitle", srt_path)):
        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            raise RuntimeError(f"QC: {label} hilang atau kosong.")
    cue_count = _validate_srt(srt_path)
    ass_path = srt_path.with_suffix(".ass")
    if not ass_path.exists() or not ass_path.read_text(encoding="utf-8").strip():
        raise RuntimeError("QC: ASS subtitle file hilang atau kosong.")
    ass_text = ass_path.read_text(encoding="utf-8")
    if "PlayResX: 1080" not in ass_text or "PlayResY: 1920" not in ass_text:
        raise RuntimeError("QC: ASS subtitle canvas harus 1080x1920.")
    if not any(line.startswith("Dialogue: ") for line in ass_text.splitlines()):
        raise RuntimeError("QC: ASS tidak memiliki subtitle dialogue.")
    if not topic_id:
        raise RuntimeError("QC: topic_id tidak tercatat.")
    report.update({"caption": True, "subtitle": True, "ass_subtitle": True, "subtitle_cues": cue_count, "topic_id": topic_id})
    return report
