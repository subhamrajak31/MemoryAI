"""
Groq LLM client implementation.
"""

from __future__ import annotations

from typing import Iterator

from groq import Groq

from config.settings import (
    GROQ_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
)
from utils.logger import logger
from llm.base_llm import BaseLLM


class GroqClient(BaseLLM):
    """
    Concrete implementation of the BaseLLM interface
    using the Groq API.
    """

    def __init__(self) -> None:
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(api_key=GROQ_API_KEY)

    def generate_response( self, messages: list[dict[str, str]], ) -> str:
        """
        Generate a complete response from the Groq model.
        """
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": messages,
                    }
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )

            return response.choices[0].message.content or ""

        except Exception:
            logger.exception(
                "Failed to generate response from Groq."
            )
            raise

    def stream_response(
    self,
    messages: list[dict[str, str]],
    ):
        """
        Stream the response from Groq.
        """
        try:
            stream = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=messages,
                            temperature=TEMPERATURE,
                            max_tokens=MAX_TOKENS,
                )
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content

                if delta:
                    yield delta

        except Exception:
            logger.exception(
                "Failed while streaming from Groq."
            )
            raise
    