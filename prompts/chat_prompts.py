"""
Prompt builders for normal chat interactions.
"""

from prompts.system_prompts import SYSTEM_PROMPT


def build_chat_messages(user_message: str) -> list[dict[str, str]]:
    """
    Build messages for a standard chat request.

    Args:
        user_message: User's input.

    Returns:
        Message list formatted for the LLM.
    """
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]