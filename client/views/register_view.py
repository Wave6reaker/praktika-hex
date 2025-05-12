from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal

class RegisterView(QWidget):
    """Представление для регистрации нового пользователя"""
    
    # Сигнал для перехода к экрану входа
    show_login_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной контейнер
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Заголовок
        title_label = QLabel("Регистрация нового пользователя")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Форма регистрации
        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # Поле для email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите email")
        self.email_input.setMinimumWidth(250)
        form_layout.addRow("Email:", self.email_input)
        
        # Поле для имени пользователя
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        form_layout.addRow("Имя пользователя:", self.username_input)
        
        # Поле для пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", self.password_input)
        
        # Поле для подтверждения пароля
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Подтвердите пароль")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Подтверждение пароля:", self.confirm_password_input)
        
        # Поле для полного имени
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Введите полное имя (опционально)")
        form_layout.addRow("Полное имя:", self.full_name_input)
        
        # Поле для телефона
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Введите телефон (опционально)")
        form_layout.addRow("Телефон:", self.phone_input)
        
        # Добавление формы в основной контейнер
        form_container = QWidget()
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(20, 10, 20, 20)
        buttons_layout.setSpacing(10)
        
        # Кнопка регистрации
        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.setMinimumWidth(150)
        self.register_button.clicked.connect(self.register)
        buttons_layout.addWidget(self.register_button)
        
        # Кнопка возврата к входу
        self.back_button = QPushButton("Назад к входу")
        self.back_button.setMinimumWidth(150)
        self.back_button.clicked.connect(self.show_login)
        buttons_layout.addWidget(self.back_button)
        
        # Добавление кнопок в основной контейнер
        main_layout.addLayout(buttons_layout)
        
        # Установка основного контейнера
        self.setLayout(main_layout)
    
    def register(self):
        """Обработка нажатия кнопки регистрации"""
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        full_name = self.full_name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        # Проверка заполнения обязательных полей
        if not email or not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля")
            return
        
        # Проверка совпадения паролей
        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        
        # Вызов контроллера для регистрации
        try:
            self.parent.auth_controller.register(email, username, password, full_name, phone)
            # Обработка успешной регистрации происходит через сигнал register_success
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка регистрации: {str(e)}")
    
    def show_login(self):
        """Переход к экрану входа"""
        self.show_login_signal.emit()
        self.parent.show_login()