"""
LangGraph nodes and state graph builder for MemoryAI agentic workflow.
"""

from __future__ import annotations

import json
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from config.settings import MODEL_NAME
from langgraph.nodes.state import AgentState
from services.llm_service import LLMService
from services.memory_service import MemoryService
from services.rag_service import RAGService
from tools.calculator import calculate
from tools.websearch import web_search
from utils.logger import logger


def memory_retrieval_node(state: AgentState) -> dict:
    """
    Retrieves relevant user memories and document context chunks.
    """
    user_id = state.get("user_id", "")
    messages = state.get("messages", [])

    last_user_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = str(msg.content)
            break

    memory_service = MemoryService()
    rag_service = RAGService()

    memories = memory_service.retrieve_memories(
        user_id=user_id,
        query=last_user_msg,
        limit=5,
    )

    doc_context = rag_service.retrieve_context(
        user_id=user_id,
        query=last_user_msg,
        top_k=4,
    )

    return {
        "memories": memories,
        "doc_context": doc_context,
    }


def agent_node(state: AgentState) -> dict:
    """
    Evaluates current conversation context and generates standard AI response or tool calls.
    """
    user_id = state.get("user_id", "")
    messages = state.get("messages", [])
    memories = state.get("memories", [])
    doc_context = state.get("doc_context", [])

    # Process and store candidate memories from the latest user message
    last_user_msg = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_msg = str(msg.content)
            break

    if last_user_msg:
        memory_service = MemoryService()
        memory_service.process_memory(user_id=user_id, user_message=last_user_msg)

    system_prompt = (
        "You are MemoryAI, an intelligent assistant equipped with long-term memory, "
        "document search capabilities, and web tools (web_search, calculate).\n"
        "If you need to search the web or perform calculations, output a JSON tool call block exactly formatted as:\n"
        '{"tool": "web_search", "query": "<search query>"}\n'
        'or\n{"tool": "calculate", "expression": "<math expression>"}\n'
        "Otherwise, answer the user query directly."
    )

    formatted_messages = [{"role": "system", "content": system_prompt}]

    if memories:
        formatted_messages.append({
            "role": "system",
            "content": "User Memories:\n" + "\n".join(f"- {m}" for m in memories),
        })

    if doc_context:
        formatted_messages.append({
            "role": "system",
            "content": "Document Context:\n" + "\n".join(doc_context),
        })

    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        formatted_messages.append({"role": role, "content": str(msg.content)})

    llm_service = LLMService()
    raw_response = llm_service.generate_response(formatted_messages)

    return {
        "messages": [AIMessage(content=raw_response)],
    }


def tool_execution_node(state: AgentState) -> dict:
    """
    Parses and executes tool call requests emitted by the agent node.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_ai_message = messages[-1]
    content = str(last_ai_message.content).strip()

    tool_result = ""
    try:
        data = json.loads(content)
        tool_name = data.get("tool")

        if tool_name == "web_search":
            query = data.get("query", "")
            tool_result = f"Web Search Result:\n{web_search(query)}"
        elif tool_name == "calculate":
            expr = data.get("expression", "")
            tool_result = f"Calculation Result:\n{calculate(expr)}"
        else:
            tool_result = f"Unknown tool specified: {tool_name}"
    except Exception as exc:
        logger.warning("Failed to parse tool JSON or execute tool: %s", exc)
        tool_result = f"Tool Execution Error: {exc}"

    return {
        "messages": [SystemMessage(content=tool_result)],
    }


def route_agent_output(state: AgentState) -> Literal["tools", "__end__"]:
    """
    Conditional router edge checking if agent requested tool execution.
    """
    messages = state.get("messages", [])
    if not messages:
        return END

    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        content = str(last_message.content).strip()
        if content.startswith("{") and '"tool":' in content:
            return "tools"

    return END


def create_agent_graph() -> CompiledStateGraph:
    """
    Builds and compiles the MemoryAI LangGraph workflow state machine.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("memory_retrieval", memory_retrieval_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_execution_node)

    # Set Graph Edges
    workflow.add_edge(START, "memory_retrieval")
    workflow.add_edge("memory_retrieval", "agent")

    workflow.add_conditional_edges(
        "agent",
        route_agent_output,
        {
            "tools": "tools",
            END: END,
        },
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()