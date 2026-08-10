from utils.message_converter import build_messages

messages = build_messages(
    system_prompt="You are MemoryAI.",
    conversation=[],
    user_message="Summarize my document.",
    memories=["User prefers concise summaries."],
    doc_context=["Chunk 1 content from PDF file..."],
)

for msg in messages:
    print(f"[{msg['role'].upper()}]\n{msg['content']}\n")