# AI PINTAR 2.0 — staging package

**Staging only. This package does not modify or replace AI PINTAR 1. PR #3 targets `ai-pintar-2-staging`. The safety-test workflow runs on pull requests to that branch and manual dispatch. It has no publishing steps or secrets.**

## What it includes

- 30-topic bank and topic rotation state
- Structured Indonesian script generator (hook, problem, solution, insight, CTA)
- Pixabay search/download with 24-hour result cache and used-ID tracking
- Edge TTS (`id-ID-ArdiNeural` by default)
- FFmpeg 1080×1920 render, burned subtitles (SRT + ASS), optional licensed music
- Cover generation from the first footage frame with title overlay and structural QC
- QC for video/audio streams, resolution, duration, caption, subtitle dwell/CPS, ASS/SRT parity and cover safe-zone
- Signed Cloudinary upload helper (optional local staging test)
- Buffer GraphQL queue helper with channel checks and manifest reconciliation; **not invoked by the GitHub safety workflow**
- Offline synthetic-media test and unit tests

## Quick offline test (local)

```bash
python -m pip install --require-hashes -r requirements.lock
sudo apt-get install ffmpeg   # Linux; install FFmpeg/ffprobe on other platforms
python -m pytest -q
python run_offline_pipeline.py
```

The offline pipeline produces a synthetic video, caption, SRT/ASS, manifest and cover. It makes no external provider calls and does not publish.

## Live media test (local)

Set `PIXABAY_API_KEY` and install requirements. Optional `TTS_VOICE` defaults to `id-ID-ArdiNeural`. Then:

```bash
python run_production.py --output output_production
```

This downloads five unique footage clips, generates narration, subtitles, footage and cover, then runs QC. It does **not** upload to Cloudinary or queue posts.

## Production format

AI PINTAR 2.0 is strictly faceless: relevant footage, Indonesian AI narration, dynamic subtitles, cover and QC. Presenter, avatar and lip-sync features are cancelled and excluded from the build.

Optional music must be supplied by the operator with rights to use it:

```bash
python run_production.py --music assets/music.mp3
```

## Cloudinary test

Set the three Cloudinary secrets in the environment and run:

```bash
python run_production.py --upload-cloudinary
```

This uploads the QC-approved video to the staging folder and does not queue it to social channels. Live account validation is not part of GitHub CI.

## Buffer queue

The helper is included and unit-tested, but **live account/channel testing has not been performed**. Queueing is not exposed by the staging GitHub workflow. For a deliberate local run only, after reviewing the video, confirming the public Cloudinary URL and checking the Buffer queue, the operator must explicitly pass `--publish`, channel IDs, and set `PUBLISH_ENABLED=true` and `PUBLISH_DRY_RUN=false`. The helper checks the channel, writes a per-channel manifest and does not blindly retry `pending`/`unknown` outcomes; reconcile them in Buffer first.

## Dependency lock

`requirements.in` lists direct dependencies and `requirements.lock` pins the full resolved set with hashes. Staging CI regenerates the lock using pinned pip/pip-tools, checks that the committed lock is unchanged, and installs with `--require-hashes`. The lock verification was included in Run #110 and passed.

## GitHub staging workflow

The current workflow is already in `.github/workflows/auto-video.yml`. See `docs/INSTALL_GITHUB.md`. **Do not upload a ZIP or create a second workflow.** Run the safe test on the repair branch or review PR #3. No secrets or publishing inputs are used.

## Safety boundaries

- The safety-test workflow runs for pull requests targeting `ai-pintar-2-staging` and manual dispatch; no cron schedule is present in this repair branch.
- GitHub CI runs compilation, unit tests and a synthetic render only.
- No Buffer token or social-publishing secrets are injected into that workflow.
- Live Pixabay/TTS and Cloudinary checks are separate local CLI actions, not workflow inputs.
- The existing `main` production schedule remains untouched and may queue posts independently. This repair branch does not stop or modify it.
- Do not merge staging into `main` or change AI PINTAR 1 before explicit approval.
