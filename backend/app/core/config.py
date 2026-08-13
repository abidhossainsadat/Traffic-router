"""
Configuration settings for the RoadPulse backend.

Loads environment variables and provides type-safe configuration access.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    GOOGLE_MAPS_API_KEY: str
    ANTHROPIC_API_KEY: str
    
    # Database
    DATABASE_URL: str = "postgresql://roadpulse_user:password@localhost:5432/roadpulse"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "./firebase_credentials.json"
    FIREBASE_PROJECT_ID: str
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:19006",  # Expo default
        "http://localhost:19002",  # Expo web
        "exp://localhost:19000",   # Expo Go
    ]
    
    # Traffic Polling
    POLL_INTERVAL_MINUTES: int = 5
    DEFAULT_DELAY_THRESHOLD_MINUTES: int = 10
    
    # AI
    AI_MODEL: str = "claude-3-sonnet-20240229"
    MAX_NOTIFICATION_WORDS: int = 25
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
