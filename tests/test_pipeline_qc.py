import json, subprocess
from pathlib import Path
import pytest
from engine.production_pipeline import caption_and_srt, _escape_filter_path
from engine.qc import prepublish_checks, probe_video, _validate_srt
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
    blocks=(tmp_path/'subtitles.srt').read_text(encoding="utf-8").strip().split("\n\n")
    assert len(blocks)>1
    for block in blocks:
        lines=block.splitlines()[2:]
        assert 1<=len(lines)<=2
        assert all(len(line)<=34 for line in lines)
        assert len(" ".join(lines).split())<=14

def test_ass_subtitles_have_portrait_canvas_and_style(tmp_path):
    caption_and_srt({"title":"Test"},"Two short subtitle phrases. Another phrase.",10.0,tmp_path)
    ass=(tmp_path/'subtitles.ass').read_text(encoding="utf-8")
    assert "PlayResX: 1080" in ass
    assert "PlayResY: 1920" in ass
    assert "Style: Default,DejaVu Sans,34" in ass
    assert "Dialogue: 0," in ass


def test_prepublish_qc_rejects_malformed_srt(tmp_path, monkeypatch):
    video=tmp_path/"fake.mp4"
    video.write_bytes(b"x"*100_000)
    caption=tmp_path/"caption.txt"
    caption.write_text("Caption",encoding="utf-8")
    srt=tmp_path/"subtitles.srt"
    srt.write_text("1\ninvalid timestamp\nText\n",encoding="utf-8")
    ass=tmp_path/"subtitles.ass"
    ass.write_text("[Script Info]\nPlayResX: 1080\nPlayResY: 1920\n[Events]\nDialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,Text\n",encoding="utf-8")
    monkeypatch.setattr("engine.qc.probe_video",lambda p:{"duration":35,"resolution":"1080x1920"})
    with pytest.raises(RuntimeError,match="timestamp SRT"):
        prepublish_checks(video,caption,"topic",srt)


def test_prepublish_qc_accepts_valid_srt_and_ass(tmp_path, monkeypatch):
    video=tmp_path/"fake.mp4"
    video.write_bytes(b"x"*100_000)
    caption=tmp_path/"caption.txt"
    caption.write_text("Caption",encoding="utf-8")
    caption_and_srt({"title":"Test"},"Short readable cue.",35.0,tmp_path)
    srt=tmp_path/"subtitles.srt"
    monkeypatch.setattr("engine.qc.probe_video",lambda p:{"duration":35,"resolution":"1080x1920"})
    report=prepublish_checks(video,caption,"topic",srt)
    assert report["subtitle_qc"]["cue_count"]>=1

@pytest.mark.parametrize("srt,reason", [
    ("2\n00:00:00,000 --> 00:00:01,000\nText\n", "nomor"),
    ("1\n00:00:00,000 --> 00:00:40,000\nText\n", "setelah durasi"),
    ("1\n00:00:00,000 --> 00:00:01,000\n" + "x"*35 + "\n", "keterbacaan"),
    ("1\n00:00:00,000 --> 00:00:01,000\nA\nB\nC\n", "keterbacaan"),
])
def test_srt_qc_rejects_sequence_duration_and_readability(tmp_path, srt, reason):
    path=tmp_path/"bad.srt"
    path.write_text(srt,encoding="utf-8")
    with pytest.raises(RuntimeError,match=reason):
        _validate_srt(path,video_duration=35)

def test_srt_qc_reports_readability_metrics(tmp_path):
    path=tmp_path/"metrics.srt"
    path.write_text("1\n00:00:00,000 --> 00:00:02,000\nReadable phrase\n",encoding="utf-8")
    from engine.qc import _validate_srt
    stats=_validate_srt(path,video_duration=3)
    assert stats["cue_count"]==1
    assert stats["max_cps"]<=24
    assert stats["min_cue_duration"]==2.0


@pytest.mark.parametrize("srt,reason", [
    ("1\n00:00:00,000 --> 00:00:00,300\nToo short\n", "terlalu singkat"),
    ("1\n00:00:00,000 --> 00:00:01,000\n" + "x"*25 + "\n", "terlalu cepat"),
])
def test_srt_qc_rejects_unreadable_speed(tmp_path,srt,reason):
    path=tmp_path/"speed.srt"
    path.write_text(srt,encoding="utf-8")
    from engine.qc import _validate_srt
    with pytest.raises(RuntimeError,match=reason):
        _validate_srt(path,video_duration=35)


def test_ass_qc_rejects_dialogue_count_mismatch(tmp_path):
    from engine.qc import _validate_ass
    path=tmp_path/"subtitles.ass"
    path.write_text("[Script Info]\nPlayResX: 1080\nPlayResY: 1920\n[Events]\nDialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,Text\n",encoding="utf-8")
    with pytest.raises(RuntimeError,match="jumlah ASS dialogue"):
        _validate_ass(path,2)


def test_ass_qc_accepts_safe_zone_style(tmp_path):
    from engine.qc import _validate_ass
    from engine.production_pipeline import caption_and_srt
    caption_and_srt({"title":"Test"},"A short readable sentence.",3.0,tmp_path)
    stats=_validate_ass(tmp_path/"subtitles.ass",1)
    assert stats["alignment"]=="lower-center"
    assert 200<=stats["margin_vertical"]<=450


def test_cover_generation_and_structural_qc(tmp_path):
    from PIL import Image
    from engine.cover import generate_cover_from_frame
    frame=tmp_path/"frame.jpg"
    Image.new("RGB",(1080,1920),(35,65,100)).save(frame,"JPEG")
    cover=tmp_path/"cover.jpg"
    report=generate_cover_from_frame(frame,cover,"BELAJAR AI DARI DASAR")
    assert report["cover_qc_status"]=="PASS"
    assert report["resolution"]=="1080x1920"
    assert report["safe_zone"]=="PASS"
    assert cover.exists() and cover.stat().st_size>10_000


def test_cover_qc_rejects_wrong_resolution(tmp_path):
    from PIL import Image
    from engine.cover import validate_cover
    path=tmp_path/"cover.jpg"
    Image.new("RGB",(640,480),(30,60,90)).save(path,"JPEG",quality=90)
    with pytest.raises(RuntimeError,match="1080x1920"):
        validate_cover(path,"title")


def test_generated_subtitles_pass_minimum_dwell_time_for_35s_story(tmp_path):
    topic={"id":"test","title":"AI PINTAR offline pipeline test","angle":"testing pipeline"}
    script=make_story(topic).narration()
    caption_and_srt(topic,script,35.0,tmp_path)
    stats=_validate_srt(tmp_path/"subtitles.srt",video_duration=35.0)
    assert stats["min_cue_duration"]>=0.45
    assert stats["max_cps"]<=24
