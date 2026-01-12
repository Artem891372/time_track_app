from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
import sys
import colorsys
import random
import sqlite3
from datetime import datetime
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
        # Формула относительной яркости
        luminance = (0.299 * background_color.red() + 
                    0.587 * background_color.green() + 
                    0.114 * background_color.blue()) / 255
        
        # Пороговое значение можно настроить
        return QtGui.QColor(0, 0, 0) if luminance > 0.55 else QtGui.QColor(255, 255, 255)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 400)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
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
        self.timer.setInterval(1000)  # 1000 мс = 1 секунда для обновления времени

        self.elapsed_timer = QtCore.QElapsedTimer()
        self.offset = 0
        self.is_running = False
        self.last_update_time = 0  # Время последнего обновления БД

        self.ui.time_number.setDigitCount(9)  # Для hh:mm:ss.zz
        self.ui.time_number.display("00:00:00")

        self.ui.start_button.clicked.connect(self.on_start_pause)

        self.series = QPieSeries()
        
        self.colors = SimpleColorGenerator.get_colors(100)
        
        data = {"Отдых":100}

        for label, value in data.items():
            slice = QPieSlice(label, value)
            slice.setColor(QtGui.QColor("gray"))
            slice.setLabelPosition(QPieSlice.LabelPosition.LabelInsideNormal)
            slice.setLabel(f"{value}%")
            slice.setLabelFont(QtGui.QFont("Arial", 10))
            slice.setLabelColor(QtGui.QColor("white"))
            
            # Подключаем обработчик события при наведении
            slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))
            
            self.series.append(slice)
        
        # Настройка отображения процентов
        self.series.setLabelsVisible(True)
        # Создаем диаграмму
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.legend().setVisible(True)

        self.chart.legend().setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        for i, marker in enumerate(self.chart.legend().markers()):
            if i < len(data):
                marker.setLabel(list(data.keys())[i])
        
        # Создаем view для диаграммы
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        self.ui.gridLayout.addWidget(self.chart_view, 0, 0, 2, 1)

        # Читаем конфиг и задаем значения для комбобокса
        self.config_data = self.read_config()

        for event_name, hour_week in self.config_data['type_events'].items():
            self.update_type_event(event_name)

        self.ui.type_combo_box.currentIndexChanged.connect(self.change_current_type_event)
        for i in range(self.ui.type_combo_box.count()):
            self.ui.type_combo_box.setCurrentIndex(i)
        self.ui.type_combo_box.setCurrentIndex(0)

        # Загружаем данные для начального типа события
        self.change_current_type_event()

    def read_config(self, config_path='config.json'):
        with open(config_path, mode='r') as f:
            return json.load(f)
        
    def on_slice_hovered(self, state, slice):
        """Обработчик наведения на сектор"""
        if state:
            slice.setExploded(True)
        else:
            slice.setExploded(False)

    def update_type_event(self, event_name, indx=None):
        if not indx:
            self.ui.type_combo_box.addItem(event_name)
            self.update_marker_pie(event_name)
        else:
            self.ui.type_combo_box.setItemText(indx, event_name)
            self.change_current_type_event()

    def update_today_data(self, event_name, complite_sec):
        """Обновляет данные в БД с указанным количеством секунд"""
        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()

        # Получаем текущее время в секундах для этой задачи
        cursor.execute("SELECT complite_sec FROM tasks WHERE event_name=? AND date_day = date('now');", (event_name,))
        result = cursor.fetchone()
        
        current_seconds = result[0] if result else 0
        
        # Обновляем только если время изменилось
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
            # Создаем новую запись, если ее нет
            cursor.execute("""
                INSERT INTO tasks (event_name, date_day, complite_sec, hour_week_limit, start_datetime, last_update)
                VALUES (?, date('now'), 0, ?, NULL, NULL);
            """, (event_name, self.config_data['type_events'][event_name]))

            connection.commit()
            connection.close()
            
            # Повторно запрашиваем данные
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
        if current_type:
            max_week_hour_for_type = self.config_data['type_events'][current_type]
            today_data = self.get_today_data_for_type(current_type)
            last_week_data = self.get_last_week_data_for_type(current_type)
            
            # Устанавливаем прогресс-бары
            completed_seconds_today = today_data[0]["complite_sec"]
            self.ui.progress_hour_day.setValue(completed_seconds_today)
            
            # Вычисляем общее время за неделю
            sum_week_secs = sum(d["complite_sec"] for d in last_week_data)
            self.ui.progress_hour_week.setValue(sum_week_secs)

            # Устанавливаем максимальные значения
            daily_max_seconds = int((max_week_hour_for_type * 3600) / 7)
            weekly_max_seconds = max_week_hour_for_type * 3600
            
            self.ui.progress_hour_day.setMaximum(daily_max_seconds)
            self.ui.progress_hour_week.setMaximum(weekly_max_seconds)

            # Устанавливаем offset для таймера
            self.offset = completed_seconds_today * 1000
            hours = int(completed_seconds_today // 3600)
            minutes = int((completed_seconds_today % 3600) // 60)
            seconds = int(completed_seconds_today % 60)
            
            text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.ui.time_number.display(text)
            self.elapsed_timer.restart()

            # Обновляем диаграмму
            daily_percentage = (completed_seconds_today / daily_max_seconds) * 100 if daily_max_seconds > 0 else 0
            self.update_marker_pie(current_type, daily_percentage, self.ui.type_combo_box.currentIndex() + 1)

    def base_slice_change(self, value):
        """
        Изменение базовой части (отдых)
        
        :param value: Величина на добавление или уменьшение базовой части
        """
        base_slice = self.series.slices()[0]
        base_value = base_slice.value()
        new_value = base_value + value

        if new_value <= 0:
            base_slice.setValue(0)
            base_slice.setLabel("0%")
            self.chart.legend().markers()[0].setVisible(False)
        else:
            base_slice.setValue(new_value)
            base_slice.setLabel(f"{new_value:.1f}%")

    def update_marker_pie(self, event_name='', value=0, indx=None):
        if indx is None:
            # Добавление нового сектора
            slice = QPieSlice(event_name, value)
            slice.setColor(self.colors.pop())
            slice.setLabelPosition(QPieSlice.LabelPosition.LabelInsideNormal)
            slice.setLabel(f"{value:.1f}%")
            slice.setLabelFont(QtGui.QFont("Arial", 10))
            slice.setLabelVisible(True)
            slice.hovered.connect(lambda state, s=slice: self.on_slice_hovered(state, s))
            self.series.append(slice)
            self.chart_view.chart().legend().markers()[-1].setLabel(event_name)
            self.chart_view.chart().legend().setFont(QtGui.QFont("Arial", 8))

            self.base_slice_change(-value)
        else:
            # Обновление существующего сектора
            if indx < len(self.series.slices()):
                current_slice = self.series.slices()[indx]
                current_value = current_slice.value()
                current_slice.setValue(value)
                current_slice.setLabel(f"{value:.1f}%")
                self.base_slice_change(current_value - value)
        
        self.chart_view.update()

    def update_display(self):
        """Обновление отображения времени"""
        if not self.is_running:
            return
            
        elapsed = self.elapsed_timer.elapsed() + self.offset
        total_seconds = elapsed / 1000.0
        
        # Обновляем данные в БД каждую 1 секунду
        current_time = int(total_seconds)
        if current_time >= self.last_update_time + 1:
            current_type = self.ui.type_combo_box.currentText()
            if current_type:
                self.update_today_data(current_type, current_time)
                self.last_update_time = current_time
                # Обновляем отображение прогресса
                self.change_current_type_event()
        
        # Форматирование времени для отображения
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.ui.time_number.display(text)

    def on_start_pause(self):
        """Обработчик нажатия кнопки Старт/Пауза"""
        if self.is_running:
            # Останавливаем таймер
            self.timer.stop()
            self.is_running = False
            self.ui.start_button.setText("Старт")
            
            # Сохраняем текущее время в БД
            current_type = self.ui.type_combo_box.currentText()
            if current_type:
                elapsed = self.elapsed_timer.elapsed() + self.offset
                completed_seconds = int(elapsed / 1000)
                self.update_today_data(current_type, completed_seconds)
        else:
            # Запускаем таймер
            self.elapsed_timer.start()
            self.timer.start()
            self.is_running = True
            self.ui.start_button.setText("Пауза")
            
            # Сбрасываем время последнего обновления
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