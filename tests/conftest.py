import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import sys

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.database import Base
from app.main import app
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.room import Room
from app.models.booking import Booking, BookingStatus
from app.utils.security import get_password_hash
from datetime import datetime, timedelta

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Создаем таблицы в базе данных
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Удаляем таблицы после завершения теста
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    # Переопределяем зависимость для получения тестовой базы данных
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Очищаем переопределения зависимостей
    app.dependency_overrides = {}

@pytest.fixture(scope="function")
def test_user(db):
    # Создаем тестового пользователя
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password"),
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(db):
    # Создаем тестового администратора
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("password"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def test_room(db):
    # Создаем тестовую комнату
    room = Room(
        name="Test Room",
        description="Test Description",
        capacity=10,
        price_per_hour=100.0,
        has_projector=True,
        has_whiteboard=True,
        has_video_conf=False,
        is_active=True
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@pytest.fixture(scope="function")
def test_booking(db, test_user, test_room):
    # Создаем тестовое бронирование
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    booking = Booking(
        user_id=test_user.id,
        room_id=test_room.id,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.PENDING,
        total_price=test_room.price_per_hour * 2,
        notes="Test booking"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@pytest.fixture(scope="function")
def user_token_headers(client, test_user):
    # Получаем токен для тестового пользователя
    login_data = {
        "username": test_user.username,
        "password": "password"
    }
    response = client.post("/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def admin_token_headers(client, test_admin):
    # Получаем токен для тестового администратора
    login_data = {
        "username": test_admin.username,
        "password": "password"
    }
    response = client.post("/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}