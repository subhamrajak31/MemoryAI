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
    Handles vector storage and semantic retrieval for long-term user memories and documents.
    """

    def __init__(self) -> None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name="user_memories"
        )
        self.doc_collection = self.client.get_or_create_collection(
            name="document_chunks"
        )

        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.genai_client = genai.Client(api_key=GEMINI_API_KEY)

    # ... existing memory methods remain unchanged ...

    def add_document_chunk(
        self,
        user_id: str,
        document_id: str,
        chunk_id: str,
        text: str,
    ) -> None:
        """
        Index a document chunk vector into ChromaDB with metadata.
        """
        try:
            embedding = self._generate_embedding(text)
            self.doc_collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{"user_id": user_id, "document_id": document_id}],
            )
        except Exception as error:
            logger.exception(
                "Failed to index chunk %s for document %s: %s",
                chunk_id,
                document_id,
                error,
            )
            raise

    def search_documents(
        self,
        user_id: str,
        query: str,
        top_k: int = 4,
    ) -> list[str]:
        """
        Search top-K semantically relevant document chunks for a user query.
        """
        if self.doc_collection.count() == 0:
            return []

        try:
            query_embedding = self._generate_embedding(query)
            results = self.doc_collection.query(
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
                "Failed to search document chunks for user %s: %s",
                user_id,
                error,
            )
            return []

    def delete_document_chunks(self, document_id: str) -> None:
        """
        Delete all indexed vector chunks belonging to a document ID.
        """
        try:
            self.doc_collection.delete(where={"document_id": document_id})
            logger.info("Removed document vectors for ID %s.", document_id)
        except Exception as error:
            logger.exception(
                "Failed to delete document vectors for ID %s: %s",
                document_id,
                error,
            )
            raise