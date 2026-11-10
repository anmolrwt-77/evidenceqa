import numpy as np
from fastembed import TextEmbedding


_model = None


def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        # Same model as before, but run through ONNX (no PyTorch).
        _model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_model()
    vectors = np.array(list(model.embed(texts)), dtype=np.float32)
    # Normalize so every vector has length 1 (same as before).
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms


def similarity(a, b) -> float:
    # For length-1 vectors, the dot product equals cosine similarity.
    return float(np.dot(a, b))