from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
# Data directories
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = DATA_DIR / "database"
UPLOADS_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma"
EXPORTS_DIR = DATA_DIR / "exports"

# Logs directory
LOGS_DIR = BASE_DIR / "logs"
# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))