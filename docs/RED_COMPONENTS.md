# Presenter, music, Cloudinary and Buffer status

## Presenter

The renderer accepts a static image overlay or a supplied video presenter clip. The adapter is now wired into the staging production pipeline when `TALKING_AVATAR_RUNNER` is configured and a presenter master is supplied. No provider/engine has been selected or live-tested; this remains an unvalidated integration. The approved presenter master image is not installed in the repository. Do not substitute generated or search-result faces. Static/video overlay is not lip-sync.

## Music

The offline pipeline uses synthetic audio only. Optional production music must be supplied by the operator with rights to use it. There is no automatic music search or license verification.

## Cloudinary

Signed upload request construction and response validation are tested with mocks. The live account has not been validated. The GitHub staging workflow never uploads to Cloudinary.

## Buffer

Channel lookup, GraphQL payload construction, channel-aware queue mode, metadata, manifest success/unknown reconciliation and failure handling are tested with mocks. Live Buffer credentials/channels have not been validated. The staging workflow never calls Buffer and has no publishing input. Pinterest is fail-closed until a board ID is explicitly configured. Do not retry a post marked `pending` or `unknown` without reconciling it in the Buffer dashboard first.

## Pixabay / Edge TTS

Provider helper paths are mocked. No live API key or network request is used in CI.

## Main branch boundary

The existing `main` workflow has a scheduled production queue and remains untouched. The staging repair does not stop or change it.
