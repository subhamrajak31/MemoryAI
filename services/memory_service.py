"""
Business logic for long-term memory management.
"""

from __future__ import annotations

from database.memory_repository import MemoryRepository
import re
from utils.helpers import generate_uuid, get_current_timestamp


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

        Returns:
            True if the memory was stored, otherwise False.
        """

        memory = memory.strip()

        if not memory:
            return False

        if self.memory_repository.memory_exists(user_id, memory):
            return False

        memory_id = generate_uuid()
        created_at = get_current_timestamp()

        self.memory_repository.create_memory(
            memory_id=memory_id,
            user_id=user_id,
            memory=memory,
            created_at=created_at,
        )

        return True

    def retrieve_memories(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[str]:
        """
        Retrieve the most recent memories for a user.
        """

        rows = self.memory_repository.get_user_memories(user_id)

        memories = [
            row["memory"]
            for row in rows
        ]

        return memories[-limit:]
    
    def inject_memories(self, *args, **kwargs):
        """Prepare memories for prompt injection."""
        raise NotImplementedError

    def update_memory(self, *args, **kwargs):
        """Update an existing memory."""
        raise NotImplementedError

    def delete_memory(self, *args, **kwargs):
        """Delete a stored memory."""
        raise NotImplementedError

    def is_valid_memory(self, memory: str) -> bool:
        """
        Determine whether a candidate memory is suitable
        for long-term storage.
        """

        memory = memory.strip()

        if not memory:
            return False

        normalized = memory.casefold()

        # Ignore questions.
        if "?" in memory:
            return False

        # Ignore common conversational messages.
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

        # Ignore obvious temporary activities.
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