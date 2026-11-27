# Talking-avatar integration sequence

The adapter remains opt-in. A real external engine is now available as a staging integration path: MuseTalk 1.5 through the public Hugging Face Space `henrybit/musetalk-1-5`.

1. The live-validation script generates the AI PINTAR master illustration and a short Indonesian test voice using Edge TTS.
2. It sends only those generated test assets to the public Hugging Face Space. No user photo, production video, Buffer/Cloudinary credential or post is used.
3. The Space returns a video, which is checked by FFprobe for video/audio streams and duration parity against the driving audio.
4. The test artifact includes the presenter master, test audio, returned video and JSON report. The output file SHA-256 is recorded.
5. A duration-parity PASS is not a perceptual lip-sync score. Human review is still required to confirm mouth movement, face identity, crop, flicker, chroma/background artifacts and visual quality.

The runner is `engine/hf_musetalk_runner.py`, and the adapter calls it through the existing `TALKING_AVATAR_RUNNER` command contract. The optional `gradio_client` dependency is installed separately and pinned in the live-validation workflow; it is not added to the normal runtime lock.

The public Space is third-party and may be paused, queue-limited or change API shape. Image and audio are sent to that Space. The workflow uses synthetic media only and does not publish.

Current status before live validation: code and mocked tests are present; actual engine availability and visual review are pending. Do not merge or publish based solely on duration-parity checks.
