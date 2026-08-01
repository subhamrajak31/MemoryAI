"""
Gemini LLM client implementation.
"""

from __future__ import annotations

from google import genai

from config.settings import (
    GEMINI_API_KEY,
    MODEL_NAME,
)
from llm.base_llm import BaseLLM


class GeminiClient(BaseLLM):
    """
    Gemini implementation of BaseLLM.
    """

    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key not found.")

        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_response(self, messages: list[dict]) -> str:
        """
        Generate a response from Gemini.
        """

        prompt = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )

        response = self.client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        return response.text

    def stream_response(self, messages: list[dict]):
        """
        Stream a response from Gemini.
        """

        prompt = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )

        stream = self.client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=prompt,
        )

        for chunk in stream:
            if chunk.text:
                yield chunk.text