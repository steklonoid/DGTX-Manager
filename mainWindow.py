# модуль главного окна
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QStatusBar, QPushButton, QLabel, QTableView, QHBoxLayout, QAbstractItemView, QListView
from PyQt5.QtGui import QIcon

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

        l_pilots = MyLabel('Пилоты')
        l_pilots.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_pilots, 0, 1, 1, 3)
        self.t_pilots = QTableView()
        self.t_pilots.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t_pilots.doubleClicked.connect(self.t_pilots_doubleClicked)
        self.t_pilots.setUpdatesEnabled(True)
        self.gridLayout.addWidget(self.t_pilots, 1, 1, 4, 3)

        l_marketinfo = MyLabel('Рыночная инфа')
        l_marketinfo.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_marketinfo, 0, 4, 1, 4)
        self.t_marketinfo = QTableView()
        self.t_marketinfo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.gridLayout.addWidget(self.t_marketinfo, 1, 4, 4, 4)

        l_parameters_temapates = MyLabel('Шаблоны параметров')
        l_parameters_temapates.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_parameters_temapates, 0, 8, 1, 2)
        self.t_parameters_temapates = QTableView()
        self.t_parameters_temapates.setContextMenuPolicy(Qt.CustomContextMenu)
        self.t_parameters_temapates.customContextMenuRequested.connect(self.t_parameters_temapates_customContextMenuRequested)
        self.gridLayout.addWidget(self.t_parameters_temapates, 1, 8, 4, 2)

        self.pb_enter = QPushButton()
        self.pb_enter.setText('вход не выполнен')
        self.pb_enter.setStyleSheet("color:rgb(255, 96, 96); font: bold 12px;border: none")
        self.pb_enter.setCursor(Qt.PointingHandCursor)
        self.gridLayout.addWidget(self.pb_enter, 5, 0, 1, 1)
        self.pb_enter.clicked.connect(self.buttonLogin_clicked)

        l_rockets = MyLabel('Ракеты')
        l_rockets.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_rockets, 5, 1, 1, 7)
        self.t_rockets = QTableView()
        self.t_rockets.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t_rockets.setUpdatesEnabled(True)
        self.t_rockets.clicked.connect(self.t_rockets_clicked)
        self.gridLayout.addWidget(self.t_rockets, 6, 0, 4, 8)

        l_param = MyLabel('Параметры')
        l_param.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_param, 5, 8, 1, 2)
        self.t_parameters = QTableView()
        self.gridLayout.addWidget(self.t_parameters, 6, 8, 4, 2)



        self.statusbar = QStatusBar(mainwindow)
        self.statusbar.setObjectName("statusbar")
        mainwindow.setStatusBar(self.statusbar)