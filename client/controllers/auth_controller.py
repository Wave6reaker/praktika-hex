from PyQt5.QtCore import QObject, pyqtSignal

class AuthController(QObject):
    """Контроллер для работы с аутентификацией"""
    
    login_success = pyqtSignal(str, dict)
    login_error = pyqtSignal(str)
    register_success = pyqtSignal(dict)
    register_error = pyqtSignal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def login(self, username, password):
        """Вход в систему"""
        try:
            # Формат данных для запроса на получение токена
            data = {
                "username": username,
                "password": password
            }
            
            # Запрос на получение токена
            response = self.api_client.post("/token", data)
            token = response.get("access_token")
            
            if token:
                # Получение данных пользователя
                self.api_client.set_token(token)
                user_data = self.api_client.get("/users/me")
                
                self.login_success.emit(token, user_data)
            else:
                self.login_error.emit("Не удалось получить токен доступа")
        except Exception as e:
            self.login_error.emit(str(e))
    
    def register(self, email, username, password, full_name=None, phone=None):
        """Регистрация нового пользователя"""
        try:
            data = {
                "email": email,
                "username": username,
                "password": password,
                "full_name": full_name,
                "phone": phone
            }
            
            response = self.api_client.post("/register", data)
            self.register_success.emit(response)
        except Exception as e:
            self.register_error.emit(str(e))
    
    def validate_token(self, success_callback=None, error_callback=None):
        """Проверка валидности токена"""
        try:
            self.api_client.get("/users/me")
            if success_callback:
                success_callback()
        except Exception:
            if error_callback:
                error_callback()