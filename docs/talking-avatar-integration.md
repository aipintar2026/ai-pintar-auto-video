# Talking-avatar integration sequence

The adapter is wired into the staging production pipeline as an opt-in path. It is **not** a claim that facial animation or lip-sync is operational.

1. If no approved master image path is supplied, the pipeline generates a deterministic illustrated master with `engine.presenter.generate_master_presenter` into the output folder. The generated image uses chroma-green for static overlay. Human visual acceptance is still required.
2. Select an approved talking-avatar runner (provider/runtime, cost, GPU requirements and license must be reviewed).
3. Configure `TALKING_AVATAR_RUNNER` as a command template containing `{image}`, `{audio}`, and `{output}`.
4. The pipeline calls `engine.talking_avatar.generate_talking_avatar(master_image, narration_audio, output_video)` when the runner variable is set. The adapter validates inputs, timeout and output-file size.
5. Validate face identity, lip-sync, audio timing, crop, chroma-key/background and visual quality on a short test before accepting the engine.
6. Keep the static-master overlay fallback until a talking-avatar test is accepted. No publishing is enabled by this adapter.

Runner command contract: placeholders are shell-quoted and the command is invoked as a subprocess. The approved runner must be installed locally and its license/provider terms reviewed. Do not place API keys in the command string; use provider-managed environment variables.

Current status: adapter wiring and mocked contract tests pass. No engine is selected or live-tested, and lip-sync validation remains pending.
