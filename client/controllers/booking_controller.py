from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime

class BookingController(QObject):
    """Контроллер для работы с бронированиями"""
    
    bookings_loaded = pyqtSignal(list)
    booking_loaded = pyqtSignal(dict)
    booking_created = pyqtSignal(dict)
    booking_updated = pyqtSignal(dict)
    booking_cancelled = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def get_bookings(self, filters=None):
        """Получение списка бронирований с возможностью фильтрации"""
        try:
            # Преобразуем даты в строки ISO формата
            if filters and "start_date" in filters and isinstance(filters["start_date"], datetime):
                filters["start_date"] = filters["start_date"].isoformat()
            if filters and "end_date" in filters and isinstance(filters["end_date"], datetime):
                filters["end_date"] = filters["end_date"].isoformat()
                
            response = self.api_client.get("/bookings/", params=filters)
            self.bookings_loaded.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return []
    
    def get_booking(self, booking_id):
        """Получение информации о конкретном бронировании"""
        try:
            response = self.api_client.get(f"/bookings/{booking_id}")
            self.booking_loaded.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None
    
    def create_booking(self, booking_data):
        """Создание нового бронирования"""
        try:
            # Преобразуем даты в строки ISO формата
            if "start_time" in booking_data and isinstance(booking_data["start_time"], datetime):
                booking_data["start_time"] = booking_data["start_time"].isoformat()
            if "end_time" in booking_data and isinstance(booking_data["end_time"], datetime):
                booking_data["end_time"] = booking_data["end_time"].isoformat()
                
            response = self.api_client.post("/bookings/", booking_data)
            self.booking_created.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None
    
    def update_booking(self, booking_id, booking_data):
        """Обновление информации о бронировании"""
        try:
            # Преобразуем даты в строки ISO формата
            if "start_time" in booking_data and isinstance(booking_data["start_time"], datetime):
                booking_data["start_time"] = booking_data["start_time"].isoformat()
            if "end_time" in booking_data and isinstance(booking_data["end_time"], datetime):
                booking_data["end_time"] = booking_data["end_time"].isoformat()
                
            response = self.api_client.put(f"/bookings/{booking_id}", booking_data)
            self.booking_updated.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None
    
    def cancel_booking(self, booking_id):
        """Отмена бронирования"""
        try:
            self.api_client.delete(f"/bookings/{booking_id}")
            self.booking_cancelled.emit(booking_id)
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False