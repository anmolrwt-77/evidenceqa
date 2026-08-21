import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingest import extract_text


RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DIR.iterdir())
    for path in files:
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue

        print(f"Reading: {path.name}")
        text = extract_text(path)
        print(f"  characters: {len(text)}")
        print(f"  preview: {text[:200]!r}")

        out_path = OUT_DIR / f"{path.stem}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"  saved: {out_path}")


if __name__ == "__main__":
    main()