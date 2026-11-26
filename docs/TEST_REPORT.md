# AI PINTAR 2.0 Staging Test Report

**Latest verified run:** GitHub Actions run #68  
**Run ID:** `45867797228`  
**Commit:** `52698e5e16c524b62beda4151c222201ebd26a42`  
**Date:** 27 November 2026  
**Artifact ID:** `15140229403`  
**Artifact SHA-256:** `4775f765274b542126ffb5192672b3ad48c42f60bbf10f6ad9f8b04d79ef0a37`

## Automated tests

- Python compilation: passed.
- Python test suite: **42 passed, 0 failed**.
- Synthetic offline render: passed.
- Artifact upload: passed.

## Offline render QC

- Duration: 30.0 seconds
- Resolution: 1080 × 1920 portrait
- Video: H.264
- Audio: AAC
- Caption: present
- SRT/ASS subtitle files: present; ASS canvas explicitly 1080 × 1920
- Subtitle cues: 14
- Presenter overlay: synthetic block only
- Music mix: synthetic audio bed exercised
- Publish: disabled
- External provider calls: none

## Manual frame QC

Sample frames at 5, 15 and 25 seconds were inspected from the run #68 artifact. Subtitles were readable in these samples and did not visibly overlap the synthetic avatar block. This is limited sample-based visual review, not semantic footage/subtitle alignment, cover QC, or validation with a real presenter.

## Mocked integration coverage

- Pixabay response/download selection
- Edge TTS API path
- Cloudinary signed-upload request and response validation
- Buffer channel lookup, GraphQL payload, metadata, scheduling mode, manifest success/unknown reconciliation
- Publish guard and duplicate/unknown reconciliation
- Talking-avatar adapter validation, timeout and output checks
- Pipeline orchestration and topic recovery after simulated download/script failures
- Stable per-topic/caption reconciliation key across media regeneration

## Not live-validated / remaining

No real Pixabay key, Edge TTS network call, Cloudinary account upload, Buffer account/channel queue, talking-avatar engine, presenter master asset, cover generation or production footage was used.

Stable local reconciliation keys and per-run manifests improve retry safety in tests, but do not replace durable manifest storage across ephemeral runners. Durable state remains a migration prerequisite.

## Main-branch boundary

The existing `main` production schedule is active and untouched. The staging repair workflow is offline-only and does not queue or publish posts. Production workflow safety remains separately under audit.
