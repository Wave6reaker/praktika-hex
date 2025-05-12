from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QComboBox, QDateEdit, QFormLayout,
                            QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime, timedelta

class AnalyticsTab(QWidget):
    """Вкладка для просмотра аналитики (только для администраторов)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.revenue_data = []
        self.room_usage_data = []
        self.user_activity_data = []
        self.init_ui()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной контейнер
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Верхняя панель с фильтрами
        top_panel = QHBoxLayout()
        
        # Форма фильтров
        filter_form = QFormLayout()
        
        # Тип отчета
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItem("Доходы", "revenue")
        self.report_type_combo.addItem("Использование комнат", "room-usage")
        self.report_type_combo.addItem("Активность пользователей", "user-activity")
        self.report_type_combo.currentIndexChanged.connect(self.on_report_type_changed)
        filter_form.addRow("Тип отчета:", self.report_type_combo)
        
        # Группировка (только для отчета по доходам)
        self.group_by_combo = QComboBox()
        self.group_by_combo.addItem("По дням", "day")
        self.group_by_combo.addItem("По неделям", "week")
        self.group_by_combo.addItem("По месяцам", "month")
        filter_form.addRow("Группировка:", self.group_by_combo)
        
        # Начальная дата
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        filter_form.addRow("Начальная дата:", self.start_date_edit)
        
        # Конечная дата
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        filter_form.addRow("Конечная дата:", self.end_date_edit)
        
        # Добавление формы фильтров в верхнюю панель
        filter_widget = QWidget()
        filter_widget.setLayout(filter_form)
        top_panel.addWidget(filter_widget)
        
        # Растягивающийся элемент для выравнивания
        top_panel.addStretch()
        
        # Кнопка обновления
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.refresh_data)
        top_panel.addWidget(refresh_button)
        
        # Добавление верхней панели в основной контейнер
        main_layout.addLayout(top_panel)
        
        # Таблица для отображения данных
        self.data_table = QTableWidget()
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        
        # Добавление таблицы в основной контейнер
        main_layout.addWidget(self.data_table)
        
        # Установка основного контейнера
        self.setLayout(main_layout)
        
        # Инициализация таблицы для текущего типа отчета
        self.on_report_type_changed()
    
    def on_report_type_changed(self):
        """Обработка изменения типа отчета"""
        report_type = self.report_type_combo.currentData()
        
        # Показать/скрыть группировку в зависимости от типа отчета
        self.group_by_combo.setVisible(report_type == "revenue")
        self.layout().itemAt(0).layout().labelForField(self.group_by_combo).setVisible(report_type == "revenue")
        
        # Настройка таблицы в зависимости от типа отчета
        if report_type == "revenue":
            self.data_table.setColumnCount(2)
            self.data_table.setHorizontalHeaderLabels(["Дата", "Доход"])
        elif report_type == "room-usage":
            self.data_table.setColumnCount(6)
            self.data_table.setHorizontalHeaderLabels([
                "ID комнаты", "Название", "Кол-во бронирований", 
                "Общий доход", "Общее время (ч)", "Загруженность (%)"
            ])
        elif report_type == "user-activity":
            self.data_table.setColumnCount(5)
            self.data_table.setHorizontalHeaderLabels([
                "ID пользователя", "Имя пользователя", "Email", 
                "Кол-во бронирований", "Общие расходы"
            ])
    
    def refresh_data(self):
        """Обновление данных аналитики"""
        # Проверка прав доступа
        if not self.parent.user_data or self.parent.user_data.get("role") != "admin":
            QMessageBox.warning(self, "Предупреждение", "Только администраторы могут просматривать аналитику")
            return
        
        # Получение параметров
        report_type = self.report_type_combo.currentData()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        try:
            # Получение данных в зависимости от типа отчета
            if report_type == "revenue":
                group_by = self.group_by_combo.currentData()
                params = {
                    "start_date": f"{start_date}T00:00:00",
                    "end_date": f"{end_date}T23:59:59",
                    "group_by": group_by
                }
                self.revenue_data = self.parent.parent.api_client.get("/analytics/revenue", params=params)
                self.update_revenue_table()
            
            elif report_type == "room-usage":
                params = {
                    "start_date": f"{start_date}T00:00:00",
                    "end_date": f"{end_date}T23:59:59"
                }
                self.room_usage_data = self.parent.parent.api_client.get("/analytics/room-usage", params=params)
                self.update_room_usage_table()
            
            elif report_type == "user-activity":
                params = {
                    "start_date": f"{start_date}T00:00:00",
                    "end_date": f"{end_date}T23:59:59",
                    "limit": 100
                }
                self.user_activity_data = self.parent.parent.api_client.get("/analytics/user-activity", params=params)
                self.update_user_activity_table()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные аналитики: {str(e)}")
    
    def update_revenue_table(self):
        """Обновление таблицы доходов"""
        # Очистка таблицы
        self.data_table.setRowCount(0)
        
        # Заполнение таблицы
        for row, data in enumerate(self.revenue_data):
            self.data_table.insertRow(row)
            
            # Дата
            self.data_table.setItem(row, 0, QTableWidgetItem(data["date"]))
            
            # Доход
            self.data_table.setItem(row, 1, QTableWidgetItem(f"{data['revenue']:.2f}"))
    
    def update_room_usage_table(self):
        """Обновление таблицы использования комнат"""
        # Очистка таблицы
        self.data_table.setRowCount(0)
        
        # Заполнение таблицы
        for row, data in enumerate(self.room_usage_data):
            self.data_table.insertRow(row)
            
            # ID комнаты
            self.data_table.setItem(row, 0, QTableWidgetItem(str(data["room_id"])))
            
            # Название
            self.data_table.setItem(row, 1, QTableWidgetItem(data["room_name"]))
            
            # Кол-во бронирований
            self.data_table.setItem(row, 2, QTableWidgetItem(str(data["booking_count"])))
            
            # Общий доход
            self.data_table.setItem(row, 3, QTableWidgetItem(f"{data['total_revenue']:.2f}"))
            
            # Общее время
            self.data_table.setItem(row, 4, QTableWidgetItem(f"{data['total_hours']:.2f}"))
            
            # Загруженность
            self.data_table.setItem(row, 5, QTableWidgetItem(f"{data['occupancy_rate']:.2f}%"))
    
    def update_user_activity_table(self):
        """Обновление таблицы активности пользователей"""
        # Очистка таблицы
        self.data_table.setRowCount(0)
        
        # Заполнение таблицы
        for row, data in enumerate(self.user_activity_data):
            self.data_table.insertRow(row)
            
            # ID пользователя
            self.data_table.setItem(row, 0, QTableWidgetItem(str(data["user_id"])))
            
            # Имя пользователя
            self.data_table.setItem(row, 1, QTableWidgetItem(data["username"]))
            
            # Email
            self.data_table.setItem(row, 2, QTableWidgetItem(data["email"]))
            
            # Кол-во бронирований
            self.data_table.setItem(row, 3, QTableWidgetItem(str(data["booking_count"])))
            
            # Общие расходы
            self.data_table.setItem(row, 4, QTableWidgetItem(f"{data['total_spent']:.2f}"))