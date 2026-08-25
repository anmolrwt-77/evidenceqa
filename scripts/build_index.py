import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunk import chunk_text
from src.embed import embed_texts
from src.store import add_chunks, reset_collection


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

    print(f"Total chunks: {len(all_chunks)}")
    print("Embedding chunks (can take a few minutes)...")

    texts = [chunk.text for chunk in all_chunks]
    embeddings = embed_texts(texts)
    # convert to plain Python lists for Chroma
    embeddings = [vector.tolist() for vector in embeddings]

    collection = reset_collection()
    add_chunks(collection, all_chunks, embeddings)

    print(f"Stored vectors: {collection.count()}")
    print("Index saved in .chroma/")


if __name__ == "__main__":
    main()