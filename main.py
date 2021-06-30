import random
import sys
import os
import time
import queue
import logging

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QSettings, pyqtSlot, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from mainWindow import UiMainWindow
from loginWindow import LoginWindow
from wss import Worker, WSSClient
import hashlib
from Crypto.Cipher import AES # pip install pycryptodome
import math
import numpy as np
from threading import Lock


class MainWindow(QMainWindow, UiMainWindow):
    settings = QSettings("./config.ini", QSettings.IniFormat)   # файл настроек
    lock = Lock()

    flConnect = False           #   флаг нормального соединения с сайтом

    def __init__(self):

        super().__init__()
        logging.basicConfig(filename='info.log', level=logging.INFO, format='%(asctime)s %(message)s')

        # создание визуальной формы
        self.setupui(self)
        self.show()

        self.m_pilots = QStandardItemModel()
        self.m_pilots.setColumnCount(3)
        self.m_pilots.setHorizontalHeaderLabels(['Имя', 'Статус'])
        self.t_pilots.setModel(self.m_pilots)

        self.m_rockets = QStandardItemModel()
        self.m_rockets.setColumnCount(3)
        self.m_rockets.setHorizontalHeaderLabels(['ID', 'Модель', 'Статус'])
        self.t_rockets.setModel(self.m_rockets)

        self.wssclient = WSSClient(self)
        self.wssclient.daemon = True
        self.wssclient.start()

        self.user = ''

    def closeEvent(self, *args, **kwargs):
        pass

    def userlogined(self, user, psw):
        if self.wssclient.flConnect and not self.wssclient.flAuth:
            self.user = user
            str = {'id':1, 'message_type':'registration', 'data':{'typereg':'manager', 'user':user, 'psw':psw}}
            self.wssclient.senddata(str)

    def change_auth_status(self):
        if self.wssclient.flAuth:
            self.pb_enter.setText('вход выполнен: ' + self.user)
            self.pb_enter.setStyleSheet("color:rgb(64, 192, 64); font: bold 12px;border: none")
        else:
            self.pb_enter.setText('вход не выполнен')
            self.pb_enter.setStyleSheet("color:rgb(255, 96, 96); font: bold 12px;border: none")

    @pyqtSlot()
    def buttonLogin_clicked(self):
        rw = LoginWindow()
        rw.userlogined.connect(lambda: self.userlogined(rw.user, rw.psw))
        rw.setupUi()
        rw.exec_()

    def getrocketslist(self, data):
        self.m_rockets.removeRows(0, self.m_rockets.rowCount())
        rownum = 0
        for rocket in data:
            self.m_rockets.appendRow([QStandardItem(), QStandardItem(), QStandardItem()])
            self.m_rockets.item(rownum, 0).setData(rocket['id'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 1).setData(rocket['version'], Qt.DisplayRole)
            self.m_rockets.item(rownum, 2).setData(rocket['status'], Qt.DisplayRole)
            rownum += 1

    def getpilotslist(self, data):
        self.m_pilots.removeRows(0, self.m_pilots.rowCount())
        rownum = 0
        for pilot in data:
            self.m_pilots.appendRow([QStandardItem(), QStandardItem()])
            self.m_pilots.item(rownum, 0).setData(pilot['name'], Qt.DisplayRole)
            self.m_pilots.item(rownum, 1).setData(pilot['status'], Qt.DisplayRole)
            rownum += 1

    def getraceslist(self, data):
        pass

app = QApplication([])
win = MainWindow()
sys.exit(app.exec_())
