"""
Business logic for chat sessions, messages, and LangGraph agent workflow execution.
"""

from __future__ import annotations

from typing import Iterator

from langchain_core.messages import AIMessage, HumanMessage

from config.constants import DEFAULT_CHAT_TITLE
from database.chat_session_repository import ChatSessionRepository
from database.message_repository import MessageRepository
from langgraph.nodes.graph import create_agent_graph
from services.llm_service import LLMService
from services.memory_service import MemoryService
from services.rag_service import RAGService
from utils.helpers import generate_uuid, get_current_timestamp
from utils.logger import logger


class ChatService:
    """
    Handles chat-related business logic and agent workflow orchestration via LangGraph.
    """

    def __init__(
        self,
        chat_session_repository: ChatSessionRepository | None = None,
        message_repository: MessageRepository | None = None,
        llm_service: LLMService | None = None,
        memory_service: MemoryService | None = None,
        rag_service: RAGService | None = None,
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

        self.rag_service = (
            rag_service
            if rag_service is not None
            else RAGService()
        )

        # Initialize the compiled LangGraph workflow state graph
        self.agent_graph = create_agent_graph()

    def create_chat_session(
        self,
        user_id: str,
    ) -> str:
        """
        Creates a new chat session for a user.
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
        Persists a user message in the database repository.
        """
        self.message_repository.create_message(
            message_id=generate_uuid(),
            session_id=session_id,
            role="user",
            content=content,
            timestamp=get_current_timestamp(),
        )

    def _prepare_graph_messages(
        self,
        conversation: list[dict[str, str]],
        user_message: str,
    ) -> list[HumanMessage | AIMessage]:
        """
        Converts dictionary conversation history into LangChain message objects.
        """
        messages: list[HumanMessage | AIMessage] = []

        for msg in conversation:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=user_message))
        return messages

    def generate_ai_response(
        self,
        user_id: str,
        conversation: list[dict[str, str]],
        user_message: str,
    ) -> str:
        """
        Generates an AI response by executing the LangGraph agent state machine.
        """
        messages = self._prepare_graph_messages(conversation, user_message)

        initial_state = {
            "messages": messages,
            "user_id": user_id,
            "session_id": "",
            "memories": [],
            "doc_context": [],
            "next_step": None,
        }

        try:
            final_state = self.agent_graph.invoke(initial_state)
            last_message = final_state["messages"][-1]
            return str(last_message.content)
        except Exception as error:
            logger.exception("Error executing LangGraph workflow: %s", error)
            return f"Error processing request: {error}"

    def stream_ai_response(
        self,
        user_id: str,
        conversation: list[dict[str, str]],
        user_message: str,
    ) -> Iterator[str]:
        """
        Executes the LangGraph agent workflow and streams response tokens to Streamlit UI.
        """
        response_text = self.generate_ai_response(
            user_id=user_id,
            conversation=conversation,
            user_message=user_message,
        )

        # Stream chunked response for UI generator compatibility
        words = response_text.split(" ")
        for idx, word in enumerate(words):
            yield word + (" " if idx < len(words) - 1 else "")

    def save_assistant_message(
        self,
        session_id: str,
        content: str,
    ) -> None:
        """
        Persists an assistant response message in the database repository.
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
        Retrieves all chat sessions for a specific user.
        """
        return self.chat_session_repository.get_user_sessions(user_id)

    def get_session_messages(
        self,
        session_id: str,
    ) -> list:
        """
        Retrieves all messages for a specific session.
        """
        return self.message_repository.get_messages(session_id)

    def update_chat_title(
        self,
        session_id: str,
        title: str,
    ) -> None:
        """
        Updates the title of a chat session.
        """
        self.chat_session_repository.update_title(
            session_id=session_id,
            title=title,
        )