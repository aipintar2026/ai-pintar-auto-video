"""Invoke a public Hugging Face Gradio MuseTalk Space for a short test render.
This runner sends the image and audio to the selected third-party Space.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests


def _resolve_output(value, output: Path):
    if isinstance(value, (list, tuple)):
        if not value:
            raise RuntimeError("MuseTalk Space returned an empty output.")
        return _resolve_output(value[0], output)
    if isinstance(value, dict):
        for key in ("video", "path", "url", "file"):
            if value.get(key) is not None:
                return _resolve_output(value[key], output)
        raise RuntimeError("MuseTalk Space output has no file/path/url field.")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("MuseTalk Space did not return a video file.")
    candidate = Path(value)
    if candidate.is_file():
        output.parent.mkdir(parents=True, exist_ok=True)
        if candidate.resolve() != output.resolve():
            shutil.copy2(candidate, output)
        return str(output)
    if value.startswith("https://") or value.startswith("http://"):
        output.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(value, timeout=(20, 180))
        response.raise_for_status()
        output.write_bytes(response.content)
        return str(output)
    raise RuntimeError("MuseTalk Space output path was not available locally or as a URL.")


def run_musetalk_space(image, audio, output, space="henrybit/musetalk-1-5"):
    image, audio, output = Path(image), Path(audio), Path(output)
    if not image.is_file():
        raise FileNotFoundError(f"Master image missing: {image}")
    if not audio.is_file():
        raise FileNotFoundError(f"Driving audio missing: {audio}")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        from gradio_client import Client, handle_file
    except ImportError as exc:
        raise RuntimeError("Install the pinned optional dependency gradio_client to use this runner.") from exc

    client = Client(space, verbose=False)
    # The Space's generate button inputs are audio, image/video, bbox shift,
    # margin, parsing mode, and cheek widths.
    result = client.predict(
        handle_file(str(audio)),
        handle_file(str(image)),
        0,
        10,
        "jaw",
        90,
        90,
        api_name="/generate",
    )
    _resolve_output(result, output)
    if not output.is_file() or output.stat().st_size < 100_000:
        raise RuntimeError("MuseTalk Space output is missing or too small to be a video.")
    return str(output)


def main():
    parser = argparse.ArgumentParser(description="Run a MuseTalk Hugging Face Space.")
    parser.add_argument("--space", default="henrybit/musetalk-1-5")
    parser.add_argument("--image", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run_musetalk_space(args.image, args.audio, args.output, args.space)


if __name__ == "__main__":
    main()
