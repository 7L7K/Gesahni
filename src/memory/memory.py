from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import chromadb
from chromadb.config import Settings

# Optional heavy dependency for embeddings
try:
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
except ImportError:
    SentenceTransformerEmbeddingFunction = None


class Memory:
    """Persistent vector store for transcripts."""

    def __init__(self, persist_directory: str = "vector_store") -> None:
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Try to use a real embedding function; otherwise fall back to dummy
        embedding_fn = None
        if SentenceTransformerEmbeddingFunction is not None:
            try:
                embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            except Exception:
                embedding_fn = None

        if embedding_fn is None:
            # Dummy embedding: fixed-size zero vectors
            class DummyEmbed:
                def __call__(self, inputs):
                    texts = inputs if isinstance(inputs, list) else [inputs]
                    return [[0.0] * 384 for _ in texts]

                @staticmethod
                def name():
                    return "dummy"

            embedding_fn = DummyEmbed()
            # In-memory client if real embeddings aren’t available
            self.client = chromadb.EphemeralClient()
        else:
            # Persistent on-disk client if embeddings work
            self.client = chromadb.PersistentClient(path=persist_directory)

        self.collection = self.client.get_or_create_collection(
            "transcripts",
            embedding_function=embedding_fn
        )

    def add(self, text: str) -> None:
        """Embed and store a text entry."""
        doc_id = str(uuid4())
        self.collection.add(documents=[text], ids=[doc_id])

    def search(self, query: str, top_k: int = 5) -> list[str]:
        """Search stored texts using semantic similarity."""
        result = self.collection.query(query_texts=[query], n_results=top_k)
        return result.get("documents", [[]])[0]
