# AI PINTAR 2.0 — Visual production target (revision)

This document defines the visual direction for the next staged build. It is a design and acceptance specification, not a claim that a talking-avatar engine is already integrated.

## Target format
- Vertical 9:16 (1080x1920), 30–46 seconds.
- One fixed stylized 3D presenter master: face, hair, outfit, proportions and voice direction must remain consistent.
- Presenter scenes must include speech-synchronized lip movement, natural head motion, expressive eyes and restrained hand/body gestures.
- Topic-relevant moving footage/scene inserts, not static text cards as the primary visual.
- Indonesian narration, timed subtitle segments (maximum two lines), clean safe-zone placement.
- Cover, final MP4 and QC report.

## Required production sequence
1. Topic selection and script.
2. Narration/TTS generation.
3. Scene beat segmentation from the narration.
4. Presenter generation using the locked master identity and per-beat prompts.
5. Topic-relevant moving B-roll/scene inserts.
6. Assemble presenter and B-roll with pacing, audio, subtitle and transitions.
7. Render final MP4 and cover.
8. Automated QC plus human visual review.
9. Optional upload to Cloudinary only after explicit opt-in. Buffer queue remains disabled until human review.

## Acceptance gates
- A rendered MP4 exists and ffprobe confirms 1080x1920, video/audio streams and 30–46 seconds.
- Presenter identity and clothing are consistent across all presenter shots.
- Lip sync visibly tracks narration; no frozen talking-head or obvious mismatch.
- No card/slideshow-only output is accepted as meeting the target.
- B-roll is motion footage and materially relevant to narration.
- Subtitles are legible, timed and within safe zones.
- Cover and final QC report are included.
- No social publishing during validation.

## Provider and cost limitation
Prompt generation alone cannot render a talking avatar. The presenter-video engine must be selected and configured with credentials/credits and licensing review. No provider or cost is assumed approved. Until the real engine is connected and tested, this acceptance gate remains NOT PASSED.
