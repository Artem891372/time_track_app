from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PyQt6.QtCore import QMargins
import sys
import colorsys
import random
import sqlite3
from datetime import datetime
import math

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
        # Формула относительной яркости
        luminance = (0.299 * background_color.red() + 
                    0.587 * background_color.green() + 
                    0.114 * background_color.blue()) / 255
        
        # Пороговое значение можно настроить
        return QtGui.QColor(0, 0, 0) if luminance > 0.55 else QtGui.QColor(255, 255, 255)

class ClockPieChart(QChart):
    """Круговая диаграмма в виде часов с легендой"""
    
    def __init__(self):
        super().__init__()
        
        # Создаем серию для часового диска
        self.clock_series = QPieSeries()
        
        # Создаем 12 секторов для часов (каждый по 30 градусов)
        self.hours_data = {}
        for hour in range(12):
            hour_name = f"{hour+1}"
            self.hours_data[hour_name] = 1  # Каждый сектор равен 1/12
        
        # Основная серия для данных
        self.data_series = QPieSeries()
        
        # Добавляем обе серии в диаграмму
        self.addSeries(self.clock_series)
        self.addSeries(self.data_series)
        
        self.setup_clock_disk()
        self.setup_legend()
        
    def setup_clock_disk(self):
        """Настройка часового диска (фон)"""
        # Добавляем сектора часов
        for hour_name, value in self.hours_data.items():
            slice = self.clock_series.append(hour_name, value)
            slice.setColor(QtGui.QColor(240, 240, 240))  # Светло-серый фон
            slice.setBorderColor(QtGui.QColor(200, 200, 200))
            slice.setBorderWidth(1)
            slice.setLabelVisible(False)
            slice.setExplodeDistanceFactor(0)  # Не выдвигать
        
        # Настройка внешнего вида часового диска
        self.clock_series.setHoleSize(0.6)  # Делаем отверстие в центре
        
    def setup_legend(self):
        """Настройка легенды"""
        legend = self.legend()
        legend.setVisible(True)
        legend.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        
        # Увеличиваем отступы для легенды
        legend.setContentsMargins(0, 0, 0, 0)
        legend.setLabelColor(QtGui.QColor(0, 0, 0))
        
        # Увеличиваем шрифт легенды
        font = legend.font()
        font.setPointSize(9)
        legend.setFont(font)
        
        # Настраиваем отступы диаграммы
        self.setMargins(QMargins(10, 10, 150, 10))  # Право 150px для легенды
        
    def add_data_slice(self, label, value, color):
        """Добавление сектора данных"""
        # Проверяем, не превышает ли сумма 100%
        total = sum(slice.value() for slice in self.data_series.slices())
        if total + value > 100:
            value = 100 - total
        
        # Создаем сектор
        slice = self.data_series.append(label, value)
        slice.setColor(color)
        slice.setBorderColor(QtGui.QColor(255, 255, 255))
        slice.setBorderWidth(2)
        
        # Настройка подписей
        slice.setLabelVisible(True)
        slice.setLabelPosition(QPieSlice.LabelPosition.LabelInsideNormal)
        
        # Автоматический выбор цвета текста
        text_color = SimpleColorGenerator.get_text_color(color)
        slice.setLabelColor(text_color)
        
        # Форматирование подписи
        slice.setLabel(f"{label}\n{value:.1f}%")
        
        # Подключаем обработчик наведения
        slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))
        
        # Обновляем легенду
        self.update_legend_label(label)
        
        return slice
    
    def update_legend_label(self, label):
        """Обновление метки в легенде"""
        for marker in self.legend().markers(self.data_series):
            if marker.slice().label().split('\n')[0] == label:
                # Устанавливаем полный текст без обрезания
                marker.setLabel(label)
                
                # Увеличиваем максимальную ширину для легенды
                marker.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))
                marker.setBrush(QtGui.QBrush(marker.slice().color()))
                
                break
    
    def on_slice_hovered(self, state, slice):
        """Обработчик наведения на сектор"""
        if state:
            slice.setExploded(True)
            slice.setExplodeDistanceFactor(0.05)
        else:
            slice.setExploded(False)
    
    def clear_data_slices(self):
        """Очистка всех секторов данных"""
        self.data_series.clear()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)  # Увеличили ширину для легенды
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        # Настройка размера столбцов
        self.gridLayout.setColumnStretch(0, 2)  # Диаграмма
        self.gridLayout.setColumnStretch(1, 1)  # Легенда и контролы
        
        self.progress_hour_day = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progress_hour_day.setProperty("value", 0)
        self.progress_hour_day.setObjectName("progress_hour_day")
        self.gridLayout.addWidget(self.progress_hour_day, 3, 1, 1, 1)
        
        self.type_combo_box = QtWidgets.QComboBox(parent=self.centralwidget)
        self.type_combo_box.setObjectName("type_combo_box")
        self.gridLayout.addWidget(self.type_combo_box, 2, 0, 1, 2)
        
        self.start_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.start_button.setObjectName("start_button")
        self.gridLayout.addWidget(self.start_button, 2, 1, 1, 1)
        
        self.progress_hour_week = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progress_hour_week.setProperty("value", 0)
        self.progress_hour_week.setObjectName("progress_hour_week")
        self.gridLayout.addWidget(self.progress_hour_week, 4, 1, 1, 1)
        
        self.dateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit.setDate(QtCore.QDate.currentDate())
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setCalendarPopup(True)
        self.gridLayout.addWidget(self.dateEdit, 0, 1, 1, 1)

        self.time_number = QtWidgets.QLCDNumber(parent=self.centralwidget)
        self.time_number.setEnabled(True)
        self.time_number.setMode(QtWidgets.QLCDNumber.Mode.Oct)
        self.time_number.setSegmentStyle(QtWidgets.QLCDNumber.SegmentStyle.Filled)
        self.time_number.setObjectName("time_number")
        self.gridLayout.addWidget(self.time_number, 1, 1, 1, 1)

        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 0, 1, 2)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 806, 24))
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

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Настройка секундомера
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.setInterval(10)  # 10 мс для миллисекунд

        self.elapsed_timer = QtCore.QElapsedTimer()
        self.offset = 0
        self.is_running = False

        self.ui.time_number.setDigitCount(11)  # Для mm:ss.zzz
        self.ui.time_number.display("00:00:00.00")

        self.ui.start_button.clicked.connect(self.on_start_pause)
        
        # Создаем часовую диаграмму
        self.chart = ClockPieChart()
        self.chart.setTitle("Распределение времени по задачам")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Настраиваем цвета
        self.colors = SimpleColorGenerator.get_colors(100)
        
        # Добавляем начальные данные
        self.add_initial_data()
        
        # Создаем view для диаграммы
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Устанавливаем минимальный размер для правильного отображения
        self.chart_view.setMinimumSize(600, 400)
        
        self.ui.gridLayout.addWidget(self.chart_view, 0, 0, 2, 1)

        # Читаем конфиг и задаем значения для комбобокса
        self.config_data = self.read_config()

        for event_name, hour_week in self.config_data['type_events'].items():
            self.update_type_event(event_name)

        self.ui.type_combo_box.currentIndexChanged.connect(self.change_current_type_event)
        for i in range(self.ui.type_combo_box.count()):
            self.ui.type_combo_box.setCurrentIndex(i)
        self.ui.type_combo_box.setCurrentIndex(0)

    def add_initial_data(self):
        """Добавление начальных данных в диаграмму"""
        # Пример данных для демонстрации
        initial_data = {
            "Рабаааааааааааааааааааааааааааааааааааааааааааааота": 25.0,
            "Учеба": 20.0,
            "Отдых": 15.0,
            "Спорт": 10.0,
            "Хобби": 10.0
        }
        
        # Сортируем по убыванию для лучшего отображения
        sorted_data = dict(sorted(initial_data.items(), key=lambda x: x[1], reverse=True))
        
        # Добавляем секторы
        for label, value in sorted_data.items():
            color = self.colors.pop() if self.colors else QtGui.QColor(
                random.randint(50, 200),
                random.randint(50, 200),
                random.randint(50, 200)
            )
            self.chart.add_data_slice(label, value, color)

    def read_config(self, config_path = 'config.json'):
        import json
        with open(config_path, mode='r') as f:
            data = json.load(f)
            return data
        
    def update_type_event(self, event_name, indx = None):
        if not indx:
            self.ui.type_combo_box.addItem(event_name)
            self.update_marker_pie(event_name)
        else:
            self.ui.type_combo_box.setItemText(indx, event_name)
            self.change_current_type_event()

    def update_today_data(self, event_name, add = True, complite_sec = None):
        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()
        
        if not add:
            cursor.execute("UPDATE tasks SET complite_sec=?, last_update=? WHERE event_name=? AND date_day = date('now');",
                        (complite_sec, datetime.now(), event_name,))
        else:
            cursor.execute("UPDATE tasks SET complite_sec=complite_sec+60, last_update=? WHERE event_name=? AND date_day = date('now');",
                        (datetime.now(), event_name,))
        
        connection.commit()
        connection.close()
    
    def get_today_data_for_type(self, event_name):
        connection = sqlite3.connect('main.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM tasks WHERE event_name=? AND date_day = date('now');",(event_name,))
        results = cursor.fetchall()

        if len(results) == 0:
            cursor.execute("""
INSERT INTO tasks (event_name, date_day, complite_sec, hour_week_limit, last_update)
VALUES (?, date('now'), 0, ?, NULL);
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

        cursor.execute("SELECT * FROM tasks WHERE event_name=? AND date_day >= date('now', '-6 days') AND date_day <  date('now', '+1 day');",(event_name,))
        results = cursor.fetchall()
        connection.close()
            
        return results

    def change_current_type_event(self):
        current_type = self.ui.type_combo_box.currentText()
        if not current_type == '':
            max_week_hour_for_type = self.config_data['type_events'][current_type]
            today_data = self.get_today_data_for_type(current_type)
            last_week_data = self.get_last_week_data_for_type(current_type)
            
            self.ui.progress_hour_day.setValue(today_data[0]["complite_sec"])
            sum_week_secs = 0
            for d in last_week_data:
                sum_week_secs+=d["complite_sec"]
                
            self.ui.progress_hour_week.setValue(sum_week_secs)

            self.ui.progress_hour_week.setMaximum(max_week_hour_for_type*3600)
            self.ui.progress_hour_day.setMaximum(int(max_week_hour_for_type*3600/7))

            self.offset = today_data[0]["complite_sec"]*1000
            self.ui.start_button.click()
            self.update_display()
            self.ui.start_button.click()

            # Обновляем диаграмму
            self.update_marker_pie(current_type, today_data[0]["complite_sec"]/(24*36))

    def update_marker_pie(self, event_name='', value=0):
        """Обновление сектора в диаграмме"""
        # Преобразуем секунды в проценты (максимум 24 часа = 100%)
        percentage = min(value / (24 * 3600) * 100, 100)
        
        # Ищем существующий сектор
        for slice in self.chart.data_series.slices():
            if slice.label().split('\n')[0] == event_name:
                # Обновляем существующий
                slice.setValue(percentage)
                slice.setLabel(f"{event_name}\n{percentage:.1f}%")
                return
        
        # Добавляем новый сектор
        if percentage > 0:
            color = self.colors.pop() if self.colors else QtGui.QColor(
                random.randint(50, 200),
                random.randint(50, 200),
                random.randint(50, 200)
            )
            self.chart.add_data_slice(event_name, percentage, color)

    def update_display(self):
        elapsed = self.elapsed_timer.elapsed() + self.offset
        secs = elapsed / 1000
        mins = int(secs // 60)
        hors = int(mins // 60)
        mins %= 60
        secs %= 60
        if secs == 1:
            self.update_today_data(self.ui.type_combo_box.currentText(), add=True)

        msecs = int((secs - int(secs)) * 100)
        text = f"{hors:02d}:{mins:02d}:{int(secs):02d}.{msecs:02d}"
        self.ui.time_number.display(text)

    def on_start_pause(self):
        if self.is_running:
            self.offset += self.elapsed_timer.elapsed()
            self.timer.stop()
            self.ui.start_button.setText("Старт")
            self.is_running = False
        else:
            self.elapsed_timer.start()
            self.timer.start()
            self.ui.start_button.setText("Пауза")
            self.is_running = True

if __name__ == "__main__":
    conn = sqlite3.connect('main.db')
    with open('init.sql', 'r') as f:
        schema = f.read()
        conn.executescript(schema)
    conn.close()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())