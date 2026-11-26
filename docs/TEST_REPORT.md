# AI PINTAR 2.0 Staging Test Report

**Verified run:** GitHub Actions run #55  
**Run ID:** `45763325239`  
**Commit:** `99e68c0b154485abeacaa6dd8188f6bf64395379`  
**Date:** 26 November 2026  
**Artifact ID:** `15091430474`

## Automated tests

- Python compilation: passed.
- Python test suite: **35 passed**.
- Synthetic offline render: passed.
- Artifact upload: passed.

## Offline render QC

- Duration: 30.0 seconds
- Resolution: 1080 × 1920 portrait
- Video: H.264
- Audio: AAC
- Caption: present
- SRT and ASS subtitle files: present; ASS canvas explicitly 1080 × 1920
- QC report: caption, subtitle, ASS subtitle, audio/video and topic ID passed
- Presenter overlay: synthetic blue block only (placement path exercised, not a real presenter)
- Music mix: synthetic audio bed exercised
- Publish: disabled
- External provider calls: none

## Manual frame QC

Frames at 5, 15 and 25 seconds were inspected from the run #55 artifact. Subtitles were readable, limited to two lines, bottom-centered, and outside the synthetic avatar overlay. The ASS renderer uses an explicit portrait canvas and fixed safe-area style. This does not validate actual footage, a real presenter, cover/thumbnail quality or semantic subtitle-to-video alignment.

## Mocked integration coverage

- Pixabay response/download/fallback selection
- Edge TTS API call path
- Cloudinary signed upload request and response validation
- Buffer channel lookup, GraphQL payload, metadata, scheduling mode, manifest success and duplicate/unknown reconciliation
- Publish guard
- Talking-avatar adapter input validation, subprocess/output validation and timeout path
- Pipeline orchestration, topic recovery after simulated download and script-generation failures

## Not live-validated / remaining

No real Pixabay key, Edge TTS network call, Cloudinary account upload, Buffer account/channel queue, talking-avatar engine, presenter master asset, cover generation or production footage was used. Durable state across ephemeral runners still requires design. The safety-test workflow is offline-only and does not publish.

## Main-branch boundary

The existing `main` production schedule is active and untouched by this staging repair. The latest scheduled run #22 completed successfully; this repair did not trigger or modify it.
