from PyQt5.QtCore import QObject, pyqtSignal

class RoomController(QObject):
    """Контроллер для работы с комнатами"""
    
    rooms_loaded = pyqtSignal(list)
    room_loaded = pyqtSignal(dict)
    room_created = pyqtSignal(dict)
    room_updated = pyqtSignal(dict)
    room_deleted = pyqtSignal(int)
    availability_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def get_rooms(self, filters=None):
        """Получение списка комнат с возможностью фильтрации"""
        try:
            response = self.api_client.get("/rooms/", params=filters)
            self.rooms_loaded.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return []
    
    def get_room(self, room_id):
        """Получение информации о конкретной комнате"""
        try:
            response = self.api_client.get(f"/rooms/{room_id}")
            self.room_loaded.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None
    
    def create_room(self, room_data):
        """Создание новой комнаты (только для администраторов)"""
        try:
            response = self.api_client.post("/rooms/", room_data)
            self.room_created.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None
    
    def update_room(self, room_id, room_data):
        """Обновление информации о комнате (только для администраторов)"""
        try:
            response = self.api_client.put(f"/rooms/{room_id}", room_data)
            self.room_updated.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return None
    
    def delete_room(self, room_id):
        """Удаление комнаты (только для администраторов)"""
        try:
            self.api_client.delete(f"/rooms/{room_id}")
            self.room_deleted.emit(room_id)
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def check_availability(self, room_id, start_date, end_date):
        """Проверка доступности комнаты в указанный период"""
        try:
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            response = self.api_client.get(f"/rooms/{room_id}/availability", params=params)
            self.availability_loaded.emit(response)
            return response
        except Exception as e:
            self.error_occurred.emit(str(e))
            return []