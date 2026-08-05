from services.memory_service import MemoryService

service = MemoryService()

user_id = "test-user"

print(service.retrieve_memories(user_id))