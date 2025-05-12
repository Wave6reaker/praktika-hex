from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator

class BookingBase(BaseModel):
    """Базовая схема бронирования"""
    room_id: int
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class BookingCreate(BookingBase):
    """Схема для создания бронирования"""
    pass

class BookingUpdate(BaseModel):
    """Схема для обновления бронирования"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if v is not None and 'start_time' in values and values['start_time'] is not None and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

    @validator('status')
    def status_must_be_valid(cls, v):
        if v is not None and v not in ['pending', 'confirmed', 'cancelled', 'completed']:
            raise ValueError('Invalid status')
        return v

class BookingInDB(BookingBase):
    """Схема бронирования в базе данных"""
    id: int
    user_id: int
    created_at: datetime
    status: str
    total_price: float

    class Config:
        orm_mode = True

class Booking(BookingInDB):
    """Схема бронирования для ответа API"""
    room_name: Optional[str] = None
    user_name: Optional[str] = None