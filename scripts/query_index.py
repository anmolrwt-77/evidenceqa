import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.embed import embed_texts
from src.store import get_collection, query_collection


def main() -> None:
    question = "What are the four core functions of the NIST AI Risk Management Framework?"

    collection = get_collection()
    print(f"Collection size: {collection.count()}")

    query_vec = embed_texts([question])[0].tolist()
    result = query_collection(collection, query_vec, n_results=3)

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    print(f"\nQuestion: {question}\n")
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
        print(f"--- Result {i} ---")
        print(f"source: {meta.get('source')}")
        print(f"index: {meta.get('index')}")
        print(f"distance: {dist:.4f}")
        print(doc[:400].replace("\n", " "))
        print("...")
        print()


if __name__ == "__main__":
    main()