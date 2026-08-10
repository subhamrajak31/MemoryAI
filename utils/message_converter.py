"""
Utilities for converting conversation history
into the format expected by the LLM.
"""

from __future__ import annotations


def build_messages(
    system_prompt: str,
    conversation: list[dict[str, str]],
    user_message: str,
    memories: list[str] | None = None,
    doc_context: list[str] | None = None,
) -> list[dict[str, str]]:
    """
    Build the final message list for the LLM.

    Args:
        system_prompt: Global system instructions.
        conversation: Previous conversation history.
        user_message: Latest user message.
        memories: Long-term memories associated with the user.
        doc_context: Context chunks retrieved from uploaded documents.

    Returns:
        Messages formatted for the LLM.
    """
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    # Inject Long-Term Memories
    if memories:
        memory_context = (
            "Long-term memory about the user:\n"
            + "\n".join(f"- {memory}" for memory in memories)
        )
        messages.append(
            {
                "role": "system",
                "content": memory_context,
            }
        )

    # Inject RAG Document Context
    if doc_context:
        rag_context = (
            "Relevant document context retrieved for this query:\n"
            + "\n".join(
                f"--- Chunk {i + 1} ---\n{chunk}"
                for i, chunk in enumerate(doc_context)
            )
        )
        messages.append(
            {
                "role": "system",
                "content": rag_context,
            }
        )

    messages.extend(conversation)

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    return messages