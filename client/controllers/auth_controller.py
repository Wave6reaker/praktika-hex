from PyQt5.QtCore import QObject, pyqtSignal

class AuthController:
    def __init__(self, api_client, parent=None):
        self.api_client = api_client
        self.parent = parent  # ссылка на CoworkingApp

    def login(self, username, password):
        """Вход пользователя"""
        # Try with the correct endpoint path
        response = self.api_client.post("/auth/login", data={  # Removed /api prefix
            "username": username,
            "password": password
        })

        if not response or "access_token" not in response:
            raise Exception("Неверный логин или пароль")

        token = response["access_token"]
        self.api_client.set_token(token)

        # Получаем данные пользователя
        user_data = self.api_client.get("/users/me")  # Removed /api prefix

        # Если всё успешно — уведомляем главное окно
        if self.parent:
            self.parent.login_success(token, user_data)

    def register(self, email, username, password, full_name="", phone=""):
        """Регистрация нового пользователя"""
        payload = {
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name,
            "phone": phone
        }

        # Try with the correct endpoint path
        response = self.api_client.post("/auth/register", data=payload)  # Removed /api prefix
        if not response:
            raise Exception("Ошибка регистрации")

        # После регистрации можно залогинить пользователя сразу
        self.login(username, password)

    def validate_token(self, success_callback, error_callback):
        """Проверка токена"""
        try:
            # Try with the correct endpoint path
            self.api_client.get("/users/me")  # Removed /api prefix
            success_callback()
        except Exception:
            error_callback()