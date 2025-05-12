from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Room(Base):
    """Модель комнаты"""
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    capacity = Column(Integer)
    price_per_hour = Column(Float)
    has_projector = Column(Boolean, default=False)
    has_whiteboard = Column(Boolean, default=False)
    has_video_conf = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)

    # Отношения
    bookings = relationship("Booking", back_populates="room")