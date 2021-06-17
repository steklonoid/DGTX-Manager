# модуль главного окна
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QStatusBar, QPushButton, QLabel, QTableView
from PyQt5.QtGui import QIcon


class UiMainWindow(object):
    def __init__(self):
        self.buttonlist = []
        self.numcontbuttonlist = []

    def setupui(self, mainwindow):
        mainwindow.setObjectName("MainWindow")
        mainwindow.setWindowTitle("DLM Center v1.0.1")
        mainwindow.resize(800, 400)

        self.centralwidget = QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")
        mainwindow.setCentralWidget(self.centralwidget)

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(1, 1, 1, 1)
        self.gridLayout.setObjectName("gridLayout")

        l_pilots = QLabel('Пилоты')
        l_pilots.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_pilots, 0, 0, 1, 1)
        self.t_pilots = QTableView()
        self.gridLayout.addWidget(self.t_pilots, 1, 0, 1, 1)

        l_rockets = QLabel('Ракеты')
        l_rockets.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_rockets, 0, 1, 1, 1)
        self.t_rockets = QTableView()
        self.gridLayout.addWidget(self.t_rockets, 1, 1, 1, 1)

        l_races = QLabel('Полеты')
        l_races.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_races, 2, 0, 1, 2)
        self.t_races = QTableView()
        self.gridLayout.addWidget(self.t_races, 3, 0, 1, 2)

        self.button1 = QPushButton()
        self.button1.setText('Get rockets list')
        self.button1.clicked.connect(self.button1_clicked)
        self.gridLayout.addWidget(self.button1, 4, 0, 1, 2)


        self.statusbar = QStatusBar(mainwindow)
        self.statusbar.setObjectName("statusbar")
        mainwindow.setStatusBar(self.statusbar)