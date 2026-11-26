"""Talking-avatar adapter: safe, opt-in orchestration for local/provider runners.

The adapter does not choose or call a paid API by default. A configured runner command
must accept source image, audio, and output path. This keeps provider credentials and
provider-specific licensing outside the core render pipeline.
"""
from __future__ import annotations
import os, shlex, subprocess
from pathlib import Path

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
    # Runner contract: command template must contain these placeholders.
    required = ("{image}", "{audio}", "{output}")
    if not all(token in runner for token in required):
        raise ValueError("TALKING_AVATAR_RUNNER must contain {image}, {audio}, and {output} placeholders.")
    command = shlex.split(runner.format(image=shlex.quote(str(image)), audio=shlex.quote(str(audio)), output=shlex.quote(str(output))))
    subprocess.run(command, check=True, timeout=timeout)
    if not output.is_file() or output.stat().st_size < 100_000:
        raise RuntimeError("Talking-avatar runner did not produce a valid video file.")
    return str(output)
