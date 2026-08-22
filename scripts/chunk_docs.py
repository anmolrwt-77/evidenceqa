import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunk import chunk_text


PROCESSED_DIR = Path("data/processed")
CHUNK_SIZE = 800
OVERLAP = 150


def main() -> None:
    all_chunks = []

    for path in sorted(PROCESSED_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        chunks = chunk_text(
            text,
            source=path.name,
            chunk_size=CHUNK_SIZE,
            overlap=OVERLAP,
        )
        print(f"{path.name}: {len(chunks)} chunks")
        all_chunks.extend(chunks)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print("\n--- 3 example chunks ---")
    for chunk in all_chunks[:3]:
        print(f"\nsource={chunk.source} index={chunk.index}")
        print(chunk.text[:300].replace("\n", " "))
        print("...")


if __name__ == "__main__":
    main()