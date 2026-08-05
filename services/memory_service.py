"""
Business logic for long-term memory management.
"""

from __future__ import annotations

from database.memory_repository import MemoryRepository
import re
from utils.helpers import get_current_timestamp


class MemoryService:
    """
    Handles all business logic related to long-term memory.

    This service is responsible for:
    - extracting memories
    - storing memories
    - retrieving memories
    - updating memories
    - deleting memories
    - injecting memories into prompts

    SQL operations are delegated to MemoryRepository.
    """

    def __init__(
        self,
        memory_repository: MemoryRepository | None = None,
    ) -> None:
        self.memory_repository = (
            memory_repository
            if memory_repository is not None
            else MemoryRepository()
        )

    def extract_memories(self, message: str) -> list[str]:
        """
        Extract candidate long-term memories from a user message.

        This implementation uses deterministic pattern matching.
        Database storage is handled separately.
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
        Store a memory if it does not already exist.
    
        Returns True if stored, False if skipped.
        """
    
        memory = memory.strip()
    
        if not memory:
            return False
    
        existing_memories = self.memory_repository.get_user_memories(user_id)
    
        normalized_memory = memory.casefold()
    
        for existing in existing_memories:
            if existing["memory"].casefold() == normalized_memory:
                return False
    
        self.memory_repository.create_memory(
            user_id=user_id,
            memory=memory,
            created_at=get_current_timestamp(),
        )
    
        return True

    def retrieve_memories(self, *args, **kwargs):
        """Retrieve memories for a user."""
        raise NotImplementedError

    def inject_memories(self, *args, **kwargs):
        """Prepare memories for prompt injection."""
        raise NotImplementedError

    def update_memory(self, *args, **kwargs):
        """Update an existing memory."""
        raise NotImplementedError

    def delete_memory(self, *args, **kwargs):
        """Delete a stored memory."""
        raise NotImplementedError