# AI PINTAR 2.0 Staging Test Report

**Latest verified run:** GitHub Actions run #69  
**Run ID:** `45912116222`  
**Commit:** `02cc680c3c28a30664981e83d70c88e7256db416`  
**Date:** 27 November 2026  
**Artifact ID:** `15160776246`

## Automated tests

- Python compilation: passed.
- Python test suite: **42 passed, 0 failed**.
- Synthetic offline render: passed.
- Artifact upload: passed.

## Offline render QC

- Duration: 30 seconds (synthetic test)
- Resolution: 1080 × 1920 portrait
- Video: H.264
- Audio: AAC
- SRT/ASS subtitles and manifest: included in the test artifact
- Publish: disabled
- External provider calls: none

## Verified workflow steps

All job steps in Run #69 completed successfully: checkout, Python setup, FFmpeg install, dependency install, compilation, unit tests, synthetic offline pipeline, and artifact upload.

Run #69 re-verifies the existing offline safety milestone; it does not by itself increase overall audit progress.

## QC boundary

This run verifies synthetic offline rendering and CI execution. It is **not** semantic footage/subtitle QC, cover QC, a real-presenter render, talking-avatar engine validation, or live provider testing.

## Mocked integration coverage (previously documented)

Mock coverage includes Pixabay selection/download path, Edge TTS path, Cloudinary signed-upload validation, Buffer scheduling/reconciliation behavior, publish guards, talking-avatar adapter validation, pipeline orchestration/recovery, and stable reconciliation keys. Mock coverage does not prove live service behavior.

## Pending live and production validation

- Live Pixabay access and download
- Live Edge TTS/network execution
- Cloudinary account upload
- Buffer channel/API validation (no content publication)
- Selected talking-avatar engine and lip-sync
- Approved master presenter installed into repository/pipeline
- Cover generation and semantic visual QC
- Durable state across ephemeral runners and production reconciliation
- Dependency lock/hash verification

## Safety boundary

PR #3 is staging repair only. No merge, production workflow changes, schedule changes, or publication were performed. The production workflow on main remains untouched and is separately under review.
