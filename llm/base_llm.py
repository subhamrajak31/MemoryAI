"""
Abstract base interface for all LLM providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


from typing import Iterator

Message = dict[str, str]

class BaseLLM(ABC):

    @abstractmethod
    def generate_response(
        self,
        messages: list[Message],
    ) -> str:
        ...

    @abstractmethod
    def stream_response(
        self,
        messages: list[Message],
    ) -> Iterator[str]:
        ...