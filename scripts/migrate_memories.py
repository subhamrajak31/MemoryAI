"""
Migration utility to backfill historical SQLite memories into ChromaDB vector store.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on Python module search path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.memory_repository import MemoryRepository
from database.user_repository import UserRepository
from memory.memory_store import VectorMemoryStore
from utils.logger import logger


def migrate_memories_to_vector_store() -> None:
    """
    Reads all memories from SQLite and indexes missing ones into ChromaDB.
    """
    user_repository = UserRepository()
    memory_repository = MemoryRepository()
    vector_store = VectorMemoryStore()

    users = user_repository.get_all_users()
    logger.info("Starting memory migration for %d user(s)...", len(users))

    total_processed = 0
    total_successful = 0

    for user in users:
        user_id = user["id"]
        username = user["username"]
        memories = memory_repository.get_user_memories(user_id)

        logger.info("Processing %d memories for user '%s'...", len(memories), username)

        for mem_row in memories:
            total_processed += 1
            memory_id = mem_row["id"]
            memory_text = mem_row["memory"]

            try:
                vector_store.add_memory(
                    user_id=user_id,
                    memory_id=memory_id,
                    text=memory_text,
                )
                total_successful += 1
            except Exception as error:
                logger.exception(
                    "Failed to migrate memory ID %s for user %s: %s",
                    memory_id,
                    user_id,
                    error,
                )

    logger.info(
        "Memory migration complete. Successfully indexed %d / %d memories.",
        total_successful,
        total_processed,
    )


if __name__ == "__main__":
    migrate_memories_to_vector_store()