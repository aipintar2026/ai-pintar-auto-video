import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from engine import production_pipeline as pipeline
from engine.topic_memory import TopicMemory


def _memory(tmp_path):
    topics=tmp_path/"topics.json"
    topics.write_text(json.dumps([{"id":"topic-a","title":"Topik uji","angle":"uji pipeline"}]),encoding="utf-8")
    state=tmp_path/"topic-state.json"
    return TopicMemory(topics,state),state


def _patch_story(monkeypatch):
    monkeypatch.setattr(pipeline,"make_story",lambda topic:SimpleNamespace(narration=lambda:"Naskah uji pipeline untuk pengujian terisolasi."))


def test_pipeline_mocked_end_to_end_offline(tmp_path,monkeypatch):
    memory,state_path=_memory(tmp_path)
    monkeypatch.setattr(pipeline,"TopicMemory",lambda:memory)
    monkeypatch.setattr(pipeline,"ROOT",tmp_path)
    monkeypatch.setenv("PIXABAY_API_KEY","test-key")
    _patch_story(monkeypatch)

    def fake_download(query,key,outdir,used_ids,count=5,cache_path=None):
        clips=[]
        for i in range(count):
            clip=Path(outdir)/f"clip-{i}.mp4"
            clip.write_bytes(b"x"*100_000)
            clips.append(str(clip))
        return clips,[str(i) for i in range(count)]
    monkeypatch.setattr(pipeline,"pixabay_download",fake_download)
    monkeypatch.setattr(pipeline,"create_tts",lambda script,path:(Path(path).write_bytes(b"x"*20_000) or str(path)))
    monkeypatch.setattr(pipeline,"_duration",lambda path:35.0)
    def fake_render(clips,narration,subtitles,avatar,out,music=None):
        Path(out).write_bytes(b"x"*200_000)
        return out
    monkeypatch.setattr(pipeline,"ffmpeg_render",fake_render)
    monkeypatch.setattr(pipeline,"prepublish_checks",lambda *a,**k:{"duration":35.0,"resolution":"1080x1920","audio":True})
    def fake_cover(video,cover,title):
        Path(cover).write_bytes(b"x"*12_000)
        return {"cover_qc_status":"PASS","resolution":"1080x1920"}
    monkeypatch.setattr(pipeline,"create_cover_from_video",fake_cover)

    out=tmp_path/"output"
    result=pipeline.run_pipeline(outdir=out,publish=False)
    manifest=json.loads((out/"manifest.json").read_text(encoding="utf-8"))
    assert result["publish_result"]=="not attempted"
    assert manifest["publish_result"]=="not attempted"
    assert manifest["qc"]["resolution"]=="1080x1920"
    assert manifest["avatar_mode"]=="static_overlay"
    assert Path(manifest["avatar_source"]).exists()
    assert manifest["cover"]["cover_qc_status"]=="PASS"
    assert (out/"final_video.mp4").stat().st_size>=100_000
    assert memory.state["used_ids"]==["topic-a"]


def test_pipeline_failure_releases_topic_for_recovery(tmp_path,monkeypatch):
    memory,state_path=_memory(tmp_path)
    monkeypatch.setattr(pipeline,"TopicMemory",lambda:memory)
    monkeypatch.setattr(pipeline,"ROOT",tmp_path)
    monkeypatch.setenv("PIXABAY_API_KEY","test-key")
    _patch_story(monkeypatch)
    monkeypatch.setattr(pipeline,"pixabay_download",lambda *a,**k: (_ for _ in ()).throw(RuntimeError("simulated download failure")))
    with pytest.raises(RuntimeError,match="simulated download failure"):
        pipeline.run_pipeline(outdir=tmp_path/"failed-output",publish=False)
    reopened=TopicMemory(tmp_path/"topics.json",state_path)
    assert "topic-a" not in reopened.state["used_ids"]
    assert reopened.state["failures"][-1]["reason"]=="simulated download failure"
    assert reopened.remaining()==1

def test_pipeline_story_failure_releases_topic(tmp_path,monkeypatch):
    memory,state_path=_memory(tmp_path)
    monkeypatch.setattr(pipeline,"TopicMemory",lambda:memory)
    monkeypatch.setattr(pipeline,"ROOT",tmp_path)
    monkeypatch.setenv("PIXABAY_API_KEY","test-key")
    monkeypatch.setattr(pipeline,"make_story",lambda topic:(_ for _ in ()).throw(RuntimeError("simulated script failure")))
    with pytest.raises(RuntimeError,match="simulated script failure"):
        pipeline.run_pipeline(outdir=tmp_path/"story-failed",publish=False)
    reopened=TopicMemory(tmp_path/"topics.json",state_path)
    assert "topic-a" not in reopened.state["used_ids"]
    assert reopened.state["failures"][-1]["reason"]=="simulated script failure"


def test_publish_reconciliation_key_stable_across_media_retries():
    from engine.production_pipeline import _publish_content_key
    key1 = _publish_content_key("topic-a", "caption")
    key2 = _publish_content_key("topic-a", "  caption  ")
    assert key1 == key2
    assert key1 != _publish_content_key("topic-b", "caption")


def test_pipeline_wires_talking_avatar_runner(tmp_path,monkeypatch):
    memory,state_path=_memory(tmp_path)
    monkeypatch.setattr(pipeline,"TopicMemory",lambda:memory)
    monkeypatch.setattr(pipeline,"ROOT",tmp_path)
    monkeypatch.setenv("PIXABAY_API_KEY","test-key")
    monkeypatch.setenv("TALKING_AVATAR_RUNNER","test-runner")
    _patch_story(monkeypatch)
    master=tmp_path/"master.png";master.write_bytes(b"image")
    monkeypatch.setattr(pipeline,"generate_master_presenter",lambda path:str(master))
    def fake_download(query,key,outdir,used_ids,count=5,cache_path=None):
        clips=[]
        for i in range(count):
            clip=Path(outdir)/f"clip-{i}.mp4";clip.write_bytes(b"x"*100_000);clips.append(str(clip))
        return clips,[str(i) for i in range(count)]
    monkeypatch.setattr(pipeline,"pixabay_download",fake_download)
    monkeypatch.setattr(pipeline,"create_tts",lambda script,path:(Path(path).write_bytes(b"x"*20_000) or str(path)))
    monkeypatch.setattr(pipeline,"_duration",lambda path:35.0)
    talking=tmp_path/"output"/"presenter_talking.mp4"
    def fake_talking(image,audio,out):
        Path(out).write_bytes(b"x"*100_000);return str(out)
    monkeypatch.setattr(pipeline,"generate_talking_avatar",fake_talking)
    captured={}
    def fake_render(clips,narration,subtitles,avatar,out,music=None):
        captured["avatar"]=avatar;Path(out).write_bytes(b"x"*200_000);return out
    monkeypatch.setattr(pipeline,"ffmpeg_render",fake_render)
    monkeypatch.setattr(pipeline,"prepublish_checks",lambda *a,**k:{"duration":35.0,"resolution":"1080x1920","audio":True})
    monkeypatch.setattr(pipeline,"create_cover_from_video",lambda video,cover,title:(Path(cover).write_bytes(b"x"*12_000) or {"cover_qc_status":"PASS"}))
    result=pipeline.run_pipeline(outdir=tmp_path/"output",publish=False,avatar=master)
    assert result["avatar_mode"]=="talking_avatar"
    assert captured["avatar"]==str(talking)
