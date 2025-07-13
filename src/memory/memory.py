from __future__ import annotations

from pathlib import Path
from uuid import uuid4

try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
except Exception:  # pragma: no cover - optional dependency
    chromadb = None


class Memory:
    """Persistent vector store for transcripts."""

    def __init__(self, persist_directory: str = "vector_store") -> None:
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        if chromadb is None:
            # simple in-memory fallback
            class _DummyCollection:
                def __init__(self):
                    self.docs = []
                def add(self, documents, ids):
                    self.docs.extend(documents)
                def query(self, query_texts, n_results=5):
                    return {"documents": [self.docs[:n_results]]}
            self.collection = _DummyCollection()
        else:
            self.client = chromadb.PersistentClient(path=persist_directory)
            embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            self.collection = self.client.get_or_create_collection(
                "transcripts", embedding_function=embedding_fn
            )

    def add(self, text: str) -> None:
        """Embed and store a text entry."""
        doc_id = str(uuid4())
        self.collection.add(documents=[text], ids=[doc_id])

    def search(self, query: str, top_k: int = 5) -> list[str]:
        """Search stored texts using semantic similarity."""
        result = self.collection.query(query_texts=[query], n_results=top_k)
        return result.get("documents", [[]])[0]
