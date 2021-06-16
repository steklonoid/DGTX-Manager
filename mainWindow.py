# модуль главного окна
from PyQt5.QtCore import Qt, pyqtSlot, QRectF
from PyQt5.QtWidgets import QWidget, QGridLayout, QStatusBar, QHBoxLayout, QPushButton, QLabel, QSplitter, QOpenGLWidget, QSizePolicy, QGroupBox, QTableView, QAbstractItemView, QHeaderView, QCheckBox
from PyQt5.QtGui import QIcon, QPainter, QStandardItemModel, QStandardItem, QPen, QColor, QFont, QPainterPath, QMouseEvent
from OpenGL import GL
import time

class UiMainWindow(object):
    def __init__(self):
        self.buttonlist = []
        self.numcontbuttonlist = []

    def setupui(self, mainwindow):
        mainwindow.setObjectName("MainWindow")
        mainwindow.setWindowTitle("DLM Center v1.0.1")
        mainwindow.setWindowIcon(QIcon("./images/main_icon.png"))
        mainwindow.resize(800, 400)

        self.centralwidget = QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")
        mainwindow.setCentralWidget(self.centralwidget)

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(1, 1, 1, 1)
        self.gridLayout.setObjectName("gridLayout")

        self.t_pilots = QTableView()
        self.gridLayout.addWidget(self.t_pilots, 0, 0, 1, 1)

        self.t_rockets = QTableView()
        self.gridLayout.addWidget(self.t_rockets, 0, 1, 1, 1)

        self.t_races = QTableView()
        self.gridLayout.addWidget(self.t_races, 1, 0, 1, 2)

        self.button1 = QPushButton()
        self.button1.setText('Get rockets list')
        self.button1.clicked.connect(self.button1_clicked)
        self.gridLayout.addWidget(self.button1, 2, 0, 1, 2)


        self.statusbar = QStatusBar(mainwindow)
        self.statusbar.setObjectName("statusbar")
        mainwindow.setStatusBar(self.statusbar)