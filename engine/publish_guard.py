"""Safe publishing controls; default is dry-run and publishing is disabled."""
import json, os, hashlib
from pathlib import Path


def content_key(topic_id: str, video_path: str, caption: str):
    video_hash = hashlib.sha256(Path(video_path).read_bytes()).hexdigest()
    payload = f"{topic_id}|{video_hash}|{caption.strip()}"
    return hashlib.sha256(payload.encode()).hexdigest()


def check_publish_allowed():
    enabled = os.getenv("PUBLISH_ENABLED", "false").strip().lower() == "true"
    dry_run = os.getenv("PUBLISH_DRY_RUN", "true").strip().lower() == "true"
    return enabled and not dry_run


class PublishManifest:
    """Manifest records attempted/succeeded channel posts; keep durable outside runner."""
    def __init__(self, path="publish_manifest.json"):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def has_success(self, key, channel):
        return self.data.get(key, {}).get(channel, {}).get("status") == "success"

    def record(self, key, channel, status, detail=""):
        self.data.setdefault(key, {})[channel] = {"status": status, "detail": detail}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
