from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QComboBox,
                            QDateTimeEdit, QTextEdit)
from PyQt5.QtCore import Qt, QDateTime
from datetime import datetime, timedelta

class BookingsTab(QWidget):
    """Вкладка для управления бронированиями"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.bookings = []
        self.rooms = []
        self.init_ui()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной контейнер
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Верхняя панель с кнопками
        top_panel = QHBoxLayout()
        
        # Заголовок
        title_label = QLabel("Управление бронированиями")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        top_panel.addWidget(title_label)
        
        # Растягивающийся элемент для выравнивания
        top_panel.addStretch()
        
        # Кнопка добавления бронирования
        self.add_booking_button = QPushButton("Новое бронирование")
        self.add_booking_button.clicked.connect(self.add_booking)
        top_panel.addWidget(self.add_booking_button)
        
        # Кнопка обновления списка
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.refresh_data)
        top_panel.addWidget(refresh_button)
        
        # Добавление верхней панели в основной контейнер
        main_layout.addLayout(top_panel)
        
        # Таблица бронирований
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(7)
        self.bookings_table.setHorizontalHeaderLabels([
            "ID", "Комната", "Начало", "Окончание", 
            "Статус", "Стоимость", "Действия"
        ])
        self.bookings_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.bookings_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bookings_table.horizontalHeader().setStretchLastSection(True)
        
        # Добавление таблицы в основной контейнер
        main_layout.addWidget(self.bookings_table)
        
        # Установка основного контейнера
        self.setLayout(main_layout)
    
    def refresh_data(self):
        """Обновление списка бронирований"""
        try:
            # Получение списка комнат
            self.rooms = self.parent.parent.room_controller.get_rooms()
            
            # Получение списка бронирований
            self.bookings = self.parent.parent.booking_controller.get_bookings()
            
            # Обновление таблицы
            self.update_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные: {str(e)}")
    
    def update_table(self):
        """Обновление таблицы бронирований"""
        # Очистка таблицы
        self.bookings_table.setRowCount(0)
        
        # Заполнение таблицы
        for row, booking in enumerate(self.bookings):
            self.bookings_table.insertRow(row)
            
            # ID
            self.bookings_table.setItem(row, 0, QTableWidgetItem(str(booking["id"])))
            
            # Комната
            room_name = booking.get("room_name", "")
            self.bookings_table.setItem(row, 1, QTableWidgetItem(room_name))
            
            # Начало
            start_time = datetime.fromisoformat(booking["start_time"].replace("Z", "+00:00"))
            self.bookings_table.setItem(row, 2, QTableWidgetItem(start_time.strftime("%d.%m.%Y %H:%M")))
            
            # Окончание
            end_time = datetime.fromisoformat(booking["end_time"].replace("Z", "+00:00"))
            self.bookings_table.setItem(row, 3, QTableWidgetItem(end_time.strftime("%d.%m.%Y %H:%M")))
            
            # Статус
            status_map = {
                "pending": "Ожидание",
                "confirmed": "Подтверждено",
                "cancelled": "Отменено",
                "completed": "Завершено"
            }
            status_text = status_map.get(booking["status"], booking["status"])
            status_item = QTableWidgetItem(status_text)
            
            # Цвет статуса
            if booking["status"] == "confirmed":
                status_item.setBackground(Qt.green)
            elif booking["status"] == "cancelled":
                status_item.setBackground(Qt.red)
            elif booking["status"] == "completed":
                status_item.setBackground(Qt.blue)
                status_item.setForeground(Qt.white)
            
            self.bookings_table.setItem(row, 4, status_item)
            
            # Стоимость
            self.bookings_table.setItem(row, 5, QTableWidgetItem(f"{booking['total_price']:.2f}"))
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            # Кнопка просмотра
            view_button = QPushButton("Просмотр")
            view_button.clicked.connect(lambda _, b=booking: self.view_booking(b))
            actions_layout.addWidget(view_button)
            
            # Кнопка редактирования (только для активных бронирований)
            if booking["status"] in ["pending", "confirmed"]:
                edit_button = QPushButton("Изменить")
                edit_button.clicked.connect(lambda _, b=booking: self.edit_booking(b))
                actions_layout.addWidget(edit_button)
                
                # Кнопка отмены
                cancel_button = QPushButton("Отменить")
                cancel_button.clicked.connect(lambda _, b=booking: self.cancel_booking(b))
                actions_layout.addWidget(cancel_button)
            
            actions_widget.setLayout(actions_layout)
            self.bookings_table.setCellWidget(row, 6, actions_widget)
    
    def add_booking(self):
        """Добавление нового бронирования"""
        # Проверка наличия комнат
        if not self.rooms:
            QMessageBox.warning(self, "Предупреждение", "Нет доступных комнат для бронирования")
            return
        
        # Создание диалога
        dialog = QDialog(self)
        dialog.setWindowTitle("Новое бронирование")
        dialog.setMinimumWidth(400)
        
        # Форма
        form_layout = QFormLayout()
        
        # Комната
        room_combo = QComboBox()
        for room in self.rooms:
            if room["is_active"]:
                room_combo.addItem(f"{room['name']} ({room['capacity']} мест, {room['price_per_hour']:.2f}/час)", room["id"])
        form_layout.addRow("Комната:", room_combo)
        
        # Начало
        start_time = QDateTime.currentDateTime().addSecs(3600)  # +1 час от текущего времени
        start_time.setTime(start_time.time().addSecs(-start_time.time().second()))  # Округление до минут
        start_time_input = QDateTimeEdit(start_time)
        start_time_input.setCalendarPopup(True)
        start_time_input.setMinimumDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Начало:", start_time_input)
        
        # Окончание
        end_time = start_time.addSecs(3600)  # +1 час от начала
        end_time_input = QDateTimeEdit(end_time)
        end_time_input.setCalendarPopup(True)
        end_time_input.setMinimumDateTime(start_time)
        form_layout.addRow("Окончание:", end_time_input)
        
        # Обновление минимального времени окончания при изменении времени начала
        def update_min_end_time():
            end_time_input.setMinimumDateTime(start_time_input.dateTime())
            if end_time_input.dateTime() < start_time_input.dateTime():
                end_time_input.setDateTime(start_time_input.dateTime().addSecs(3600))
        
        start_time_input.dateTimeChanged.connect(update_min_end_time)
        
        # Примечания
        notes_input = QTextEdit()
        notes_input.setMaximumHeight(100)
        form_layout.addRow("Примечания:", notes_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        # Кнопка сохранения
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(dialog.accept)
        buttons_layout.addWidget(save_button)
        
        # Кнопка отмены
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)
        
        # Добавление формы и кнопок в диалог
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(form_layout)
        dialog_layout.addLayout(buttons_layout)
        dialog.setLayout(dialog_layout)
        
        # Показ диалога
        if dialog.exec_() == QDialog.Accepted:
            # Получение выбранной комнаты
            room_id = room_combo.currentData()
            
            # Получение времени начала и окончания
            start_time = start_time_input.dateTime().toPyDateTime()
            end_time = end_time_input.dateTime().toPyDateTime()
            
            # Создание данных бронирования
            booking_data = {
                "room_id": room_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "notes": notes_input.toPlainText().strip() or None
            }
            
            try:
                # Создание бронирования
                self.parent.parent.booking_controller.create_booking(booking_data)
                
                # Обновление списка бронирований
                self.refresh_data()
                
                QMessageBox.information(self, "Успех", "Бронирование успешно создано")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать бронирование: {str(e)}")
    
    def view_booking(self, booking):
        """Просмотр информации о бронировании"""
        # Создание диалога
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Бронирование #{booking['id']}")
        dialog.setMinimumWidth(400)
        
        # Форма
        form_layout = QFormLayout()
        
        # ID
        id_label = QLabel(str(booking["id"]))
        form_layout.addRow("ID:", id_label)
        
        # Комната
        room_name = booking.get("room_name", "")
        room_label = QLabel(room_name)
        form_layout.addRow("Комната:", room_label)
        
        # Начало
        start_time = datetime.fromisoformat(booking["start_time"].replace("Z", "+00:00"))
        start_time_label = QLabel(start_time.strftime("%d.%m.%Y %H:%M"))
        form_layout.addRow("Начало:", start_time_label)
        
        # Окончание
        end_time = datetime.fromisoformat(booking["end_time"].replace("Z", "+00:00"))
        end_time_label = QLabel(end_time.strftime("%d.%m.%Y %H:%M"))
        form_layout.addRow("Окончание:", end_time_label)
        
        # Статус
        status_map = {
            "pending": "Ожидание",
            "confirmed": "Подтверждено",
            "cancelled": "Отменено",
            "completed": "Завершено"
        }
        status_text = status_map.get(booking["status"], booking["status"])
        status_label = QLabel(status_text)
        form_layout.addRow("Статус:", status_label)
        
        # Стоимость
        price_label = QLabel(f"{booking['total_price']:.2f}")
        form_layout.addRow("Стоимость:", price_label)
        
        # Дата создания
        created_at = datetime.fromisoformat(booking["created_at"].replace("Z", "+00:00"))
        created_at_label = QLabel(created_at.strftime("%d.%m.%Y %H:%M"))
        form_layout.addRow("Дата создания:", created_at_label)
        
        # Примечания
        notes_label = QLabel(booking.get("notes", "") or "")
        notes_label.setWordWrap(True)
        form_layout.addRow("Примечания:", notes_label)
        
        # Кнопка закрытия
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(dialog.accept)
        
        # Добавление формы и кнопки в диалог
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(form_layout)
        dialog_layout.addWidget(close_button)
        dialog.setLayout(dialog_layout)
        
        # Показ диалога
        dialog.exec_()
    
    def edit_booking(self, booking):
        """Редактирование бронирования"""
        # Проверка статуса бронирования
        if booking["status"] not in ["pending", "confirmed"]:
            QMessageBox.warning(self, "Предупреждение", "Нельзя изменить отмененное или завершенное бронирование")
            return
        
        # Создание диалога
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактирование бронирования #{booking['id']}")
        dialog.setMinimumWidth(400)
        
        # Форма
        form_layout = QFormLayout()
        
        # Комната (только для информации)
        room_name = booking.get("room_name", "")
        room_label = QLabel(room_name)
        form_layout.addRow("Комната:", room_label)
        
        # Начало
        start_time = QDateTime.fromString(
            datetime.fromisoformat(booking["start_time"].replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%S"),
            "yyyy-MM-ddThh:mm:ss"
        )
        start_time_input = QDateTimeEdit(start_time)
        start_time_input.setCalendarPopup(True)
        start_time_input.setMinimumDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Начало:", start_time_input)
        
        # Окончание
        end_time = QDateTime.fromString(
            datetime.fromisoformat(booking["end_time"].replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%S"),
            "yyyy-MM-ddThh:mm:ss"
        )
        end_time_input = QDateTimeEdit(end_time)
        end_time_input.setCalendarPopup(True)
        end_time_input.setMinimumDateTime(start_time)
        form_layout.addRow("Окончание:", end_time_input)
        
        # Обновление минимального времени окончания при изменении времени начала
        def update_min_end_time():
            end_time_input.setMinimumDateTime(start_time_input.dateTime())
            if end_time_input.dateTime() < start_time_input.dateTime():
                end_time_input.setDateTime(start_time_input.dateTime().addSecs(3600))
        
        start_time_input.dateTimeChanged.connect(update_min_end_time)
        
        # Примечания
        notes_input = QTextEdit()
        notes_input.setPlainText(booking.get("notes", "") or "")
        notes_input.setMaximumHeight(100)
        form_layout.addRow("Примечания:", notes_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        # Кнопка сохранения
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(dialog.accept)
        buttons_layout.addWidget(save_button)
        
        # Кнопка отмены
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)
        
        # Добавление формы и кнопок в диалог
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(form_layout)
        dialog_layout.addLayout(buttons_layout)
        dialog.setLayout(dialog_layout)
        
        # Показ диалога
        if dialog.exec_() == QDialog.Accepted:
            # Получение времени начала и окончания
            start_time = start_time_input.dateTime().toPyDateTime()
            end_time = end_time_input.dateTime().toPyDateTime()
            
            # Создание данных бронирования
            booking_data = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "notes": notes_input.toPlainText().strip() or None
            }
            
            try:
                # Обновление бронирования
                self.parent.parent.booking_controller.update_booking(booking["id"], booking_data)
                
                # Обновление списка бронирований
                self.refresh_data()
                
                QMessageBox.information(self, "Успех", "Бронирование успешно обновлено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить бронирование: {str(e)}")
    
    def cancel_booking(self, booking):
        """Отмена бронирования"""
        # Проверка статуса бронирования
        if booking["status"] not in ["pending", "confirmed"]:
            QMessageBox.warning(self, "Предупреждение", "Нельзя отменить уже отмененное или завершенное бронирование")
            return
        
        # Подтверждение отмены
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Вы уверены, что хотите отменить бронирование #{booking['id']}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Отмена бронирования
                self.parent.parent.booking_controller.cancel_booking(booking["id"])
                
                # Обновление списка бронирований
                self.refresh_data()
                
                QMessageBox.information(self, "Успех", "Бронирование успешно отменено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось отменить бронирование: {str(e)}")