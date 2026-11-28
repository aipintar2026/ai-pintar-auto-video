"""External providers for AI PINTAR 2.0. Staging is safe-by-default."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Iterable

import requests

PIXABAY_URL = "https://pixabay.com/api/videos/"
BUFFER_URL = "https://api.buffer.com"


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", str(value)).strip("-")[:80] or "asset"


def _pixabay_video_url(hit: dict) -> str | None:
    videos = hit.get("videos") or {}
    for size in ("medium", "small", "tiny", "large"):
        entry = videos.get(size) or {}
        if entry.get("url"):
            return entry["url"]
    return None


def pixabay_download(query: str, key: str, outdir, used_ids: Iterable[int] | None = None, count: int = 5, cache_path=None):
    """Search once and download a small set of unique, usable video clips."""
    if not key or not str(key).strip():
        raise RuntimeError("PIXABAY_API_KEY belum diset.")
    if not query or not str(query).strip():
        raise ValueError("Query Pixabay kosong.")
    if count < 1 or count > 10:
        raise ValueError("Jumlah footage harus 1-10.")
    used = {str(x) for x in (used_ids or [])}
    # Normalize query and use only documented, minimal search parameters.
    normalized_query = re.sub(r"[^\w\s-]", " ", str(query), flags=re.UNICODE)
    normalized_query = re.sub(r"\s+", " ", normalized_query).strip()[:80]
    if not normalized_query:
        raise ValueError("Query Pixabay tidak valid setelah normalisasi.")
    cache_path = Path(cache_path) if cache_path else Path(outdir).parent.parent / "state" / "pixabay_search_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
            if not isinstance(cache, dict): raise ValueError("Cache bukan object.")
        except (OSError, json.JSONDecodeError, ValueError):
            raise RuntimeError("Cache Pixabay rusak; jangan hapus otomatis, periksa state/pixabay_search_cache.json.")

    # Try the full scene phrase, a shorter phrase, then broad fallback terms.
    tokens = normalized_query.split()
    queries = [normalized_query, " ".join(tokens[:4]), " ".join(tokens[:2]), "technology", "computer"]
    unique_queries = list(dict.fromkeys(q for q in queries if q))
    hits = []
    for search_q in unique_queries:
        params = {"key": key, "q": search_q, "per_page": 30}
        cache_key = hashlib.sha256(("|" + search_q.lower().strip()).encode()).hexdigest()
        entry = cache.get(cache_key)
        if entry and (time.time() - float(entry.get("fetched_at", 0))) < 24 * 60 * 60:
            candidate_hits = entry.get("hits") or []
        else:
            response = requests.get(PIXABAY_URL, params=params, timeout=30)
            if getattr(response, "status_code", 200) == 400:
                shorter = " ".join(search_q.split()[:3])
                if shorter and shorter != search_q:
                    response = requests.get(PIXABAY_URL, params={"key":key,"q":shorter}, timeout=30)
            response.raise_for_status()
            candidate_hits = response.json().get("hits") or []
            cache[cache_key] = {"query": search_q, "fetched_at": time.time(), "hits": candidate_hits}
            temp_cache = cache_path.with_suffix(cache_path.suffix + ".tmp")
            temp_cache.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            temp_cache.replace(cache_path)
        if any(str(h.get("id")) not in used and _pixabay_video_url(h) for h in candidate_hits):
            hits = candidate_hits
            break
    # Rank search results by tag relevance and usable source quality instead of
    # taking the API's first hits blindly. This remains heuristic, not semantic QC.
    # Normalize tokenization consistently; prioritize semantic tag overlap and usable resolution.
    query_tokens = {t.lower() for t in re.findall(r"\w+", normalized_query) if len(t) > 2}
    def _details(hit):
        tags = {t.lower() for t in re.findall(r"\w+", str(hit.get("tags", "")))}
        relevance = len(query_tokens & tags) / max(1, len(query_tokens))
        videos = hit.get("videos") or {}
        best = videos.get("large") or videos.get("medium") or videos.get("small") or videos.get("tiny") or {}
        width = int(best.get("width") or 0); height = int(best.get("height") or 0)
        duration = int(hit.get("duration") or 0)
        quality = min(width / 1080, 1.0) if width else 0.0
        return relevance, quality, duration, width, height
    def _score(hit):
        relevance, quality, duration, width, height = _details(hit)
        return relevance * 4.0 + quality + (0.15 if duration >= 8 else 0.0) + (0.1 if height >= 720 else 0.0)
    eligible = [h for h in hits if str(h.get("id")) not in used and _pixabay_video_url(h)]
    # Prefer tag overlap; if it removes every result, keep provider-returned clips
    # rather than aborting a scene. Ranking still favors matching tags and quality.
    relevant = [h for h in eligible if _details(h)[0] >= 0.15 or len(query_tokens) <= 1]
    chosen = sorted(relevant or eligible, key=_score, reverse=True)[:count]
    if len(chosen) < count:
        # A smaller set is allowed only if at least one usable result is found.
        if not chosen:
            raise RuntimeError("Pixabay tidak menemukan footage yang belum dipakai.")
    target = Path(outdir)
    target.mkdir(parents=True, exist_ok=True)
    files, ids = [], []
    for hit in chosen:
        video_url = _pixabay_video_url(hit)
        if not video_url:
            continue
        clip_id = str(hit.get("id"))
        path = target / f"pixabay_{_safe_name(clip_id)}.mp4"
        temp = path.with_suffix(path.suffix + ".part")
        try:
            with requests.get(video_url, stream=True, timeout=(20, 90)) as dl:
                dl.raise_for_status()
                size = 0
                with temp.open("wb") as fh:
                    for chunk in dl.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            size += len(chunk)
                            if size > 600 * 1024 * 1024:
                                raise RuntimeError("Footage melewati batas 600 MB.")
                            fh.write(chunk)
            if temp.stat().st_size < 100_000:
                raise RuntimeError(f"Footage Pixabay {clip_id} terlalu kecil atau tidak valid.")
            temp.replace(path)
            files.append(str(path))
            ids.append(clip_id)
        except Exception:
            temp.unlink(missing_ok=True)
            path.unlink(missing_ok=True)
            raise
    if not files:
        raise RuntimeError("Tidak ada footage yang berhasil diunduh.")
    return files, ids


def create_tts(text: str, output):
    """Generate narration using the Edge TTS Python API; never relies on a CLI path."""
    if not text or not str(text).strip():
        raise ValueError("Teks TTS kosong.")
    voice = os.getenv("TTS_VOICE", "id-ID-ArdiNeural")
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError("Paket edge-tts belum terpasang; install requirements.txt.") from exc

    async def _save():
        communicator = edge_tts.Communicate(text, voice)
        await communicator.save(str(target))

    asyncio.run(_save())
    if not target.exists() or target.stat().st_size < 10_000:
        raise RuntimeError("Edge TTS tidak menghasilkan file audio yang valid.")
    return str(target)


def cloudinary_upload(video_path, public_id=None, folder="ai-pintar-2-staging"):
    """Signed video upload; caller must opt in and supply credentials."""
    cloud = os.environ.get("CLOUDINARY_CLOUD_NAME")
    key = os.environ.get("CLOUDINARY_API_KEY")
    secret = os.environ.get("CLOUDINARY_API_SECRET")
    if not all((cloud, key, secret)):
        raise RuntimeError("Cloudinary: CLOUD_NAME, API_KEY, dan API_SECRET wajib diset.")
    path = Path(video_path)
    if not path.exists() or path.stat().st_size < 100_000:
        raise RuntimeError("Cloudinary: file video tidak valid.")
    if not public_id:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        public_id = f"staging_{digest}"
    params = {"timestamp": str(int(time.time())), "folder": folder, "public_id": public_id, "overwrite": "true"}
    canonical = "&".join(f"{k}={params[k]}" for k in sorted(params))
    signature = hashlib.sha1((canonical + secret).encode("utf-8")).hexdigest()
    with path.open("rb") as fh:
        response = requests.post(
            f"https://api.cloudinary.com/v1_1/{cloud}/video/upload",
            data={**params, "api_key": key, "signature": signature},
            files={"file": fh},
            timeout=(30, 180),
        )
    response.raise_for_status()
    data = response.json()
    if not data.get("secure_url") or not data.get("public_id"):
        raise RuntimeError("Cloudinary upload tidak mengonfirmasi secure_url/public_id.")
    return {"secure_url": data["secure_url"], "public_id": data["public_id"], "bytes": data.get("bytes")}


def _buffer_post_json(token, payload):
    response = requests.post(
        BUFFER_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=(20, 60),
    )
    response.raise_for_status()
    data = response.json()
    if data.get("errors"):
        raise RuntimeError("Buffer GraphQL error: " + json.dumps(data["errors"], ensure_ascii=False))
    return data


def buffer_channel_info(token: str, channel_id: str):
    query = "query GetChannel($input: ChannelInput!) { channel(input: $input) { id name service type isDisconnected isQueuePaused } }"
    data = _buffer_post_json(token, {"query": query, "variables": {"input": {"id": channel_id}}})
    channel = (data.get("data") or {}).get("channel")
    if not channel or channel.get("id") != channel_id:
        raise RuntimeError(f"Buffer tidak mengonfirmasi channel {channel_id}.")
    if channel.get("isDisconnected"):
        raise RuntimeError(f"Buffer channel {channel_id} sedang disconnected.")
    if channel.get("isQueuePaused"):
        raise RuntimeError(f"Queue Buffer channel {channel_id} sedang pause.")
    return channel


def _scheduling_type(channel: dict) -> str:
    service = (channel.get("service") or "").lower()
    channel_type = (channel.get("type") or "").lower()
    if (service == "instagram" and channel_type == "profile") or (service == "facebook" and channel_type == "group"):
        return "notification"
    return "automatic"




def _post_metadata(channel: dict, caption: str):
    service=(channel.get("service") or "").lower()
    channel_type=(channel.get("type") or "").lower()
    title=(caption.splitlines()[0] if caption.splitlines() else "AI PINTAR")[:100]
    if service == "instagram":
        return {"instagram": {"type": "reel", "shouldShareToFeed": True, "isAiGenerated": True}}
    if service == "facebook":
        return {"facebook": {"type": "post" if channel_type == "group" else "reel"}}
    if service in ("youtube", "yt"):
        return {"youtube": {"title": title, "categoryId": "27", "type": "short", "privacy": "public", "isAiGenerated": True}}
    if service == "tiktok":
        # Explicit AI disclosure for AI-generated content.
        return {"tiktok": {"isAiGenerated": True}}
    if service in ("google", "googlebusiness", "google_business"):
        return {"google": {"type": "post"}}
    if service == "pinterest":
        raise RuntimeError("Buffer Pinterest memerlukan boardServiceId; helper staging belum mengonfigurasi board dan berhenti aman.")
    # LinkedIn, X/Twitter, Threads, Bluesky, Mastodon use the generic video asset shape.
    return {}


def buffer_queue(video_url: str, caption: str, channel_ids, enabled=False, manifest_path=None, content_key=None):
    """Queue a video only with two explicit safety flags and per-channel reconciliation."""
    ids = [str(x).strip() for x in (channel_ids or []) if str(x).strip()]
    if not ids:
        return {"dry_run": True, "channels": [], "message": "Tidak ada channel ID; publikasi tidak dilakukan."}
    if not enabled or os.getenv("PUBLISH_ENABLED", "false").lower() != "true" or os.getenv("PUBLISH_DRY_RUN", "true").lower() != "false":
        return {"dry_run": True, "channels": ids, "message": "Publikasi disabled; tidak ada post dibuat."}
    token = os.environ.get("BUFFER_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("BUFFER_ACCESS_TOKEN belum diset.")
    if not video_url.startswith("https://"):
        raise ValueError("Buffer memerlukan URL HTTPS yang dapat diakses publik.")
    if not content_key:
        content_key = hashlib.sha256((video_url + "|" + caption).encode()).hexdigest()
    manifest_path = Path(manifest_path or "publish_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    except (OSError, json.JSONDecodeError):
        raise RuntimeError("Publish manifest rusak/tidak dapat dibaca; hentikan untuk mencegah post ganda.")
    result = []
    mutation = """mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess { post { id dueAt } }
        ... on MutationError { message }
      }
    }"""
    for channel_id in ids:
        state = manifest.get(content_key, {}).get(channel_id, {})
        status = state.get("status")
        if status in ("success", "pending", "unknown"):
            result.append({"channel": channel_id, "status": "skipped_reconcile", "detail": status})
            continue
        channel = buffer_channel_info(token, channel_id)
        manifest.setdefault(content_key, {})[channel_id] = {"status": "pending", "channel": channel.get("name", "")}
        _write_manifest(manifest_path, manifest)
        variables = {"input": {
            "channelId": channel_id,
            "text": caption,
            "schedulingType": _scheduling_type(channel),
            "mode": "addToQueue",
            "assets": [{"video": {"url": video_url}}],
            "metadata": _post_metadata(channel, caption),
        }}
        try:
            data = _buffer_post_json(token, {"query": mutation, "variables": variables})
            action = (data.get("data") or {}).get("createPost") or {}
            post = action.get("post") or {}
            post_id = post.get("id")
            if not post_id:
                message = action.get("message") or "Buffer tidak mengonfirmasi ID post."
                manifest[content_key][channel_id] = {"status": "unknown", "detail": message}
                _write_manifest(manifest_path, manifest)
                raise RuntimeError(message)
            manifest[content_key][channel_id] = {"status": "success", "post_id": post_id, "dueAt": post.get("dueAt")}
            _write_manifest(manifest_path, manifest)
            result.append({"channel": channel_id, "status": "success", "post_id": post_id})
        except Exception as exc:
            # A timeout/connection loss may happen after Buffer created the post; don't auto-retry.
            if manifest.get(content_key, {}).get(channel_id, {}).get("status") == "pending":
                manifest[content_key][channel_id] = {"status": "unknown", "detail": str(exc)[:300]}
                _write_manifest(manifest_path, manifest)
            raise
    return {"dry_run": False, "results": result}


def _write_manifest(path, data):
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)
