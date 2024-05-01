from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QLabel, QListView, QStyledItemDelegate, QCheckBox, QGridLayout, QPushButton
from PyQt5.QtCore import QStringListModel, Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QStandardItem, QStandardItemModel, QPainter, QColor, QPen, QClipboard, QIcon, QPixmap
from python_imagesearch.imagesearch import imagesearch, imagesearcharea
import pydirectinput
import pygetwindow as gw
import pyautogui
import threading
import atexit
import psutil
import random
import time
import math
import os
import keyboard
import mouse
import json
import sys

### PROGRAM KAPANIŞINDA İLGİLİ SERVİSLERİ SONLANDIR ###
def shutdown_on_exit():
    try:
        for proc in psutil.process_iter():
            if "Legend.exe" in proc.name():
                proc.terminate()
            if "Python.exe" in proc.name():
                proc.terminate()
    except Exception as e:
        print(f"Error: {e}")
    try:
        current_process = psutil.Process(os.getpid())
        current_process.terminate()
    except Exception as e:
        print(f"Error: {e}")

atexit.register(shutdown_on_exit)
### PROGRAM KAPANIŞINDA İLGİLİ SERVİSLERİ SONLANDIR ###

### OYUNU ÖNE GETİR ###
def bring_window_to_front(window_title):
    windows = pyautogui.getAllTitles()

    for window in windows:
        if window_title.lower() in window.lower():
            pyautogui.getWindowsWithTitle(window)[0].maximize()
            break
    
window_title = "LegendPirates"
#bring_window_to_front(window_title)
#time.sleep(1)
### OYUNU ÖNE GETİR ###

