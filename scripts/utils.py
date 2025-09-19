from pathlib import Path

def load_prompt(name: str) -> str:
    return (Path("prompts")/name).read_text(encoding="utf-8").strip()
