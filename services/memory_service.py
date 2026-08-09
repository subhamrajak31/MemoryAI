"""
Business logic for long-term memory management.
"""

from __future__ import annotations

import re

from database.memory_repository import MemoryRepository
from memory.memory_store import VectorMemoryStore
from utils.helpers import generate_uuid, get_current_timestamp
from utils.logger import logger


class MemoryService:
    """
    Handles all business logic related to long-term memory.

    This service is responsible for:
    - extracting memories
    - storing memories in SQLite and ChromaDB
    - semantically retrieving memories
    - validating candidate memories
    """

    def __init__(
        self,
        memory_repository: MemoryRepository | None = None,
        vector_memory_store: VectorMemoryStore | None = None,
    ) -> None:
        self.memory_repository = (
            memory_repository
            if memory_repository is not None
            else MemoryRepository()
        )
        self.vector_memory_store = (
            vector_memory_store
            if vector_memory_store is not None
            else VectorMemoryStore()
        )

    def extract_memories(self, message: str) -> list[str]:
        """
        Extract candidate long-term memories from a user message using pattern matching.
        """
        text = message.strip()
        memories: list[str] = []

        patterns = [
            r"my name is (.+)",
            r"i am (.+)",
            r"i'm (.+)",
            r"i live in (.+)",
            r"i study at (.+)",
            r"i work at (.+)",
            r"i work as (.+)",
            r"i like (.+)",
            r"i love (.+)",
            r"i prefer (.+)",
            r"i use (.+)",
            r"i want to (.+)",
            r"i am building (.+)",
            r"i am working on (.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                memory = match.group(0).strip()
                if memory not in memories:
                    memories.append(memory)

        return memories

    def store_memory(
        self,
        user_id: str,
        memory: str,
    ) -> bool:
        """
        Store a memory in SQLite and ChromaDB if it does not already exist.
        """
        memory = memory.strip()

        if not memory:
            return False

        if self.memory_repository.memory_exists(user_id, memory):
            return False

        memory_id = generate_uuid()
        created_at = get_current_timestamp()

        # 1. Primary relational storage in SQLite
        self.memory_repository.create_memory(
            memory_id=memory_id,
            user_id=user_id,
            memory=memory,
            created_at=created_at,
        )

        # 2. Vector indexing in ChromaDB
        try:
            self.vector_memory_store.add_memory(
                user_id=user_id,
                memory_id=memory_id,
                text=memory,
            )
        except Exception as error:
            logger.exception(
                "Failed to index memory ID %s in vector store: %s",
                memory_id,
                error,
            )

        return True

    def retrieve_memories(
        self,
        user_id: str,
        query: str | None = None,
        limit: int = 5,
    ) -> list[str]:
        """
        Retrieve memories for a user. Performs semantic vector search if query is provided,
        otherwise falls back to SQLite recency.
        """
        if query:
            try:
                semantic_memories = self.vector_memory_store.search_memories(
                    user_id=user_id,
                    query=query,
                    top_k=limit,
                )
                if semantic_memories:
                    return semantic_memories
            except Exception as error:
                logger.exception(
                    "Semantic search failed for user %s, falling back to SQLite: %s",
                    user_id,
                    error,
                )

        # Fallback to recency-ordered SQLite retrieval
        rows = self.memory_repository.get_user_memories(user_id)
        memories = [row["memory"] for row in rows]
        return memories[-limit:]

    def is_valid_memory(self, memory: str) -> bool:
        """
        Determine whether a candidate memory is suitable for long-term storage.
        """
        memory = memory.strip()

        if not memory:
            return False

        normalized = memory.casefold()

        if "?" in memory:
            return False

        ignored_phrases = {
            "hello",
            "hi",
            "hey",
            "thanks",
            "thank you",
            "okay",
            "ok",
            "bye",
            "goodbye",
        }

        if normalized.rstrip(".!") in ignored_phrases:
            return False

        temporary_phrases = (
            "i am going to ",
            "i'm going to ",
            "i am currently ",
            "i'm currently ",
            "i am doing ",
            "i'm doing ",
            "i am solving ",
            "i'm solving ",
        )

        if normalized.startswith(temporary_phrases):
            return False

        return True

    def process_memory(
        self,
        user_id: str,
        user_message: str,
    ) -> None:
        """
        Extract, validate, and store long-term memories.
        """
        memories = self.extract_memories(user_message)

        for memory in memories:
            if not self.is_valid_memory(memory):
                continue

            self.store_memory(
                user_id=user_id,
                memory=memory,
            )

    def get_all_user_memories(self, user_id: str) -> list[dict[str, str]]:
        """
        Retrieve all stored memory records for a user formatted for UI display.
        """
        rows = self.memory_repository.get_user_memories(user_id)
        return [
            {
                "id": row["id"],
                "memory": row["memory"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def delete_memory(self, user_id: str, memory_id: str) -> None:
        """
        Delete a memory record from both SQLite and ChromaDB vector store.
        """
        # 1. Delete from SQLite relational storage
        self.memory_repository.delete_memory(memory_id)

        # 2. Delete from ChromaDB vector index
        try:
            self.vector_memory_store.delete_memory(memory_id)
            logger.info("Memory ID %s purged from vector store.", memory_id)
        except Exception as error:
            logger.exception(
                "Failed to delete memory ID %s from vector store: %s",
                memory_id,
                error,
            )