class AreaSelectionWindow(QtWidgets.QMainWindow):
    def __init__(self, json_filename, json_key, index=None):
        super().__init__()

        self.setWindowTitle("Area Selection")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setWindowOpacity(0.5)

        self.selected_area = None
        self.selection_started = False
        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()

        self.json_filename = json_filename
        self.json_key = json_key
        self.index = index

        self.label = QtWidgets.QLabel("Click and drag to select an area. Press ESC to exit.", self)
        self.label.setGeometry(50, 50, 400, 30)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.confirm_button = QtWidgets.QPushButton("ONAYLA", self)
        self.confirm_button.clicked.connect(self.confirm_selection)
        self.confirm_button.setGeometry(0, 0, 100, 30)

        self.coordinates_label = QtWidgets.QLabel("", self)
        self.coordinates_label.setGeometry(0, 40, 400, 30)


    def confirm_selection(self):
        if self.selected_area:
            min_x = self.selected_area.x()
            max_x = self.selected_area.x() + self.selected_area.width()
            min_y = self.selected_area.y()
            max_y = self.selected_area.y() + self.selected_area.height()

            self.coordinates_label.setText(f"Selected Coordinates: ({min_x}, {max_x}, {min_y}, {max_y})")

            with open(self.json_filename, 'r') as f:
                data = json.load(f)

            if self.json_key == "minimap_corners":
                data["minimap_corners"][self.index] = {"x1": min_x, "x2": max_x, "y1": min_y, "y2": max_y}
            elif self.json_key == "map_coordinates":
                data["map_coordinates"][0] = {"x1": min_x, "x2": max_x, "y1": min_y, "y2": max_y}

            with open(self.json_filename, 'w') as f:
                json.dump(data, f, indent=4)

    def mousePressEvent(self, event):
        if not self.selection_started:
            self.start_point = event.pos()
            self.selection_started = True

    def mouseMoveEvent(self, event):
        if self.selection_started:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.selection_started:
            self.end_point = event.pos()
            self.selected_area = QtCore.QRect(self.start_point, self.end_point)
            self.selection_started = False
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 100))
        if self.selection_started:
            painter.setOpacity(1)
            pen = QtGui.QPen(QtCore.Qt.red)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(QtCore.QRect(self.start_point, self.end_point))
        elif self.selected_area:
            painter.setPen(QtCore.Qt.green)
            painter.drawRect(self.selected_area)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            event.accept()
            self.close()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(415, 265)
        MainWindow.setMinimumSize(QtCore.QSize(415, 265))
        MainWindow.setMaximumSize(QtCore.QSize(415, 265))
        MainWindow.setStyleSheet("background-color: #333333;\n"
"color: #ffffff;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 421, 251))
        self.tabWidget.setStyleSheet("QTabWidget {\n"
"    background-color: #222222;\n"
"    color: #ffffff;\n"
"    font-family: Arial;\n"
"    font-size: 10pt;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border: none;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background-color: #444444;\n"
"    color: #ffffff;\n"
"    font-family: Arial;\n"
"    font-size: 11pt;\n"
"    min-width: 120px;   /* Set the minimum width of the tabs */\n"
"    max-width: 150px;  /* Set the maximum width of the tabs */\n"
"    height: 30px;      /* Set the height of the tabs */\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    background-color: #666666;\n"
"}\n"
"\n"
"")
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.pushButton_8 = QtWidgets.QPushButton(self.tab)
        self.pushButton_8.setGeometry(QtCore.QRect(210, 170, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_8.setFont(font)
        self.pushButton_8.setStyleSheet("QPushButton {\n"
"    background-color: #34495e; /* Darker background color */\n"
"    color: white; /* Text color */\n"
"    border: none; /* No border */\n"
"    border-radius: 4px; /* Rounded button shape */\n"
"    padding: 12px 24px; /* Padding for button */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2c3e50; /* Darker background color on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #233140; /* Even darker background color on button press */\n"
"}\n"
"")
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_7 = QtWidgets.QPushButton(self.tab)
        self.pushButton_7.setGeometry(QtCore.QRect(40, 170, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setWhatsThis("")
        self.pushButton_7.setAutoFillBackground(False)
        self.pushButton_7.setStyleSheet("QPushButton {\n"
"    background-color: #34495e; /* Darker background color */\n"
"    color: white; /* Text color */\n"
"    border: none; /* No border */\n"
"    border-radius: 4px; /* Rounded button shape */\n"
"    padding: 12px 24px; /* Padding for button */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2c3e50; /* Darker background color on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #233140;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: #233140; /* Even darker background color when button is checked */\n"
"}")
        self.pushButton_7.setObjectName("pushButton_7")
        self.frame_2 = QtWidgets.QFrame(self.tab)
        self.frame_2.setGeometry(QtCore.QRect(40, 10, 331, 51))
        self.frame_2.setStyleSheet("background-color: #465968;")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.comboBox = QtWidgets.QComboBox(self.frame_2)
        self.comboBox.setGeometry(QtCore.QRect(80, 10, 231, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.comboBox.setFont(font)
        self.comboBox.setStyleSheet("QComboBox QAbstractItemView::item {\n"
"    padding: 50px; /* Adjust the padding to increase the item height */\n"
"}\n"
"")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(20, 0, 51, 51))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.frame_5 = QtWidgets.QFrame(self.tab)
        self.frame_5.setGeometry(QtCore.QRect(40, 70, 331, 91))
        self.frame_5.setStyleSheet("background-color: #465968;")
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.label_3 = QtWidgets.QLabel(self.frame_5)
        self.label_3.setGeometry(QtCore.QRect(0, 0, 331, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.frame_5)
        self.lineEdit_3.setGeometry(QtCore.QRect(205, 43, 111, 31))
        self.lineEdit_3.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.comboBox_2 = QtWidgets.QComboBox(self.frame_5)
        self.comboBox_2.setGeometry(QtCore.QRect(10, 43, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.comboBox_2.setFont(font)
        self.comboBox_2.setStyleSheet("QComboBox QAbstractItemView::item {\n"
"    padding: 50px; /* Adjust the padding to increase the item height */\n"
"}\n"
"")
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.frame_3 = QtWidgets.QFrame(self.tab_2)
        self.frame_3.setGeometry(QtCore.QRect(18, 7, 381, 121))
        self.frame_3.setStyleSheet("background-color: #465968;")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setGeometry(QtCore.QRect(10, 0, 361, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.frame_3)
        self.pushButton.setGeometry(QtCore.QRect(30, 40, 151, 31))
        self.pushButton.setStyleSheet("QPushButton {\n"
"    background-color: #34495e; /* Darker background color */\n"
"    color: white; /* Text color */\n"
"    border: none; /* No border */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2c3e50; /* Darker background color on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #233140;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: #233140; /* Even darker background color when button is checked */\n"
"}")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame_3)
        self.pushButton_2.setGeometry(QtCore.QRect(200, 40, 151, 31))
        self.pushButton_2.setStyleSheet("QPushButton {\n"
"    background-color: #34495e; /* Darker background color */\n"
"    color: white; /* Text color */\n"
"    border: none; /* No border */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2c3e50; /* Darker background color on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #233140;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: #233140; /* Even darker background color when button is checked */\n"
"}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.frame_3)
        self.pushButton_3.setGeometry(QtCore.QRect(200, 78, 151, 31))
        self.pushButton_3.setStyleSheet("QPushButton {\n"
"    background-color: #34495e; /* Darker background color */\n"
"    color: white; /* Text color */\n"
"    border: none; /* No border */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2c3e50; /* Darker background color on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #233140;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: #233140; /* Even darker background color when button is checked */\n"
"}")
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_3)
        self.pushButton_4.setGeometry(QtCore.QRect(30, 78, 151, 31))
        self.pushButton_4.setStyleSheet("QPushButton {\n"
"    background-color: #34495e; /* Darker background color */\n"
"    color: white; /* Text color */\n"
"    border: none; /* No border */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2c3e50; /* Darker background color on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #233140;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: #233140; /* Even darker background color when button is checked */\n"
"}")
        self.pushButton_4.setObjectName("pushButton_4")
        self.frame_4 = QtWidgets.QFrame(self.tab_2)
        self.frame_4.setGeometry(QtCore.QRect(18, 130, 311, 81))
        self.frame_4.setStyleSheet("background-color: #465968;")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.label_7 = QtWidgets.QLabel(self.frame_4)
        self.label_7.setGeometry(QtCore.QRect(10, 0, 291, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_5.setGeometry(QtCore.QRect(80, 40, 151, 31))
        self.pushButton_5.setStyleSheet("QPushButton {\n"
"    background-color: #34495e; /* Darker background color */\n"
"    color: white; /* Text color */\n"
"    border: none; /* No border */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #2c3e50; /* Darker background color on hover */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #233140;\n"
"}\n"
"\n"
"QPushButton:checked {\n"
"    background-color: #233140; /* Even darker background color when button is checked */\n"
"}")
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_6.setGeometry(QtCore.QRect(330, 130, 81, 81))
        self.pushButton_6.setText("")
        self.pushButton_6.setIconSize(QtCore.QSize(64, 64))
        self.pushButton_6.setFlat(True)
        self.pushButton_6.setObjectName("pushButton_6")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        
        self.pushButton.clicked.connect(self.select_area_button1)
        self.pushButton_2.clicked.connect(self.select_area_button2)
        self.pushButton_3.clicked.connect(self.select_area_button3)
        self.pushButton_4.clicked.connect(self.select_area_button4)
        self.pushButton_5.clicked.connect(self.select_area_button5)

    def select_area_button1(self):
        self.area_selection_window = AreaSelectionWindow("coordinates.json", "minimap_corners", index=0)
        self.area_selection_window.show()

    def select_area_button2(self):
        self.area_selection_window = AreaSelectionWindow("coordinates.json", "minimap_corners", index=1)
        self.area_selection_window.show()

    def select_area_button3(self):
        self.area_selection_window = AreaSelectionWindow("coordinates.json", "minimap_corners", index=3)
        self.area_selection_window.show()

    def select_area_button4(self):
        self.area_selection_window = AreaSelectionWindow("coordinates.json", "minimap_corners", index=2)
        self.area_selection_window.show()

    def select_area_button5(self):
        self.area_selection_window = AreaSelectionWindow("coordinates.json", "map_coordinates")
        self.area_selection_window.show()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Legend Pirates Yardımcı"))
        self.pushButton_8.setText(_translate("MainWindow", "Durdur"))
        self.pushButton_7.setText(_translate("MainWindow", "Başlat"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Speaker & Admiral"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Ranger & Admiral"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Elite Voyager"))
        self.comboBox.setItemText(3, _translate("MainWindow", "Boat & Sailor & Viking"))
        self.comboBox.setItemText(4, _translate("MainWindow", "Hazine"))
        self.comboBox.setItemText(5, _translate("MainWindow", "Market"))
        self.label.setText(_translate("MainWindow", "Mod:"))
        self.label_3.setText(_translate("MainWindow", "Market"))
        self.lineEdit_3.setText(_translate("MainWindow", "9999999"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "Explosive Rocket"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "co2"))
        self.comboBox_2.setItemText(2, _translate("MainWindow", "Sailors Salvation"))
        self.comboBox_2.setItemText(3, _translate("MainWindow", "co2"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Genel"))
        self.label_2.setText(_translate("MainWindow", "Minimap köşeleri"))
        self.pushButton.setText(_translate("MainWindow", "..."))
        self.pushButton_2.setText(_translate("MainWindow", "..."))
        self.pushButton_3.setText(_translate("MainWindow", "..."))
        self.pushButton_4.setText(_translate("MainWindow", "..."))
        self.label_7.setText(_translate("MainWindow", "Orta alan"))
        self.pushButton_5.setText(_translate("MainWindow", "..."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Ayarlar"))

        ### AYARLAR ###
        self.pushButton_7.clicked.connect(search_thread_start)
        self.pushButton_8.clicked.connect(search_thread_stop)
        self.pushButton_6.clicked.connect(update_ui_buttons)
        ### AYARLAR ###

minimap_corners = []
map_coordinates = []

with open('coordinates.json') as f:
    data = json.load(f)
    minimap_corners = data.get('minimap_corners', [])
    map_coordinates = data.get('map_coordinates', [])

def update_ui_buttons():
    global minimap_corners, map_coordinates
    with open('coordinates.json') as f:
        data = json.load(f)
        minimap_corners_json = data['minimap_corners']
        map_coordinates_json = data['map_coordinates']

        if minimap_corners:
            first_corner = minimap_corners_json[0]
            x1 = first_corner['x1']
            x2 = first_corner['x2']
            y1 = first_corner['y1']
            y2 = first_corner['y2']
            ui.pushButton.setText(f"{x1}, {x2}, {y1}, {y2}")

            second_corner = minimap_corners_json[1]
            x1 = second_corner['x1']
            x2 = second_corner['x2']
            y1 = second_corner['y1']
            y2 = second_corner['y2']
            ui.pushButton_2.setText(f"{x1}, {x2}, {y1}, {y2}") 

            third_corner = minimap_corners_json[2]
            x1 = third_corner['x1']
            x2 = third_corner['x2']
            y1 = third_corner['y1']
            y2 = third_corner['y2']
            ui.pushButton_4.setText(f"{x1}, {x2}, {y1}, {y2}")

            fourth_corner = minimap_corners_json[3]
            x1 = fourth_corner['x1']
            x2 = fourth_corner['x2']
            y1 = fourth_corner['y1']
            y2 = fourth_corner['y2']
            ui.pushButton_3.setText(f"{x1}, {x2}, {y1}, {y2}")

        if map_coordinates:
            map_list = map_coordinates_json[0]
            x1 = map_list['x1']
            x2 = map_list['x2']
            y1 = map_list['y1']
            y2 = map_list['y2']
            ui.pushButton_5.setText(f"{x1}, {x2}, {y1}, {y2}")

    ################

    with open('coordinates.json') as f:
        data = json.load(f)
        minimap_corners = data.get('minimap_corners', [])
        map_coordinates = data.get('map_coordinates', [])


############################################################

pyautogui.FAILSAFE = False
keep_searching = False
keep_shooting = False

mob_folder = "Resimler/Moblar/"
mob_images = [os.path.join(mob_folder, filename) for filename in os.listdir(mob_folder)]

############################################################

screen_width, screen_height = pyautogui.size()
center_x, center_y = screen_width // 2, screen_height // 2

    
def wander_randomly(min_x, max_x, min_y, max_y):
    random_x = random.randint(min_x, max_x)
    random_y = random.randint(min_y, max_y)
    time.sleep(1.5)
    pyautogui.click(random_x, random_y)

def wander_randomly_2(min_x, max_x, min_y, max_y):
    random_x = random.randint(min_x, max_x)
    random_y = random.randint(min_y, max_y)
    pyautogui.click(random_x, random_y)

last_selected_indices = []

def random_click_away_from_center(ui):
    global last_selected_indices, minimap_corners, map_coordinates, keep_shooting

    outer_loop_break = False

    if ui.comboBox.currentText() != 'Hazine' and ui.comboBox.currentText() != 'Market':
        # seyahat ederken mob tespit ederse loop'tan çık
        if ui.comboBox.currentText() == 'Speaker & Admiral':
            if (
                imagesearch('Resimler/Moblar/speaker.png')[0] != -1 or
                imagesearch('Resimler/Moblar/admiral.png')[0] != -1 or
                imagesearch('Resimler/Kilitlendi/kilitlendi_speaker.png')[0] != -1
            ):
                outer_loop_break = True
                print("Mob tespit edildi.")
        elif ui.comboBox.currentText() == 'Ranger & Admiral':
            if (
                imagesearch('Resimler/Moblar/ranger.png')[0] != -1 or
                imagesearch('Resimler/Moblar/admiral_ranger.png')[0] != -1 or
                imagesearch('Resimler/Kilitlendi/kilitlendi_ranger.png')[0] != -1
            ):
                outer_loop_break = True
                print("Mob tespit edildi.")
        elif ui.comboBox.currentText() == 'Elite Voyager':
            if (
                imagesearch('Resimler/Moblar/elite_voyager.png')[0] != -1 or
                imagesearch('Resimler/Kilitlendi/kilitlendi_elite_voyager.png')[0] != -1
            ):
                outer_loop_break = True
                print("Mob tespit edildi.")


    elif ui.comboBox.currentText() == 'Hazine':
        if imagesearch('Resimler/Diger/hazine_mor.png')[0] != -1:
            outer_loop_break = True
            print("Hazine tespit edildi.")
        if imagesearch('Resimler/Diger/hazine_mor_2.png')[0] != -1:
            outer_loop_break = True
            print("Hazine tespit edildi.")


    if not outer_loop_break:
        while True:
            new_index = random.randint(0, len(minimap_corners) - 1)
            if new_index not in last_selected_indices[-2:]:
                last_selected_indices.append(new_index)
                if len(last_selected_indices) > 2:
                    last_selected_indices.pop(0)
                break

        corner = minimap_corners[new_index]
        min_x, max_x, min_y, max_y = map(int, corner.values())
        wander_randomly(min_x, max_x, min_y, max_y)

        for _ in range(4):
            coordinates = map_coordinates[0]
            min_xx, max_xx, min_yy, max_yy = map(int, coordinates.values())
            wander_randomly_2(min_xx, max_xx, min_yy, max_yy)
            time.sleep(0.15)



        keyboard.press('space')
        keyboard.release('space')
        yolculuk_suresi = 15
        yolculuk_devam = True
        for _ in range(yolculuk_suresi * 2):
            if yolculuk_devam:
                if ui.comboBox.currentText() != 'Hazine' and ui.comboBox.currentText() != 'Market':
                    if ui.comboBox.currentText() == 'Speaker & Admiral':
                        if (
                            imagesearch('Resimler/Moblar/speaker.png')[0] != -1 or
                            imagesearch('Resimler/Moblar/admiral.png')[0] != -1 or
                            imagesearch('Resimler/Kilitlendi/kilitlendi_speaker.png')[0] != -1
                        ):
                            outer_loop_break = True
                            yolculuk_devam = False
                            print("Mob tespit edildi.")
                    elif ui.comboBox.currentText() == 'Ranger & Admiral':
                        if (
                            imagesearch('Resimler/Moblar/ranger.png')[0] != -1 or
                            imagesearch('Resimler/Moblar/admiral_ranger.png')[0] != -1 or
                            imagesearch('Resimler/Kilitlendi/kilitlendi_ranger.png')[0] != -1
                        ):
                            outer_loop_break = True
                            yolculuk_devam = False
                            print("Mob tespit edildi.")
                    elif ui.comboBox.currentText() == 'Elite Voyager':
                        if (
                            imagesearch('Resimler/Moblar/elite_voyager.png')[0] != -1 or
                            imagesearch('Resimler/Kilitlendi/kilitlendi_elite_voyager.png')[0] != -1
                        ):
                            outer_loop_break = True
                            yolculuk_devam = False
                            print("Mob tespit edildi.")
                    if outer_loop_break:
                        break
                elif ui.comboBox.currentText() == 'Hazine':
                    if imagesearch('Resimler/Diger/hazine_mor.png')[0] != -1:
                        outer_loop_break = True
                        print("Hazine tespit edildi.")
                    if imagesearch('Resimler/Diger/hazine_mor_2.png')[0] != -1:
                        outer_loop_break = True
                        print("Hazine tespit edildi.")
            else:
                break
            time.sleep(0.5)
            if outer_loop_break:
                break

############################################################

def attack_mob(mob_image, lock_image):
    mob = imagesearch(mob_image)
    lock = imagesearch(lock_image)

    if mob[0] != -1:
        print(f"[{mob}] found.")
        pyautogui.click(mob[0] + 30, mob[1] - 30) # First click attempt
        time.sleep(0.01)
        pyautogui.click(mob[0] + 40, mob[1] - 20) # Second click attempt
        time.sleep(0.25)

        # Unlocking
        if lock[0] != -1:
            print(f"[{mob}] locked.")
            radius = 110
            counter = 0
            max_attempts = 200
            for _ in range(3):
                random_x = random.randint(mob[0] - radius, mob[0] + radius)
                random_y = random.randint(mob[1] - radius, mob[1] + radius)
                
                while not (70 <= random_x <= 1130 and 100 <= random_y <= 600):
                    random_x = random.randint(mob[0] - radius, mob[0] + radius)
                    random_y = random.randint(mob[1] - radius, mob[1] + radius)

                    counter += 1
                    print(counter)
                    if counter >= max_attempts:
                        break

                time.sleep(0.2)
                random_x = max(70, min(random_x, 1130))
                random_y = max(100, min(random_y, 600))
                pyautogui.click(random_x, random_y)

            while lock[0] != -1:
                lock = imagesearch(lock_image)
                if lock[0] == -1:
                    break
                time.sleep(0.5)
    else:
        print(f"[{mob}] not found.")
    

############################################################

def search(ui):
    global keep_shooting

    # Kesilme kontrolü
    canlan = imagesearch('Resimler/Diger/canlan.png')
    if canlan[0] != -1: 
        pyautogui.click(canlan[0], canlan[1])
        time.sleep(0.2)
        pyautogui.click(canlan[0], canlan[1])
        time.sleep(3)

        keyboard.press('q')
        keyboard.release('q')
        time.sleep(60)


    # Hazine seçiliyse
    if ui.comboBox.currentText() == 'Hazine':
        hazine_mor = imagesearch('Resimler/Diger/hazine_mor.png')
        hazine_mor_2 = imagesearch('Resimler/Diger/hazine_mor_2.png')

        if hazine_mor[0] != -1:
            keyboard.press('a')
            keyboard.release('a')
            time.sleep(0.5)
            hazine_mor = imagesearch('Resimler/Diger/hazine_mor.png')
            if hazine_mor[0] != -1:
                pyautogui.click(hazine_mor[0] + 7, hazine_mor[1] + 7)
                time.sleep(0.25)
                pyautogui.click(hazine_mor[0] + 7, hazine_mor[1] + 7)
                max_errors = 0
                continue_search = True
                while continue_search and max_errors <= 7:
                    try:
                        collected = imagesearch("Resimler/Diger/collected.png")
                        if collected[0] != -1:
                            continue_search = False
                            time.sleep(1)
                        else:
                            max_errors += 1
                            time.sleep(1)
                    except Exception as e:
                        print(f"Resim ararken sistem hatası: {str(e)}")
                        time.sleep(1)
                keyboard.press('space')
                keyboard.release('space')

            # captcha #
            detected = imagesearch('Resimler/Captcha/detected.png')
            if detected[0] != -1:
                captcha = True
                pyautogui.moveTo(detected[0], detected[1], duration=0.35)
                pyautogui.click(detected[0], detected[1])
                time.sleep(2)

                captcha_hold = imagesearch('Resimler/Captcha/hold.png')
                captcha_checkbox = imagesearch('Resimler/Captcha/checkbox.png')
                if captcha_hold[0] != -1:
                    pyautogui.moveTo(captcha_hold[0], captcha_hold[1], duration=0.35)
                    pyautogui.mouseDown()
                    time.sleep(6)
                    pyautogui.mouseUp()
                    print("Hold çözüldü.")
                    captcha = False
                if captcha_checkbox[0] != -1:
                    pyautogui.moveTo(captcha_checkbox[0], captcha_checkbox[1], duration=0.35)
                    pyautogui.click(captcha_checkbox[0], captcha_checkbox[1])
                    print("Checkbox çözüldü.")
                    captcha = False
            # captcha #

        elif hazine_mor_2[0] != -1:
            keyboard.press('a')
            keyboard.release('a')
            time.sleep(0.5)
            hazine_mor_2 = imagesearch('Resimler/Diger/hazine_mor_2.png')
            if hazine_mor_2[0] != -1:
                pyautogui.click(hazine_mor_2[0] + 7, hazine_mor_2[1] + 7)
                time.sleep(0.25)
                pyautogui.click(hazine_mor_2[0] + 7, hazine_mor_2[1] + 7)
                max_errors = 0
                continue_search = True
                while continue_search and max_errors <= 7:
                    try:
                        collected = imagesearch("Resimler/Diger/collected.png")
                        if collected[0] != -1:
                            continue_search = False
                            time.sleep(1)
                        else:
                            max_errors += 1
                            time.sleep(1)
                    except Exception as e:
                        print(f"Resim ararken sistem hatası: {str(e)}")
                        time.sleep(1)
                keyboard.press('space')
                keyboard.release('space')

            # captcha #
            detected = imagesearch('Resimler/Captcha/detected.png')
            if detected[0] != -1:
                captcha = True
                pyautogui.moveTo(detected[0], detected[1], duration=0.35)
                pyautogui.click(detected[0], detected[1])
                time.sleep(2)

                captcha_hold = imagesearch('Resimler/Captcha/hold.png')
                captcha_checkbox = imagesearch('Resimler/Captcha/checkbox.png')
                if captcha_hold[0] != -1:
                    pyautogui.moveTo(captcha_hold[0], captcha_hold[1], duration=0.35)
                    pyautogui.mouseDown()
                    time.sleep(6)
                    pyautogui.mouseUp()
                    print("Hold çözüldü.")
                    captcha = False
                if captcha_checkbox[0] != -1:
                    pyautogui.moveTo(captcha_checkbox[0], captcha_checkbox[1], duration=0.35)
                    pyautogui.click(captcha_checkbox[0], captcha_checkbox[1])
                    print("Checkbox çözüldü.")
                    captcha = False
            # captcha #

        elif hazine_mor[0] == -1:
            print("Seyahat ediliyor. (Hazine)")
            random_click_away_from_center(ui)


    # Market seçiliyse
    elif ui.comboBox.currentText() == 'Market':
        while ui.comboBox.currentText() == 'Market':
            border_left = 381
            border_top = 241
            border_right = 958
            border_bottom = 665

            section_lenght = border_right - border_left
            buy_button = section_lenght // 4
            section_height = (border_bottom - border_top) // 8
            sections = []

            for i in range(8):
                top = border_top + i * section_height
                bottom = border_top + (i + 1) * section_height
                sections.append((border_left, top, border_right, bottom))

            co2 = 'Resimler/market/co2.png'
            explosive = 'Resimler/market/explosive.png'
            deceleration = 'Resimler/market/deceleration.png'
            salvation = 'Resimler/market/salvation.png'
            sold_out = 'Resimler/market/sold_out.png'

            selected_item = ui.comboBox_2.currentText()

            for section in sections:
                buy_item = None
                ran_out = None

                if selected_item == "Explosive Rocket":
                    buy_item = imagesearcharea(explosive, *section)
                elif selected_item == "Deceleration Rocket":
                    buy_item = imagesearcharea(deceleration, *section)
                elif selected_item == "Sailors Salvation":
                    buy_item = imagesearcharea(salvation, *section)
                elif selected_item == "co2":
                    buy_item = imagesearcharea(co2, *section)

                if buy_item and buy_item[0] != -1:
                    ran_out = imagesearcharea(sold_out, *section)
                    if ran_out and ran_out[0] != -1:
                        print(f"[{selected_item}] Hepsi satılmış.")
                    else:
                        center_x = (section[0] + section[2]) / 2 + (buy_button * 1.5)  # x coordinate calculation
                        center_y_amount = (section[1] + section[3]) / 2 - 10  # y amount entry coordinate
                        center_y_buy = (section[1] + section[3]) / 2 + 10  # y buy button coordinate

                        pyautogui.click(center_x, center_y_amount)  # click on amount entry
                        time.sleep(0.25)
                        integer_value = int(ui.lineEdit_3.text())
                        pyautogui.typewrite(str(integer_value))
                        time.sleep(0.25)
                        pyautogui.click(center_x, center_y_buy)  # click on buy button
                        print(f"[{selected_item}] Satın alındı.")
                else:
                    print(f"[{selected_item}] bulunamadı.")
            time.sleep(2)


    # Hazine ve Market seçili değilse
    elif ui.comboBox.currentText() != 'Hazine' and ui.comboBox.currentText() != 'Market':
        speaker = imagesearch('Resimler/Moblar/speaker.png')
        admiral = imagesearch('Resimler/Moblar/admiral.png')

        if ui.comboBox.currentText() == 'Speaker & Admiral':
            if admiral[0] != -1: ### admiral
                keyboard.press('a')
                keyboard.release('a')
                time.sleep(0.5)
                admiral = imagesearch('Resimler/Moblar/admiral.png')

                print(f"[{admiral}] bulundu.")
                pyautogui.click(admiral[0] + 30, admiral[1] - 30) # 1. tıklama denemesi
                time.sleep(0.01)
                pyautogui.click(admiral[0] + 40, admiral[1] - 20) # 2. tıklama denemesi
                time.sleep(0.25)

                kilitlendi_admiral = imagesearch('Resimler/Kilitlendi/kilitlendi_speaker.png')
                if kilitlendi_admiral[0] != -1:
                    print(f"[{admiral}] kilitlendi.")
                    yaricap = 90
                    counter = 0
                    max_attempts = 200
                    for _ in range(3):
                        random_x = random.randint(speaker[0] - yaricap, admiral[0] + yaricap)
                        random_y = random.randint(speaker[1] - yaricap, admiral[1] + yaricap)
                        
                        while not (70 <= random_x <= 1130 and 100 <= random_y <= 600):
                            random_x = random.randint(speaker[0] - yaricap, admiral[0] + yaricap)
                            random_y = random.randint(speaker[1] - yaricap, admiral[1] + yaricap)

                            counter += 1
                            print(counter)
                            if counter >= max_attempts:
                                break

                        time.sleep(0.2)
                        random_x = max(70, min(random_x, 1130))
                        random_y = max(100, min(random_y, 600))
                        pyautogui.click(random_x, random_y)

                    keyboard.press('space')
                    keyboard.release('space')

                    while kilitlendi_admiral[0] != -1:
                        kilitlendi_admiral = imagesearch('Resimler/Kilitlendi/kilitlendi_speaker.png')
                        if kilitlendi_admiral[0] == -1:
                            break
                        time.sleep(0.5)


            elif speaker[0] != -1:
                keyboard.press('a')
                keyboard.release('a')
                time.sleep(0.5)
                speaker = imagesearch('Resimler/Moblar/speaker.png')

                print(f"[{speaker}] bulundu.")
                pyautogui.click(speaker[0] + 30, speaker[1] - 30) # 1. tıklama denemesi
                time.sleep(0.01)
                pyautogui.click(speaker[0] + 40, speaker[1] - 20) # 2. tıklama denemesi
                time.sleep(0.25)

                #speaker
                kilitlendi_speaker = imagesearch('Resimler/Kilitlendi/kilitlendi_speaker.png')
                if kilitlendi_speaker[0] != -1:
                    print(f"[{speaker}] kilitlendi.")
                    # Diğer işlemler
                    yaricap = 90
                    counter = 0
                    max_attempts = 200
                    for _ in range(3):
                        random_x = random.randint(speaker[0] - yaricap, speaker[0] + yaricap)
                        random_y = random.randint(speaker[1] - yaricap, speaker[1] + yaricap)
                        
                        while not (70 <= random_x <= 1130 and 100 <= random_y <= 600):
                            random_x = random.randint(speaker[0] - yaricap, speaker[0] + yaricap)
                            random_y = random.randint(speaker[1] - yaricap, speaker[1] + yaricap)

                            counter += 1
                            print(counter)
                            if counter >= max_attempts:
                                break

                        time.sleep(0.2)
                        random_x = max(70, min(random_x, 1130))
                        random_y = max(100, min(random_y, 600))
                        pyautogui.click(random_x, random_y)

                    keyboard.press('space')
                    keyboard.release('space')

                    while kilitlendi_speaker[0] != -1:
                        kilitlendi_speaker = imagesearch('Resimler/Kilitlendi/kilitlendi_speaker.png')
                        if kilitlendi_speaker[0] == -1:
                            break
                        time.sleep(0.5)


            elif speaker[0] == -1 and admiral[0] == -1:
                print("Seyahat ediliyor.")
                time.sleep(5)
                keyboard.press('q')
                keyboard.release('q')
                random_click_away_from_center(ui)


        elif ui.comboBox.currentText() == 'Ranger & Admiral':
            ranger = imagesearch('Resimler/Moblar/ranger.png')
            admiral_ranger = imagesearch('Resimler/Moblar/admiral_ranger.png')

            if ranger[0] != -1: ### rangeree
                keyboard.press('a')
                keyboard.release('a')
                time.sleep(0.5)
                ranger = imagesearch('Resimler/Moblar/ranger.png')

                print(f"[{ranger}] bulundu.")
                pyautogui.click(ranger[0] + 30, ranger[1] - 30) # 1. tıklama denemesi
                time.sleep(0.01)
                pyautogui.click(ranger[0] + 40, ranger[1] - 20) # 2. tıklama denemesi
                time.sleep(0.25)

                kilitlendi_ranger = imagesearch('Resimler/Kilitlendi/kilitlendi_ranger.png')
                if kilitlendi_ranger[0] != -1:
                    print(f"[{ranger}] kilitlendi.")
                    yaricap = 90
                    counter = 0
                    max_attempts = 200
                    for _ in range(3):
                        random_x = random.randint(ranger[0] - yaricap, ranger[0] + yaricap)
                        random_y = random.randint(ranger[1] - yaricap, ranger[1] + yaricap)
                        
                        while not (70 <= random_x <= 1130 and 100 <= random_y <= 600):
                            random_x = random.randint(ranger[0] - yaricap, ranger[0] + yaricap)
                            random_y = random.randint(ranger[1] - yaricap, ranger[1] + yaricap)

                            counter += 1
                            print(counter)
                            if counter >= max_attempts:
                                break

                        time.sleep(0.2)
                        random_x = max(70, min(random_x, 1130))
                        random_y = max(100, min(random_y, 600))
                        pyautogui.click(random_x, random_y)

                    keyboard.press('space')
                    keyboard.release('space')

                    while kilitlendi_ranger[0] != -1:
                        kilitlendi_ranger = imagesearch('Resimler/Kilitlendi/kilitlendi_ranger.png')
                        if kilitlendi_ranger[0] == -1:
                            break
                        time.sleep(0.5)

            elif admiral_ranger[0] != -1: ### admrial ranger
                keyboard.press('a')
                keyboard.release('a')
                time.sleep(0.5)
                admiral_ranger = imagesearch('Resimler/Moblar/admiral_ranger.png')

                print(f"[{admiral_ranger}] bulundu.")
                pyautogui.click(admiral[0] + 30, admiral[1] - 30) # 1. tıklama denemesi
                time.sleep(0.01)
                pyautogui.click(admiral[0] + 40, admiral[1] - 20) # 2. tıklama denemesi
                time.sleep(0.25)

                kilitlendi_ranger = imagesearch('Resimler/Kilitlendi/kilitlendi_ranger.png') # mecbur kendimde bakıyım buna hocam anlayamadım
                if kilitlendi_ranger[0] != -1:
                    print(f"[{kilitlendi_ranger}] kilitlendi.")
                    yaricap = 110
                    counter = 0
                    max_attempts = 200
                    for _ in range(3):
                        random_x = random.randint(admiral[0] - yaricap, admiral[0] + yaricap)
                        random_y = random.randint(admiral[1] - yaricap, admiral[1] + yaricap)
                        
                        while not (70 <= random_x <= 1130 and 100 <= random_y <= 600):
                            random_x = random.randint(admiral[0] - yaricap, admiral[0] + yaricap)
                            random_y = random.randint(admiral[1] - yaricap, admiral[1] + yaricap)
                            
                            counter += 1
                            print(counter)
                            if counter >= max_attempts:
                                break

                        time.sleep(0.2)
                        random_x = max(70, min(random_x, 1130))
                        random_y = max(100, min(random_y, 600))
                        pyautogui.click(random_x, random_y)

                    keyboard.press('space')
                    keyboard.release('space')

                    while kilitlendi_admiral_ranger[0] != -1:
                        kilitlendi_admiral_ranger = imagesearch('Resimler/Kilitlendi/kilitlendi_ranger.png')
                        if kilitlendi_ranger[0] == -1:
                            break
                        time.sleep(0.5)

            elif ranger[0] == -1 and admiral_ranger[0] == -1:
                print("Seyahat ediliyor.")
                time.sleep(3)
                keyboard.press('q')
                keyboard.release('q')
                random_click_away_from_center(ui)


        elif ui.comboBox.currentText() == 'Elite Voyager':
            elite_voyager = imagesearch('Resimler/Moblar/elite_voyager.png')

            if elite_voyager[0] != -1: ### elite_voyager
                keyboard.press('a')
                keyboard.release('a')
                time.sleep(0.5)
                elite_voyager = imagesearch('Resimler/Moblar/elite_voyager.png')

                print(f"[{elite_voyager}] bulundu.")
                pyautogui.click(elite_voyager[0] + 30, elite_voyager[1] - 30) # 1. tıklama denemesi
                time.sleep(0.01)
                pyautogui.click(elite_voyager[0] + 40, elite_voyager[1] - 20) # 2. tıklama denemesi
                time.sleep(0.25)

                kilitlendi_elite_voyager = imagesearch('Resimler/Kilitlendi/kilitlendi_elite_voyager.png')
                if kilitlendi_elite_voyager[0] != -1:
                    print(f"[{elite_voyager}] kilitlendi.")
                    yaricap = 90
                    counter = 0
                    max_attempts = 200
                    for _ in range(3):
                        random_x = random.randint(elite_voyager[0] - yaricap, elite_voyager[0] + yaricap)
                        random_y = random.randint(elite_voyager[1] - yaricap, elite_voyager[1] + yaricap)
                        
                        while not (70 <= random_x <= 1130 and 100 <= random_y <= 600):
                            random_x = random.randint(elite_voyager[0] - yaricap, elite_voyager[0] + yaricap)
                            random_y = random.randint(elite_voyager[1] - yaricap, elite_voyager[1] + yaricap)

                            counter += 1
                            print(counter)
                            if counter >= max_attempts:
                                break

                        time.sleep(0.2)
                        if elite_voyager[0] != -1:
                            random_x = max(70, min(random_x, 1130))
                            random_y = max(100, min(random_y, 600))
                            pyautogui.click(random_x, random_y)
                        elite_voyager = imagesearch('Resimler/Moblar/elite_voyager.png')

                    keyboard.press('space')
                    keyboard.release('space')

                    def distance(point1, point2):
                        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

                    saved_location = None

                    screen_width, screen_height = pyautogui.size()
                    left = screen_width // 4
                    top = screen_height // 4
                    right = left * 3 
                    bottom = top * 3

                    while kilitlendi_elite_voyager[0] != -1:
                        ### kilitliyken devamlı yakınında kal ###
                        counter = 0
                        max_attempts = 200
                        for _ in range(3):
                            random_x = random.randint(elite_voyager[0] - yaricap, elite_voyager[0] + yaricap)
                            random_y = random.randint(elite_voyager[1] - yaricap, elite_voyager[1] + yaricap)
                            
                            while not (70 <= random_x <= 1130 and 100 <= random_y <= 600):
                                random_x = random.randint(elite_voyager[0] - yaricap, elite_voyager[0] + yaricap)
                                random_y = random.randint(elite_voyager[1] - yaricap, elite_voyager[1] + yaricap)
                                counter += 1
                                print(counter)
                                if counter >= max_attempts:
                                    break

                            time.sleep(0.2)
                            kilitlendi_elite_voyager = imagesearch('Resimler/Kilitlendi/kilitlendi_elite_voyager.png')
                            if elite_voyager[0] != -1:
                                pyautogui.click(random_x + left, random_y + top)
                            elif kilitlendi_elite_voyager[0] == -1: 
                                break

                            elite_voyager = imagesearcharea('Resimler/Moblar/elite_voyager.png', left, top, right, bottom)
                        kilitlendi_elite_voyager = imagesearch('Resimler/Kilitlendi/kilitlendi_elite_voyager.png')
                        time.sleep(1)
                        ### kilitliyken devamlı yakınında kal ###

                        if kilitlendi_elite_voyager[0] == -1:
                            break

            elif elite_voyager[0] == -1:
                print("Seyahat ediliyor.")
                random_click_away_from_center(ui)

############################################################

def popup_start():
    while ui.comboBox.currentText() != 'Market':
        x_button = imagesearch('Resimler/Diger/kapat.png')
        x_button_2 = imagesearch('Resimler/Diger/kapat2.png')
        if x_button[0] != -1:
            pyautogui.click(x_button[0], x_button[1])
            time.sleep(0.25)
        elif x_button_2[0] != -1:
            pyautogui.click(x_button_2[0], x_button_2[1])
            time.sleep(0.25)
        time.sleep(1)

captcha = False
def captcha_start():
    global captcha
    while True:
        """detected = imagesearch('Resimler/Captcha/detected.png')
        if detected[0] != -1:
            captcha = True
            pyautogui.moveTo(detected[0], detected[1], duration=0.35)
            pyautogui.click(detected[0], detected[1])
            time.sleep(2)

            captcha_hold = imagesearch('Resimler/Captcha/hold.png')
            captcha_checkbox = imagesearch('Resimler/Captcha/checkbox.png')
            if captcha_hold[0] != -1:
                pyautogui.moveTo(captcha_hold[0], captcha_hold[1], duration=0.35)
                pyautogui.mouseDown()
                time.sleep(6)
                pyautogui.mouseUp()
                print("Hold çözüldü.")
                captcha = False
            if captcha_checkbox[0] != -1:
                pyautogui.moveTo(captcha_checkbox[0], captcha_checkbox[1], duration=0.35)
                pyautogui.click(captcha_checkbox[0], captcha_checkbox[1])
                print("Checkbox çözüldü.")
                captcha = False"""
        time.sleep(9999)


def search_start():
    global keep_searching, captcha
    pyautogui.click(300,300)
    while keep_searching:
        search(ui)

def search_thread_start():
    global keep_searching, keep_shooting
    keep_searching = True
    keep_shooting = True
    thread1 = threading.Thread(target=search_start)
    thread2 = threading.Thread(target=shoot_start)
    thread3 = threading.Thread(target=popup_start)
    thread4 = threading.Thread(target=captcha_start)
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

def search_stop():
    global keep_searching, keep_shooting
    keep_searching = False
    keep_shooting = False

def search_thread_stop():
    print("Durduruluyor.")
    thread1_ = threading.Thread(target=search_stop)
    thread1_.start()
    print("Durduruldu.")

############################################################

def shoot():
    time.sleep(0.2)
    # ateş et
    keyboard.press('e')
    keyboard.release('e')

def shoot_start():
    global keep_shooting
    while keep_shooting:
        shoot()

def shoot_thread_start():
    global keep_shooting
    keep_shooting = True
    thread2 = threading.Thread(target=shoot_start)
    thread2.start()

def shoot_stop():
    global keep_shooting
    keep_shooting = False

def shoot_thread_stop():
    thread2_ = threading.Thread(target=shoot_stop)
    thread2_.start()

############################################################

"""def shutdown_app(event=None):
    print("Program kapatılıyor.")
    QtWidgets.QApplication.quit()"""

############################################################


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    image_path = "Resimler/renew.png"
    icon = QIcon(image_path)
    ui.pushButton_6.setIcon(icon)

    #keyboard.on_press_key("delete", lambda event: shutdown_app())

    sys.exit(app.exec_())