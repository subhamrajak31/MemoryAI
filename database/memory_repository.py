"""
Repository for long-term memory operations.
"""

from __future__ import annotations

import sqlite3

from database.base_repository import BaseRepository


class MemoryRepository(BaseRepository):
    """Handles CRUD operations for user memories."""

    def create_memory(
        self,
        memory_id: str,
        user_id: str,
        memory: str,
        created_at: str,
    ) -> None:
        query = """
        INSERT INTO memory
        (id, user_id, memory, created_at)
        VALUES (?, ?, ?, ?)
        """

        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    memory_id,
                    user_id,
                    memory,
                    created_at,
                ),
            )
            conn.commit()

    def get_user_memories(
        self,
        user_id: str,
    ) -> list[sqlite3.Row]:
        query = """
        SELECT *
        FROM memory
        WHERE user_id = ?
        ORDER BY created_at ASC
        """

        with self.db.get_connection() as conn:
            return conn.execute(query, (user_id,)).fetchall()

    def delete_memory(
        self,
        memory_id: str,
    ) -> None:
        query = """
        DELETE FROM memory
        WHERE id = ?
        """

        with self.db.get_connection() as conn:
            conn.execute(query, (memory_id,))
            conn.commit()

    def memory_exists(
        self,
        user_id: str,
        memory: str,
    ) -> bool:
        query = """
            SELECT 1
            FROM memory
            WHERE user_id = ?
              AND LOWER(memory) = LOWER(?)
            LIMIT 1
        """
    
        with self.db.get_connection() as conn:
            row = conn.execute(
                query,
                (
                    user_id,
                    memory,
                ),
            ).fetchone()
    
        return row is not None