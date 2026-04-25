import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
    OLLAMA_VISION = os.getenv("OLLAMA_VISION", "llava:latest")
    PDF_SERVICE_URL = os.getenv("PDF_SERVICE_URL", "")