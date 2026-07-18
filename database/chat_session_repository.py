"""
Repository for chat session database operations.
"""

from __future__ import annotations

import sqlite3

from database.base_repository import BaseRepository
from utils.logger import logger


class ChatSessionRepository(BaseRepository):
    """Handles CRUD operations for chat sessions."""

    def create_session(
        self,
        session_id: str,
        user_id: str,
        title: str,
        created_at: str,
        updated_at: str,
    ) -> None:
        query = """
        INSERT INTO chat_sessions
        (id, user_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """

        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (session_id, user_id, title, created_at, updated_at),
            )
            conn.commit()

    def get_session_by_id(
        self,
        session_id: str,
    ) -> sqlite3.Row | None:
        query = "SELECT * FROM chat_sessions WHERE id = ?"

        with self.db.get_connection() as conn:
            return conn.execute(query, (session_id,)).fetchone()

    def get_user_sessions(
        self,
        user_id: str,
    ) -> list[sqlite3.Row]:
        query = """
        SELECT *
        FROM chat_sessions
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """

        with self.db.get_connection() as conn:
            return conn.execute(query, (user_id,)).fetchall()

    def update_title(
        self,
        session_id: str,
        title: str,
    ) -> None:
        query = """
        UPDATE chat_sessions
        SET title = ?
        WHERE id = ?
        """

        with self.db.get_connection() as conn:
            conn.execute(query, (title, session_id))
            conn.commit()

    def update_timestamp(
        self,
        session_id: str,
        updated_at: str,
    ) -> None:
        query = """
        UPDATE chat_sessions
        SET updated_at = ?
        WHERE id = ?
        """

        with self.db.get_connection() as conn:
            conn.execute(query, (updated_at, session_id))
            conn.commit()

    def delete_session(
        self,
        session_id: str,
    ) -> None:
        query = "DELETE FROM chat_sessions WHERE id = ?"

        with self.db.get_connection() as conn:
            conn.execute(query, (session_id,))
            conn.commit()