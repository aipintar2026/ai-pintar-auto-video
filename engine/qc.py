"""Media quality checks for short-form video output."""
from pathlib import Path
import json, subprocess


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


def prepublish_checks(video, caption, topic_id, subtitles):
    report = probe_video(video)
    for label, path in (("caption", caption), ("subtitle", subtitles)):
        p = Path(path)
        if not p.exists() or not p.read_text(encoding="utf-8").strip():
            raise RuntimeError(f"QC: {label} hilang atau kosong.")
    ass_path=Path(subtitles).with_suffix(".ass")
    if not ass_path.exists() or not ass_path.read_text(encoding="utf-8").strip():
        raise RuntimeError("QC: ASS subtitle file hilang atau kosong.")
    ass_text=ass_path.read_text(encoding="utf-8")
    if "PlayResX: 1080" not in ass_text or "PlayResY: 1920" not in ass_text:
        raise RuntimeError("QC: ASS subtitle canvas harus 1080x1920.")
    if not topic_id:
        raise RuntimeError("QC: topic_id tidak tercatat.")
    report.update({"caption": True, "subtitle": True, "ass_subtitle": True, "topic_id": topic_id})
    return report
