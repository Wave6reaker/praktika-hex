import os
from pydantic import Field, BaseModel

class Settings(BaseModel):
    """Настройки приложения"""
    # Настройки базы данных
    DATABASE_URL: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./coworking.db"))

    # Настройки безопасности
    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY", "your-secret-key-for-development"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки приложения
    APP_NAME: str = "Coworking Management System"
    ADMIN_EMAIL: str = Field(default=os.getenv("ADMIN_EMAIL", "admin@example.com"))
    ADMIN_PASSWORD: str = Field(default=os.getenv("ADMIN_PASSWORD", "admin"))

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()