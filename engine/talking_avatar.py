"""Talking-avatar adapter with output and audio/video duration-parity validation."""
from __future__ import annotations
import os, shlex, subprocess, json
from pathlib import Path


def _probe_media(path: Path):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height,duration",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    try:
        return json.loads(probe.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Talking-avatar media metadata could not be parsed by ffprobe.") from exc


def _validate_video(path: Path):
    """Require readable video and audio streams and a positive media duration."""
    metadata = _probe_media(Path(path))
    videos = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"]
    audios = [s for s in metadata.get("streams", []) if s.get("codec_type") == "audio"]
    if not videos:
        raise RuntimeError("Talking-avatar output contains no video stream.")
    if not audios:
        raise RuntimeError("Talking-avatar output contains no audio stream.")
    duration = float(metadata.get("format", {}).get("duration", 0) or 0)
    if duration <= 0:
        raise RuntimeError("Talking-avatar output has invalid duration.")
    return {"duration": duration, "width": int(videos[0].get("width", 0)),
            "height": int(videos[0].get("height", 0)), "audio": True}


def _validate_lip_sync_output(output_video, narration_audio, tolerance_seconds=1.25):
    """Verify output audio exists and duration is close to the driving narration.

    This is a duration-parity gate, not a perceptual lip-sync score. Human visual
    review of mouth movement and artifacts is still required.
    """
    output_video, narration_audio = Path(output_video), Path(narration_audio)
    video_metadata = _probe_media(output_video)
    videos = [s for s in video_metadata.get("streams", []) if s.get("codec_type") == "video"]
    output_audios = [s for s in video_metadata.get("streams", []) if s.get("codec_type") == "audio"]
    if not videos:
        raise RuntimeError("Talking-avatar output contains no video stream.")
    if not output_audios:
        raise RuntimeError("Talking-avatar output contains no audio stream.")
    video_duration = float(videos[0].get("duration") or video_metadata.get("format", {}).get("duration") or 0)
    output_audio_duration = float(output_audios[0].get("duration") or video_metadata.get("format", {}).get("duration") or 0)
    source_metadata = _probe_media(narration_audio)
    source_duration = float(source_metadata.get("format", {}).get("duration", 0) or 0)
    if min(video_duration, output_audio_duration, source_duration) <= 0:
        raise RuntimeError("Talking-avatar output or driving audio has invalid duration.")
    delta = abs(video_duration - source_duration)
    audio_delta = abs(output_audio_duration - source_duration)
    if delta > tolerance_seconds or audio_delta > tolerance_seconds:
        raise RuntimeError(
            f"Talking-avatar duration parity failed: video delta={delta:.3f}s, audio delta={audio_delta:.3f}s."
        )
    return {
        "video_duration_seconds": round(video_duration, 3),
        "output_audio_duration_seconds": round(output_audio_duration, 3),
        "source_audio_duration_seconds": round(source_duration, 3),
        "video_duration_delta_seconds": round(delta, 3),
        "output_audio_duration_delta_seconds": round(audio_delta, 3),
        "tolerance_seconds": tolerance_seconds,
        "lip_sync_duration_parity": "PASS",
        "perceptual_lip_sync_score": "NOT_MEASURED",
    }


def generate_talking_avatar(master_image, narration_audio, output_video, timeout=600):
    runner = os.getenv("TALKING_AVATAR_RUNNER", "").strip()
    if not runner:
        raise RuntimeError("Talking avatar disabled: set TALKING_AVATAR_RUNNER to an approved runner command.")
    image, audio, output = Path(master_image), Path(narration_audio), Path(output_video)
    if not image.is_file():
        raise FileNotFoundError(f"Master presenter image not found: {image}")
    if not audio.is_file():
        raise FileNotFoundError(f"Narration audio not found: {audio}")
    output.parent.mkdir(parents=True, exist_ok=True)
    required = ("{image}", "{audio}", "{output}")
    if not all(token in runner for token in required):
        raise ValueError("TALKING_AVATAR_RUNNER must contain {image}, {audio}, and {output} placeholders.")
    command = shlex.split(runner.format(image=shlex.quote(str(image)), audio=shlex.quote(str(audio)), output=shlex.quote(str(output))))
    subprocess.run(command, check=True, timeout=timeout)
    if not output.is_file() or output.stat().st_size < 100_000:
        raise RuntimeError("Talking-avatar runner did not produce a valid video file.")
    _validate_lip_sync_output(output, audio)
    return str(output)
