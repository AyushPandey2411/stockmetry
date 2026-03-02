"""app/core/config.py — Application settings via Pydantic BaseSettings."""
from functools import lru_cache
from typing import List
from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # App
    APP_NAME: str = "Stockmetry"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/stockmetry"

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Demo passwords
    ADMIN_PASSWORD: str = "Admin@Stockmetry2024"
    MANAGER_PASSWORD: str = "Manager@Stockmetry2024"
    ANALYST_PASSWORD: str = "Analyst@Stockmetry2024"

    # AI
    ANTHROPIC_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # Upload
    MAX_UPLOAD_SIZE_MB: int = 50

    def get_allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
