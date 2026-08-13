"""
State definition for the MemoryAI LangGraph agent graph.
"""

from __future__ import annotations

from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Maintains workflow state across all graph nodes in LangGraph.

    Attributes:
        messages: Sequence of chat messages updated via the `add_messages` reducer.
        user_id: Unique identifier of the target user for context filtering.
        session_id: Active chat session identifier.
        memories: Retrieved user long-term memory statements.
        doc_context: Retrieved document chunks from vector store.
        next_step: Optional string directive used by routing edges to guide execution.
    """

    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    session_id: str
    memories: list[str]
    doc_context: list[str]
    next_step: str | None