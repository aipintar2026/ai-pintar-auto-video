# AI PINTAR 2.0 — Consolidated Build Plan

## 1. Production baseline (keep untouched)
The current `main.py`/workflow is the production fallback: Pixabay footage, Edge TTS (`id-ID-ArdiNeural`), 5 overlays, MP4 output, QC, Cloudinary upload, Buffer Facebook/TikTok queue. The current schedule (`17 7 * * *`, 14:17 WIB) is not to be changed in migration.

## 2. Target modules
1. Content Intelligence: 30-topic bank, topic history persisted between GitHub runner runs, topic exhaustion alert, no automatic reset.
2. Story/Script: 3-second hook, relatable problem, actionable demonstration, extra insight, concise CTA; 35–45 seconds; natural Indonesian; fact-check guard.
3. Video: Pixabay relevance/novelty scoring and history, five or more visual beats, subtitle (SRT and burned-in), brand-safe overlay.
4. Music: royalty/licence review; user-supplied or verified licensed library only; configurable low gain, narration ducking; fail gracefully without music.
5. Presenter: identity consistency via approved reference and provider only; no fabricated API. Initially optional and disabled until asset/provider selected.
6. QC: video exists/size, 1080x1920, duration, audio streams, subtitle presence, caption, topic ID, visual scene count, render log; fail before upload on QC failure.
7. Publishing: Cloudinary/Buffer; preflight channels; dry-run; durable publish manifest; reconciliation after partial failure; avoid blindly retrying the channel that succeeded.
8. Business layer: product generation, catalogue, analytics, affiliate, and ads Guardian are later isolated modules. Ads remain disabled pending user approval, budget caps, and attribution validation.

## 3. Durable topic state
Runner-local GitHub cache is not a durable source of truth. Candidate approach for first migration: tracked JSON state in repository, with workflow `contents: write`, fetch/rebase-safe commit of state only after a successful production run. If commit conflict occurs, fail safely and retain topic in log. Consider external DB only if justified.

## 4. Migration gates
- Gate A: unit tests for topic state/script/QC/publish guard.
- Gate B: offline render tests with synthetic/test media; no credentials.
- Gate C: GitHub Actions dry-run, artifact and QC logs only.
- Gate D: private Buffer/Cloudinary validation on controlled test channel/content, duplicate reconciliation tested.
- Gate E: compare output with baseline and review presenter/music licensing.
- Gate F: migrate with backup commit and rollback instructions. Schedule preserved.

## 5. No production changes yet
Files in this build directory are a staged prototype. No GitHub changes, publishing, spending, or schedule modifications have been performed.
