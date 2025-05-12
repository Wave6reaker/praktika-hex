from PyQt5.QtCore import QObject, pyqtSignal

class AuthController:
    def __init__(self, api_client, parent=None):
        self.api_client = api_client
        self.parent = parent  # ссылка на CoworkingApp

    def login(self, username, password):
        """Вход пользователя"""
        response = self.api_client.post("/api/auth/login", data={
            "username": username,
            "password": password
        })

        if not response or "access_token" not in response:
            raise Exception("Неверный логин или пароль")

        token = response["access_token"]
        self.api_client.set_token(token)

        # Получаем данные пользователя
        user_data = self.api_client.get("/api/users/me")

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

        response = self.api_client.post("/api/auth/register", data=payload)
        if not response:
            raise Exception("Ошибка регистрации")

        # После регистрации можно залогинить пользователя сразу
        self.login(username, password)

    def validate_token(self, success_callback, error_callback):
        """Проверка токена"""
        try:
            self.api_client.get("/api/users/me")
            success_callback()
        except Exception:
            error_callback()