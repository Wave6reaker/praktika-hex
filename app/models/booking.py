from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class BookingStatus(str, enum.Enum):
    """Статусы бронирования"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Booking(Base):
    """Модель бронирования"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    total_price = Column(Float)
    notes = Column(String, nullable=True)

    # Отношения
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")