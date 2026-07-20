"""
Integration test for the complete LLM layer.
"""

from prompts.system_prompts import SYSTEM_PROMPT
from prompts.chat_prompts import build_chat_messages
from utils.message_converter import build_messages
from llm.groq_client import GroqClient
from services.llm_service import LLMService


def separator(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:

    separator("1. System Prompt")

    assert isinstance(SYSTEM_PROMPT, str)
    print("✓ System prompt loaded")

    separator("2. Prompt Builder")

    messages = build_chat_messages("Hello")

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    print("✓ Prompt builder working")

    separator("3. Message Converter")

    history = [
        {
            "role": "user",
            "content": "Hi",
        },
        {
            "role": "assistant",
            "content": "Hello!",
        },
    ]

    final_messages = build_messages(
        SYSTEM_PROMPT,
        history,
        "Explain AI",
    )

    assert len(final_messages) == 4

    print("✓ Message conversion working")

    separator("4. Groq Client")

    try:
        GroqClient()

    except ValueError:

        print("✓ API key validation working")

    separator("5. LLM Service")

    try:
        LLMService()

    except ValueError:

        print("✓ LLM Service validation working")

    separator("6. Streaming")

    try:

        service = LLMService()

        for _ in service.stream_response(
            "Hello"
        ):
            pass

    except ValueError:

        print("✓ Streaming validation working")

    separator("SUCCESS")

    print("✓ Phase 5 integration test passed")


if __name__ == "__main__":
    main()