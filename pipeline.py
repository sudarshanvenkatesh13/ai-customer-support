from agents.memory import MemoryManager
from agents.intent import IntentClassifier
from agents.responder import ResponseGenerator
from agents.escalation import EscalationManager
from config import Config


class SupportPipeline:
    """Main pipeline that orchestrates memory, intent, response, and escalation."""

    def __init__(self):
        Config.validate()
        self.memory = MemoryManager(persist_directory=Config.CHROMA_PERSIST_DIR)
        self.intent_classifier = IntentClassifier(model=Config.LLM_MODEL)
        self.responder = ResponseGenerator(model=Config.LLM_MODEL)
        self.escalation_manager = EscalationManager()
        self.conversation_counts = {}  # tracks turns per user

    def process_message(self, user_id: str, user_message: str,
                        conversation_history: list = None) -> dict:
        """Process a user message through the full pipeline.
        
        Flow: Memory Retrieval → Intent Classification → Response Generation 
              → Escalation Check → Store to Memory
        """
        # Track conversation turns
        self.conversation_counts[user_id] = self.conversation_counts.get(user_id, 0) + 1
        turn_count = self.conversation_counts[user_id]

        # Step 1: Retrieve relevant memories
        memories = self.memory.retrieve_memories(
            query=user_message,
            user_id=user_id,
            n_results=Config.MEMORY_RESULTS_COUNT
        )
        memories_context = self.memory.format_memories_for_prompt(memories)

        # Step 2: Classify intent
        intent_result = self.intent_classifier.classify(user_message)

        # Step 3: Generate response
        response = self.responder.generate_response(
            user_message=user_message,
            memories_context=memories_context,
            intent_result=intent_result,
            conversation_history=conversation_history
        )

        # Step 4: Check for escalation
        escalation_result = self.escalation_manager.check_escalation(
            user_id=user_id,
            user_message=user_message,
            intent_result=intent_result,
            conversation_count=turn_count
        )

        # Step 5: Store conversation in memory
        self.memory.store_conversation(
            user_id=user_id,
            user_message=user_message,
            assistant_response=response,
            intent=intent_result.get("intent", "general")
        )

        # Build escalation ticket if needed
        escalation_ticket = None
        if escalation_result["should_escalate"]:
            escalation_ticket = self.escalation_manager.format_escalation_ticket(
                escalation_result=escalation_result,
                user_message=user_message,
                conversation_summary=f"Turn {turn_count}: User asked about {intent_result.get('intent', 'general')}"
            )

        return {
            "response": response,
            "intent": intent_result,
            "escalation": escalation_result,
            "escalation_ticket": escalation_ticket,
            "memories_used": len(memories),
            "turn_count": turn_count
        }

    def reset_conversation(self, user_id: str):
        """Reset conversation turn count for a user."""
        self.conversation_counts[user_id] = 0