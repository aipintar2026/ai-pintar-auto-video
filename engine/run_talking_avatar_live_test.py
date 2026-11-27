"""Generate a short synthetic-media test and render it through a real MuseTalk Space."""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import sys
from pathlib import Path

from engine.integrations import create_tts
from engine.presenter import generate_master_presenter
from engine.talking_avatar import generate_talking_avatar, _validate_lip_sync_output

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "talking_avatar_live"


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / "report.json"
    space = os.getenv("TALKING_AVATAR_SPACE", "henrybit/musetalk-1-5")
    report = {
        "engine": "MuseTalk 1.5 via public Hugging Face Space",
        "space": space,
        "media": "synthetic AI PINTAR master illustration and synthetic TTS test phrase",
        "publishing": False,
        "human_visual_review_required": True,
    }
    try:
        master = OUT / "presenter_master.png"
        audio = OUT / "test_narration.mp3"
        video = OUT / "talking_avatar.mp4"
        generate_master_presenter(master)
        create_tts("Halo, ini uji presenter AI PINTAR.", audio)
        script = ROOT / "engine" / "hf_musetalk_runner.py"
        command = (
            f"{shlex.quote(sys.executable)} {shlex.quote(str(script))} "
            f"--space {shlex.quote(space)} --image {{image}} --audio {{audio}} --output {{output}}"
        )
        os.environ["TALKING_AVATAR_RUNNER"] = command
        generate_talking_avatar(master, audio, video, timeout=900)
        parity = _validate_lip_sync_output(video, audio)
        report.update({
            "status": "PASS",
            "output": str(video.relative_to(ROOT)),
            "video_bytes": video.stat().st_size,
            "video_sha256": _sha256(video),
            "lip_sync_duration_parity": parity,
            "visual_review_required": True,
        })
    except Exception as exc:
        report.update({"status": "FAIL", "error": f"{type(exc).__name__}: {str(exc)[:500]}"})
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
