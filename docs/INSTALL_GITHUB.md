# AI PINTAR 2.0 — safe staging workflow

The staging safety workflow is already present in `.github/workflows/auto-video.yml`. **Do not upload a package ZIP or create another workflow file.**

## Run the test

1. Open repository `aipintar2026/ai-pintar-auto-video`.
2. Use branch `ai-pintar-2-safety-fixes` or review PR #3, which targets `ai-pintar-2-staging`.
3. On a pull request targeting staging, the workflow runs automatically. For a manual test, open **Actions → AI PINTAR 2.0 Staging Safety Test → Run workflow** and select the repair branch.
4. There are no workflow inputs. Do not select `main` or run the production workflow.
5. Inspect the job logs and `AI-PINTAR-STAGING-OFFLINE` artifact. The artifact contains the synthetic video, caption, SRT, ASS, manifest and script.
6. This workflow uses no provider credentials, makes no external calls, and cannot enqueue or publish posts.

## What the workflow verifies

- Python compilation and unit tests
- Offline mocked integration paths
- Topic recovery and publish-manifest failure handling
- Synthetic 30-second 1080×1920 H.264/AAC render
- Caption, SRT and ASS subtitle QC, plus artifact upload

## Separate live validation

Live Pixabay/Edge TTS, Cloudinary and Buffer checks are not workflow inputs and are not part of this safe CI run. They require separate credentials, explicit operator action and review. The current presenter master image and talking-avatar engine are not installed/validated.

## Rollback

Close/revert PR #3 or revert changes on the staging branch. Do not merge to `main`. The existing `main` schedule is active and untouched by this repair.
