import requests
import json
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

class ApiClient(QObject):
    """Клиент для работы с API сервера"""
    
    # Сигналы для уведомления о событиях
    request_started = pyqtSignal(str)
    request_finished = pyqtSignal(str)
    request_error = pyqtSignal(str, str)
    
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.token = None
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def set_token(self, token):
        """Установка токена авторизации"""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def clear_token(self):
        """Очистка токена авторизации"""
        self.token = None
        if "Authorization" in self.headers:
            del self.headers["Authorization"]
    
    def _handle_response(self, response):
        """Обработка ответа от сервера"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except:
                pass
            self.request_error.emit(response.url, error_msg)
            raise Exception(error_msg)
        except json.JSONDecodeError:
            return response.text
    
    def get(self, endpoint, params=None):
        """Выполнение GET-запроса"""
        url = f"{self.base_url}{endpoint}"
        self.request_started.emit(url)
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            self.request_finished.emit(url)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.request_error.emit(url, str(e))
            raise
    
    def post(self, endpoint, data=None):
        """Выполнение POST-запроса"""
        url = f"{self.base_url}{endpoint}"
        self.request_started.emit(url)
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            self.request_finished.emit(url)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.request_error.emit(url, str(e))
            raise
    
    def put(self, endpoint, data=None):
        """Выполнение PUT-запроса"""
        url = f"{self.base_url}{endpoint}"
        self.request_started.emit(url)
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            self.request_finished.emit(url)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.request_error.emit(url, str(e))
            raise
    
    def delete(self, endpoint):
        """Выполнение DELETE-запроса"""
        url = f"{self.base_url}{endpoint}"
        self.request_started.emit(url)
        
        try:
            response = requests.delete(url, headers=self.headers)
            self.request_finished.emit(url)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            self.request_error.emit(url, str(e))
            raise

class DateTimeEncoder(json.JSONEncoder):
    """Кастомный JSON энкодер для работы с datetime"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)