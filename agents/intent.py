from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json


class IntentClassifier:
    """Classifies user messages into support intents using LLM."""

    VALID_INTENTS = [
        "billing",        # Payment issues, charges, refunds, subscriptions
        "technical",      # Bugs, errors, how-to questions, feature usage
        "complaint",      # Frustration, dissatisfaction, escalation requests
        "account",        # Login, password, profile, settings
        "general"         # Greetings, general questions, off-topic
    ]

    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.system_prompt = """You are an intent classifier for a customer support system.
Analyze the user's message and classify it into exactly ONE intent.

Valid intents:
- billing: Payment issues, charges, refunds, invoices, subscription problems
- technical: Bugs, errors, feature questions, how-to, product not working
- complaint: User is frustrated, angry, wants to escalate, dissatisfied with service
- account: Login issues, password reset, profile updates, account settings
- general: Greetings, general questions, anything that doesn't fit above

Also assess:
- confidence: How confident you are (0.0 to 1.0)
- frustration_level: How frustrated the user seems (low, medium, high)
- needs_escalation: Whether this should be escalated to a human (true/false)
  Set to true if: user explicitly asks for a human, frustration is high, 
  or the issue seems too complex for automated support.

Respond ONLY with valid JSON, no other text:
{
    "intent": "one of the valid intents",
    "confidence": 0.95,
    "frustration_level": "low",
    "needs_escalation": false,
    "reasoning": "Brief explanation of why this intent was chosen"
}"""

    def classify(self, user_message: str) -> dict:
        """Classify a user message into an intent."""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Classify this message:\n\n{user_message}")
        ]

        try:
            response = self.llm.invoke(messages)
            result = json.loads(response.content)

            # Validate the intent
            if result.get("intent") not in self.VALID_INTENTS:
                result["intent"] = "general"
                result["confidence"] = 0.5

            return result

        except (json.JSONDecodeError, Exception) as e:
            return {
                "intent": "general",
                "confidence": 0.0,
                "frustration_level": "low",
                "needs_escalation": False,
                "reasoning": f"Classification failed: {str(e)}"
            }