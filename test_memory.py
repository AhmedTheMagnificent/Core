from dotenv import load_dotenv
from src.memory import save_to_memory, recall_memory

# Load your API keys
load_dotenv()

print("--- 1. TEACHING CORE ---")
save_to_memory("My favorite food is Pizza.", source="user")
save_to_memory("I live in New York City.", source="user")
save_to_memory("The secret password is 'Blue77'.", source="user")

print("\n--- 2. ASKING CORE ---")
# We ask a question. Note: We don't ask for the exact sentence.
# We ask a related question to prove the AI understands meaning, not just keywords.
query = "Where is my home?"
answers = recall_memory(query)

print(f"Question: {query}")
print(f"Found Memories: {answers}")