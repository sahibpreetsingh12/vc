"""
Configuration management for the Voice Cursor system.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Global settings loaded from environment variables."""
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT_ID: str = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
    
    # Speech-to-Text
    STT_PROVIDER: str = os.getenv("STT_PROVIDER", "google")
    
    # Security
    ENABLE_SANITIZER: bool = os.getenv("ENABLE_SANITIZER", "true").lower() == "true"
    ALLOWED_OPERATIONS: list = os.getenv("ALLOWED_OPERATIONS", "read,write,create,update").split(",")
    
    # Code Generation
    AUTO_FORMAT: bool = os.getenv("AUTO_FORMAT", "true").lower() == "true"
    REQUIRE_APPROVAL: bool = os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required settings are present."""
        if cls.LLM_PROVIDER == "gemini":
            if not cls.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required for Gemini. Get one from https://aistudio.google.com/app/apikey")
        elif cls.LLM_PROVIDER == "groq":
            if not cls.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is required for Groq")
        return True


# Singleton instance
settings = Settings()