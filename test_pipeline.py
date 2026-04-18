from pipeline import SupportPipeline

pipeline = SupportPipeline()

# Test 1: General greeting
print("=" * 60)
print("TEST 1: General greeting")
result = pipeline.process_message("user_001", "Hi, I need some help")
print(f"Response: {result['response']}")
print(f"Intent: {result['intent']['intent']} ({result['intent']['confidence']})")
print(f"Escalation: {result['escalation']['should_escalate']}")
print()

# Test 2: Billing issue
print("=" * 60)
print("TEST 2: Billing issue")
result = pipeline.process_message("user_001", "I was charged twice for my subscription last month")
print(f"Response: {result['response']}")
print(f"Intent: {result['intent']['intent']} ({result['intent']['confidence']})")
print(f"Memories used: {result['memories_used']}")
print()

# Test 3: Angry escalation
print("=" * 60)
print("TEST 3: Angry customer wanting escalation")
result = pipeline.process_message("user_002", "This is ridiculous! I've been waiting for a week and nobody has fixed my issue. I want to speak to a manager RIGHT NOW!")
print(f"Response: {result['response']}")
print(f"Intent: {result['intent']['intent']} ({result['intent']['confidence']})")
print(f"Escalation: {result['escalation']['should_escalate']}")
print(f"Priority: {result['escalation']['priority']}")
if result['escalation_ticket']:
    print(f"Ticket: {result['escalation_ticket']['ticket_id']}")
    print(f"Reasons: {result['escalation_ticket']['reasons']}")