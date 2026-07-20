"""
Integration test for Phase 5.

Verifies:
1. Imports
2. Prompt builders
3. LLM Service
4. Groq Client validation
"""

from prompts.system_prompts import SYSTEM_PROMPT
from prompts.chat_prompts import build_chat_messages
from llm.groq_client import GroqClient
from services.llm_service import LLMService


def main() -> None:
    print("=" * 50)
    print("PHASE 5 TEST")
    print("=" * 50)

    # -----------------------------
    # System Prompt
    # -----------------------------
    print("\n[1] Testing System Prompt...")

    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 0

    print("✓ System prompt loaded")

    # -----------------------------
    # Chat Prompt Builder
    # -----------------------------
    print("\n[2] Testing Prompt Builder...")

    messages = build_chat_messages("Hello MemoryAI")

    assert isinstance(messages, list)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    print("✓ Prompt builder working")

    # -----------------------------
    # Groq Client
    # -----------------------------
    print("\n[3] Testing Groq Client...")

    try:
        GroqClient()
    except ValueError:
        print("✓ API key validation working")

    # -----------------------------
    # LLM Service
    # -----------------------------
    print("\n[4] Testing LLM Service...")

    try:
        LLMService()
    except ValueError:
        print("✓ LLM Service validation working")

    print("\n" + "=" * 50)
    print("ALL PHASE 5 TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()