# Faceless pipeline and external integration status

## Format
AI PINTAR 2.0 staging is faceless: footage, Indonesian narration, subtitles, cover and QC. Presenter, talking-avatar and lip-sync work is cancelled and excluded from the production pipeline.

## Cover
Cover generation uses a frame from footage with an AI PINTAR title overlay. Structural QC checks resolution, title layout and safe-zone. Semantic footage/title match still needs human review.

## Music
Optional music must be supplied by the operator with rights to use it. Automatic music search/license verification is not implemented.

## Cloudinary
Signed upload construction and response validation are mock-tested. Live account validation remains pending. CI does not upload.

## Buffer
Channel lookup, payload construction, queue-mode, metadata and reconciliation are mock-tested. Live Buffer credentials/channel validation remain pending. CI does not publish.

## Pixabay / Edge TTS
Provider paths are mocked in tests. No live network/API calls are performed by CI.

## Safety boundary
PR #3 is staging-only and unmerged. The production workflow on main remains untouched.
