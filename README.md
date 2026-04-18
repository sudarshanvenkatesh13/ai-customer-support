# 🤖 AI Customer Support Agent

An intelligent customer support agent with **long-term memory**, **intent detection**, and **automatic escalation logic**. Built with LangChain, ChromaDB, and OpenAI.

The agent remembers past conversations, classifies user intent in real-time, and knows when to escalate to a human — just like a real support team.

🔗 **[Live Demo](https://your-streamlit-url.streamlit.app)** · 📦 **[GitHub](https://github.com/sudarshanvenkatesh13/ai-customer-support)**

---

## 🎯 What It Does

- **Long-term memory** — Stores and retrieves past conversations using ChromaDB vector search. Returning users get personalized responses.
- **Intent classification** — Detects billing, technical, complaint, account, or general intents with confidence scores using structured JSON outputs.
- **Smart escalation** — Triggers on frustration keywords, repeated high frustration, complaint+anger combos, and conversation length. Generates priority-ranked tickets with reasoning.
- **Admin dashboard** — View escalation queue, resolve/assign tickets, browse user memory history.

---

## 🏗️ Architecture

```
User message
    ↓
[Memory Retrieval] ← ChromaDB (past conversations)
    ↓
[Intent Classifier] → intent + confidence score
    ↓
[Response Generator] ← context + memory + intent
    ↓
[Escalation Check] → escalate? → Admin Queue
    ↓
[Store to Memory] → ChromaDB
    ↓
Response to user
```

---

## 🧠 How Memory Works

Unlike basic chatbots that forget everything after a session, this agent uses **semantic search over past conversations**:

1. User sends a message
2. ChromaDB finds the most relevant past conversations (vector similarity)
3. Those memories are injected into the LLM's context
4. The agent references past interactions naturally ("I see we discussed this before...")
5. After responding, the new conversation is stored for future retrieval

---

## 🚨 Escalation System

The agent uses **5 independent escalation triggers**:

1. LLM-detected escalation need (via intent classifier)
2. Keyword matching ("speak to a manager", "legal action", etc.)
3. Repeated high frustration (tracked per user over time)
4. Complaint intent + high frustration combo
5. Conversation exceeding 8 turns without resolution

Each trigger generates a **priority-ranked ticket** (critical/high/medium/low) with full reasoning.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | OpenAI GPT-4o-mini |
| Orchestration | LangChain |
| Vector DB | ChromaDB (persistent) |
| Frontend | Streamlit |
| Language | Python 3.13 |

---

## 📂 Project Structure

```
ai-customer-support/
├── app.py                  # Streamlit UI (customer chat + admin dashboard)
├── pipeline.py             # Main orchestration pipeline
├── agents/
│   ├── memory.py           # ChromaDB memory manager
│   ├── intent.py           # Intent classifier (structured JSON)
│   ├── responder.py        # Response generator
│   └── escalation.py       # Escalation logic (5 triggers)
├── config.py               # Central configuration
├── prompts.py              # All system prompts
├── requirements.txt        # Pinned dependencies
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key

### Setup

```bash
git clone https://github.com/sudarshanvenkatesh13/ai-customer-support.git
cd ai-customer-support
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
streamlit run app.py
```

---

## 💡 Test Scenarios

Try these to see the agent in action:

1. **General greeting** → "Hi, I need some help"
2. **Billing issue** → "I was charged twice for my subscription"
3. **Returning user** → Send another billing message — the agent remembers
4. **Escalation trigger** → "This is ridiculous! I want to speak to a manager!"
5. **Check Admin Dashboard** → Switch to admin view to see the escalation ticket

---

## 👤 Author

**Sudarshan Venkatesh** — AI Engineer building production AI agents

- GitHub: [@sudarshanvenkatesh13](https://github.com/sudarshanvenkatesh13)
- Twitter: [@SudarshanVenk](https://x.com/SudarshanVenk)
- LinkedIn: [sudarshan2020](https://linkedin.com/in/sudarshan2020)