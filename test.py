from services.memory_service import MemoryService

service = MemoryService()

user_id = "test-user"

print(
    service.store_memory(
        user_id,
        "I prefer Python",
    )
)

print(
    service.store_memory(
        user_id,
        "I prefer Python",
    )
)