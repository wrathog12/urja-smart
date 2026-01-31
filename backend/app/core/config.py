# backend/app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Find the project root (where test4.py is)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    """
    Load environment variables from .env file.
    """
    DEEPGRAM_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    CARTESIA_API_KEY: str = ""
    SUPERTONIC_API_KEY: str = ""
    
    class Config:
        env_file = str(ENV_FILE)  # Use absolute path to project root .env
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()

# Singleton instance
settings = get_settings()
