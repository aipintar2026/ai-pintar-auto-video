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
