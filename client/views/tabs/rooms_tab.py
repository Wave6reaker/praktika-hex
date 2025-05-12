from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QMessageBox, QDialog, QFormLayout, QLineEdit,
                            QSpinBox, QDoubleSpinBox, QCheckBox, QTextEdit)
from PyQt5.QtCore import Qt

class RoomsTab(QWidget):
    """Вкладка для управления комнатами"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
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
        title_label = QLabel("Управление комнатами")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        top_panel.addWidget(title_label)
        
        # Растягивающийся элемент для выравнивания
        top_panel.addStretch()
        
        # Кнопка добавления комнаты (только для администраторов)
        self.add_room_button = QPushButton("Добавить комнату")
        self.add_room_button.clicked.connect(self.add_room)
        top_panel.addWidget(self.add_room_button)
        
        # Кнопка обновления списка
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.refresh_data)
        top_panel.addWidget(refresh_button)
        
        # Добавление верхней панели в основной контейнер
        main_layout.addLayout(top_panel)
        
        # Таблица комнат
        self.rooms_table = QTableWidget()
        self.rooms_table.setColumnCount(8)
        self.rooms_table.setHorizontalHeaderLabels([
            "ID", "Название", "Вместимость", "Цена/час", 
            "Проектор", "Доска", "Видеоконференция", "Действия"
        ])
        self.rooms_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rooms_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.rooms_table.horizontalHeader().setStretchLastSection(True)
        
        # Добавление таблицы в основной контейнер
        main_layout.addWidget(self.rooms_table)
        
        # Установка основного контейнера
        self.setLayout(main_layout)
    
    def refresh_data(self):
        """Обновление списка комнат"""
        try:
            # Получение списка комнат
            self.rooms = self.parent.parent.room_controller.get_rooms()
            
            # Обновление таблицы
            self.update_table()
            
            # Скрытие кнопки добавления комнаты для обычных пользователей
            is_admin = self.parent.user_data and self.parent.user_data.get("role") == "admin"
            self.add_room_button.setVisible(is_admin)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить список комнат: {str(e)}")
    
    def update_table(self):
        """Обновление таблицы комнат"""
        # Очистка таблицы
        self.rooms_table.setRowCount(0)
        
        # Заполнение таблицы
        for row, room in enumerate(self.rooms):
            self.rooms_table.insertRow(row)
            
            # ID
            self.rooms_table.setItem(row, 0, QTableWidgetItem(str(room["id"])))
            
            # Название
            self.rooms_table.setItem(row, 1, QTableWidgetItem(room["name"]))
            
            # Вместимость
            self.rooms_table.setItem(row, 2, QTableWidgetItem(str(room["capacity"])))
            
            # Цена/час
            self.rooms_table.setItem(row, 3, QTableWidgetItem(f"{room['price_per_hour']:.2f}"))
            
            # Проектор
            self.rooms_table.setItem(row, 4, QTableWidgetItem("Да" if room["has_projector"] else "Нет"))
            
            # Доска
            self.rooms_table.setItem(row, 5, QTableWidgetItem("Да" if room["has_whiteboard"] else "Нет"))
            
            # Видеоконференция
            self.rooms_table.setItem(row, 6, QTableWidgetItem("Да" if room["has_video_conf"] else "Нет"))
            
            # Кнопки действий
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            # Кнопка просмотра
            view_button = QPushButton("Просмотр")
            view_button.clicked.connect(lambda _, r=room: self.view_room(r))
            actions_layout.addWidget(view_button)
            
            # Кнопка редактирования (только для администраторов)
            if self.parent.user_data and self.parent.user_data.get("role") == "admin":
                edit_button = QPushButton("Изменить")
                edit_button.clicked.connect(lambda _, r=room: self.edit_room(r))
                actions_layout.addWidget(edit_button)
                
                # Кнопка удаления (только для администраторов)
                delete_button = QPushButton("Удалить")
                delete_button.clicked.connect(lambda _, r=room: self.delete_room(r))
                actions_layout.addWidget(delete_button)
            
            actions_widget.setLayout(actions_layout)
            self.rooms_table.setCellWidget(row, 7, actions_widget)
    
    def add_room(self):
        """Добавление новой комнаты"""
        # Проверка прав доступа
        if not self.parent.user_data or self.parent.user_data.get("role") != "admin":
            QMessageBox.warning(self, "Предупреждение", "Только администраторы могут добавлять комнаты")
            return
        
        # Создание диалога
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление комнаты")
        dialog.setMinimumWidth(400)
        
        # Форма
        form_layout = QFormLayout()
        
        # Название
        name_input = QLineEdit()
        form_layout.addRow("Название:", name_input)
        
        # Описание
        description_input = QTextEdit()
        description_input.setMaximumHeight(100)
        form_layout.addRow("Описание:", description_input)
        
        # Вместимость
        capacity_input = QSpinBox()
        capacity_input.setMinimum(1)
        capacity_input.setMaximum(100)
        capacity_input.setValue(10)
        form_layout.addRow("Вместимость:", capacity_input)
        
        # Цена/час
        price_input = QDoubleSpinBox()
        price_input.setMinimum(0)
        price_input.setMaximum(10000)
        price_input.setValue(100)
        price_input.setSingleStep(10)
        form_layout.addRow("Цена/час:", price_input)
        
        # Проектор
        projector_input = QCheckBox()
        form_layout.addRow("Проектор:", projector_input)
        
        # Доска
        whiteboard_input = QCheckBox()
        form_layout.addRow("Доска:", whiteboard_input)
        
        # Видеоконференция
        video_conf_input = QCheckBox()
        form_layout.addRow("Видеоконференция:", video_conf_input)
        
        # URL изображения
        image_url_input = QLineEdit()
        form_layout.addRow("URL изображения:", image_url_input)
        
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
            # Создание данных комнаты
            room_data = {
                "name": name_input.text().strip(),
                "description": description_input.toPlainText().strip(),
                "capacity": capacity_input.value(),
                "price_per_hour": price_input.value(),
                "has_projector": projector_input.isChecked(),
                "has_whiteboard": whiteboard_input.isChecked(),
                "has_video_conf": video_conf_input.isChecked(),
                "image_url": image_url_input.text().strip() or None
            }
            
            # Проверка обязательных полей
            if not room_data["name"]:
                QMessageBox.warning(self, "Предупреждение", "Название комнаты обязательно")
                return
            
            try:
                # Создание комнаты
                self.parent.parent.room_controller.create_room(room_data)
                
                # Обновление списка комнат
                self.refresh_data()
                
                QMessageBox.information(self, "Успех", "Комната успешно добавлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить комнату: {str(e)}")
    
    def view_room(self, room):
        """Просмотр информации о комнате"""
        # Создание диалога
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Комната: {room['name']}")
        dialog.setMinimumWidth(400)
        
        # Форма
        form_layout = QFormLayout()
        
        # ID
        id_label = QLabel(str(room["id"]))
        form_layout.addRow("ID:", id_label)
        
        # Название
        name_label = QLabel(room["name"])
        form_layout.addRow("Название:", name_label)
        
        # Описание
        description_label = QLabel(room["description"] or "")
        description_label.setWordWrap(True)
        form_layout.addRow("Описание:", description_label)
        
        # Вместимость
        capacity_label = QLabel(str(room["capacity"]))
        form_layout.addRow("Вместимость:", capacity_label)
        
        # Цена/час
        price_label = QLabel(f"{room['price_per_hour']:.2f}")
        form_layout.addRow("Цена/час:", price_label)
        
        # Проектор
        projector_label = QLabel("Да" if room["has_projector"] else "Нет")
        form_layout.addRow("Проектор:", projector_label)
        
        # Доска
        whiteboard_label = QLabel("Да" if room["has_whiteboard"] else "Нет")
        form_layout.addRow("Доска:", whiteboard_label)
        
        # Видеоконференция
        video_conf_label = QLabel("Да" if room["has_video_conf"] else "Нет")
        form_layout.addRow("Видеоконференция:", video_conf_label)
        
        # Активность
        active_label = QLabel("Да" if room["is_active"] else "Нет")
        form_layout.addRow("Активна:", active_label)
        
        # URL изображения
        image_url_label = QLabel(room["image_url"] or "")
        image_url_label.setWordWrap(True)
        form_layout.addRow("URL изображения:", image_url_label)
        
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
    
    def edit_room(self, room):
        """Редактирование комнаты"""
        # Проверка прав доступа
        if not self.parent.user_data or self.parent.user_data.get("role") != "admin":
            QMessageBox.warning(self, "Предупреждение", "Только администраторы могут редактировать комнаты")
            return
        
        # Создание диалога
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактирование комнаты: {room['name']}")
        dialog.setMinimumWidth(400)
        
        # Форма
        form_layout = QFormLayout()
        
        # Название
        name_input = QLineEdit(room["name"])
        form_layout.addRow("Название:", name_input)
        
        # Описание
        description_input = QTextEdit()
        description_input.setPlainText(room["description"] or "")
        description_input.setMaximumHeight(100)
        form_layout.addRow("Описание:", description_input)
        
        # Вместимость
        capacity_input = QSpinBox()
        capacity_input.setMinimum(1)
        capacity_input.setMaximum(100)
        capacity_input.setValue(room["capacity"])
        form_layout.addRow("Вместимость:", capacity_input)
        
        # Цена/час
        price_input = QDoubleSpinBox()
        price_input.setMinimum(0)
        price_input.setMaximum(10000)
        price_input.setValue(room["price_per_hour"])
        price_input.setSingleStep(10)
        form_layout.addRow("Цена/час:", price_input)
        
        # Проектор
        projector_input = QCheckBox()
        projector_input.setChecked(room["has_projector"])
        form_layout.addRow("Проектор:", projector_input)
        
        # Доска
        whiteboard_input = QCheckBox()
        whiteboard_input.setChecked(room["has_whiteboard"])
        form_layout.addRow("Доска:", whiteboard_input)
        
        # Видеоконференция
        video_conf_input = QCheckBox()
        video_conf_input.setChecked(room["has_video_conf"])
        form_layout.addRow("Видеоконференция:", video_conf_input)
        
        # Активность
        active_input = QCheckBox()
        active_input.setChecked(room["is_active"])
        form_layout.addRow("Активна:", active_input)
        
        # URL изображения
        image_url_input = QLineEdit(room["image_url"] or "")
        form_layout.addRow("URL изображения:", image_url_input)
        
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
            # Создание данных комнаты
            room_data = {
                "name": name_input.text().strip(),
                "description": description_input.toPlainText().strip(),
                "capacity": capacity_input.value(),
                "price_per_hour": price_input.value(),
                "has_projector": projector_input.isChecked(),
                "has_whiteboard": whiteboard_input.isChecked(),
                "has_video_conf": video_conf_input.isChecked(),
                "is_active": active_input.isChecked(),
                "image_url": image_url_input.text().strip() or None
            }
            
            # Проверка обязательных полей
            if not room_data["name"]:
                QMessageBox.warning(self, "Предупреждение", "Название комнаты обязательно")
                return
            
            try:
                # Обновление комнаты
                self.parent.parent.room_controller.update_room(room["id"], room_data)
                
                # Обновление списка комнат
                self.refresh_data()
                
                QMessageBox.information(self, "Успех", "Комната успешно обновлена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить комнату: {str(e)}")
    
    def delete_room(self, room):
        """Удаление комнаты"""
        # Проверка прав доступа
        if not self.parent.user_data or self.parent.user_data.get("role") != "admin":
            QMessageBox.warning(self, "Предупреждение", "Только администраторы могут удалять комнаты")
            return
        
        # Подтверждение удаления
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Вы уверены, что хотите удалить комнату '{room['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Удаление комнаты
                self.parent.parent.room_controller.delete_room(room["id"])
                
                # Обновление списка комнат
                self.refresh_data()
                
                QMessageBox.information(self, "Успех", "Комната успешно удалена")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить комнату: {str(e)}")