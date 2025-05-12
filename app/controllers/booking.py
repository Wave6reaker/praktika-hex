from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.room import Room
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import Booking as BookingSchema, BookingCreate, BookingUpdate
from app.utils.security import get_current_active_user
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=List[BookingSchema])
async def read_bookings(
    skip: int = 0,
    limit: int = 100,
    room_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение списка бронирований текущего пользователя с возможностью фильтрации"""
    # Базовый запрос
    query = db.query(Booking)
    
    # Если пользователь не администратор, показываем только его бронирования
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Booking.user_id == current_user.id)
    
    # Применение фильтров
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    if start_date:
        query = query.filter(Booking.start_time >= start_date)
    
    if end_date:
        query = query.filter(Booking.end_time <= end_date)
    
    # Сортировка и пагинация
    bookings = query.order_by(Booking.start_time.desc()).offset(skip).limit(limit).all()
    
    # Добавление информации о комнате и пользователе
    result = []
    for booking in bookings:
        booking_dict = BookingSchema.from_orm(booking).dict()
        
        # Добавление имени комнаты
        room = db.query(Room).filter(Room.id == booking.room_id).first()
        if room:
            booking_dict["room_name"] = room.name
        
        # Добавление имени пользователя (только для администраторов)
        if current_user.role == UserRole.ADMIN and booking.user_id != current_user.id:
            user = db.query(User).filter(User.id == booking.user_id).first()
            if user:
                booking_dict["user_name"] = user.username
        
        result.append(booking_dict)
    
    return result

@router.get("/{booking_id}", response_model=BookingSchema)
async def read_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации о конкретном бронировании"""
    # Получение бронирования
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Проверка прав доступа
    if booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Добавление информации о комнате и пользователе
    booking_dict = BookingSchema.from_orm(booking).dict()
    
    # Добавление имени комнаты
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if room:
        booking_dict["room_name"] = room.name
    
    # Добавление имени пользователя (только для администраторов)
    if current_user.role == UserRole.ADMIN and booking.user_id != current_user.id:
        user = db.query(User).filter(User.id == booking.user_id).first()
        if user:
            booking_dict["user_name"] = user.username
    
    return booking_dict

@router.post("/", response_model=BookingSchema)
async def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создание нового бронирования"""
    # Проверка существования комнаты
    room = db.query(Room).filter(Room.id == booking.room_id, Room.is_active == True).first()
    
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Проверка корректности времени
    if booking.start_time >= booking.end_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Проверка, что время бронирования не в прошлом
    if booking.start_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Cannot book in the past")
    
    # Проверка доступности комнаты в указанный период
    overlapping_bookings = db.query(Booking).filter(
        Booking.room_id == booking.room_id,
        Booking.status.in_(["pending", "confirmed"]),
        Booking.start_time < booking.end_time,
        Booking.end_time > booking.start_time
    ).all()
    
    if overlapping_bookings:
        raise HTTPException(status_code=400, detail="Room is already booked for this time")
    
    # Расчет общей стоимости
    duration_hours = (booking.end_time - booking.start_time).total_seconds() / 3600
    total_price = room.price_per_hour * duration_hours
    
    # Создание бронирования
    db_booking = Booking(
        user_id=current_user.id,
        room_id=booking.room_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        status=BookingStatus.PENDING,
        total_price=total_price,
        notes=booking.notes
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    # Добавление информации о комнате
    booking_dict = BookingSchema.from_orm(db_booking).dict()
    booking_dict["room_name"] = room.name
    
    return booking_dict

@router.put("/{booking_id}", response_model=BookingSchema)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновление информации о бронировании"""
    # Получение бронирования
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Проверка прав доступа
    if db_booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Проверка статуса бронирования
    if db_booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="Cannot update cancelled or completed booking")
    
    # Обновление полей бронирования
    update_data = booking_update.dict(exclude_unset=True)
    
    # Если обновляется время, проверяем доступность комнаты
    if "start_time" in update_data or "end_time" in update_data:
        start_time = update_data.get("start_time", db_booking.start_time)
        end_time = update_data.get("end_time", db_booking.end_time)
        
        # Проверка корректности времени
        if start_time >= end_time:
            raise HTTPException(status_code=400, detail="End time must be after start time")
        
        # Проверка, что время бронирования не в прошлом
        if start_time < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Cannot book in the past")
        
        # Проверка доступности комнаты в указанный период
        overlapping_bookings = db.query(Booking).filter(
            Booking.room_id == db_booking.room_id,
            Booking.id != booking_id,
            Booking.status.in_(["pending", "confirmed"]),
            Booking.start_time < end_time,
            Booking.end_time > start_time
        ).all()
        
        if overlapping_bookings:
            raise HTTPException(status_code=400, detail="Room is already booked for this time")
        
        # Если время изменилось, пересчитываем стоимость
        if start_time != db_booking.start_time or end_time != db_booking.end_time:
            room = db.query(Room).filter(Room.id == db_booking.room_id).first()
            duration_hours = (end_time - start_time).total_seconds() / 3600
            update_data["total_price"] = room.price_per_hour * duration_hours
    
    # Обновление полей
    for key, value in update_data.items():
        setattr(db_booking, key, value)
    
    db.commit()
    db.refresh(db_booking)
    
    # Добавление информации о комнате
    room = db.query(Room).filter(Room.id == db_booking.room_id).first()
    booking_dict = BookingSchema.from_orm(db_booking).dict()
    booking_dict["room_name"] = room.name
    
    return booking_dict

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отмена бронирования"""
    # Получение бронирования
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Проверка прав доступа
    if db_booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Проверка статуса бронирования
    if db_booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        raise HTTPException(status_code=400, detail="Booking is already cancelled or completed")
    
    # Отмена бронирования
    db_booking.status = BookingStatus.CANCELLED
    
    db.commit()
    
    return None