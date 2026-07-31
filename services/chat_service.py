"""
Business logic for chat sessions and messages.
"""

from __future__ import annotations

from config.constants import DEFAULT_CHAT_TITLE
from database.chat_session_repository import ChatSessionRepository
from database.message_repository import MessageRepository
from utils.helpers import generate_uuid, get_current_timestamp
from services.llm_service import LLMService
from prompts.system_prompts import SYSTEM_PROMPT
from utils.message_converter import build_messages
from services.llm_service import LLMService


class ChatService:
    """
    Handles chat-related business logic.

    Responsibilities:
    - Create chat sessions.
    - Save user messages.
    """

    def __init__(self) -> None:
        self.chat_session_repository = ChatSessionRepository()
        self.message_repository = MessageRepository()
        self.llm_service = LLMService()

    def create_chat_session(
        self,
        user_id: str,
    ) -> str:
        """
        Creates a new chat session for the user.

        Args:
            user_id: User ID.

        Returns:
            Newly created chat session ID.
        """

        session_id = generate_uuid()
        timestamp = get_current_timestamp()

        self.chat_session_repository.create_session(
            session_id=session_id,
            user_id=user_id,
            title=DEFAULT_CHAT_TITLE,
            created_at=timestamp,
            updated_at=timestamp,
        )

        return session_id

    def save_user_message(
        self,
        session_id: str,
        content: str,
    ) -> None:
        """
        Saves a user message.

        Args:
            session_id: Chat session ID.
            content: User message.
        """

        self.message_repository.create_message(
            message_id=generate_uuid(),
            session_id=session_id,
            role="user",
            content=content,
            timestamp=get_current_timestamp(),
        )
    def generate_ai_response(
        self,
        conversation: list[dict[str, str]],
        user_message: str,
    ) -> str:
        """
        Generate an AI response.

        Args:
            conversation: Previous chat history.
            user_message: Latest user message.

        Returns:
            AI response.
        """

        messages = build_messages(
            system_prompt=SYSTEM_PROMPT,
            conversation=conversation,
            user_message=user_message,
        )

        return self.llm_service.generate_response(messages)

    def save_assistant_message(
        self,
        session_id: str,
        content: str,
    ) -> None:
        """
        Save an assistant response.
        """
    
        self.message_repository.create_message(
            message_id=generate_uuid(),
            session_id=session_id,
            role="assistant",
            content=content,
            timestamp=get_current_timestamp(),
        )