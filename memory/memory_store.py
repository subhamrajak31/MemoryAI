"""
Vector store implementation for semantic memory retrieval using ChromaDB.
"""

from __future__ import annotations

import chromadb
from google import genai

from config.settings import (
    CHROMA_DIR,
    EMBEDDING_MODEL_NAME,
    GEMINI_API_KEY,
)
from utils.logger import logger


class VectorMemoryStore:
    """
    Handles vector storage and semantic retrieval for long-term user memories.
    """

    def __init__(self) -> None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name="user_memories"
        )

        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.genai_client = genai.Client(api_key=GEMINI_API_KEY)

    def _generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector using configured Gemini embedding model.
        """
        model_candidates = [
            EMBEDDING_MODEL_NAME,
            "gemini-embedding-001",
            "gemini-embedding-2",
        ]

        last_error = None
        for model_name in dict.fromkeys(model_candidates):
            try:
                response = self.genai_client.models.embed_content(
                    model=model_name,
                    contents=text,
                )

                if hasattr(response, "embedding") and response.embedding:
                    return response.embedding.values
                if hasattr(response, "embeddings") and response.embeddings:
                    return response.embeddings[0].values
            except Exception as error:
                last_error = error
                continue

        raise ValueError(
            f"Failed to generate embedding with models {model_candidates}. "
            f"Last error: {last_error}"
        )

    def add_memory(
        self,
        user_id: str,
        memory_id: str,
        text: str,
    ) -> None:
        """
        Add a memory embedding to ChromaDB with user isolation metadata.
        """
        try:
            embedding = self._generate_embedding(text)
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{"user_id": user_id}],
            )
            logger.info(
                "Memory ID %s indexed in ChromaDB for user %s.",
                memory_id,
                user_id,
            )
        except Exception as error:
            logger.exception(
                "Failed to index memory ID %s in ChromaDB: %s",
                memory_id,
                error,
            )
            raise

    def search_memories(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[str]:
        """
        Search top-K semantically relevant memories for a user query.
        """
        if self.collection.count() == 0:
            return []

        try:
            query_embedding = self._generate_embedding(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"user_id": user_id},
            )

            documents = results.get("documents", [[]])
            if documents and len(documents[0]) > 0:
                return documents[0]
            return []
        except Exception as error:
            logger.exception(
                "Failed to search memories in ChromaDB for user %s: %s",
                user_id,
                error,
            )
            return []

    def delete_memory(self, memory_id: str) -> None:
        """
        Delete a memory vector by memory ID.
        """
        try:
            self.collection.delete(ids=[memory_id])
            logger.info("Memory ID %s removed from ChromaDB.", memory_id)
        except Exception as error:
            logger.exception(
                "Failed to delete memory ID %s from ChromaDB: %s",
                memory_id,
                error,
            )
            raise