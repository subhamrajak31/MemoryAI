"""
Service layer for interacting with language models.
"""

from __future__ import annotations

from typing import Iterator

from llm.base_llm import BaseLLM
from llm.groq_client import GroqClient
from prompts.chat_prompts import build_chat_messages


class LLMService:
    """
    Provides a high-level interface for LLM interactions.
    """

    def __init__(self, llm: BaseLLM | None = None) -> None:
        """
        Initialize the service with an LLM implementation.

        Args:
            llm: Optional LLM implementation. If not provided,
                 GroqClient is used.
        """
        self.llm = llm or GroqClient()

    def generate_response(self, user_message: str) -> str:
        """
        Generate a response for a user message.
        """
        messages = build_chat_messages(user_message)

        return self.llm.generate_response(messages)

    def stream_response(
        self,
        user_message: str,
    ) -> Iterator[str]:
        """
        Stream a response for a user message.
        """
        messages = build_chat_messages(user_message)

        yield from self.llm.stream_response(messages)