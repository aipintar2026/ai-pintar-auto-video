# AI PINTAR 2.0 — Faceless Build Plan

## 1. Production baseline (keep untouched)
The existing `main.py`/workflow is the production fallback. AI PINTAR 2.0 remains staging-only until the validation gates below pass and migration is explicitly approved.

## 2. Active faceless system
1. Content intelligence: topic bank, topic rotation and recovery after failed runs.
2. Script: short hook, relatable problem, practical demonstration, extra insight and concise CTA; natural Indonesian; fact-check guard.
3. Footage: Pixabay relevance, novelty/history controls and at least three distinct visual beats.
4. Narration: Indonesian Edge TTS; validate duration before render.
5. Subtitles: timed SRT and burned-in ASS; readable line length, dwell time and CPS.
6. Cover: 1080×1920 cover generated from a footage frame, title overlay and safe-zone structural QC.
7. Render/QC: portrait H.264/AAC output, stream/duration/resolution checks, subtitle parity/readability, cover structural checks, caption and topic manifest.
8. Providers: Pixabay and TTS production tests; optional Cloudinary upload test; Buffer channel preflight and reconciliation. Publication stays disabled by default.
9. Safety: publishing guard, durable manifest and no automatic retry after uncertain outcomes.

## 3. Explicitly cancelled
Talking-avatar, lip-sync, presenter generation and presenter overlays are removed from the AI PINTAR 2.0 scope. Do not reintroduce or test them.

## 4. Durable state
Runner-local state is not a durable source of truth. Topic/media state and publish reconciliation need a durable design before production migration. A failed or uncertain publish must be reconciled before retry.

## 5. Migration gates
- A: unit tests for topic selection, script, subtitles, QC and publish guard.
- B: offline synthetic render, cover, artifact and QC report.
- C: live Pixabay + TTS + render + QC without publishing.
- D: Cloudinary controlled upload and Buffer channel validation/dry-run without queuing.
- E: human review of footage/title/subtitle/cover alignment, rights and output.
- F: production workflow review, backup, rollback and explicit migration approval.

## 6. No production changes
This PR remains staging-only. Do not merge, queue, publish, spend or change the existing schedule without explicit approval.
