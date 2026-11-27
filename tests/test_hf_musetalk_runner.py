from pathlib import Path
from types import ModuleType
import sys

from engine import hf_musetalk_runner


def test_runner_calls_space_with_expected_inputs_and_copies_video(tmp_path, monkeypatch):
    image = tmp_path / "master.png"
    audio = tmp_path / "audio.mp3"
    image.write_bytes(b"image")
    audio.write_bytes(b"audio")
    source = tmp_path / "space-output.mp4"
    source.write_bytes(b"x" * 120_000)
    target = tmp_path / "result.mp4"
    calls = {}

    class FakeClient:
        def __init__(self, space, verbose=False):
            calls["space"] = space

        def predict(self, *args, api_name=None):
            calls["args"] = args
            calls["api_name"] = api_name
            return (str(source), "parameters")

    fake = ModuleType("gradio_client")
    fake.Client = FakeClient
    fake.handle_file = lambda path: path
    monkeypatch.setitem(sys.modules, "gradio_client", fake)

    result = hf_musetalk_runner.run_musetalk_space(image, audio, target, "test/space")
    assert result == str(target)
    assert target.stat().st_size == 120_000
    assert calls["space"] == "test/space"
    assert calls["args"] == (str(audio), str(image), 0, 10, "jaw", 90, 90)
    assert calls["api_name"] == "/generate"


def test_runner_rejects_missing_input(tmp_path):
    target = tmp_path / "result.mp4"
    try:
        hf_musetalk_runner.run_musetalk_space(tmp_path / "missing.png", tmp_path / "audio.mp3", target)
    except FileNotFoundError as exc:
        assert "Master image" in str(exc)
    else:
        raise AssertionError("missing input must fail")
