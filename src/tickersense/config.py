import os

from dotenv import load_dotenv

load_dotenv()

# A 3B model is deliberate: MCP clients default to a 60s request timeout, and
# an 8B model on CPU can't finish this pipeline in that budget. The LLM here
# only summarizes text we hand it, so it doesn't need an 8B model's knowledge.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
