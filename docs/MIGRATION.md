# Safe staging migration

- AI PINTAR 1/main is untouched.
- Install the ZIP and workflow only on `ai-pintar-2-staging`.
- The safety-test workflow runs for pull requests targeting `ai-pintar-2-staging` and manual dispatch; it has no schedule or publishing input.
- GitHub CI is offline-only; live-media and Cloudinary tests are separate local CLI actions requiring credentials.
- Buffer queue code is not called by the staging workflow.
- The production pipeline's topic/media state files are runner-local. They are not durable across ephemeral GitHub runners unless a separate persistence mechanism is configured; the current safety workflow does not run that production pipeline.

## Rollback

Revert/delete staging branch changes or the branch itself. Do not merge to `main`. No production schedule or workflow is modified.
