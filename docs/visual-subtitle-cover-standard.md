# AI PINTAR 2.0 — Subtitle & Cover Visual Standard

## Subtitle style

- Keep subtitles concise and conversational; rewrite narration into readable phrase chunks rather than transcribing every word.
- Limit to 1–2 lines, with line lengths short enough for a phone screen.
- Keep text in a lower-middle safe zone but above platform UI; do not cover the main subject, face, or key footage.
- Target subtitle block width around 75–82% of frame; avoid full-width banners and large opaque boxes.
- Use high contrast, clean rounded sans-serif, subtle shadow/outline, and restrained accent highlighting for 1–3 keywords per phrase.
- Use motion sparingly: fade/pop-in or gentle word emphasis; no bouncing/flashy effects on every phrase.
- Maintain consistent typography, padding, line spacing, and placement. Never let captions overlap one another.
- Use phrase-level timing, punctuation and natural pauses; avoid stiff robotic line breaks.
- Do not cover more than approximately 15% of the vertical frame with subtitles.

## Implemented subtitle renderer

The current staging render creates both SRT and ASS. ASS uses an explicit 1080×1920 canvas, DejaVu Sans 34 px, 2 px outline, 1 px shadow, bottom-center alignment and 300 px bottom margin. The SRT/ASS phrase chunks are limited to two lines. Automated QC now validates SRT cue durations (minimum 0.45s), character speed (maximum 24 characters/second), cue sequence, timing bounds, 2-line/34-character limits, ASS dialogue count parity, font size range (28–48), lower-center alignment, and vertical safe-zone margin (200–450). The QC report explicitly marks manual visual review as required; it does not claim automated face/object obstruction or semantic footage matching.

## Cover / thumbnail

Cover generation is implemented in the staging pipeline. It extracts a frame from the first footage clip and adds an AI PINTAR label plus a title in a dark, high-contrast overlay.

- Create a distinct opening cover/thumbnail for every video, not a generic still.
- Use a strong curiosity-based 3–7-word headline in large readable type, plus a visually relevant focal image.
- Headline must promise a clear benefit or curiosity without misleading clickbait.
- Keep text and important elements inside a centered mobile-safe area; avoid edges and lower UI zones.
- Contrast headline and background; use a subtle dark overlay behind text only if needed.
- Use consistent AI PINTAR brand colors/logo in a restrained way, not oversized.
- For platforms that use a cover frame, set/choose the cover deliberately; where the API does not support cover upload, create the cover as the opening frame and document the platform limitation.

## QC checks

- Automated cover structural QC: file exists, 1080×1920 resolution, title non-empty, no more than 5 lines, and safe-zone layout PASS.
- Automated subtitle QC: cue duration, CPS, sequence/timing, line length, ASS/SRT parity, font and safe-zone checks.
- Human review remains required for semantic footage/title match, subtitle obstruction, face/key-object obstruction, small-screen readability and spelling/natural Indonesian.
- Fail QC or flag for review when these checks cannot be verified automatically.

Cover generation and structural QC are now exercised in the synthetic offline pipeline. Semantic cover/footage match and subtitle-to-footage semantic alignment are not automated; manual review remains a release prerequisite.
