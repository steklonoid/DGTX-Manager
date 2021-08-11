# модуль главного окна
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QStatusBar, QPushButton, QLabel, QTableView, QAbstractItemView, QListView
from PyQt5.QtGui import QFont

class MyLabel(QLabel):
    def __init__(self, text=None):
        QLabel.__init__(self)
        self.setText(text)
        self.setMaximumHeight(20)

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

        l_managers = MyLabel('Менеждеры')
        l_managers.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_managers, 0, 0, 1, 1)
        self.lv_managers = QListView()
        self.lv_managers.setMaximumWidth(100)
        self.gridLayout.addWidget(self.lv_managers, 1, 0, 4, 1)

        l_marketinfo = MyLabel('Рыночная инфа')
        l_marketinfo.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_marketinfo, 0, 1, 1, 3)
        self.t_marketinfo = QTableView()
        self.t_marketinfo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.gridLayout.addWidget(self.t_marketinfo, 1, 1, 4, 3)

        l_parameters_temapates = MyLabel('Шаблоны параметров')
        l_parameters_temapates.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_parameters_temapates, 0, 4, 1, 4)
        self.t_parameters_temapates = QTableView()
        self.t_parameters_temapates.setContextMenuPolicy(Qt.CustomContextMenu)
        self.t_parameters_temapates.customContextMenuRequested.connect(self.t_parameters_temapates_customContextMenuRequested)
        self.gridLayout.addWidget(self.t_parameters_temapates, 1, 4, 4, 4)

        l_param = MyLabel('Параметры')
        l_param.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_param, 0, 8, 1, 2)
        self.t_parameters = QTableView()
        self.t_parameters.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.gridLayout.addWidget(self.t_parameters, 1, 8, 4, 2)

        self.pb_enter = QPushButton()
        self.pb_enter.setText('вход не выполнен')
        self.pb_enter.setCursor(Qt.PointingHandCursor)
        self.gridLayout.addWidget(self.pb_enter, 5, 0, 1, 1)
        self.pb_enter.clicked.connect(self.buttonLogin_clicked)

        self.l_serveraddress = QLabel(mainwindow.serveraddress)
        self.gridLayout.addWidget(self.l_serveraddress, 5, 1, 1, 1)
        self.l_serverport = QLabel(mainwindow.serverport)
        self.gridLayout.addWidget(self.l_serverport, 5, 2, 1, 1)
        self.l_core = QLabel('Нет соединения с ядром')
        self.l_core.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(self.l_core, 5, 3, 1, 1)
        self.l_pilot = QLabel()
        self.l_pilot.setFont(QFont("Helvetica", 12, QFont.Bold))
        self.gridLayout.addWidget(self.l_pilot, 5, 6, 1, 1)

        self.t_rockets = QTableView()
        self.t_rockets.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t_rockets.setContextMenuPolicy(Qt.CustomContextMenu)
        self.t_rockets.customContextMenuRequested.connect(self.t_rockets_customContextMenuRequested)
        self.t_rockets.clicked.connect(self.t_rockets_clicked)
        self.gridLayout.addWidget(self.t_rockets, 6, 0, 4, 10)

        self.statusbar = QStatusBar(mainwindow)
        self.statusbar.setObjectName("statusbar")
        mainwindow.setStatusBar(self.statusbar)