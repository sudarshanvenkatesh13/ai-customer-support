import chromadb
from chromadb.config import Settings
from datetime import datetime
import uuid
import json


class MemoryManager:
    """Manages long-term conversation memory using ChromaDB."""

    def __init__(self, persist_directory: str = "./chroma_data"):
        """Initialize ChromaDB client with persistent storage."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="conversation_memory",
            metadata={"description": "Stores customer support conversations"}
        )
    
    def store_conversation(self, user_id: str, user_message: str, 
                           assistant_response: str, intent: str = "general",
                           metadata: dict = None):
        """Store a conversation turn in memory."""
        conversation_text = f"User: {user_message}\nAssistant: {assistant_response}"

        doc_metadata = {
            "user_id": user_id,
            "intent": intent,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message[:500],
            "assistant_response": assistant_response[:500]
        }

        if metadata:
            doc_metadata.update(metadata)

        self.collection.add(
            documents=[conversation_text],
            metadatas=[doc_metadata],
            ids=[str(uuid.uuid4())]
        )
    
    def retrieve_memories(self, query: str, user_id: str = None, 
                          n_results: int = 3):
        """Retrieve relevant past conversations for context."""
        where_filter = {"user_id": user_id} if user_id else None

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
        except Exception:
            return []

        memories = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                memory = {
                    "conversation": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "relevance_score": results["distances"][0][i] if results["distances"] else None
                }
                memories.append(memory)

        return memories
    
    def format_memories_for_prompt(self, memories: list) -> str:
        """Format retrieved memories into a string for the LLM prompt."""
        if not memories:
            return "No previous conversation history found for this user."

        formatted = "=== Relevant Past Conversations ===\n\n"
        for i, memory in enumerate(memories, 1):
            metadata = memory.get("metadata", {})
            timestamp = metadata.get("timestamp", "Unknown time")
            intent = metadata.get("intent", "Unknown")
            formatted += f"--- Memory {i} (Intent: {intent}, Time: {timestamp}) ---\n"
            formatted += f"{memory['conversation']}\n\n"

        return formatted
    
    def get_user_history(self, user_id: str, limit: int = 10):
        """Get recent conversation history for a specific user."""
        try:
            results = self.collection.get(
                where={"user_id": user_id},
                limit=limit
            )
        except Exception:
            return []

        history = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"]):
                history.append({
                    "conversation": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                })

        return history