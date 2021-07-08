# модуль главного окна
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QStatusBar, QPushButton, QLabel, QTableView, QHBoxLayout, QAbstractItemView, QTableWidget
from PyQt5.QtGui import QIcon


class UiMainWindow(object):
    def __init__(self):
        self.buttonlist = []
        self.numcontbuttonlist = []

    def setupui(self, mainwindow):
        mainwindow.setObjectName("MainWindow")
        mainwindow.setWindowTitle('DLM Center v' + mainwindow.version)
        # mainwindow.resize(800, 400)

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
        self.t_pilots.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t_pilots.doubleClicked.connect(self.t_pilots_doubleClicked)
        self.gridLayout.addWidget(self.t_pilots, 1, 0, 1, 1)

        l_rockets = QLabel('Ракеты')
        l_rockets.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_rockets, 0, 1, 1, 1)
        self.t_rockets = QTableView()
        self.t_rockets.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.gridLayout.addWidget(self.t_rockets, 1, 1, 1, 1)

        l_managers = QLabel('Менеждеры')
        l_managers.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_managers, 0, 2, 1, 1)
        self.t_managers = QTableView()
        self.t_managers.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.gridLayout.addWidget(self.t_managers, 1, 2, 1, 1)

        l_races = QLabel('Полеты')
        l_races.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.gridLayout.addWidget(l_races, 2, 0, 1, 3)
        self.t_races = QTableView()
        self.t_races.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t_races.clicked.connect(self.t_races_clicked)
        self.gridLayout.addWidget(self.t_races, 3, 0, 1, 3)

        hb_cp1_w = QWidget()
        hb_cp1 = QHBoxLayout()
        hb_cp1_w.setLayout(hb_cp1)
        pb1_cp1 = QPushButton()
        pb1_cp1.setText('Старт')
        hb_cp1.addWidget(pb1_cp1)
        pb2_cp1 = QPushButton()
        pb2_cp1.setText('Стоп')
        hb_cp1.addWidget(pb2_cp1)
        self.gridLayout.addWidget(hb_cp1_w, 4, 0, 1, 3)

        self.pb_enter = QPushButton()
        self.pb_enter.setText('вход не выполнен')
        self.pb_enter.setStyleSheet("color:rgb(255, 96, 96); font: bold 12px;border: none")
        self.pb_enter.setCursor(Qt.PointingHandCursor)
        self.gridLayout.addWidget(self.pb_enter, 0, 3, 1, 1)
        self.pb_enter.clicked.connect(self.buttonLogin_clicked)

        self.t_config = QTableView()
        self.gridLayout.addWidget(self.t_config, 1, 3, 1, 1)

        hb_cp2_w = QWidget()
        hb_cp2 = QHBoxLayout()
        hb_cp2_w.setLayout(hb_cp2)
        pb1_cp2 = QPushButton()
        pb1_cp2.setText('Вниз')
        hb_cp2.addWidget(pb1_cp2)
        pb2_cp2 = QPushButton()
        pb2_cp2.setText('Вверх')
        hb_cp2.addWidget(pb2_cp2)
        self.gridLayout.addWidget(hb_cp2_w, 2, 3, 1, 1)

        self.t_param = QTableView()
        self.gridLayout.addWidget(self.t_param, 3, 3, 2, 1)


        self.statusbar = QStatusBar(mainwindow)
        self.statusbar.setObjectName("statusbar")
        mainwindow.setStatusBar(self.statusbar)