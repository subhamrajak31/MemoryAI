"""
Integration test for the MemoryAI database layer.
"""

from database.user_repository import UserRepository
from database.chat_session_repository import ChatSessionRepository
from database.message_repository import MessageRepository
from database.memory_repository import MemoryRepository
from database.document_repository import DocumentRepository

from utils.helpers import (
    generate_uuid,
    get_current_timestamp,
)


def main() -> None:
    # Initialize repositories
    user_repo = UserRepository()
    chat_repo = ChatSessionRepository()
    message_repo = MessageRepository()
    memory_repo = MemoryRepository()
    document_repo = DocumentRepository()

    timestamp = get_current_timestamp()

    # -------------------------
    # Create User
    # -------------------------
    user_id = generate_uuid()

    user_repo.create_user(
        user_id=user_id,
        username=f"test_user_{user_id[:8]}",
        password_hash="dummy_password_hash",
        created_at=timestamp,
    )

    print("✓ User created")

    # -------------------------
    # Create Chat Session
    # -------------------------
    session_id = generate_uuid()

    chat_repo.create_session(
        session_id=session_id,
        user_id=user_id,
        title="Integration Test Chat",
        created_at=timestamp,
        updated_at=timestamp,
    )

    print("✓ Chat session created")

    # -------------------------
    # Insert Messages
    # -------------------------
    messages = [
        ("user", "Hello MemoryAI!"),
        ("assistant", "Hello! How can I help you today?"),
        ("user", "This is an integration test."),
    ]

    for role, content in messages:
        message_repo.create_message(
            message_id=generate_uuid(),
            session_id=session_id,
            role=role,
            content=content,
            timestamp=get_current_timestamp(),
        )

    print(f"✓ {len(messages)} messages stored")

    # -------------------------
    # Create Memory
    # -------------------------
    memory_repo.create_memory(
        memory_id=generate_uuid(),
        user_id=user_id,
        memory="User likes AI engineering projects.",
        created_at=get_current_timestamp(),
    )

    print("✓ Memory stored")

    # -------------------------
    # Create Document
    # -------------------------
    document_repo.create_document(
        document_id=generate_uuid(),
        user_id=user_id,
        filename="sample.pdf",
        file_path="data/uploads/sample.pdf",
        uploaded_at=get_current_timestamp(),
    )

    print("✓ Document stored")

    # -------------------------
    # Read Back Data
    # -------------------------
    user = user_repo.get_user_by_id(user_id)
    sessions = chat_repo.get_user_sessions(user_id)
    retrieved_messages = message_repo.get_messages(session_id)
    memories = memory_repo.get_user_memories(user_id)
    documents = document_repo.get_user_documents(user_id)

    print("\n========== DATABASE SUMMARY ==========")
    print(f"Username          : {user['username']}")
    print(f"Chat Sessions     : {len(sessions)}")
    print(f"Messages          : {len(retrieved_messages)}")
    print(f"Memories          : {len(memories)}")
    print(f"Documents         : {len(documents)}")
    print("======================================")

    print("\n✅ Database integration test passed successfully!")


if __name__ == "__main__":
    main()