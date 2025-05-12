from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal

class LoginView(QWidget):
    """Представление для входа в систему"""
    
    # Сигнал для перехода к экрану регистрации
    show_register_signal = pyqtSignal()
    
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
        title_label = QLabel("Вход в систему управления коворкингом")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Форма входа
        form_layout = QFormLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # Поле для имени пользователя
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        self.username_input.setMinimumWidth(250)
        form_layout.addRow("Имя пользователя:", self.username_input)
        
        # Поле для пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", self.password_input)
        
        # Добавление формы в основной контейнер
        form_container = QWidget()
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(20, 10, 20, 20)
        buttons_layout.setSpacing(10)
        
        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.setMinimumWidth(120)
        self.login_button.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_button)
        
        # Кнопка регистрации
        self.register_button = QPushButton("Регистрация")
        self.register_button.setMinimumWidth(120)
        self.register_button.clicked.connect(self.show_register)
        buttons_layout.addWidget(self.register_button)
        
        # Добавление кнопок в основной контейнер
        main_layout.addLayout(buttons_layout)
        
        # Установка основного контейнера
        self.setLayout(main_layout)
    
    def login(self):
        """Обработка нажатия кнопки входа"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Проверка заполнения полей
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля")
            return
        
        # Вызов контроллера для входа
        try:
            self.parent.auth_controller.login(username, password)
            # Обработка успешного входа происходит через сигнал login_success
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка входа: {str(e)}")
    
    def show_register(self):
        """Переход к экрану регистрации"""
        self.show_register_signal.emit()
        self.parent.show_register()