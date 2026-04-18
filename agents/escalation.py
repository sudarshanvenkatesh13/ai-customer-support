from datetime import datetime


class EscalationManager:
    """Manages escalation logic for the support agent."""

    ESCALATION_KEYWORDS = [
        "speak to a human", "talk to a person", "real person",
        "speak to someone", "talk to someone", "human agent",
        "speak to a manager", "talk to a manager", "supervisor",
        "escalate", "this is unacceptable", "i want to complain",
        "lawyer", "legal action", "sue", "report you"
    ]

    def __init__(self):
        self.frustration_history = {}  # tracks per-user frustration over time

    def check_escalation(self, user_id: str, user_message: str,
                         intent_result: dict, conversation_count: int = 0) -> dict:
        """Check if the conversation should be escalated to a human."""
        reasons = []
        should_escalate = False

        # Check 1: Intent classifier already flagged escalation
        if intent_result.get("needs_escalation", False):
            should_escalate = True
            reasons.append("Intent classifier flagged escalation needed")

        # Check 2: Explicit escalation keywords in user message
        message_lower = user_message.lower()
        for keyword in self.ESCALATION_KEYWORDS:
            if keyword in message_lower:
                should_escalate = True
                reasons.append(f"User used escalation keyword: '{keyword}'")
                break

        # Check 3: High frustration level
        frustration = intent_result.get("frustration_level", "low")
        if frustration == "high":
            self._track_frustration(user_id, "high")
            high_count = self.frustration_history.get(user_id, []).count("high")
            if high_count >= 2:
                should_escalate = True
                reasons.append(f"User showed high frustration {high_count} times")
        else:
            self._track_frustration(user_id, frustration)

        # Check 4: Complaint intent with high frustration
        if intent_result.get("intent") == "complaint" and frustration == "high":
            should_escalate = True
            reasons.append("Complaint with high frustration detected")

        # Check 5: Too many conversation turns without resolution
        if conversation_count >= 8:
            should_escalate = True
            reasons.append(f"Conversation reached {conversation_count} turns without resolution")

        # Build escalation result
        priority = self._calculate_priority(reasons, frustration)

        return {
            "should_escalate": should_escalate,
            "reasons": reasons,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "intent": intent_result.get("intent", "general"),
            "frustration_level": frustration
        }

    def _track_frustration(self, user_id: str, level: str):
        """Track frustration levels over time for a user."""
        if user_id not in self.frustration_history:
            self.frustration_history[user_id] = []
        self.frustration_history[user_id].append(level)
        # Keep only the last 10 entries
        self.frustration_history[user_id] = self.frustration_history[user_id][-10:]

    def _calculate_priority(self, reasons: list, frustration: str) -> str:
        """Calculate escalation priority based on reasons and frustration."""
        if not reasons:
            return "none"

        reason_count = len(reasons)
        if reason_count >= 3 or "legal" in " ".join(reasons).lower():
            return "critical"
        elif reason_count >= 2 or frustration == "high":
            return "high"
        elif reason_count >= 1:
            return "medium"
        return "low"

    def format_escalation_ticket(self, escalation_result: dict,
                                 user_message: str,
                                 conversation_summary: str = "") -> dict:
        """Format an escalation ticket for the admin queue."""
        return {
            "ticket_id": f"ESC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": escalation_result["user_id"],
            "priority": escalation_result["priority"],
            "intent": escalation_result["intent"],
            "frustration_level": escalation_result["frustration_level"],
            "reasons": escalation_result["reasons"],
            "last_user_message": user_message[:500],
            "conversation_summary": conversation_summary[:1000],
            "created_at": escalation_result["timestamp"],
            "status": "open"
        }