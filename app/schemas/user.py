from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import re

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

    @validator('username')
    def username_alphanumeric(cls, v):
        assert re.match(r'^[a-zA-Z0-9_-]+$', v), 'Username must be alphanumeric'
        return v

class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str

    @validator('password')
    def password_min_length(cls, v):
        assert len(v) >= 6, 'Password must be at least 6 characters'
        return v

class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserInDB(UserBase):
    """Схема пользователя в базе данных"""
    id: int
    role: str
    is_active: bool

    class Config:
        orm_mode = True

class User(UserInDB):
    """Схема пользователя для ответа API"""
    pass

class UserPasswordUpdate(BaseModel):
    """Схема для обновления пароля"""
    current_password: str
    new_password: str

    @validator('new_password')
    def password_min_length(cls, v):
        assert len(v) >= 6, 'Password must be at least 6 characters'
        return v