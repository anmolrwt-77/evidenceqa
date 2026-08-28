import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate import generate_answer
from src.retrieve import retrieve


def main() -> None:
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "What are the four core functions of the NIST AI Risk Management Framework?"

    chunks = retrieve(question, k=3, min_score=0.0)
    answer = generate_answer(question, chunks)

    print("Question:")
    print(question)
    print("\nRetrieved sources:")
    for i, chunk in enumerate(chunks, start=1):
        print(f"  [{i}] {chunk.source} (score={chunk.score:.4f})")

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()