"""D-ID photo-avatar adapter. Live generation is opt-in and requires credentials/credits."""
from __future__ import annotations
import os, time, requests
from pathlib import Path

API = "https://api.d-id.com"


def _headers(key):
    return {"Authorization": "Basic " + key, "accept": "application/json"}


def _check(response, step):
    if not response.ok:
        # Provider diagnostics are useful for troubleshooting; never include request headers.
        try:
            payload = response.json()
            detail = str(payload)[:1800]
        except Exception:
            detail = response.text[:1800]
        request_id = response.headers.get("x-request-id") or response.headers.get("request-id")
        suffix = f" (request_id={request_id})" if request_id else ""
        raise RuntimeError(f"D-ID {step} HTTP {response.status_code}{suffix}: {detail}")
    return response


def create_avatar_video(audio_path, output, source_url=None, api_key=None, timeout=600):
    key = api_key or os.getenv("DID_API_KEY")
    image = source_url or os.getenv("DID_SOURCE_URL")
    if not key:
        raise RuntimeError("D-ID: DID_API_KEY belum tersedia.")
    if not image or not image.startswith("https://"):
        raise RuntimeError("D-ID: DID_SOURCE_URL harus berupa URL HTTPS gambar master presenter.")
    audio = Path(audio_path)
    target = Path(output)
    if not audio.exists():
        raise RuntimeError("D-ID: audio narasi tidak ditemukan.")
    if audio.stat().st_size > 6 * 1024 * 1024:
        raise RuntimeError("D-ID: audio melewati batas upload 6 MB.")
    target.parent.mkdir(parents=True, exist_ok=True)

    # Upload narration, then use the returned provider-hosted URL in AudioScript.
    with audio.open("rb") as fh:
        r = requests.post(API + "/audios", headers=_headers(key),
                         files={"audio": (audio.name, fh, "audio/mpeg")}, timeout=60)
    _check(r, "upload audio")
    try:
        audio_data = r.json()
    except ValueError as exc:
        raise RuntimeError(f"D-ID upload audio: respons bukan JSON (HTTP {r.status_code}).") from exc
    audio_url = audio_data.get("url") or audio_data.get("audio_url")
    if not audio_url:
        raise RuntimeError(f"D-ID upload audio: respons tidak berisi URL audio (keys={list(audio_data.keys())}).")

    # Keep the payload minimal to avoid unsupported config parameters.
    payload = {"source_url": image, "script": {"type": "audio", "audio_url": audio_url}}
    r = requests.post(API + "/talks", headers={**_headers(key), "content-type": "application/json"},
                      json=payload, timeout=60)
    _check(r, "create talk")
    try:
        job = r.json()
    except ValueError as exc:
        raise RuntimeError(f"D-ID create talk: respons bukan JSON (HTTP {r.status_code}).") from exc
    talk_id = job.get("id")
    if not talk_id:
        raise RuntimeError(f"D-ID create talk: respons tidak berisi job ID (keys={list(job.keys())}).")

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        check = requests.get(API + "/talks/" + talk_id, headers=_headers(key), timeout=30)
        _check(check, "poll talk")
        try:
            data = check.json()
        except ValueError as exc:
            raise RuntimeError("D-ID poll talk: respons bukan JSON.") from exc
        status = data.get("status")
        if status == "done":
            url = data.get("result_url")
            if not url:
                raise RuntimeError("D-ID job done tetapi result_url kosong.")
            with requests.get(url, stream=True, timeout=(30, 120)) as dl:
                _check(dl, "download video")
                temp = target.with_suffix(target.suffix + ".part")
                with temp.open("wb") as fh:
                    for chunk in dl.iter_content(1024 * 1024):
                        if chunk:
                            fh.write(chunk)
                if temp.stat().st_size < 100_000:
                    temp.unlink(missing_ok=True)
                    raise RuntimeError("D-ID video terlalu kecil.")
                temp.replace(target)
            return {"provider": "D-ID", "talk_id": talk_id, "status": "done",
                    "video": str(target), "bytes": target.stat().st_size}
        if status in ("error", "rejected"):
            error_detail = data.get("error") or data.get("message") or status
            raise RuntimeError("D-ID talk gagal: " + str(error_detail)[:1500])
        time.sleep(8)
    raise TimeoutError(f"D-ID processing timeout untuk talk {talk_id}; cek job di dashboard sebelum retry.")
