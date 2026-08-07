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
from services.memory_service import MemoryService


class ChatService:
    """
    Handles chat-related business logic.

    Responsibilities:
    - Create chat sessions.
    - Save user messages.
    """

    def __init__(
        self,
        chat_session_repository: ChatSessionRepository | None = None,
        message_repository: MessageRepository | None = None,
        llm_service: LLMService | None = None,
        memory_service: MemoryService | None = None,
    ) -> None:

        self.chat_session_repository = (
            chat_session_repository
            if chat_session_repository is not None
            else ChatSessionRepository()
        )

        self.message_repository = (
            message_repository
            if message_repository is not None
            else MessageRepository()
        )

        self.llm_service = (
            llm_service
            if llm_service is not None
            else LLMService()
        )

        self.memory_service = (
            memory_service
            if memory_service is not None
            else MemoryService()
        )

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
        user_id,
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

        memories = self.memory_service.retrieve_memories(user_id)

        messages = build_messages(
            system_prompt=SYSTEM_PROMPT,
            conversation=conversation,
            user_message=user_message,
            memories=memories,
        )

        return self.llm_service.generate_response(messages)
    
    def stream_ai_response(
        self,
        user_id : str,
        conversation: list[dict[str, str]],
        user_message: str,
    ):
        """
        Stream an AI response.
        """
    
        memories = self.memory_service.retrieve_memories(user_id)

        messages = build_messages(
            system_prompt=SYSTEM_PROMPT,
            conversation=conversation,
            user_message=user_message,
            memories=memories,
        )

        yield from self.llm_service.stream_response(messages)

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

    def get_user_sessions(
        self,
        user_id: str,
    ) -> list:
        """
        Returns all chat sessions for a user.

        Args:
            user_id: User ID.

        Returns:
            List of chat sessions.
        """

        return self.chat_session_repository.get_user_sessions(user_id)


    def get_session_messages(
        self,
        session_id: str,
    ) -> list:
        """
        Returns all messages for a chat session.

        Args:
            session_id: Chat session ID.

        Returns:
            List of messages.
        """

        return self.message_repository.get_messages(session_id)
    
    def update_chat_title(
        self,
        session_id: str,
        title: str,
    ) -> None:
        """
        Updates a chat session title.
        """

        self.chat_session_repository.update_title(
            session_id=session_id,
            title=title,
        )