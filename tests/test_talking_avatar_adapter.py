import os
from pathlib import Path
from types import SimpleNamespace
import pytest
from engine import talking_avatar


def test_adapter_disabled_without_runner(monkeypatch, tmp_path):
    monkeypatch.delenv("TALKING_AVATAR_RUNNER", raising=False)
    with pytest.raises(RuntimeError, match="disabled"):
        talking_avatar.generate_talking_avatar(tmp_path/"image.png", tmp_path/"audio.mp3", tmp_path/"out.mp4")


def test_adapter_requires_template_placeholders(monkeypatch, tmp_path):
    monkeypatch.setenv("TALKING_AVATAR_RUNNER", "fake-runner --image {image}")
    image=tmp_path/"image.png"; image.write_bytes(b"image")
    audio=tmp_path/"audio.mp3"; audio.write_bytes(b"audio")
    with pytest.raises(ValueError, match="placeholders"):
        talking_avatar.generate_talking_avatar(image, audio, tmp_path/"out.mp4")


def test_adapter_checks_inputs(monkeypatch, tmp_path):
    monkeypatch.setenv("TALKING_AVATAR_RUNNER", "fake-runner --image {image} --audio {audio} --output {output}")
    with pytest.raises(FileNotFoundError, match="Master presenter"):
        talking_avatar.generate_talking_avatar(tmp_path/"missing.png", tmp_path/"audio.mp3", tmp_path/"out.mp4")
    image=tmp_path/"image.png"; image.write_bytes(b"image")
    with pytest.raises(FileNotFoundError, match="Narration audio"):
        talking_avatar.generate_talking_avatar(image, tmp_path/"missing.mp3", tmp_path/"out.mp4")


def test_adapter_runner_output_and_timeout(monkeypatch, tmp_path):
    monkeypatch.setenv("TALKING_AVATAR_RUNNER", "fake-runner --image {image} --audio {audio} --output {output}")
    image=tmp_path/"image.png"; image.write_bytes(b"image")
    audio=tmp_path/"audio.mp3"; audio.write_bytes(b"audio")
    output=tmp_path/"out.mp4"
    calls=[]
    def fake_run(command, check, timeout):
        calls.append((command,check,timeout))
        output.write_bytes(b"x"*100_000)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(talking_avatar.subprocess,"run",fake_run)
    result=talking_avatar.generate_talking_avatar(image,audio,output,timeout=42)
    assert result==str(output)
    assert calls[0][1] is True and calls[0][2]==42
    assert "--image" in calls[0][0] and "--audio" in calls[0][0] and "--output" in calls[0][0]


def test_adapter_rejects_small_runner_output(monkeypatch, tmp_path):
    monkeypatch.setenv("TALKING_AVATAR_RUNNER", "fake-runner --image {image} --audio {audio} --output {output}")
    image=tmp_path/"image.png"; image.write_bytes(b"image")
    audio=tmp_path/"audio.mp3"; audio.write_bytes(b"audio")
    output=tmp_path/"out.mp4"
    monkeypatch.setattr(talking_avatar.subprocess,"run",lambda *a,**k: output.write_bytes(b"x"*10))
    with pytest.raises(RuntimeError,match="valid video"):
        talking_avatar.generate_talking_avatar(image,audio,output)
