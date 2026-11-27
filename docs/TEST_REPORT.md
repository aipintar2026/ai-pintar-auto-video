# AI PINTAR 2.0 Staging Test Report

**Latest verified run:** Run #96  
**Run ID:** `45936879451`  
**Commit:** `08e683864b5e7d205a0db70016bb104f978f24a5`  
**Date:** 27 November 2026  
**Artifact ID:** `15170991631`  
**Artifact ZIP SHA-256:** `ef56a52479a18153eb316fce18d2637eb47c9df4f7aa04b13c74557900bcbf1d`

## Automated CI

- Python compilation: passed.
- Unit tests: **51 passed, 0 failed**.
- Synthetic offline render: passed.
- Artifact upload: passed.
- All workflow steps completed successfully.

## Synthetic render evidence

- Duration: 35 seconds
- Resolution: 1080 × 1920 portrait
- Video/audio: H.264/AAC
- Output video size: 985,467 bytes
- Caption, SRT, ASS and manifest: present
- Subtitle cues: 14
- Generated presenter master: included
- Chroma-key static overlay: exercised
- Cover generation from a synthetic footage frame: exercised
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

The cover QC checks file/resolution/title layout and safe-zone metrics. It does **not** automatically verify semantic footage-to-title match or replace human visual review. The presenter render is a generated static master illustration; it is not lip-synced.

## Implemented and tested in the staging branch

- Deterministic master-presenter generator.
- Static presenter chromakey overlay in FFmpeg render.
- Talking-avatar adapter wiring when `TALKING_AVATAR_RUNNER` is configured.
- Cover generation and structural cover QC.
- SRT minimum dwell-time and character-speed validation.
- ASS/SRT cue parity, font-size and safe-zone validation.
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
- Dependency lock/hash verification
- Review of the active production workflow on main before any migration

## Safety boundary

PR #3 remains staging-only, open/draft/unmerged. No merge, production workflow changes, schedule changes or publication were performed. The existing production workflow on `main` remains untouched and may queue content independently.
