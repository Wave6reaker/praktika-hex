from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# Создаем асинхронный движок для PostgreSQL с asyncpg
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Создаем фабрику асинхронных сессий
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Функция для получения асинхронной сессии
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session