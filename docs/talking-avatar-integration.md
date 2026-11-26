# Talking-avatar integration sequence

This is an opt-in integration point, not a claim that facial animation is already operational.

1. Install the official master image as `assets/aipintar_host_master.jpg`.
2. Select and approve a talking-avatar runner (provider, GPU/runtime, cost, and license must be reviewed).
3. Configure `TALKING_AVATAR_RUNNER` as a command template containing `{image}`, `{audio}`, and `{output}`.
4. Use `engine.talking_avatar.generate_talking_avatar(master_image, narration_audio, output_video)` to generate a talking clip. The adapter validates inputs, timeout, and output file.
5. Validate face identity, lip sync, audio timing, cropping, and visual quality on a short test before wiring it into the full render pipeline.
6. Keep the existing static-avatar fallback until the talking-avatar test is accepted. No publishing is enabled by this adapter.

Runner command contract: placeholders are shell-quoted and the command is invoked as a subprocess. The approved runner must be installed locally and its license/provider terms reviewed. Do not place API keys in the command string; use provider-managed environment variables.
