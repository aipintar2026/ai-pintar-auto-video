# AI PINTAR 2.0 Staging Test Report

**Latest CI confirmation:** Run #70  
**Run ID:** `45925023349`  
**Commit:** `84e403afbeb3e229afbfab97bf6f2ae0980dc829`  
**Date:** 27 November 2026  
**Artifact ID:** `15165468848`  
**Artifact SHA-256:** `63a81a14d84b99436e900d034db62f7be2ba56461a202eb3ecb4b18dcd7e9b2c`

## Run #70 status

The reported workflow steps succeeded: checkout, Python setup, FFmpeg setup, dependency install, compilation, unit-test step, offline render and artifact upload.

Run #70 is a CI confirmation. It does not replace the more detailed test-count record from Run #69, nor validate live integrations.

## Earlier detailed test record

- Run #69: 42 tests passed, 0 failed.
- Synthetic offline render: passed.
- Artifact upload: passed.
- 30-second synthetic render, 1080×1920, H.264/AAC, SRT/ASS and manifest.
- No publication or external provider calls.

## QC boundary

The staging runs verify synthetic/offline rendering and CI execution only. They are not semantic footage/subtitle QC, cover QC, a real presenter render, talking-avatar engine/lip-sync validation or live provider tests.

## Mock integration coverage (as documented)

Mock coverage includes Pixabay selection/download, Edge TTS, Cloudinary signed-upload validation, Buffer queue/reconciliation, publish guards, talking-avatar adapter validation, pipeline orchestration/recovery and stable reconciliation keys. Mock coverage is not live service validation.

## Pending live and production validation

- Live Pixabay access and download
- Live TTS/network execution
- Cloudinary account upload
- Buffer channel/API validation (no content publication)
- Selected talking-avatar engine and lip-sync
- Owner-approved master presenter asset
- Cover generation and semantic visual QC
- Durable state across ephemeral runners and production reconciliation
- Dependency lock/hash verification

## Safety boundary

PR #3 is staging repair only. No merge, production workflow changes, schedule changes or publication were performed. The production workflow on main remains untouched and separately under review.
