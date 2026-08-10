"""
Business logic for Retrieval-Augmented Generation (RAG) document processing and context retrieval.
"""

from __future__ import annotations

from pathlib import Path

from database.document_repository import DocumentRepository
from memory.memory_store import VectorMemoryStore
from rag.loader import DocumentLoader
from utils.helpers import generate_uuid, get_current_timestamp
from utils.logger import logger


class RAGService:
    """
    Handles document ingestion, text chunking, vector indexing, and RAG context retrieval.
    """

    def __init__(
        self,
        document_repository: DocumentRepository | None = None,
        vector_memory_store: VectorMemoryStore | None = None,
        document_loader: DocumentLoader | None = None,
    ) -> None:
        self.document_repository = (
            document_repository
            if document_repository is not None
            else DocumentRepository()
        )
        self.vector_store = (
            vector_memory_store
            if vector_memory_store is not None
            else VectorMemoryStore()
        )
        self.loader = (
            document_loader
            if document_loader is not None
            else DocumentLoader()
        )

    def ingest_document(
        self,
        user_id: str,
        filename: str,
        file_path: str | Path,
    ) -> str:
        """
        Process an uploaded document file: extract text, save metadata, chunk, and index vectors.
        """
        document_id = generate_uuid()
        uploaded_at = get_current_timestamp()

        # 1. Extract raw text and chunk document
        raw_text = self.loader.load_document_text(file_path)
        chunks = self.loader.chunk_text(raw_text)

        if not chunks:
            raise ValueError("Document contains no extractable text.")

        # 2. Persist metadata in SQLite
        self.document_repository.create_document(
            document_id=document_id,
            user_id=user_id,
            filename=filename,
            file_path=str(file_path),
            uploaded_at=uploaded_at,
        )

        # 3. Index chunks into ChromaDB
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{idx}"
            self.vector_store.add_document_chunk(
                user_id=user_id,
                document_id=document_id,
                chunk_id=chunk_id,
                text=chunk,
            )

        logger.info(
            "Document '%s' (ID: %s) ingested with %d chunk(s).",
            filename,
            document_id,
            len(chunks),
        )

        return document_id

    def retrieve_context(
        self,
        user_id: str,
        query: str,
        top_k: int = 4,
    ) -> list[str]:
        """
        Retrieve semantically relevant document context chunks for a query.
        """
        return self.vector_store.search_documents(
            user_id=user_id,
            query=query,
            top_k=top_k,
        )

    def get_user_documents(self, user_id: str) -> list[dict]:
        """
        Get list of uploaded documents for a user.
        """
        rows = self.document_repository.get_user_documents(user_id)
        return [
            {
                "id": row["id"],
                "filename": row["filename"],
                "uploaded_at": row["uploaded_at"],
            }
            for row in rows
        ]

    def delete_document(self, user_id: str, document_id: str) -> None:
        """
        Synchronized deletion of document metadata from SQLite and vectors from ChromaDB.
        """
        self.document_repository.delete_document(document_id)
        self.vector_store.delete_document_chunks(document_id)
        logger.info("Document ID %s successfully deleted.", document_id)