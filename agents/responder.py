from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


class ResponseGenerator:
    """Generates contextual support responses using memory and intent."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0.7)
        self.base_system_prompt = """You are a helpful, professional customer support agent.
Your name is Atlas. You work for TechFlow, a SaaS company that provides 
project management tools.

Your guidelines:
1. Be warm, professional, and empathetic
2. If you have past conversation history with this user, reference it naturally
   (e.g., "I see we spoke about this before..." or "Following up on your earlier issue...")
3. Provide clear, actionable solutions
4. If you cannot solve something, acknowledge it honestly
5. Keep responses concise but thorough — aim for 2-4 sentences unless more detail is needed
6. Never make up information about the user's account or billing

Current intent detected: {intent} (confidence: {confidence})
Frustration level: {frustration_level}
"""

    def generate_response(self, user_message: str, memories_context: str,
                          intent_result: dict, conversation_history: list = None) -> str:
        """Generate a response using memory context and intent classification."""
        system_prompt = self.base_system_prompt.format(
            intent=intent_result.get("intent", "general"),
            confidence=intent_result.get("confidence", 0.0),
            frustration_level=intent_result.get("frustration_level", "low")
        )

        # Add memory context to the system prompt
        if memories_context:
            system_prompt += f"\n\n{memories_context}"

        # Add intent-specific instructions
        intent = intent_result.get("intent", "general")
        system_prompt += self._get_intent_instructions(intent)

        # Build message list
        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history if available (for multi-turn)
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages to stay within context
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    from langchain_core.messages import AIMessage
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=user_message))

        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Please try again shortly. (Error: {str(e)})"

    def _get_intent_instructions(self, intent: str) -> str:
        """Get additional instructions based on detected intent."""
        instructions = {
            "billing": """
BILLING INSTRUCTIONS:
- Ask for order/invoice numbers if not provided
- Explain charges clearly
- If they need a refund, explain the process and timeline
- Never promise specific refund amounts without verification""",

            "technical": """
TECHNICAL INSTRUCTIONS:
- Ask what they were trying to do and what happened instead
- Suggest step-by-step troubleshooting
- If it sounds like a bug, acknowledge it and say you'll log it
- Ask for browser/device info if relevant""",

            "complaint": """
COMPLAINT INSTRUCTIONS:
- Lead with empathy — acknowledge their frustration first
- Don't be defensive about the product or company
- Offer a concrete next step or solution
- If they want to speak to a human, respect that immediately""",

            "account": """
ACCOUNT INSTRUCTIONS:
- For password resets, guide them to the reset flow
- Never ask for or display passwords
- Verify identity concerns before making account changes
- Be extra careful with security-related requests""",

            "general": """
GENERAL INSTRUCTIONS:
- Be friendly and welcoming
- Guide them to the right topic if their question is vague
- Offer to help with specific areas (billing, technical, account)"""
        }
        return instructions.get(intent, instructions["general"])