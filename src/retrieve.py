import logging
from dataclasses import dataclass

from src.embed import embed_texts
from src.store import get_collection, query_collection


logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    text: str
    source: str
    index: int
    distance: float
    score: float


def distance_to_score(distance: float) -> float:
    # Chroma cosine distance: lower is better. Convert to similarity-like score.
    return 1.0 - distance


def retrieve(
    question: str,
    k: int = 3,
    min_score: float = 0.0,
) -> list[RetrievedChunk]:
    if not question.strip():
        raise ValueError("question must not be empty")
    if k <= 0:
        raise ValueError("k must be positive")

    collection = get_collection()
    query_vec = embed_texts([question.strip()])[0].tolist()

    raw = query_collection(collection, query_vec, n_results=k)

    documents = raw["documents"][0]
    metadatas = raw["metadatas"][0]
    distances = raw["distances"][0]

    results: list[RetrievedChunk] = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        score = distance_to_score(dist)
        if score < min_score:
            continue

        chunk = RetrievedChunk(
            text=doc,
            source=str(meta.get("source", "")),
            index=int(meta.get("index", -1)),
            distance=float(dist),
            score=score,
        )
        results.append(chunk)

    logger.info(
        "retrieve question=%r k=%s min_score=%s hits=%s max_score=%s",
        question,
        k,
        min_score,
        len(results),
        max((c.score for c in results), default=0.0),
    )

    return results