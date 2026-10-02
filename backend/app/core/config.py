import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
EXPORTS_DIR = DATA_DIR / "exports"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareerForge AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'careerforge.db'}"
    
    # Security
    SECRET_KEY: str = "careerforge-local-secret-key-change-in-production-2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Ollama Local AI
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_ENABLED: bool = True
    OLLAMA_TIMEOUT_SECONDS: int = 45
    
    # Default Provider Credentials (can be configured via UI / DB)
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_APP_KEY: Optional[str] = None
    JOOBLE_API_KEY: Optional[str] = None
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_DEFAULT_CHAT_ID: Optional[str] = None
    
    # India Defaults
    DEFAULT_COUNTRY: str = "in"
    DEFAULT_CURRENCY: str = "INR"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
