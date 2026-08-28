import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate import build_prompt
from src.retrieve import retrieve


def main() -> None:
    question = "What are the four core functions of the NIST AI Risk Management Framework?"
    chunks = retrieve(question, k=3, min_score=0.0)
    prompt = build_prompt(question, chunks)

    print(prompt)
    print("\n--- prompt stats ---")
    print(f"chunks used: {len(chunks)}")
    print(f"prompt characters: {len(prompt)}")


if __name__ == "__main__":
    main()