from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.db.database import get_db
from app.models.user import User
from app.models.room import Room
from app.models.booking import Booking, BookingStatus
from app.utils.dependencies import get_current_admin
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/revenue", response_model=List[dict])
async def get_revenue_stats(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Получение статистики по доходам (только для администраторов)"""
    # Определение группировки в зависимости от параметра group_by
    if group_by == "day":
        date_trunc = func.date_trunc('day', Booking.start_time)
        date_format = "%Y-%m-%d"
    elif group_by == "week":
        date_trunc = func.date_trunc('week', Booking.start_time)
        date_format = "%Y-%m-%d"
    else:  # month
        date_trunc = func.date_trunc('month', Booking.start_time)
        date_format = "%Y-%m"
    
    # Запрос для получения статистики по доходам
    revenue_stats = db.query(
        date_trunc.label('date'),
        func.sum(Booking.total_price).label('revenue')
    ).filter(
        Booking.status == BookingStatus.COMPLETED,
        Booking.start_time >= start_date,
        Booking.start_time <= end_date
    ).group_by('date').order_by('date').all()
    
    # Форматирование результатов
    result = []
    for stat in revenue_stats:
        result.append({
            "date": stat.date.strftime(date_format),
            "revenue": float(stat.revenue)
        })
    
    return result

@router.get("/room-usage", response_model=List[dict])
async def get_room_usage_stats(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Получение статистики по использованию комнат (только для администраторов)"""
    # Запрос для получения статистики по использованию комнат
    room_stats = db.query(
        Room.id,
        Room.name,
        func.count(Booking.id).label('booking_count'),
        func.sum(Booking.total_price).label('total_revenue'),
        func.sum(func.extract('epoch', Booking.end_time - Booking.start_time) / 3600).label('total_hours')
    ).join(Booking, Room.id == Booking.room_id).filter(
        Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CONFIRMED]),
        Booking.start_time >= start_date,
        Booking.start_time <= end_date
    ).group_by(Room.id).order_by(func.count(Booking.id).desc()).all()
    
    # Расчет общего количества часов в периоде
    total_hours = (end_date - start_date).total_seconds() / 3600
    
    # Форматирование результатов
    result = []
    for stat in room_stats:
        # Расчет коэффициента занятости (в процентах)
        occupancy_rate = (stat.total_hours / total_hours) * 100 if total_hours > 0 else 0
        
        result.append({
            "room_id": stat.id,
            "room_name": stat.name,
            "booking_count": stat.booking_count,
            "total_revenue": float(stat.total_revenue) if stat.total_revenue else 0,
            "total_hours": float(stat.total_hours) if stat.total_hours else 0,
            "occupancy_rate": round(occupancy_rate, 2)
        })
    
    return result

@router.get("/user-activity", response_model=List[dict])
async def get_user_activity_stats(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Получение статистики по активности пользователей (только для администраторов)"""
    # Запрос для получения статистики по активности пользователей
    user_stats = db.query(
        User.id,
        User.username,
        User.email,
        func.count(Booking.id).label('booking_count'),
        func.sum(Booking.total_price).label('total_spent')
    ).join(Booking, User.id == Booking.user_id).filter(
        Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CONFIRMED]),
        Booking.start_time >= start_date,
        Booking.start_time <= end_date
    ).group_by(User.id).order_by(func.count(Booking.id).desc()).limit(limit).all()
    
    # Форматирование результатов
    result = []
    for stat in user_stats:
        result.append({
            "user_id": stat.id,
            "username": stat.username,
            "email": stat.email,
            "booking_count": stat.booking_count,
            "total_spent": float(stat.total_spent) if stat.total_spent else 0
        })
    
    return result