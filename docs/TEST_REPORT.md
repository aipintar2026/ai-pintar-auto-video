# AI PINTAR 2.0 Staging Test Report

## Active scope
Faceless production only: footage, Indonesian narration, dynamic subtitles, cover, render and QC. Talking-avatar, lip-sync, presenter generator and overlays are cancelled and removed.

## Latest verified CI after faceless cleanup
- Run #148: https://github.com/aipintar2026/ai-pintar-auto-video/actions/runs/46109002331
- Head: `22e415e044cfd0eca1f07ac3162a741985754728`
- Compile passed; hash-lock regeneration/verification and install passed; **47 tests passed**; synthetic render passed; artifact upload passed.
- Synthetic output: 35 seconds, 1080×1920, automated QC PASS.
- Subtitles: 14 SRT/ASS cues; max CPS 19.2; min cue 0.564 seconds; max cue 3.438 seconds; ASS lower-center, font 34, margin 300.
- Cover: 1080×1920; 2 title lines; structural safe-zone PASS. Semantic footage/title match and human visual review are not automated.
- Artifact: `AI-PINTAR-STAGING-OFFLINE`, ID `15248682584`, digest `sha256:876adf9b8f890817b6fa245c753c246631f50ce2378483f891904d0b648f8f4f`, expires 5 December 2026.
- Artifact link: https://github.com/aipintar2026/ai-pintar-auto-video/actions/runs/46109002331/artifacts/15248682584

## Changes verified in the cleanup
- Render API no longer accepts a presenter/avatar overlay input.
- Production and offline CLI calls aligned with the faceless render API.
- Presenter generator, talking-avatar adapter, experimental live runner and integration note removed from the branch.
- Build plan, monitor and test report aligned to the faceless-only scope.

## Pending validation
- Live Pixabay download and Edge TTS.
- Full real-media faceless render and human visual review.
- Cloudinary account/upload validation.
- Buffer channel/API validation without publication.
- Durable topic/media state and publish reconciliation across ephemeral runners.

## Safety boundary
PR #3 targets `ai-pintar-2-staging`, remains open/draft/unmerged. No merge, publication, production schedule or configuration changes were made.
