from src.retrieve import RetrievedChunk


def format_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "(no context)"

    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(
            f"[{i}] source={chunk.source} index={chunk.index} score={chunk.score:.4f}\n"
            f"{chunk.text}"
        )
    return "\n\n".join(parts)


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = format_context(chunks)

    return f"""You are EvidenceQA, an assistant that answers ONLY from the provided context.

Rules:
1. Use only the context below. Do not use outside knowledge.
2. If the context is insufficient, say exactly: I don't know based on the provided documents.
3. Cite sources using the [number] labels from the context.
4. Keep the answer short and factual.

Context:
{context}

Question:
{question.strip()}

Answer:
"""