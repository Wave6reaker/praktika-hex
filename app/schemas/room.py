from typing import Optional
from pydantic import BaseModel, validator

class RoomBase(BaseModel):
    """Базовая схема комнаты"""
    name: str
    description: Optional[str] = None
    capacity: int
    price_per_hour: float
    has_projector: bool = False
    has_whiteboard: bool = False
    has_video_conf: bool = False
    image_url: Optional[str] = None

    @validator('capacity')
    def capacity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be positive')
        return v

    @validator('price_per_hour')
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Price must be non-negative')
        return v

class RoomCreate(RoomBase):
    """Схема для создания комнаты"""
    pass

class RoomUpdate(BaseModel):
    """Схема для обновления комнаты"""
    name: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    price_per_hour: Optional[float] = None
    has_projector: Optional[bool] = None
    has_whiteboard: Optional[bool] = None
    has_video_conf: Optional[bool] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None

    @validator('capacity')
    def capacity_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Capacity must be positive')
        return v

    @validator('price_per_hour')
    def price_must_be_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price must be non-negative')
        return v

class RoomInDB(RoomBase):
    """Схема комнаты в базе данных"""
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Room(RoomInDB):
    """Схема комнаты для ответа API"""
    pass