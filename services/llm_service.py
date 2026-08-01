"""
Service layer for interacting with language models.
"""

from __future__ import annotations

from typing import Iterator

from llm.base_llm import BaseLLM
from llm.gemini_client import GeminiClient


class LLMService:
    """
    Provides a high-level interface for LLM interactions.
    """

    def __init__(self, llm: BaseLLM | None = None) -> None:
        """
        Initialize the service with an LLM implementation.

        Args:
            llm: Optional LLM implementation. If not provided,
                 GeminiClient is used.
        """
        self.llm = llm or GeminiClient()

    def generate_response(
      self,
      messages: list[dict[str, str]],
    )-> str:
      """
      Generate a response from prepared chat messages.
      """
      return self.llm.generate_response(messages)

    def stream_response(
        self,
        messages: list[dict[str, str]],
    ) -> Iterator[str]:
        """
        Stream a response from prepared chat messages.
        """
        yield from self.llm.stream_response(messages)