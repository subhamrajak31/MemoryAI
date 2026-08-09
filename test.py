from google import genai
from config.settings import GEMINI_API_KEY
from memory.memory_store import VectorMemoryStore

# 1. List available embedding models on your API key
client = genai.Client(api_key=GEMINI_API_KEY)
print("Available models on key:")
for m in client.models.list():
    if "embed" in m.name.lower():
        print(" -", m.name)

# 2. Test VectorMemoryStore embedding generation
store = VectorMemoryStore()
vector = store._generate_embedding("Testing Gemini embedding generation")
print("Successfully generated vector of length:", len(vector))