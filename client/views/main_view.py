from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt

from .tabs.rooms_tab import RoomsTab
from .tabs.bookings_tab import BookingsTab
from .tabs.analytics_tab import AnalyticsTab

class MainView(QWidget):
    """Главное представление приложения"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.user_data = None
        self.init_ui()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной контейнер
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Верхняя панель с информацией о пользователе и кнопкой выхода
        top_panel = QHBoxLayout()
        
        # Информация о пользователе
        self.user_info_label = QLabel("Пользователь: Не авторизован")
        self.user_info_label.setStyleSheet("font-weight: bold;")
        top_panel.addWidget(self.user_info_label)
        
        # Растягивающийся элемент для выравнивания
        top_panel.addStretch()
        
        # Кнопка выхода
        self.logout_button = QPushButton("Выйти")
        self.logout_button.setMaximumWidth(100)
        self.logout_button.clicked.connect(self.logout)
        top_panel.addWidget(self.logout_button)
        
        # Добавление верхней панели в основной контейнер
        main_layout.addLayout(top_panel)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        
        # Вкладка комнат
        self.rooms_tab = RoomsTab(self)
        self.tab_widget.addTab(self.rooms_tab, "Комнаты")
        
        # Вкладка бронирований
        self.bookings_tab = BookingsTab(self)
        self.tab_widget.addTab(self.bookings_tab, "Бронирования")
        
        # Вкладка аналитики (только для администраторов)
        self.analytics_tab = AnalyticsTab(self)
        self.tab_widget.addTab(self.analytics_tab, "Аналитика")
        
        # Добавление вкладок в основной контейнер
        main_layout.addWidget(self.tab_widget)
        
        # Установка основного контейнера
        self.setLayout(main_layout)
    
    def set_user_data(self, user_data):
        """Установка данных пользователя"""
        self.user_data = user_data
        
        # Обновление информации о пользователе
        if user_data:
            username = user_data.get("username", "Неизвестно")
            role = user_data.get("role", "user")
            role_text = "Администратор" if role == "admin" else "Пользователь"
            self.user_info_label.setText(f"Пользователь: {username} ({role_text})")
            
            # Скрытие вкладки аналитики для обычных пользователей
            if role != "admin":
                self.tab_widget.removeTab(self.tab_widget.indexOf(self.analytics_tab))
    
    def refresh_data(self):
        """Обновление данных на всех вкладках"""
        # Получение данных пользователя
        try:
            user_data = self.parent.api_client.get("/users/me")
            self.set_user_data(user_data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные пользователя: {str(e)}")
            self.parent.logout()
            return
        
        # Обновление данных на вкладках
        self.rooms_tab.refresh_data()
        self.bookings_tab.refresh_data()
        
        # Обновление данных на вкладке аналитики (только для администраторов)
        if self.user_data and self.user_data.get("role") == "admin":
            self.analytics_tab.refresh_data()
    
    def logout(self):
        """Выход из системы"""
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.parent.logout()