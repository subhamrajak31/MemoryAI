"""
Repository for uploaded document metadata.
"""

from __future__ import annotations

import sqlite3

from database.base_repository import BaseRepository


class DocumentRepository(BaseRepository):
    """Handles CRUD operations for document metadata."""

    def create_document(
        self,
        document_id: str,
        user_id: str,
        filename: str,
        file_path: str,
        uploaded_at: str,
    ) -> None:
        query = """
        INSERT INTO documents
        (id, user_id, filename, file_path, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
        """

        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    document_id,
                    user_id,
                    filename,
                    file_path,
                    uploaded_at,
                ),
            )
            conn.commit()

    def get_user_documents(
        self,
        user_id: str,
    ) -> list[sqlite3.Row]:
        query = """
        SELECT *
        FROM documents
        WHERE user_id = ?
        ORDER BY uploaded_at DESC
        """

        with self.db.get_connection() as conn:
            return conn.execute(query, (user_id,)).fetchall()

    def delete_document(
        self,
        document_id: str,
    ) -> None:
        query = """
        DELETE FROM documents
        WHERE id = ?
        """

        with self.db.get_connection() as conn:
            conn.execute(query, (document_id,))
            conn.commit()