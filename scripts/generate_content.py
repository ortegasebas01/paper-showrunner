import os, json
from pathlib import Path
from tqdm import tqdm
from openai import OpenAI
from utils import load_prompt
from parse_pdf import parse_incoming

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")  # long-context model
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def respond(system, user, temperature=0.7, max_output_tokens=8000):
    r = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    return r.output_text

def build_user_input(doc_text, meta, extra=""):
    return (
        "SOURCE DOCUMENT (full text below)\n"
        f"METADATA: {json.dumps(meta, ensure_ascii=False)}\n"
        "-----\n"
        f"{doc_text}\n"
        "-----\n"
        f"ADDITIONAL INSTRUCTIONS:\n{extra}\n"
    )

def main():
    base = Path("content")
    for item in tqdm(list(parse_incoming())):
        slug, text, meta = item["slug"], item["text"], item["meta"]
        out = base / slug

        # 1) Technical summary
        sys = load_prompt("resumen_tecnico.txt")
        (out / "01_technical_summary.md").write_text(
            respond(sys, build_user_input(text, meta), temperature=0.2),
            encoding="utf-8"
        )

        # 2) Pedagogical explanation
        sys = load_prompt("explicacion_pedagogica.txt")
        (out / "02_pedagogical_explanation.md").write_text(
            respond(sys, build_user_input(text, meta), temperature=0.6),
            encoding="utf-8"
        )

        # 3) Premium long-form narrative (book-like, no script format)
        sys = load_prompt("narrativa_premium.txt")
        (out / "03_premium_narrative.md").write_text(
            respond(
                sys,
                build_user_input(text, meta, "No script format. Continuous, smooth prose."),
                temperature=0.85,
                max_output_tokens=20000
            ),
            encoding="utf-8"
        )

if __name__ == "__main__":
    main()
