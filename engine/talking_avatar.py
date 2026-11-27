"""Talking-avatar adapter with opt-in runner and basic output validation.

No provider is selected by default. The configured runner must accept image, audio,
and output path placeholders. A runner/model license and provider terms require review.
"""
from __future__ import annotations
import os, shlex, subprocess, json
from pathlib import Path


def _validate_video(path: Path):
    """Require a readable video stream and positive duration using ffprobe."""
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,width,height",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True, timeout=30,
    )
    try:
        metadata = json.loads(probe.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Talking-avatar output could not be parsed by ffprobe.") from exc
    videos = [s for s in metadata.get("streams", []) if s.get("codec_type") == "video"]
    if not videos:
        raise RuntimeError("Talking-avatar output contains no video stream.")
    duration = float(metadata.get("format", {}).get("duration", 0) or 0)
    if duration <= 0:
        raise RuntimeError("Talking-avatar output has invalid duration.")
    return {"duration": duration, "width": int(videos[0].get("width", 0)),
            "height": int(videos[0].get("height", 0))}


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
    _validate_video(output)
    return str(output)
