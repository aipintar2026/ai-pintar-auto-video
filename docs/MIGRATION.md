# Safe staging migration

- PR #3 targets `ai-pintar-2-staging`; `main` and AI PINTAR 1 are untouched.
- The repair workflow is manual/PR-test only, no schedule and no publishing input.
- CI uses read-only repository permissions, pinned GitHub Actions SHAs, mocked integrations and synthetic media.
- CI does not use Pixabay, Edge TTS, Cloudinary or Buffer credentials; no posts are queued or published by this workflow.
- The existing `main` production schedule remains active and may queue posts independently. This PR does not stop it.
- Publish reconciliation keys now remain stable per topic ID and caption across media regeneration; regression-tested.
- Topic/media state and publish manifests are runner-local; durable persistence across ephemeral runners needs a separate design before production migration.

## Review gates

1. Review PR #3 and the run/artifact results.
2. Confirm the synthetic video and subtitle QC.
3. Install the approved presenter master asset and select/validate an actual talking-avatar engine before any presenter production test.
4. Validate live Pixabay/Edge TTS and Cloudinary separately with controlled credentials.
5. Validate Buffer live channel operations only after reconciliation safeguards and durable state are reviewed.
6. Verify cover/thumbnail generation and visual QC, which are not implemented in this safety-test package.
7. Only then prepare a migration plan with explicit approval, backup and rollback.

## Rollback

Close/revert the staging PR or branch. Do not merge to `main`; no production workflow or schedule has been modified.
