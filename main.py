from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
import sys
import colorsys
import random
import sqlite3
from datetime import datetime

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
        self.timer.setInterval(10)  # 10 мс для миллисекунд

        self.elapsed_timer = QtCore.QElapsedTimer()
        self.offset = 0
        self.is_running = False

        self.ui.time_number.setDigitCount(11)  # Для mm:ss.zzz
        self.ui.time_number.display("00:00:00.00")

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

    def read_config(self, config_path = 'config.json'):
        import json

        with open(config_path, mode='r') as f:
            data = json.load(f)
            return data
        
    def on_slice_hovered(self, state, slice):
        """Обработчик наведения на сектор"""
        if state:
            slice.setExploded(True)
        else:
            slice.setExploded(False)

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
        
        cursor.execute("UPDATE tasks SET start_datetime = datetime('now', 'localtime') WHERE complite_sec=0;")

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
            self.ui.progress_hour_day.setMaximum(int(max_week_hour_for_type*(3600/7)))

            self.offset = today_data[0]["complite_sec"]*1000
            self.elapsed_timer.restart()
            self.update_display()

            self.update_marker_pie(current_type, today_data[0]["complite_sec"]/(24*36), self.ui.type_combo_box.currentIndex()+1)

    def base_slice_change(self, value):
        """
        Docstring для base_slice_change
        
        :param value: Величина на добавление или уменьшение базовой части
        """

        base_value = self.series.slices()[0].value()
        new_value = base_value + value

        if new_value <= 0:
            slice = self.series.slices()[0]
            slice.setValue(0)
            slice.setLabel(f"0%")
            self.chart.legend().markers()[0].setVisible(False)
        else:
            slice = self.series.slices()[0]
            slice.setValue(new_value)
            slice.setLabel(f"{new_value:.1f}%")

    def update_marker_pie(self, event_name = '', value = 0, indx = None):
        if not indx:
            value = float(value)
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
            current_value = self.series.slices()[indx].value()
            self.series.slices()[indx].setValue(value)
            self.base_slice_change(current_value-value)
        
        self.chart_view.update()

    def update_display(self):
        elapsed = self.elapsed_timer.elapsed() + self.offset
        secs = elapsed / 1000
        mins = int(secs // 60)
        hors = int(mins // 60)
        mins %= 60
        secs %= 60
        hors %= 24
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
