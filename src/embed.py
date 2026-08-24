from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        # Small, common starter model. First run downloads it.
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: list[str]):
    model = get_model()
    return model.encode(texts, normalize_embeddings=True)


def similarity(a, b) -> float:
    return float(cos_sim(a, b).item())