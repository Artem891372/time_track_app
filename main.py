from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
import sys
import colorsys
import random
import sqlite3
from datetime import datetime, timedelta
import json

class SimpleColorGenerator:
    """Простой генератор хорошо различимых цветов"""
    
    @staticmethod
    def get_colors(n, theme='both'):
        """
        Возвращает n хорошо различимых цветов
        
        Args:
            n: количество цветов
            theme: 'light', 'dark' или 'both' (для любой темы)
        """
        colors = []
        
        # Золотое сечение для равномерного распределения
        golden_ratio_conjugate = 0.618033988749895
        
        for i in range(n):
            hue = (i * golden_ratio_conjugate) % 1.0
            
            if theme == 'light':
                # Для светлой темы - более насыщенные цвета
                saturation = 0.7 + random.uniform(0.1, 0.2)
                value = 0.7 + random.uniform(0.1, 0.2)
            elif theme == 'dark':
                # Для темной темы - более яркие цвета
                saturation = 0.6 + random.uniform(0.1, 0.2)
                value = 0.8 + random.uniform(0.1, 0.15)
            else:  # both
                # Компромиссный вариант
                saturation = 0.65 + random.uniform(0.1, 0.2)
                value = 0.75 + random.uniform(0.1, 0.15)
            
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(QtGui.QColor(int(r * 255), int(g * 255), int(b * 255)))
        
        return colors
    
    @staticmethod
    def get_text_color(background_color):
        """Возвращает черный или белый в зависимости от яркости фона"""
        luminance = (0.299 * background_color.red() + 
                    0.587 * background_color.green() + 
                    0.114 * background_color.blue()) / 255
        return QtGui.QColor(0, 0, 0) if luminance > 0.55 else QtGui.QColor(255, 255, 255)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)  # Увеличил размер окна для лучшего отображения
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        # Контейнер для диаграммы с выбором периода
        self.chart_container = QtWidgets.QWidget(parent=self.centralwidget)
        self.chart_container.setObjectName("chart_container")
        self.chart_layout = QtWidgets.QVBoxLayout(self.chart_container)
        self.chart_layout.setObjectName("chart_layout")
        
        # Комбобокс для выбора периода диаграммы (добавлен)
        self.chart_period_combo = QtWidgets.QComboBox(parent=self.chart_container)
        self.chart_period_combo.setObjectName("chart_period_combo")
        self.chart_period_combo.addItems(["День", "Неделя", "Месяц"])
        self.chart_layout.addWidget(self.chart_period_combo)
        
        # Виджет для самой диаграммы (будет заполнен в MainWindow)
        self.chart_widget = QtWidgets.QWidget(parent=self.chart_container)
        self.chart_widget.setObjectName("chart_widget")
        self.chart_layout.addWidget(self.chart_widget)
        
        # Помещаем контейнер диаграммы на его место (0,0,2,1)
        self.gridLayout.addWidget(self.chart_container, 0, 0, 2, 1)
        
        # Остальные элементы остаются на своих местах
        self.progress_hour_day = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progress_hour_day.setProperty("value", 0)
        self.progress_hour_day.setObjectName("progress_hour_day")
        self.gridLayout.addWidget(self.progress_hour_day, 3, 2, 1, 1)
        
        self.type_combo_box = QtWidgets.QComboBox(parent=self.centralwidget)
        self.type_combo_box.setObjectName("type_combo_box")
        self.gridLayout.addWidget(self.type_combo_box, 2, 0, 1, 2)
        
        self.start_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.start_button.setObjectName("start_button")
        self.gridLayout.addWidget(self.start_button, 2, 2, 1, 1)
        
        self.progress_hour_week = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progress_hour_week.setProperty("value", 0)
        self.progress_hour_week.setObjectName("progress_hour_week")
        self.gridLayout.addWidget(self.progress_hour_week, 4, 2, 1, 1)
        
        self.dateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit.setDate(QtCore.QDate.currentDate())
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setCalendarPopup(True)
        self.gridLayout.addWidget(self.dateEdit, 0, 2, 1, 1)

        self.time_number = QtWidgets.QLCDNumber(parent=self.centralwidget)
        self.time_number.setEnabled(True)
        self.time_number.setMode(QtWidgets.QLCDNumber.Mode.Oct)
        self.time_number.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Filled)
        self.time_number.setObjectName("time_number")
        self.gridLayout.addWidget(self.time_number, 1, 2, 1, 1)

        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 0, 1, 2)
        
        # Кнопка обновления диаграммы (добавлена)
        self.refresh_chart_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.refresh_chart_button.setObjectName("refresh_chart_button")
        self.gridLayout.addWidget(self.refresh_chart_button, 5, 0, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Таймер работы"))
        self.start_button.setText(_translate("MainWindow", "Начать"))
        self.label_2.setText(_translate("MainWindow", "Часов в среднем на день выполнено:"))
        self.label.setText(_translate("MainWindow", "Часов на неделе выполнено:"))
        self.refresh_chart_button.setText(_translate("MainWindow", "Обновить диаграмму"))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Настройка секундомера
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.setInterval(1000)

        self.elapsed_timer = QtCore.QElapsedTimer()
        self.offset = 0
        self.is_running = False
        self.last_update_time = 0

        self.ui.time_number.display("00:00:00")
        self.ui.time_number.setDigitCount(9) 
        self.ui.time_number.setMode(QtWidgets.QLCDNumber.Mode.Dec)
        self.ui.start_button.clicked.connect(self.on_start_pause)
        self.ui.refresh_chart_button.clicked.connect(self.update_chart)
        self.ui.chart_period_combo.currentIndexChanged.connect(self.update_chart)

        # Инициализация диаграммы
        self.init_chart()

        # Читаем конфиг и задаем значения для комбобокса
        self.config_data = self.read_config()

        for event_name, hour_week in self.config_data['type_events'].items():
            self.ui.type_combo_box.addItem(event_name)

        self.ui.type_combo_box.currentIndexChanged.connect(self.change_current_type_event)
        self.ui.type_combo_box.setCurrentIndex(0)

        # Загружаем данные для начального типа события
        self.change_current_type_event()
        
        # Обновляем диаграмму при запуске
        self.update_chart()

    def init_chart(self):
        """Инициализация диаграммы"""
        self.chart = QChart()
        self.chart.setTitle("Распределение времени")
        #self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        layout = QtWidgets.QVBoxLayout(self.ui.chart_widget)
        layout.addWidget(self.chart_view)
        self.ui.chart_widget.setLayout(layout)

    def read_config(self, config_path='config.json'):
        with open(config_path, mode='r') as f:
            return json.load(f)
        
    def get_period_data(self, period):
        """
        Получает данные для указанного периода
        
        Args:
            period: 'День', 'Неделя' или 'Месяц'
        """
        connection = sqlite3.connect('main.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        if period == 'День':
            cursor.execute("""
                SELECT event_name, SUM(complite_sec) as total_seconds 
                FROM tasks 
                WHERE date_day = date('now')
                GROUP BY event_name
            """)
        elif period == 'Неделя':
            cursor.execute("""
                SELECT event_name, SUM(complite_sec) as total_seconds 
                FROM tasks 
                WHERE date_day >= date('now', '-6 days') AND date_day <= date('now')
                GROUP BY event_name
            """)
        elif period == 'Месяц':
            cursor.execute("""
                SELECT event_name, SUM(complite_sec) as total_seconds 
                FROM tasks 
                WHERE date_day >= date('now', '-30 days') AND date_day <= date('now')
                GROUP BY event_name
            """)
        
        results = cursor.fetchall()
        connection.close()
        
        # Преобразуем в словарь
        data = {}
        total_seconds = 0
        for row in results:
            data[row['event_name']] = row['total_seconds']
            total_seconds += row['total_seconds']
        
        # Добавляем "Неучтенное время" (разница до 24 часов)
        if period == 'День':
            remaining_time = 24 * 3600 - total_seconds
            if remaining_time > 0:
                data['Неучтенное время'] = remaining_time
                total_seconds += remaining_time
        elif period == 'Неделя':
            remaining_time = 7 * 24 * 3600 - total_seconds
            if remaining_time > 0:
                data['Неучтенное время'] = remaining_time
                total_seconds += remaining_time
        elif period == 'Месяц':
            # Для месяца не добавляем неучтенное время
            pass
        
        return data, total_seconds

    def update_chart(self):
        """Обновление круговой диаграммы"""
        period = self.ui.chart_period_combo.currentText()
        data, total_seconds = self.get_period_data(period)
        
        # Удаляем старые серии
        self.chart.removeAllSeries()
        
        if not data:
            # Нет данных - показываем пустую диаграмму
            self.chart.setTitle(f"{period}: Нет данных")
            return
        
        # Создаем новую серию
        series = QPieSeries()
        series.setLabelsVisible(True)
        
        # Генерируем цвета
        colors = SimpleColorGenerator.get_colors(len(data))
        
        for (label, value), color in zip(data.items(), colors):
            # Преобразуем секунды в проценты
            percentage = (value / total_seconds * 100) if total_seconds > 0 else 0
            
            # Преобразуем секунды в часы для отображения
            hours = value / 3600
            
            slice = QPieSlice(f"{percentage:.1f}%", percentage)
            slice.setColor(color)
            
            # Настройка отображения текста
            slice.setLabelVisible(True)
            slice.setLabelPosition(QPieSlice.LabelPosition.LabelInsideNormal)
            
            # Подключаем обработчик наведения
            slice.setLabelFont(QtGui.QFont("Arial", 10))
            #slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))
            
            series.append(slice)
        
        # Добавляем серию на диаграмму
        self.chart.addSeries(series)
        self.chart.setTitle(f"{period}: {total_seconds/3600:.1f} часов")
        
        # Настройка легенды
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.chart_view.chart().legend().setFont(QtGui.QFont("Arial", 8))
        labels = list(data.keys())
        for i, marker in enumerate(self.chart.legend().markers()):
            if i < len(data):
                marker.setLabel(labels[i])

    def on_slice_hovered(self, state, slice):
        """Обработчик наведения на сектор"""
        if state:
            slice.setExploded(True)
        else:
            slice.setExploded(False)

    def update_type_event(self, event_name, indx=None):
        if not indx:
            self.ui.type_combo_box.addItem(event_name)
        else:
            self.ui.type_combo_box.setItemText(indx, event_name)
            self.change_current_type_event()

    def update_today_data(self, event_name, complite_sec):
        """Обновляет данные в БД с указанным количеством секунд"""
        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()

        cursor.execute("SELECT complite_sec FROM tasks WHERE event_name=? AND date_day = date('now');", (event_name,))
        result = cursor.fetchone()
        
        current_seconds = result[0] if result else 0
        
        if complite_sec != current_seconds:
            cursor.execute("""
                UPDATE tasks 
                SET complite_sec=?, last_update=?
                WHERE event_name=? AND date_day = date('now');
            """, (complite_sec, datetime.now().isoformat(), event_name))
            
            connection.commit()
        
        connection.close()

    def get_today_data_for_type(self, event_name):
        connection = sqlite3.connect('main.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM tasks WHERE event_name=? AND date_day = date('now');", (event_name,))
        results = cursor.fetchall()

        if len(results) == 0:
            cursor.execute("""
                INSERT INTO tasks (event_name, date_day, complite_sec, hour_week_limit, start_datetime, last_update)
                VALUES (?, date('now'), 0, ?, NULL, NULL);
            """, (event_name, self.config_data['type_events'][event_name]))

            connection.commit()
            connection.close()
            
            return self.get_today_data_for_type(event_name)
        
        connection.close()
        return results
    
    def get_last_week_data_for_type(self, event_name):
        connection = sqlite3.connect('main.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM tasks 
            WHERE event_name=? AND date_day >= date('now', '-6 days') AND date_day <= date('now');
        """, (event_name,))
        results = cursor.fetchall()
        connection.close()
            
        return results

    def change_current_type_event(self):
        current_type = self.ui.type_combo_box.currentText()
        if current_type and current_type in self.config_data['type_events']:
            max_week_hour_for_type = self.config_data['type_events'][current_type]
            today_data = self.get_today_data_for_type(current_type)
            last_week_data = self.get_last_week_data_for_type(current_type)
            
            completed_seconds_today = today_data[0]["complite_sec"] if today_data else 0
            self.ui.progress_hour_day.setValue(completed_seconds_today)
            
            sum_week_secs = sum(d["complite_sec"] for d in last_week_data)
            self.ui.progress_hour_week.setValue(sum_week_secs)

            daily_max_seconds = int((max_week_hour_for_type * 3600) / 7)
            weekly_max_seconds = max_week_hour_for_type * 3600
            
            self.ui.progress_hour_day.setMaximum(daily_max_seconds)
            self.ui.progress_hour_week.setMaximum(weekly_max_seconds)

            self.offset = completed_seconds_today * 1000
            hours = int(completed_seconds_today // 3600)
            minutes = int((completed_seconds_today % 3600) // 60)
            seconds = int(completed_seconds_today % 60)
            
            text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.ui.time_number.display(text)
            self.elapsed_timer.restart()

    def update_display(self):
        """Обновление отображения времени"""
        if not self.is_running:
            return
            
        elapsed = self.elapsed_timer.elapsed() + self.offset
        total_seconds = elapsed / 1000.0
        
        current_time = int(total_seconds)
        if current_time >= self.last_update_time + 10:
            current_type = self.ui.type_combo_box.currentText()
            if current_type and current_type in self.config_data['type_events']:
                self.update_today_data(current_type, current_time)
                self.last_update_time = current_time
                self.change_current_type_event()
                # Обновляем диаграмму, если смотрим текущий день
                #if self.ui.chart_period_combo.currentText() == 'День':
                    #self.update_chart()
        
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.ui.time_number.display(text)

    def on_start_pause(self):
        """Обработчик нажатия кнопки Старт/Пауза"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            self.ui.start_button.setText("Старт")
            
            current_type = self.ui.type_combo_box.currentText()
            if current_type and current_type in self.config_data['type_events']:
                elapsed = self.elapsed_timer.elapsed() + self.offset
                completed_seconds = int(elapsed / 1000)
                self.update_today_data(current_type, completed_seconds)
                # Обновляем диаграмму
                self.update_chart()
        else:
            self.elapsed_timer.start()
            self.timer.start()
            self.is_running = True
            self.ui.start_button.setText("Пауза")
            self.last_update_time = 0

if __name__ == "__main__":
    # Инициализация базы данных
    conn = sqlite3.connect('main.db')
    
    with open('init.sql', 'r') as f:
        schema = f.read()
        conn.executescript(schema)
    
    conn.close()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())