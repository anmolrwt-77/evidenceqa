import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.embed import embed_texts, similarity


def main() -> None:
    sentences = [
        "The EU AI Act bans certain manipulative AI practices.",
        "European law prohibits some harmful uses of artificial intelligence.",
        "I like to bake chocolate chip cookies on weekends.",
        "How do I change the oil in a bicycle?",
    ]

    vectors = embed_texts(sentences)

    pairs = [
        (0, 1, "similar policy meanings"),
        (0, 2, "policy vs cookies"),
        (0, 3, "policy vs bicycle"),
        (2, 3, "cookies vs bicycle"),
    ]

    print("Cosine similarities:")
    for i, j, label in pairs:
        score = similarity(vectors[i], vectors[j])
        print(f"  [{label}] {score:.4f}")
        print(f"    A: {sentences[i]}")
        print(f"    B: {sentences[j]}")


if __name__ == "__main__":
    main()