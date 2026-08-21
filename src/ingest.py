from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts)


def extract_text_from_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix == ".md":
        return extract_text_from_markdown(path)
    raise ValueError(f"Unsupported file type: {path}")