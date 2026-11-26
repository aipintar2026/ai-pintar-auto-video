import json, tempfile
from pathlib import Path
from engine.script_engine import Story, validate_story
from engine.publish_guard import check_publish_allowed, PublishManifest
from engine.topic_memory import TopicMemory


def test_topic_memory_selects_without_repeat_and_exhaustion():
    with tempfile.TemporaryDirectory() as d:
        topics = Path(d)/"topics.json"
        state = Path(d)/"state.json"
        topics.write_text(json.dumps([{"id":"a","title":"A"},{"id":"b","title":"B"}]))
        memory = TopicMemory(topics, state)
        assert memory.choose(seed=1)["topic"]
        assert memory.choose(seed=1)["topic"]
        assert memory.choose(seed=1)["bank_exhausted"] is True


def test_story_validation():
    story = Story("Hook yang singkat", "Masalah yang umum", "Solusi praktis yang dapat diterapkan", "Tambahan insight dan cara memeriksa hasil", "Ikuti AI PINTAR")
    assert validate_story(story, min_chars=30, max_chars=400)


def test_publish_guard_defaults_disabled(monkeypatch):
    monkeypatch.delenv("PUBLISH_ENABLED", raising=False)
    monkeypatch.delenv("PUBLISH_DRY_RUN", raising=False)
    assert check_publish_allowed() is False


def test_manifest_channel_success():
    with tempfile.TemporaryDirectory() as d:
        m=PublishManifest(Path(d)/"manifest.json")
        m.record("k","fb","success","post id")
        assert m.has_success("k","fb")
        assert not m.has_success("k","tt")


def test_topic_bank_duplicate_ids_rejected():
    with tempfile.TemporaryDirectory() as d:
        topics=Path(d)/'topics.json';topics.write_text(json.dumps([{'id':'x','title':'X'},{'id':'x','title':'X2'}]))
        with __import__('pytest').raises(ValueError): TopicMemory(topics,Path(d)/'state.json')


def test_corrupt_state_not_silently_reset():
    with tempfile.TemporaryDirectory() as d:
        topics=Path(d)/'topics.json';topics.write_text(json.dumps([{'id':'x','title':'X'}]))
        state=Path(d)/'state.json';state.write_text('broken')
        with __import__('pytest').raises(RuntimeError): TopicMemory(topics,state)


def test_topic_memory_mark_failed_releases_topic_and_records_reason():
    with tempfile.TemporaryDirectory() as d:
        topics = Path(d)/"topics.json"
        state = Path(d)/"state.json"
        topics.write_text(json.dumps([{"id":"a","title":"A"},{"id":"b","title":"B"}]))
        memory = TopicMemory(topics, state)
        chosen = memory.choose(seed=0)["topic"]
        memory.mark_failed(chosen["id"], reason="render_failed")
        reopened = TopicMemory(topics, state)
        assert chosen["id"] not in reopened.state["used_ids"]
        assert reopened.remaining() == 2
        assert reopened.state["failures"][-1]["reason"] == "render_failed"
