from pathlib import Path
import json, re
import fitz  # PyMuPDF
from slugify import slugify

def extract_text_from_pdf(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    # Using sort=True helps keep reading order top-left to bottom-right for many PDFs
    texts = [page.get_text("text", sort=True) for page in doc]
    return "\n".join(texts)

def guess_metadata(text: str) -> dict:
    title = text.split("\n", 1)[0].strip()[:200]
    abstract_match = re.search(r"(?i)\babstract\b[:\s]*([\s\S]{300,2000})\n\n", text)
    abstract = abstract_match.group(1).strip() if abstract_match else ""
    return {"title": title, "abstract": abstract}

def parse_incoming(incoming_dir="incoming", out_dir="content"):
    in_dir, out = Path(incoming_dir), Path(out_dir)
    out.mkdir(exist_ok=True)
    for f in sorted(in_dir.glob("*")):
        if f.suffix.lower() not in (".pdf", ".txt"):
            continue
        if f.suffix.lower() == ".txt":
            raw = f.read_text(encoding="utf-8", errors="ignore")
        else:
            raw = extract_text_from_pdf(f)
        meta = guess_metadata(raw)
        slug = (slugify(meta["title"]) or slugify(f.stem))[:80] or slugify(f.stem)
        target = out / slug
        target.mkdir(parents=True, exist_ok=True)
        (target / "raw.txt").write_text(raw, encoding="utf-8")
        (target / "00_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        yield {"slug": slug, "text": raw, "meta": meta}
