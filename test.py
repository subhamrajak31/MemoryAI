from utils.message_converter import build_messages

# messages = build_messages(
#     system_prompt="You are MemoryAI.",
#     conversation=[],
#     user_message="What should I learn?",
#     memories=[
#         "User prefers Python.",
#         "User is building MemoryAI.",
#     ],
# )

messages = build_messages(
    "You are MemoryAI.",
    [],
    "Hello",
)

for message in messages:
    print(message)

