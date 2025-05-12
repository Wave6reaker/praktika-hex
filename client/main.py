import sys
import os


from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import QSettings

from views.login_view import LoginView
from views.register_view import RegisterView
from views.main_view import MainView
from controllers.auth_controller import AuthController
from controllers.room_controller import RoomController
from controllers.booking_controller import BookingController
from utils.api_client import ApiClient

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

class CoworkingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coworking Management System")
        self.setMinimumSize(1000, 700)
        
        # Инициализация настроек приложения
        self.settings = QSettings("CoworkingApp", "CoworkingManagement")
        
        # Инициализация API клиента
        base_url = os.environ.get("API_URL", "http://localhost:8000")
        self.api_client = ApiClient(base_url)
        
        # Инициализация контроллеров
        self.auth_controller = AuthController(self.api_client)
        self.room_controller = RoomController(self.api_client)
        self.booking_controller = BookingController(self.api_client)
        
        # Инициализация стека виджетов для навигации между экранами
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Инициализация представлений
        self.login_view = LoginView(self)
        self.register_view = RegisterView(self)
        self.main_view = MainView(self)
        
        # Добавление представлений в стек
        self.stacked_widget.addWidget(self.login_view)
        self.stacked_widget.addWidget(self.register_view)
        self.stacked_widget.addWidget(self.main_view)
        
        # Установка начального представления
        self.show_login()
        
        # Восстановление токена, если он сохранен
        self.restore_session()
    
    def show_login(self):
        """Показать экран входа"""
        self.stacked_widget.setCurrentWidget(self.login_view)
    
    def show_register(self):
        """Показать экран регистрации"""
        self.stacked_widget.setCurrentWidget(self.register_view)
    
    def show_main(self):
        """Показать главный экран приложения"""
        self.main_view.refresh_data()
        self.stacked_widget.setCurrentWidget(self.main_view)
    
    def login_success(self, token, user_data):
        """Обработка успешного входа"""
        self.api_client.set_token(token)
        self.settings.setValue("token", token)
        self.settings.setValue("user_data", user_data)
        self.show_main()
    
    def logout(self):
        """Выход из системы"""
        self.api_client.clear_token()
        self.settings.remove("token")
        self.settings.remove("user_data")
        self.show_login()
    
    def restore_session(self):
        """Восстановление сессии из сохраненных настроек"""
        token = self.settings.value("token")
        user_data = self.settings.value("user_data")
        
        if token and user_data:
            self.api_client.set_token(token)
            # Проверяем валидность токена
            self.auth_controller.validate_token(
                success_callback=lambda: self.show_main(),
                error_callback=lambda: self.logout()
            )

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Используем стиль Fusion для современного вида
    
    # Установка стилей приложения
    with open("client/resources/styles.css", "r") as f:
        app.setStyleSheet(f.read())
    
    window = CoworkingApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()