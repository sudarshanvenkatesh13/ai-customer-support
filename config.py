import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for the support agent."""

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_MODEL = "gpt-4o-mini"

    # ChromaDB
    CHROMA_PERSIST_DIR = "./chroma_data"

    # Agent settings
    MAX_CONVERSATION_TURNS = 10
    MEMORY_RESULTS_COUNT = 3

    # Escalation thresholds
    HIGH_FRUSTRATION_THRESHOLD = 2
    MAX_TURNS_BEFORE_ESCALATION = 8

    @classmethod
    def validate(cls):
        """Validate that required config is set."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found. Set it in your .env file.")