import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate import answer_question


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "What are the four core functions of the NIST AI Risk Management Framework?"

    result = answer_question(question)

    print("Question:")
    print(question)
    print(f"\nRefused by score gate: {result['refused']}")

    if result["citations"]:
        print("\nCitations:")
        for i, cite in enumerate(result["citations"], start=1):
            print(
                f"  [{i}] {cite['source']} "
                f"(index={cite['index']}, score={cite['score']:.4f})"
            )
    else:
        print("\nCitations: (none)")

    print("\nAnswer:")
    print(result["answer"])


if __name__ == "__main__":
    main()