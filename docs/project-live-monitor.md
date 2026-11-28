# AI PINTAR 2.0 — Project Live Monitor

> Static snapshot as of 28 November 2026. Milestone percentages are estimates, not telemetry.

## Active scope: faceless video production

| Workstream | Estimate | Status | Verified basis / remaining |
|---|---:|---|---|
| Staging CI & safety | 100% of offline scope | GREEN | Run #148 compile, hash-lock install, 47 tests, synthetic render, QC and artifact upload passed after avatar cleanup. |
| Subtitle / cover QC | 85% | YELLOW | SRT/ASS readability, dwell/CPS, parity and cover structural safe-zone checks passed. Semantic review pending. |
| Core faceless pipeline | 80% | YELLOW | Offline render, subtitles, cover and QC orchestration exercised. Live media and durable state pending. |
| Provider integrations | 45% | YELLOW | Mocked paths tested. Live Pixabay/TTS, Cloudinary and Buffer validation pending. |
| Production hardening | 30% | YELLOW / RED | Hash lock and safety guard tested. Durable state, production workflow review and rollback plan pending. |

## Weighted estimate

Weights: CI/safety 25%, subtitle/cover QC 20%, faceless pipeline 20%, provider integration 15%, hardening/migration 20%.

`25 + 17 + 16 + 6.75 + 6 = 70.75%` — **about 71%**.

The estimate excludes the cancelled presenter/avatar feature. Repeated CI runs alone do not increase progress.

## Latest verified evidence

- Run #148: https://github.com/aipintar2026/ai-pintar-auto-video/actions/runs/46109002331
- Head: `22e415e044cfd0eca1f07ac3162a741985754728`
- 47 tests passed; compile, hashed dependency verification/install, synthetic render and artifact upload passed.
- Synthetic video: 35 seconds, 1080×1920; automated QC PASS.
- Subtitle QC: 14 cues, max CPS 19.2, minimum dwell 0.564s, maximum dwell 3.438s; ASS lower-center, font 34, margin 300.
- Cover QC: 1080×1920, 2 lines, structural safe-zone PASS. Human semantic/visual review remains required.
- Artifact ID: `15248682584`; SHA-256: `876adf9b8f890817b6fa245c753c246631f50ce2378483f891904d0b648f8f4f`; expires 5 December 2026.

## Changes in the cleanup
- Presenter/avatar/lip-sync code and experimental runner removed.
- Avatar input/overlay path removed from staging render API.
- Production CLI and offline render updated to match.
- Build plan, monitor, report and PR scope aligned with faceless-only direction.

## Pending blockers

- Live Pixabay and TTS/render/QC run.
- Human semantic review of footage, title, subtitles and cover.
- Cloudinary controlled upload.
- Buffer channel validation/reconciliation without publication.
- Durable state across ephemeral runners and separate production workflow review/approval.

## Safety

PR #3 remains staging-only, open/draft/unmerged. No publishing steps in staging CI; production configuration and schedule remain untouched.

## Next

1. Live faceless render with provider credentials.
2. Human visual review.
3. Controlled Cloudinary and Buffer checks.
4. Durable state and production migration review only after evidence and explicit approval.
