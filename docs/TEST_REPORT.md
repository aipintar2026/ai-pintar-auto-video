# AI PINTAR 2.0 Staging Test Report

**Date:** 26 November 2026

## Automated tests

- Python test suite: **22 passed**.
- Python compilation: passed.
- Offline synthetic render: passed.

## Offline render QC

- Duration: 30.0 seconds
- Resolution: 1080 × 1920 portrait
- Video: H.264
- Audio: AAC
- Caption file: present
- SRT: multiple sentence-timed cues, present and burned into video
- Presenter overlay: synthetic image overlay exercised
- Music mixing: synthetic audio bed exercised
- Publish: disabled
- External provider calls: none
- Test render frame rate: 10 fps to keep the offline test quick; the production renderer defaults to 30 fps.

## Mocked integration coverage

- Pixabay response and download/fallback selection
- Edge TTS Python API call path
- Cloudinary signed upload request construction and response validation
- Buffer channel lookup, GraphQL create-post payload, platform metadata, scheduling mode, manifest success and duplicate/unknown reconciliation
- Publish guard dry-run defaults

## Not live-validated

No real Pixabay API key, Edge TTS network call, Cloudinary account upload, or Buffer account/channel queue was used. The safety-test workflow is offline-only. Live media and Cloudinary checks are separate local CLI actions; Buffer posting is not included in the workflow.
