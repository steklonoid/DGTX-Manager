# модуль главного окна
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QStatusBar, QPushButton, QLabel, QTableView, QHBoxLayout, QAbstractItemView, QListView
from PyQt5.QtGui import QIcon


class UiMainWindow(object):
    def __init__(self):
        self.buttonlist = []
        self.numcontbuttonlist = []

    def setupui(self, mainwindow):
        mainwindow.setObjectName("MainWindow")
        mainwindow.setWindowTitle('DLM Center v' + mainwindow.version)
        mainwindow.resize(1200, 800)

        self.centralwidget = QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")
        mainwindow.setCentralWidget(self.centralwidget)

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(1, 1, 1, 1)
        self.gridLayout.setObjectName("gridLayout")

        l_managers = QLabel('Менеждеры')
        l_managers.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_managers, 0, 0, 1, 1)
        self.lt_managers = QListView()
        self.lt_managers.setMaximumWidth(100)
        self.gridLayout.addWidget(self.lt_managers, 1, 0, 4, 1)

        l_pilots = QLabel('Пилоты')
        l_pilots.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_pilots, 0, 1, 1, 3)
        self.t_pilots = QTableView()
        self.t_pilots.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t_pilots.doubleClicked.connect(self.t_pilots_doubleClicked)
        self.t_pilots.setUpdatesEnabled(True)
        self.gridLayout.addWidget(self.t_pilots, 1, 1, 4, 3)

        l_marketinfo = QLabel('Рыночная инфа')
        l_marketinfo.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_marketinfo, 0, 4, 1, 4)
        self.t_marketinfo = QTableView()
        self.t_marketinfo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.gridLayout.addWidget(self.t_marketinfo, 1, 4, 4, 6)

        self.pb_enter = QPushButton()
        self.pb_enter.setText('вход не выполнен')
        self.pb_enter.setStyleSheet("color:rgb(255, 96, 96); font: bold 12px;border: none")
        self.pb_enter.setCursor(Qt.PointingHandCursor)
        self.gridLayout.addWidget(self.pb_enter, 0, 8, 1, 2)
        self.pb_enter.clicked.connect(self.buttonLogin_clicked)

        l_rockets = QLabel('Ракеты')
        l_rockets.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_rockets, 5, 0, 1, 8)
        self.t_rockets = QTableView()
        self.t_rockets.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t_rockets.setUpdatesEnabled(True)
        self.t_rockets.clicked.connect(self.t_rockets_clicked)
        self.gridLayout.addWidget(self.t_rockets, 6, 0, 4, 8)

        l_param = QLabel('Параметры')
        l_param.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_param, 5, 8, 1, 2)
        self.t_param = QTableView()
        self.gridLayout.addWidget(self.t_param, 6, 8, 4, 2)



        self.statusbar = QStatusBar(mainwindow)
        self.statusbar.setObjectName("statusbar")
        mainwindow.setStatusBar(self.statusbar)