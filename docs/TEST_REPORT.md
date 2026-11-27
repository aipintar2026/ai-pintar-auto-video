# AI PINTAR 2.0 Staging Test Report

**Latest verified run:** Run #110  
**Run ID:** `45937716274`  
**Commit:** `bc491076445c9fc233518d76b57295b4cffffcb2`  
**Date:** 27 November 2026  
**Artifact ID:** `15171790401`  
**Artifact ZIP SHA-256:** `a1a88ab4688f9c6706ca92ff9237a12b13506fb93aadc402086224f7471da115`

## Automated CI

- Python compilation: passed.
- Unit tests: **51 passed, 0 failed**.
- Hashed dependency lock regeneration and committed-lock diff: passed.
- Installation with `--require-hashes`: passed.
- Synthetic offline render: passed.
- Artifact upload: passed.
- All workflow steps completed successfully.

## Synthetic render evidence

- Duration: 35 seconds
- Resolution: 1080 × 1920 portrait
- Video/audio: H.264/AAC
- Caption, SRT, ASS and manifest: present
- Subtitle cues: 14
- Generated presenter master: included
- Chroma-key static overlay: exercised
- Cover generation from synthetic footage frame: exercised
- Publish: disabled
- External provider calls: none

## Automated subtitle / cover QC

- Maximum subtitle line: 34 characters
- Maximum character speed: 19.2 characters/second
- Minimum cue duration: 0.564 seconds
- Maximum cue duration: 3.438 seconds
- ASS dialogue count: 14
- ASS font size: 34
- ASS alignment: lower-center
- ASS vertical margin: 300
- Subtitle QC: PASS
- Cover: 1080 × 1920, 2 title lines, structural safe-zone QC PASS

Cover QC verifies file/resolution/title layout and safe-zone metrics. It does **not** automatically verify semantic footage-to-title match or replace human visual review. The presenter render is a generated static illustration; it is not lip-synced.

## Implemented and tested in staging

- Deterministic master-presenter generator.
- Static presenter chromakey overlay in FFmpeg render.
- Talking-avatar adapter wiring when `TALKING_AVATAR_RUNNER` is configured.
- Cover generation and structural cover QC.
- SRT minimum dwell-time and character-speed validation.
- ASS/SRT cue parity, font-size and safe-zone validation.
- Direct dependency input and full hash-locked requirements.
- CI regenerates the lock, verifies the committed file has no diff, and installs with `--require-hashes`.
- Offline pipeline artifact includes video, cover and presenter master.

## Mocked integration coverage

Pixabay selection/download, Edge TTS, Cloudinary signed-upload validation, Buffer queue/reconciliation, publish guards, talking-avatar adapter contract, pipeline orchestration/recovery and reconciliation keys remain mock-tested. Mock tests do not prove live provider behavior.

## Pending external or production validation

- Live Pixabay access/download
- Live Edge TTS network execution
- Cloudinary account upload
- Buffer channel/API validation (no content publication)
- Selected talking-avatar engine and real lip-sync
- Human visual/semantic review of presenter, cover and footage alignment
- Durable state/reconciliation across ephemeral runners
- Production workflow review and migration approval

## Safety boundary

PR #3 remains staging-only, open/draft/unmerged. No merge, production workflow changes, schedule changes or publication were performed. The existing production workflow on `main` remains untouched and may queue content independently.
