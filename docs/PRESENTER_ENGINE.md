# Presenter engine integration

## Provider
Staging supports the optional D-ID photo-avatar adapter. It uploads existing narration audio, animates a master presenter image, waits for the asynchronous job, downloads the generated MP4, and composes the presenter as a portrait inset over the scene render.

## Required GitHub Actions/local secrets
- `DID_API_KEY`: D-ID API key (Basic-auth key as documented by D-ID)
- `DID_SOURCE_URL`: HTTPS URL to the chosen master presenter portrait (JPG/PNG). The image should be owned/licensed and clearly frontal, shoulders visible.

Enable only for a paid, authorized test: set `DID_AVATAR_ENABLED=true`. This may consume provider credits. The workflow must not set it by default.

## Acceptance and caveats
- A provider job must return a video URL and the downloaded file must be probed.
- API processing consumes provider credits and cannot be simulated by CI tests.
- One still image does not guarantee body gestures; photo-avatar motion is mostly facial/head movement. A stronger full-body animation/video model may be needed for the aspirational target.
- This path is optional and fails closed when credentials or image URL are missing.
- Social publishing remains disabled.
