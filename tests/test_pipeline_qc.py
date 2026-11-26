import json, subprocess
from pathlib import Path
import pytest
from engine.production_pipeline import caption_and_srt, _escape_filter_path
from engine.qc import prepublish_checks, probe_video
from engine.production import make_story


def test_caption_srt_valid_timestamp(tmp_path):
    topic={'title':'Test'}
    script='Hello world. Second sentence. Third sentence.'
    caption_and_srt(topic,script,35.5,tmp_path)
    srt=(tmp_path/'subtitles.srt').read_text()
    assert '00:00:35,500' in srt
    assert srt.count('-->') >= 2
    assert (tmp_path/'caption.txt').exists()


def test_filter_path_escape():
    assert '\\:' in _escape_filter_path('a:b')


def test_qc_rejects_missing(tmp_path):
    with pytest.raises(RuntimeError): probe_video(tmp_path/'missing.mp4')


def test_story_length_for_all_topics():
    topics=json.loads(Path('topics.json').read_text())
    for topic in topics:
        script=make_story(topic).narration()
        assert 650 <= len(script) <= 800
        assert 95 <= len(script.split()) <= 110

def test_subtitles_are_limited_to_two_readable_lines(tmp_path):
    script=("AI membantu pekerjaan dengan cara yang praktis dan mudah dipahami. " * 12).strip()
    caption_and_srt({"title":"Test"},script,36.0,tmp_path)
    blocks=(tmp_path/"subtitles.srt").read_text(encoding="utf-8").strip().split("\n\n")
    assert len(blocks)>1
    for block in blocks:
        lines=block.splitlines()[2:]
        assert 1<=len(lines)<=2
        assert all(len(line)<=34 for line in lines)
        assert len(" ".join(lines).split())<=14
