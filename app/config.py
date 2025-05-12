import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки приложения"""
    # Настройки базы данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://coworking_user:admin@localhost:5432/coworking_db")

    # Настройки безопасности
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки приложения
    APP_NAME: str = "Coworking Management System"
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()