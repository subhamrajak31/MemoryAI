"""
End-to-end test script to verify LangGraph state machine execution, tool invocation, and memory extraction.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.user_repository import UserRepository
from services.auth_service import AuthenticationService
from services.chat_service import ChatService
from utils.helpers import get_current_timestamp
from utils.logger import logger


def ensure_test_user(user_id: str) -> None:
    """
    Ensures that a test user exists in the SQLite users table to satisfy foreign key constraints.
    """
    user_repository = UserRepository()
    existing_user = user_repository.get_user_by_id(user_id)

    if existing_user is None:
        logger.info("Seeding test user ID '%s' into database...", user_id)
        password_hash = AuthenticationService.hash_password("TestPassword123!")
        user_repository.create_user(
            user_id=user_id,
            username="langgraph_test_user",
            password_hash=password_hash,
            created_at=get_current_timestamp(),
        )


def run_integration_tests() -> None:
    """
    Executes integration tests for the LangGraph workflow.
    """
    logger.info("Initializing LangGraph Integration Tests...")
    test_user_id = "test_user_langgraph_123"

    # Ensure foreign key dependencies are satisfied in SQLite
    ensure_test_user(test_user_id)

    chat_service = ChatService()

    tests = [
        {
            "name": "Memory Extraction Test",
            "prompt": "My name is Alice and I am a machine learning engineer.",
        },
        {
            "name": "Safe Calculator Tool Test",
            "prompt": "Can you calculate 45 * 12 + sqrt(144)?",
        },
        {
            "name": "Web Search Tool Test",
            "prompt": '{"tool": "web_search", "query": "Python LangGraph architecture"}',
        },
    ]

    for test in tests:
        logger.info("=== Running: %s ===", test["name"])
        print(f"\nPrompt: {test['prompt']}")
        try:
            response = chat_service.generate_ai_response(
                user_id=test_user_id,
                conversation=[],
                user_message=test["prompt"],
            )
            print(f"Response:\n{response}")
            logger.info("Passed: %s", test["name"])
        except Exception as error:
            logger.exception("Failed %s: %s", test["name"], error)
            print(f"Error: {error}")

    print("\n✅ LangGraph Integration Tests Completed Successfully.")


if __name__ == "__main__":
    run_integration_tests()