"""Structured story format and lightweight validation for AI PINTAR scripts."""
from dataclasses import dataclass

@dataclass
class Story:
    hook: str
    problem: str
    solution: str
    extra: str
    cta: str

    def narration(self) -> str:
        return " ".join(part.strip() for part in (self.hook, self.problem, self.solution, self.extra, self.cta) if part.strip())


def validate_story(story: Story, min_chars: int = 250, max_chars: int = 850):
    parts = [story.hook, story.problem, story.solution, story.extra, story.cta]
    if any(not p.strip() for p in parts):
        raise ValueError("Story harus memiliki hook, problem, solution, extra, dan CTA.")
    if len(story.hook.split()) > 24:
        raise ValueError("Hook terlalu panjang; target ringkas untuk 3 detik pertama.")
    narration = story.narration()
    if not min_chars <= len(narration) <= max_chars:
        raise ValueError(f"Panjang naskah {len(narration)} karakter di luar batas {min_chars}-{max_chars}.")
    return narration
