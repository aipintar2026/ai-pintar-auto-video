# AI PINTAR 2.0 Staging Test Report

**Latest verified run:** GitHub Actions run #62  
**Run ID:** \`45773091004\`  
**Commit:** \`1f720f471d1d5c8e19ea6bda8b427b0ef56504d7\`  
**Date:** 26 November 2026  
**Artifact ID:** \`15094942814\`

## Automated tests

- Python compilation: passed.
- Python test suite: **38 passed**.
- Synthetic offline render: passed.
- Artifact upload: passed.

## Offline render QC

- Duration: 30.0 seconds
- Resolution: 1080 × 1920 portrait
- Video: H.264
- Audio: AAC
- Caption: present
- SRT/ASS subtitle files: present; ASS canvas explicitly 1080 × 1920
- QC: audio/video, caption, subtitle, ASS canvas and topic ID passed
- Subtitle cues: 14
- Presenter overlay: synthetic block only
- Music mix: synthetic audio bed exercised
- Publish: disabled
- External provider calls: none

## Manual frame QC

Frames at 5, 15 and 25 seconds were inspected from run #62 artifact. Subtitles were readable, limited to two lines, bottom-centered and outside the synthetic avatar overlay. The avatar was a synthetic block; this frame review does not validate a real presenter, cover/thumbnail quality or semantic subtitle-to-footage alignment.

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

Stable local reconciliation keys improve retry safety but do not replace durable manifest storage across ephemeral runners. Durable state remains a migration prerequisite.

## Main-branch boundary

The existing \`main\` production schedule is active and untouched. The staging repair workflow is offline-only and does not queue or publish posts.
