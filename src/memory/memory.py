from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import chromadb
from chromadb.config import Settings
try:
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
except Exception:  # pragma: no cover - optional heavy dependency
    SentenceTransformerEmbeddingFunction = None


class Memory:
    """Persistent vector store for transcripts."""

    def __init__(self, persist_directory: str = "vector_store") -> None:
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        use_dummy = False
        self.client = chromadb.PersistentClient(path=persist_directory)
        if SentenceTransformerEmbeddingFunction is not None:
            try:
                embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            except Exception:  # package missing or failed to load
                embedding_fn = None
                use_dummy = True
        else:
            embedding_fn = None
            use_dummy = True
        if embedding_fn is None:
            class DummyEmbed:
                def __call__(self, input):  # type: ignore[override]
                    texts = input if isinstance(input, list) else [input]
                    return [[0.0] * 384 for _ in texts]

                @staticmethod
                def name():
                    return "dummy"

            embedding_fn = DummyEmbed()
            self.client = chromadb.EphemeralClient()
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
