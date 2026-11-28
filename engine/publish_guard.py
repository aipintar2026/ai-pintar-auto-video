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
    """Manifest records attempted/succeeded channel posts.

    Writes are atomic to reduce corruption when a runner exits during a write.
    A malformed existing manifest fails closed; it is never silently reset.
    """
    def __init__(self, path="publish_manifest.json"):
        self.path = Path(path)
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                raise RuntimeError(f"Publish manifest unreadable; reconcile manually: {self.path}") from exc
            if not isinstance(self.data, dict):
                raise RuntimeError(f"Publish manifest invalid root type; reconcile manually: {self.path}")
        else:
            self.data = {}

    def has_success(self, key, channel):
        return self.data.get(key, {}).get(channel, {}).get("status") == "success"

    def get_status(self, key, channel):
        return self.data.get(key, {}).get(channel, {}).get("status")

    def record(self, key, channel, status, detail=""):
        if status not in {"pending", "success", "failed", "unknown"}:
            raise ValueError("Manifest status must be pending, success, failed, or unknown.")
        self.data.setdefault(key, {})[channel] = {"status": status, "detail": detail}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)
