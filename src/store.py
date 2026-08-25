from pathlib import Path

import chromadb


DEFAULT_DB_PATH = ".chroma"
COLLECTION_NAME = "evidenceqa"


def get_collection(db_path: str = DEFAULT_DB_PATH):
    client = chromadb.PersistentClient(path=db_path)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def reset_collection(db_path: str = DEFAULT_DB_PATH):
    client = chromadb.PersistentClient(path=db_path)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return get_collection(db_path)


def add_chunks(collection, chunks, embeddings) -> None:
    ids = [f"{chunk.source}::{chunk.index}" for chunk in chunks]
    documents = [chunk.text for chunk in chunks]
    metadatas = [{"source": chunk.source, "index": chunk.index} for chunk in chunks]

    batch_size = 100
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )


def query_collection(collection, query_embedding, n_results: int = 3):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )