"""
Utilities for converting conversation history
into the format expected by the LLM.
"""

from __future__ import annotations


def build_messages(
    system_prompt: str,
    conversation: list[dict[str, str]],
    user_message: str,
) -> list[dict[str, str]]:
    """
    Build the final message list for the LLM.

    Args:
        system_prompt:
            Global system instructions.

        conversation:
            Previous conversation history.

        user_message:
            Latest user message.

    Returns:
            Messages formatted for the LLM.
    """

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    messages.extend(conversation)

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    return messages