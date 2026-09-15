import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# Retrieval gate: if best chunk score is below this, refuse without calling the LLM.
MIN_SCORE = 0.50
REFUSE_MESSAGE = "I don't know based on the provided documents."