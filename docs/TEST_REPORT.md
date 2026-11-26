# AI PINTAR 2.0 Staging Test Report

**Verified run:** GitHub Actions run #51  
**Run ID:** `45762724410`  
**Commit:** `ce474b82c77cf5f626c81060f05bf613aa8d01e7`  
**Date:** 26 November 2026

## Automated tests

- Python test suite: **34 passed**.
- Synthetic offline render: passed.
- Artifact upload: passed; artifact ID `15090606425`.

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

Frames at 5, 15 and 25 seconds were inspected from the artifact. Subtitles were readable, limited to two lines, bottom-centered, and outside the synthetic avatar overlay. The ASS renderer uses an explicit portrait canvas and fixed safe-area style. This does not validate actual footage, a real presenter, cover/thumbnail quality or semantic subtitle-to-video alignment.

## Mocked integration coverage

- Pixabay response/download/fallback selection
- Edge TTS API call path
- Cloudinary signed upload request and response validation
- Buffer channel lookup, GraphQL payload, metadata, scheduling mode, manifest success and duplicate/unknown reconciliation
- Publish guard
- Talking-avatar adapter input validation, subprocess/output validation and timeout path
- Pipeline orchestration, topic recovery after a simulated download failure

## Not live-validated / remaining

No real Pixabay key, Edge TTS network call, Cloudinary account upload, Buffer account/channel queue, talking-avatar engine, presenter master asset, cover generation or production footage was used. Durable state across ephemeral runners still requires design. The safety-test workflow is offline-only and does not publish.
