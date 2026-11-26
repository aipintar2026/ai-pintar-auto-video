"""Persistent topic tracker with atomic state writes."""
import json, random
from pathlib import Path
from datetime import datetime, timezone

class TopicMemory:
    def __init__(self, topics_path=None, state_path=None):
        base = Path(__file__).resolve().parent.parent
        self.topics_path = Path(topics_path or base / "topics.json")
        self.state_path = Path(state_path or base / "state" / "topic_state.json")
        self.topics = json.loads(self.topics_path.read_text(encoding="utf-8"))
        if not isinstance(self.topics, list) or not self.topics:
            raise ValueError("Topic bank kosong atau format tidak valid.")
        ids = [t.get("id") for t in self.topics]
        if any(not x for x in ids) or len(ids) != len(set(ids)):
            raise ValueError("Topic bank harus memiliki ID unik dan non-kosong.")
        self.state = self._load_state()

    def _load_state(self):
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                if not isinstance(data, dict) or not isinstance(data.get("used_ids", []), list):
                    raise ValueError("State topic tidak valid.")
                data.setdefault("history", [])
                data.setdefault("bank_version", 1)
                return data
            except (json.JSONDecodeError, OSError, ValueError):
                # Corrupt state is not silently overwritten; preserve it for recovery.
                raise RuntimeError("State topic rusak; periksa file state/topic_state.json sebelum lanjut.")
        return {"used_ids": [], "history": [], "bank_version": 1}

    def _save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.state_path)

    def choose(self, seed=None):
        used = set(self.state.get("used_ids", []))
        available = [t for t in self.topics if t["id"] not in used]
        if not available:
            return {"bank_exhausted": True, "message": "Bank topik habis; tambahkan topik baru sebelum melanjutkan.", "topic": None}
        rng = random.Random(seed)
        topic = rng.choice(available)
        self.state.setdefault("used_ids", []).append(topic["id"])
        self.state.setdefault("history", []).append({"id": topic["id"], "title": topic["title"], "used_at": datetime.now(timezone.utc).isoformat()})
        self._save()
        return {"bank_exhausted": False, "topic": topic}

    def mark_failed(self, topic_id, reason="production_failed"):
        self.state["used_ids"] = [x for x in self.state.get("used_ids", []) if x != topic_id]
        self.state.setdefault("failures", []).append({"id": topic_id, "reason": reason, "at": datetime.now(timezone.utc).isoformat()})
        self._save()

    def remaining(self):
        return len([t for t in self.topics if t["id"] not in set(self.state.get("used_ids", []))])

    def reset_bank(self):
        self.state["used_ids"] = []
        self.state["bank_version"] = self.state.get("bank_version", 1) + 1
        self._save()
