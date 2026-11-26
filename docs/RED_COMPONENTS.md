# Presenter, music, Cloudinary and Buffer status

## Presenter

The renderer accepts a static image overlay or a supplied video presenter clip. A video clip can show motion; the package does not generate a talking-head or lip-sync avatar. The same approved asset can be used on every run to keep visual identity consistent. Place it in `assets/presenter.png` or `assets/presenter.mp4` and pass `--avatar`.

## Music

Optional, operator-supplied licensed music is mixed at a low fixed volume. There is no automatic music search or license verification. Use `--music` only with audio that you have rights to use.

## Cloudinary

Signed upload integration is included and tested with a mocked response. The live account has not been validated. The staging workflow has an opt-in Cloudinary test, which uploads but does not publish.

## Buffer

The current GraphQL mutation, channel lookup, video asset shape, scheduling mode, Instagram/Facebook/YouTube metadata, and manifest reconciliation are included and tested with mocks. Live Buffer credentials/channels have not been validated. The staging workflow never calls Buffer and has no publishing input. Pinterest is fail-closed until a board ID is explicitly configured. Do not retry a post marked `pending` or `unknown` without reconciling it in the Buffer dashboard first.
