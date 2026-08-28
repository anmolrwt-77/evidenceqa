import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.retrieve import retrieve


def show(question: str, k: int = 3, min_score: float = 0.0) -> None:
    print("\n" + "=" * 80)
    print(f"Question: {question}")
    print(f"k={k}, min_score={min_score}")

    hits = retrieve(question, k=k, min_score=min_score)
    print(f"Returned: {len(hits)} chunks")

    for i, hit in enumerate(hits, start=1):
        print(f"\n--- Hit {i} ---")
        print(f"source: {hit.source}")
        print(f"index: {hit.index}")
        print(f"distance: {hit.distance:.4f}")
        print(f"score: {hit.score:.4f}")
        print(hit.text[:300].replace("\n", " "))
        print("...")


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    show(
        "What are the four core functions of the NIST AI Risk Management Framework?",
        k=3,
        min_score=0.0,
    )

    show(
        "What is the best pizza topping in Tokyo?",
        k=3,
        min_score=0.0,
    )

    show(
        "What is the best pizza topping in Tokyo?",
        k=3,
        min_score=0.5,
    )


if __name__ == "__main__":
    main()