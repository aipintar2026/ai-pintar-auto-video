# Safe staging migration

- AI PINTAR 1/main is untouched.
- Install the ZIP and workflow only on `ai-pintar-2-staging`.
- The workflow is manual-only, branch-gated, and has no publish input.
- Offline render is the default; live media and Cloudinary upload require separate inputs and secrets.
- Buffer queue code is not called by the staging workflow.
- Topic/media rotation state is saved in GitHub Actions cache, not committed to `main`.

## Rollback

Revert/delete staging branch changes or the branch itself. Do not merge to `main`. No production schedule or workflow is modified.
