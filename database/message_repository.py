"""
Repository for message database operations.
"""

from __future__ import annotations

import sqlite3

from database.base_repository import BaseRepository


class MessageRepository(BaseRepository):
    """
    Handles CRUD operations for chat messages.
    """

    def create_message(
        self,
        message_id: str,
        session_id: str,
        role: str,
        content: str,
        timestamp: str,
    ) -> None:
        query = """
        INSERT INTO messages
        (id, session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """

        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    message_id,
                    session_id,
                    role,
                    content,
                    timestamp,
                ),
            )
            conn.commit()

    def get_messages(
        self,
        session_id: str,
    ) -> list[sqlite3.Row]:
        query = """
        SELECT *
        FROM messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """

        with self.db.get_connection() as conn:
            return conn.execute(query, (session_id,)).fetchall()

    def get_message_count(
        self,
        session_id: str,
    ) -> int:
        query = """
        SELECT COUNT(*) AS total
        FROM messages
        WHERE session_id = ?
        """

        with self.db.get_connection() as conn:
            row = conn.execute(query, (session_id,)).fetchone()
            return row["total"]

    def delete_messages(
        self,
        session_id: str,
    ) -> None:
        query = """
        DELETE FROM messages
        WHERE session_id = ?
        """

        with self.db.get_connection() as conn:
            conn.execute(query, (session_id,))
            conn.commit()