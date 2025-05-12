from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.room import Room
from app.models.booking import Booking
from app.schemas.room import Room as RoomSchema, RoomCreate, RoomUpdate
from app.utils.security import get_current_active_user
from app.utils.dependencies import get_current_admin
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=List[RoomSchema])
async def read_rooms(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    min_capacity: Optional[int] = None,
    max_price: Optional[float] = None,
    has_projector: Optional[bool] = None,
    has_whiteboard: Optional[bool] = None,
    has_video_conf: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка комнат с возможностью фильтрации"""
    query = db.query(Room).filter(Room.is_active == True)
    
    # Применение фильтров
    if name:
        query = query.filter(Room.name.ilike(f"%{name}%"))
    
    if min_capacity:
        query = query.filter(Room.capacity >= min_capacity)
    
    if max_price:
        query = query.filter(Room.price_per_hour <= max_price)
    
    if has_projector is not None:
        query = query.filter(Room.has_projector == has_projector)
    
    if has_whiteboard is not None:
        query = query.filter(Room.has_whiteboard == has_whiteboard)
    
    if has_video_conf is not None:
        query = query.filter(Room.has_video_conf == has_video_conf)
    
    # Пагинация
    rooms = query.offset(skip).limit(limit).all()
    
    return rooms

@router.get("/{room_id}", response_model=RoomSchema)
async def read_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации о конкретной комнате"""
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return room

@router.post("/", response_model=RoomSchema)
async def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Создание новой комнаты (только для администраторов)"""
    db_room = Room(**room.dict())
    
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    
    return db_room

@router.put("/{room_id}", response_model=RoomSchema)
async def update_room(
    room_id: int,
    room_update: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Обновление информации о комнате (только для администраторов)"""
    db_room = db.query(Room).filter(Room.id == room_id).first()
    
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Обновление полей комнаты
    update_data = room_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_room, key, value)
    
    db.commit()
    db.refresh(db_room)
    
    return db_room

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Удаление комнаты (только для администраторов)"""
    db_room = db.query(Room).filter(Room.id == room_id).first()
    
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    db.delete(db_room)
    db.commit()
    
    return None

@router.get("/{room_id}/availability", response_model=List[dict])
async def check_room_availability(
    room_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Проверка доступности комнаты в указанный период"""
    # Проверка существования комнаты
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Получение бронирований комнаты в указанный период
    bookings = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status.in_(["pending", "confirmed"]),
        Booking.start_time < end_date,
        Booking.end_time > start_date
    ).order_by(Booking.start_time).all()
    
    # Формирование списка доступных слотов
    availability = []
    current_time = start_date
    
    for booking in bookings:
        # Если есть свободное время до бронирования
        if current_time < booking.start_time:
            availability.append({
                "start_time": current_time.isoformat(),
                "end_time": booking.start_time.isoformat(),
                "available": True
            })
        
        # Добавление занятого слота
        availability.append({
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "available": False,
            "booking_id": booking.id
        })
        
        # Обновление текущего времени
        current_time = booking.end_time
    
    # Если есть свободное время после последнего бронирования
    if current_time < end_date:
        availability.append({
            "start_time": current_time.isoformat(),
            "end_time": end_date.isoformat(),
            "available": True
        })
    
    # Если нет бронирований, весь период доступен
    if not bookings:
        availability.append({
            "start_time": start_date.isoformat(),
            "end_time": end_date.isoformat(),
            "available": True
        })
    
    return availability