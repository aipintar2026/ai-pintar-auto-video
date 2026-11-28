"""Scene-level prompt pack generator for the AI PINTAR 3D presenter workflow."""
from __future__ import annotations
import re, json
from pathlib import Path

MASTER_PRESENTER = (
    "One consistent stylized 3D animated Indonesian female technology educator, "
    "young adult, friendly expressive face, large natural eyes, straight dark hair, "
    "smart modest khaki/beige professional outfit, warm confident manner, "
    "consistent face, hairstyle, clothing and proportions in every scene. "
    "Polished cinematic 3D animation, not photorealistic."
)
STYLE = (
    "Vertical 9:16 social video framing. Modern Indonesian office or topic-relevant "
    "workspace, cinematic lighting combined with polished 3D character, natural hand "
    "gestures, subtle head and body motion, medium shot, presenter looking toward camera. "
    "No captions, no text, no logos, no watermarks, no UI overlays."
)
NEGATIVE = (
    "face identity drift, different outfit, extra fingers, warped hands, distorted face, "
    "frozen pose, uncanny eyes, duplicate person, random text, subtitles, logo, watermark, "
    "poor anatomy, low resolution, jitter, abrupt camera movement"
)

def beats_from_script(script, max_words=26):
    sentences=[s.strip() for s in re.split(r"(?<=[.!?])\\s+",script.strip()) if s.strip()]
    beats=[]
    for sentence in sentences:
        words=sentence.split()
        while words:
            beats.append(" ".join(words[:max_words]))
            words=words[max_words:]
    return beats

def build_prompt_pack(topic, script, outdir, max_scene_words=26):
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    beats=beats_from_script(script,max_scene_words)
    title=str(topic.get("title","AI PINTAR"))
    prompts=[]
    for i,beat in enumerate(beats,1):
        prompt=(
            f"{MASTER_PRESENTER} Explain this narration beat naturally: {beat!r}. "
            f"Topic: {title!r}. Add a subtle visual prop or environmental detail relevant "
            f"to the concept, without written words. {STYLE}"
        )
        prompts.append({"scene":i,"beat":beat,"prompt":prompt,"negative_prompt":NEGATIVE,
                       "duration_seconds":5,"aspect_ratio":"9:16",
                       "model_hint":"kling/v4/text-to-video"})
    pack={"topic":topic,"presenter_master_prompt":MASTER_PRESENTER,
          "visual_style":STYLE,"negative_prompt":NEGATIVE,
          "provider":"prompt_pack_only","scenes":prompts,
          "notes":"Prompt pack only. Video generation requires provider API key and cost authorization."}
    (outdir/"ai_video_prompt_pack.json").write_text(json.dumps(pack,ensure_ascii=False,indent=2),encoding="utf-8")
    (outdir/"ai_video_prompts.txt").write_text(
        "\\n\\n".join(f"SCENE {x['scene']}\\nBeat: {x['beat']}\\nPrompt: {x['prompt']}\\nNegative: {x['negative_prompt']}" for x in prompts),encoding="utf-8")
    return pack
