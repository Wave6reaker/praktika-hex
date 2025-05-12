from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Создание экземпляра приложения
app = FastAPI(
    title=settings.APP_NAME,
    description="API для системы управления коворкингом",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Welcome to Coworking Management System API",
        "docs": "/docs",
        "version": "1.0.0"
    }